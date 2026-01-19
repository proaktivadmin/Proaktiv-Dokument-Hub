"""
Sync Proaktiv offices and employees from proaktiv.no/eiendomsmegler.

Defaults are conservative to avoid hammering the site.

Run with:
  python -m scripts.sync_proaktiv_directory --dry-run
  python -m scripts.sync_proaktiv_directory --max-pages 120 --delay-ms 1500
"""

from __future__ import annotations

import argparse
import asyncio
import os
import re
import sys
import time
from dataclasses import dataclass
from typing import Iterable, List, Optional, Dict, Tuple, Set
from urllib.parse import urljoin, urlparse, unquote, quote

import httpx
from bs4 import BeautifulSoup
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.database import async_engine
from app.models.office import Office
from app.models.employee import Employee
from app.services.firecrawl_service import FirecrawlService


DEFAULT_START_URLS = [
    "https://proaktiv.no/eiendomsmegler/oslo",
    "https://proaktiv.no/eiendomsmegler/drammen-lier-holmestrand",
    "https://proaktiv.no/eiendomsmegler/lillestrom",
    "https://proaktiv.no/eiendomsmegler/lorenskog",
    "https://proaktiv.no/eiendomsmegler/bergen",
    "https://proaktiv.no/eiendomsmegler/voss",
    "https://proaktiv.no/eiendomsmegler/stavanger",
    "https://proaktiv.no/eiendomsmegler/sandnes",
    "https://proaktiv.no/eiendomsmegler/sola",
    "https://proaktiv.no/eiendomsmegler/trondheim",
    "https://proaktiv.no/eiendomsmegler/alesund",
    "https://proaktiv.no/eiendomsmegler/skien",
    "https://proaktiv.no/eiendomsmegler/haugesund",
    "https://proaktiv.no/eiendomsmegler/kjedeledelse",
    "https://proaktiv.no/eiendomsmegler/sarpsborg",
    "https://proaktiv.no/eiendomsmegler/jaeren",
    "https://proaktiv.no/eiendomsmegler/kristiansand",
]

STOP_SECTION_MARKERS = [
    "Bolig til salgs",
    "Boliger til salgs",
    "Solgte boliger",
    "Utleide boliger",
    "Boligmagasin",
    "Kundeuttalelser",
    "Se flere",
    "Inspirasjon",
    "Lurer du på noe",
    "Ta kontakt",
    "Les hva kundene sier",
]


@dataclass
class OfficePayload:
    name: str
    homepage_url: str
    email: Optional[str] = None
    phone: Optional[str] = None
    street_address: Optional[str] = None
    postal_code: Optional[str] = None
    city: Optional[str] = None
    description: Optional[str] = None
    profile_image_url: Optional[str] = None


@dataclass
class EmployeePayload:
    first_name: str
    last_name: str
    office_url: Optional[str]
    office_name: Optional[str]
    title: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    homepage_profile_url: Optional[str] = None
    profile_image_url: Optional[str] = None
    description: Optional[str] = None


def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    normalized_path = quote(unquote(parsed.path), safe="/")
    normalized = parsed._replace(path=normalized_path, fragment="", query="").geturl()
    if normalized.endswith("/") and normalized.count("/") > 2:
        normalized = normalized.rstrip("/")
    return normalized


def is_eiendomsmegler_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.netloc.endswith("proaktiv.no") and "/eiendomsmegler" in parsed.path


def classify_url(url: str) -> Optional[str]:
    parsed = urlparse(url)
    parts = parsed.path.strip("/").split("/")
    if not parts or parts[0] != "eiendomsmegler":
        return None
    segments = parts[1:]
    if len(segments) == 1:
        return "city"
    if len(segments) == 2:
        return "office"
    if len(segments) == 3:
        slug = unquote(segments[-1])
        if any(char.isdigit() for char in slug):
            return None
        return "employee"
    return None


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def extract_lines(html: str) -> List[str]:
    soup = BeautifulSoup(html, "lxml")
    text = soup.get_text("\n")
    return [line for line in (clean_text(line) for line in text.splitlines()) if line]


def find_primary_heading(soup: BeautifulSoup) -> Tuple[Optional[object], str]:
    bad_fragments = ("logg inn", "registrer bruker", "glemt passord", "ny bruker")
    candidate = None
    candidate_el = None
    for h1 in soup.find_all("h1"):
        text = clean_text(h1.get_text(" "))
        if not text:
            continue
        lower = text.lower()
        if any(fragment in lower for fragment in bad_fragments):
            continue
        if "proaktiv" in lower or "eiendomsmegler" in lower:
            return h1, text
        if not candidate:
            candidate = text
            candidate_el = h1
    return candidate_el, candidate or ""


def extract_primary_heading(soup: BeautifulSoup, fallback: str) -> str:
    _, text = find_primary_heading(soup)
    return text or fallback


def slice_lines_between(lines: List[str], start_patterns: Iterable[str], stop_markers: Iterable[str]) -> List[str]:
    start_idx = -1
    for idx, line in enumerate(lines):
        if any(re.search(pattern, line, re.IGNORECASE) for pattern in start_patterns):
            start_idx = idx
            break
    if start_idx == -1:
        return lines

    sliced: List[str] = []
    for line in lines[start_idx + 1:]:
        if any(marker.lower() in line.lower() for marker in stop_markers):
            break
        sliced.append(line)
    return sliced


def looks_like_name(line: str) -> bool:
    if ":" in line or "@" in line:
        return False
    if any(char.isdigit() for char in line):
        return False
    words = line.split()
    if len(words) < 2:
        return False
    if len(line) > 80:
        return False
    return True


def looks_like_title(line: str) -> bool:
    if ":" in line or "@" in line:
        return False
    if len(line) > 120:
        return False
    return True


def extract_email(value: str) -> Optional[str]:
    match = re.search(r"([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})", value, re.IGNORECASE)
    return match.group(1) if match else None


def format_phone(value: str) -> Optional[str]:
    digits = re.sub(r"\D", "", value or "")
    if not digits:
        return None
    if digits.startswith("47") and len(digits) > 8:
        digits = digits[-8:]
    if len(digits) == 8:
        return " ".join(digits[i:i + 2] for i in range(0, 8, 2))
    return value.strip() if value else None


def looks_like_phone_line(line: str) -> bool:
    digits = re.sub(r"\D", "", line or "")
    return len(digits) == 8 and len(line.strip()) <= 20


def extract_named_contacts(lines: List[str]) -> List[Dict[str, Optional[str]]]:
    results: List[Dict[str, Optional[str]]] = []
    seen: Set[Tuple[Optional[str], Optional[str]]] = set()
    for i, line in enumerate(lines):
        if not line.lower().startswith("telefon"):
            continue
        phone = format_phone(line)
        email = None
        for j in range(i + 1, min(i + 4, len(lines))):
            email = extract_email(lines[j])
            if email:
                break
        name = None
        title = None
        name_idx = None
        for k in range(i - 1, max(i - 6, -1), -1):
            if looks_like_name(lines[k]):
                name = lines[k]
                name_idx = k
                break
        if name_idx is not None:
            for k in range(name_idx + 1, i):
                if looks_like_title(lines[k]) and lines[k] != name:
                    title = lines[k]
                    break
        if not name:
            continue
        key = (name, email or phone)
        if key in seen:
            continue
        seen.add(key)
        results.append({"name": name, "title": title, "email": email, "phone": phone})
    return results


def extract_name_title_map(soup: BeautifulSoup, base_url: str) -> Dict[str, str]:
    links: Dict[str, str] = {}
    for a in soup.find_all("a", href=True):
        text = clean_text(a.get_text(" "))
        if not looks_like_name(text):
            continue
        href = a.get("href", "")
        if "/eiendomsmegler/" not in href:
            continue
        url = normalize_url(urljoin(base_url, href))
        links[text] = url
    return links


def extract_image_url(soup: BeautifulSoup, base_url: str, name: Optional[str]) -> Optional[str]:
    candidates: List[str] = []
    for img in soup.find_all("img"):
        alt = clean_text(img.get("alt", ""))
        classes = " ".join(img.get("class", [])).lower()
        src = img.get("src") or img.get("data-src") or img.get("data-lazy-src")
        if not src:
            srcset = img.get("srcset")
            if srcset:
                src = srcset.split(",")[0].strip().split(" ")[0]
        if not src:
            continue
        url = urljoin(base_url, src)
        if name and name.lower() in alt.lower():
            return url
        if "profile" in classes or "agent" in classes:
            candidates.append(url)
    return candidates[0] if candidates else None


def derive_office_from_profile(profile_url: str) -> Tuple[Optional[str], Optional[str]]:
    parsed = urlparse(profile_url)
    parts = parsed.path.strip("/").split("/")
    if len(parts) >= 3 and parts[0] == "eiendomsmegler":
        office_url = f"{parsed.scheme}://{parsed.netloc}/" + "/".join(parts[:3])
        return office_url, slug_to_city(parts[2])
    return None, None


def extract_employee_cards(soup: BeautifulSoup, base_url: str) -> List[EmployeePayload]:
    payloads: List[EmployeePayload] = []
    seen: Set[str] = set()
    for card in soup.select("div.flexcolumn0.pane"):
        email_link = card.select_one("a[href^=mailto]")
        tel_link = card.select_one("a[href^=tel]")
        if not email_link or not tel_link:
            continue
        name_el = card.select_one("div.Heading") or card.find(["h3", "h4", "h5"])
        name = clean_text(name_el.get_text(" ")) if name_el else ""
        if not looks_like_name(name):
            continue
        if "proaktiv" in name.lower():
            continue
        if any(
            fragment in name.lower()
            for fragment in (
                "ta kontakt",
                "kontakt oss",
                "megler i",
                "eiendomsmegler",
            )
        ):
            continue
        title_el = card.select_one("div.name_tittel")
        title = clean_text(title_el.get_text(" ")) if title_el else None
        email = extract_email(email_link.get("href", ""))
        phone = format_phone(tel_link.get("href", ""))
        profile_url = None
        for link in card.find_all("a", href=True):
            href = link.get("href", "")
            if href.startswith("mailto:") or href.startswith("tel:"):
                continue
            if "/eiendomsmegler/" in href:
                profile_url = normalize_url(urljoin(base_url, href))
                break
        office_url, office_name = (None, None)
        if profile_url:
            office_url, office_name = derive_office_from_profile(profile_url)
        first_name, last_name = parse_employee_name(name)
        unique_key = profile_url or email or f"{first_name} {last_name} {phone}"
        if unique_key in seen:
            continue
        seen.add(unique_key)
        payloads.append(
            EmployeePayload(
                first_name=first_name,
                last_name=last_name,
                title=title,
                email=email,
                phone=phone,
                office_url=office_url,
                office_name=office_name,
                homepage_profile_url=profile_url,
                profile_image_url=extract_image_url(card, base_url, name),
            )
        )
    return payloads


def extract_description(soup: BeautifulSoup, *, anchor: Optional[str] = None) -> Optional[str]:
    paragraphs: List[str] = []
    lines = extract_lines(str(soup))
    start_idx = 0
    if anchor:
        anchor_lower = anchor.lower()
        anchor_indices = [i for i, line in enumerate(lines) if anchor_lower in line.lower()]
        if anchor_indices:
            start_idx = anchor_indices[-1]
    for line in lines[start_idx:]:
        lower = line.lower()
        if any(marker.lower() in lower for marker in STOP_SECTION_MARKERS):
            break
        if "telefon" in lower or "e-post" in lower or lower.startswith("kontor"):
            continue
        if len(line) < 60:
            continue
        paragraphs.append(line)
        if sum(len(t) for t in paragraphs) > 1600:
            break
    if paragraphs:
        return " ".join(paragraphs)

    for p in soup.find_all("p"):
        text = clean_text(p.get_text(" "))
        if not text:
            continue
        if any(marker.lower() in text.lower() for marker in STOP_SECTION_MARKERS):
            break
        if "Telefon" in text or "E-post" in text:
            continue
        if len(text) < 60:
            continue
        paragraphs.append(text)
        if sum(len(t) for t in paragraphs) > 1600:
            break
    return " ".join(paragraphs) if paragraphs else None


def parse_employee_name(full_name: str) -> Tuple[str, str]:
    parts = full_name.split()
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], " ".join(parts[1:])


def parse_office_contact(lines: List[str]) -> Dict[str, Optional[str]]:
    email = None
    phone = None
    street_address = None
    postal_code = None
    city = None

    for idx, line in enumerate(lines):
        lower = line.lower()
        if not email and "@" in line:
            email = extract_email(line)
        if not email and lower.startswith("e-post") and idx + 1 < len(lines):
            email = extract_email(lines[idx + 1])
        if not phone and lower.startswith("telefon"):
            phone = format_phone(line)
            if not phone and idx + 1 < len(lines):
                phone = format_phone(lines[idx + 1])
        if "Adresse" in line:
            line = clean_text(line.split("Adresse", 1)[-1].replace(":", " "))
        if (
            not street_address
            and any(char.isdigit() for char in line)
            and "/" not in line
            and "telefon" not in lower
            and "e-post" not in lower
            and not looks_like_phone_line(line)
        ):
            street_address = line

    if street_address:
        match = re.search(r"(\d{4})\s+([A-Za-zÆØÅæøå\-\s]+)", street_address)
        if match:
            postal_code = match.group(1)
            city = clean_text(match.group(2))
            street_address = clean_text(street_address.replace(match.group(0), ""))
            street_address = street_address.rstrip(",")
    return {
        "email": email,
        "phone": phone,
        "street_address": street_address,
        "postal_code": postal_code,
        "city": city,
    }


def slug_to_city(slug: str) -> str:
    decoded = unquote(slug)
    return clean_text(decoded.replace("-", " ").title())


async def fetch_html(
    client: httpx.AsyncClient,
    url: str,
    *,
    use_firecrawl: bool,
    timeout_ms: int,
) -> str:
    if use_firecrawl:
        if not FirecrawlService.is_configured():
            raise RuntimeError("FIRECRAWL_API_KEY is not configured")
        normalized, payload = await FirecrawlService.run_scrape(
            url=url,
            formats=["html", "rawHtml", "links"],
            only_main_content=False,
            wait_for_ms=1000,
            timeout_ms=timeout_ms,
            include_tags=None,
            exclude_tags=None,
        )
        return payload.get("rawHtml") or payload.get("html") or ""
    response = await client.get(url)
    response.raise_for_status()
    return response.text


async def ensure_unique_short_code(db: AsyncSession, base_code: str) -> str:
    candidate = base_code[:10].upper()
    suffix = 1
    while True:
        result = await db.execute(select(Office).where(Office.short_code == candidate))
        if not result.scalar_one_or_none():
            return candidate
        suffix += 1
        trim_len = max(1, 8 - len(str(suffix)))
        candidate = f"{base_code[:trim_len].upper()}{suffix}"


async def upsert_office(
    db: AsyncSession,
    payload: OfficePayload,
    *,
    overwrite: bool,
    dry_run: bool,
) -> Optional[Office]:
    existing = None
    if payload.homepage_url:
        result = await db.execute(select(Office).where(Office.homepage_url == payload.homepage_url))
        existing = result.scalar_one_or_none()
    if not existing and payload.name:
        result = await db.execute(
            select(Office).where(Office.name == payload.name)
        )
        existing = result.scalar_one_or_none()

    if dry_run:
        print(f"[Dry-run] Office: {payload.name} ({payload.homepage_url})")
        return existing

    if not existing:
        slug = urlparse(payload.homepage_url).path.rstrip("/").split("/")[-1]
        base_code = re.sub(r"[^A-Za-z0-9]", "", slug or payload.name) or "OFF"
        short_code = await ensure_unique_short_code(db, base_code)
        office = Office(
            name=payload.name,
            short_code=short_code,
            email=payload.email,
            phone=payload.phone,
            street_address=payload.street_address,
            postal_code=payload.postal_code,
            city=payload.city,
            homepage_url=payload.homepage_url,
            description=payload.description,
            profile_image_url=payload.profile_image_url,
        )
        db.add(office)
        await db.flush()
        await db.refresh(office)
        return office

    updates = {
        "email": payload.email,
        "phone": payload.phone,
        "street_address": payload.street_address,
        "postal_code": payload.postal_code,
        "city": payload.city,
        "homepage_url": payload.homepage_url,
        "description": payload.description,
        "profile_image_url": payload.profile_image_url,
    }
    for field, value in updates.items():
        if value and (overwrite or not getattr(existing, field)):
            setattr(existing, field, value)
    await db.flush()
    await db.refresh(existing)
    return existing


def infer_roles(title: Optional[str]) -> List[str]:
    if not title:
        return []
    mapping = {
        "eiendomsmeglerfullmektig": "eiendomsmeglerfullmektig",
        "eiendomsmegler": "eiendomsmegler",
        "fagansvarlig": "fagansvarlig",
        "daglig leder": "daglig_leder",
    }
    roles = []
    lower = title.lower()
    for key, role in mapping.items():
        if key in lower and role not in roles:
            roles.append(role)
    return roles


async def upsert_employee(
    db: AsyncSession,
    payload: EmployeePayload,
    office: Optional[Office],
    *,
    overwrite: bool,
    dry_run: bool,
) -> Optional[Employee]:
    existing = None
    if payload.email:
        result = await db.execute(select(Employee).where(Employee.email == payload.email))
        existing = result.scalar_one_or_none()
    if not existing and payload.homepage_profile_url:
        result = await db.execute(select(Employee).where(Employee.homepage_profile_url == payload.homepage_profile_url))
        existing = result.scalar_one_or_none()

    if dry_run:
        print(f"[Dry-run] Employee: {payload.first_name} {payload.last_name} ({payload.email})")
        return existing

    if not existing:
        if not office:
            return None
        employee = Employee(
            office_id=str(office.id),
            first_name=payload.first_name,
            last_name=payload.last_name,
            title=payload.title,
            email=payload.email,
            phone=payload.phone,
            homepage_profile_url=payload.homepage_profile_url,
            profile_image_url=payload.profile_image_url,
            description=payload.description,
            system_roles=infer_roles(payload.title),
        )
        db.add(employee)
        await db.flush()
        await db.refresh(employee)
        return employee

    updates = {
        "title": payload.title,
        "email": payload.email,
        "phone": payload.phone,
        "homepage_profile_url": payload.homepage_profile_url,
        "profile_image_url": payload.profile_image_url,
        "description": payload.description,
    }
    for field, value in updates.items():
        if value and (overwrite or not getattr(existing, field)):
            setattr(existing, field, value)
    if office and (overwrite or not existing.office_id):
        existing.office_id = str(office.id)
    if payload.title:
        roles = infer_roles(payload.title)
        if roles and (overwrite or not existing.system_roles):
            existing.system_roles = roles
    await db.flush()
    await db.refresh(existing)
    return existing


async def sync_proaktiv(
    *,
    start_urls: List[str],
    delay_ms: int,
    max_pages: int,
    max_runtime_minutes: int,
    max_office_pages: int,
    max_employee_pages: int,
    use_firecrawl: bool,
    overwrite: bool,
    dry_run: bool,
    deep_employees: bool,
) -> None:
    async_session = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
    queue = [normalize_url(url) for url in start_urls]
    visited: Set[str] = set()
    processed_offices = 0
    processed_employees = 0
    total_processed = 0
    start_time = time.monotonic()
    delay_seconds = max(0, delay_ms / 1000)

    async with async_session() as db, httpx.AsyncClient(
        headers={"User-Agent": "Mozilla/5.0"},
        follow_redirects=True,
        timeout=30,
    ) as client:
        while queue and total_processed < max_pages:
            if (time.monotonic() - start_time) > (max_runtime_minutes * 60):
                print("[Sync] Max runtime reached, stopping.")
                break

            url = queue.pop(0)
            if url in visited:
                continue
            visited.add(url)

            if processed_offices >= max_office_pages and processed_employees >= max_employee_pages:
                break

            if delay_seconds:
                await asyncio.sleep(delay_seconds)

            try:
                html = await fetch_html(client, url, use_firecrawl=use_firecrawl, timeout_ms=settings.FIRECRAWL_TIMEOUT_MS)
            except Exception as exc:
                print(f"[Sync] Failed to fetch {url}: {exc}")
                continue

            total_processed += 1
            soup = BeautifulSoup(html, "lxml")
            page_type = classify_url(url)

            for link in extract_links(soup, url):
                if deep_employees and classify_url(link) != "employee":
                    continue
                if link not in visited and link not in queue:
                    queue.append(link)

            if page_type == "office" and processed_offices < max_office_pages:
                office_payload, employee_payloads = parse_office_page(soup, url)
                office = await upsert_office(db, office_payload, overwrite=overwrite, dry_run=dry_run)
                if office:
                    processed_offices += 1
                for emp_payload in employee_payloads:
                    if emp_payload.homepage_profile_url and emp_payload.homepage_profile_url not in visited:
                        if emp_payload.homepage_profile_url not in queue:
                            queue.append(emp_payload.homepage_profile_url)
                    if deep_employees:
                        continue
                    if processed_employees >= max_employee_pages:
                        break
                    emp_office = office
                    if emp_payload.office_url and (not office or office.homepage_url != emp_payload.office_url):
                        emp_office = await upsert_office(
                            db,
                            OfficePayload(
                                name=emp_payload.office_name or office_payload.name,
                                homepage_url=emp_payload.office_url,
                                city=office_payload.city,
                            ),
                            overwrite=overwrite,
                            dry_run=dry_run,
                        )
                    employee = await upsert_employee(
                        db,
                        emp_payload,
                        emp_office,
                        overwrite=overwrite,
                        dry_run=dry_run,
                    )
                    if employee:
                        processed_employees += 1

            if page_type == "employee" and processed_employees < max_employee_pages:
                employee_payload, office_stub = parse_employee_page(soup, url)
                office = None
                if office_stub:
                    office = await upsert_office(db, office_stub, overwrite=overwrite, dry_run=dry_run)
                employee = await upsert_employee(
                    db,
                    employee_payload,
                    office,
                    overwrite=overwrite,
                    dry_run=dry_run,
                )
                if employee:
                    processed_employees += 1

            if page_type == "city":
                employee_payloads = parse_city_employees(soup, url)
                for emp_payload in employee_payloads:
                    if processed_employees >= max_employee_pages:
                        break
                    if emp_payload.homepage_profile_url and emp_payload.homepage_profile_url not in visited:
                        if emp_payload.homepage_profile_url not in queue:
                            queue.append(emp_payload.homepage_profile_url)
                    if deep_employees:
                        continue
                    office = None
                    if emp_payload.office_url:
                        office = await upsert_office(
                            db,
                            OfficePayload(
                                name=emp_payload.office_name or slug_to_city(urlparse(emp_payload.office_url).path.split("/")[-1]),
                                homepage_url=emp_payload.office_url,
                                city=slug_to_city(urlparse(url).path.split("/")[-1]),
                            ),
                            overwrite=overwrite,
                            dry_run=dry_run,
                        )
                    employee = await upsert_employee(
                        db,
                        emp_payload,
                        office,
                        overwrite=overwrite,
                        dry_run=dry_run,
                    )
                    if employee:
                        processed_employees += 1

            if not dry_run:
                await db.commit()

    print(
        f"[Sync] Done. processed_pages={total_processed} "
        f"offices={processed_offices} employees={processed_employees}"
    )


def extract_links(soup: BeautifulSoup, base_url: str) -> List[str]:
    links: List[str] = []
    for a in soup.find_all("a", href=True):
        href = a.get("href", "")
        if href.startswith("#") or href.startswith("mailto:") or href.startswith("tel:"):
            continue
        url = normalize_url(urljoin(base_url, href))
        if not is_eiendomsmegler_url(url):
            continue
        if not classify_url(url):
            continue
        links.append(url)
    return links


def parse_office_page(soup: BeautifulSoup, url: str) -> Tuple[OfficePayload, List[EmployeePayload]]:
    lines = extract_lines(str(soup))
    heading_el, office_name = find_primary_heading(soup)
    office_name = office_name or "Proaktiv Office"
    office_section = slice_lines_between(lines, [office_name], ["Våre meglere", "Ta kontakt"])
    contact = parse_office_contact(office_section)
    description = extract_description(soup, anchor=office_name)
    profile_image_url = extract_image_url(soup, url, office_name)
    city_slug = urlparse(url).path.strip("/").split("/")[1] if classify_url(url) == "office" else None
    city = contact.get("city") or (slug_to_city(city_slug) if city_slug else None)

    office_payload = OfficePayload(
        name=office_name,
        homepage_url=url,
        email=contact.get("email"),
        phone=contact.get("phone"),
        street_address=contact.get("street_address"),
        postal_code=contact.get("postal_code"),
        city=city,
        description=description,
        profile_image_url=profile_image_url,
    )

    employee_payloads = extract_employee_cards(soup, url)
    return office_payload, employee_payloads


def parse_city_employees(soup: BeautifulSoup, url: str) -> List[EmployeePayload]:
    return extract_employee_cards(soup, url)


def parse_employee_page(soup: BeautifulSoup, url: str) -> Tuple[EmployeePayload, Optional[OfficePayload]]:
    heading_el, name = find_primary_heading(soup)
    title = None
    if heading_el:
        for sibling in heading_el.find_all_next(["h2", "h3", "h4", "h5", "p", "div"], limit=10):
            text = clean_text(sibling.get_text(" "))
            if not text:
                continue
            if "Telefon" in text or "E-post" in text:
                continue
            if len(text) > 100:
                continue
            title = text
            break
    if title and name and title.strip().lower() == name.strip().lower():
        title = None
    mailto = soup.find("a", href=re.compile(r"^mailto:", re.IGNORECASE))
    tel = soup.find("a", href=re.compile(r"^tel:", re.IGNORECASE))
    email = extract_email(mailto.get("href", "")) if mailto else None
    phone = format_phone(tel.get("href", "")) if tel else None
    description = extract_description(soup, anchor=name)

    office_name = None
    office_url = None
    lines = extract_lines(str(soup))
    for line in lines:
        if line.lower().startswith("kontor"):
            office_name = clean_text(line.split(":", 1)[-1])
            break
    derived_office_url = None
    parsed = urlparse(url)
    parts = parsed.path.strip("/").split("/")
    if len(parts) >= 3 and parts[0] == "eiendomsmegler":
        derived_office_url = f"{parsed.scheme}://{parsed.netloc}/" + "/".join(parts[:3])
        if not office_name:
            office_name = slug_to_city(parts[2])

    if office_name:
        for link in extract_links(soup, url):
            if office_name.lower().replace(" ", "-") in link:
                office_url = link
                break
    if not office_url:
        office_url = derived_office_url

    first_name, last_name = parse_employee_name(name) if name else ("", "")
    employee_payload = EmployeePayload(
        first_name=first_name,
        last_name=last_name,
        office_url=office_url,
        office_name=office_name,
        title=title,
        email=email,
        phone=phone,
        homepage_profile_url=url,
        profile_image_url=extract_image_url(soup, url, name),
        description=description,
    )

    office_payload = None
    if office_url and office_name:
        office_payload = OfficePayload(
            name=office_name,
            homepage_url=office_url,
            city=slug_to_city(urlparse(office_url).path.split("/")[-2]),
        )

    return employee_payload, office_payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync Proaktiv offices/employees")
    parser.add_argument("--start", action="append", default=None, help="Start URL (repeatable)")
    parser.add_argument("--delay-ms", type=int, default=1500, help="Delay between requests (ms)")
    parser.add_argument("--max-pages", type=int, default=150, help="Max pages to process")
    parser.add_argument("--max-runtime-minutes", type=int, default=120, help="Max runtime minutes")
    parser.add_argument("--max-office-pages", type=int, default=80, help="Max office pages")
    parser.add_argument("--max-employee-pages", type=int, default=400, help="Max employee pages")
    parser.add_argument("--use-firecrawl", action="store_true", help="Use Firecrawl for fetching HTML")
    parser.add_argument(
        "--deep-employees",
        action="store_true",
        help="Only upsert employees from profile pages (queue profile links).",
    )
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing data")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without DB writes")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    start_urls = [normalize_url(url) for url in (args.start or DEFAULT_START_URLS)]
    asyncio.run(
        sync_proaktiv(
            start_urls=start_urls,
            delay_ms=args.delay_ms,
            max_pages=args.max_pages,
            max_runtime_minutes=args.max_runtime_minutes,
            max_office_pages=args.max_office_pages,
            max_employee_pages=args.max_employee_pages,
            use_firecrawl=args.use_firecrawl,
            overwrite=args.overwrite,
            dry_run=args.dry_run,
            deep_employees=args.deep_employees,
        )
    )


if __name__ == "__main__":
    main()
