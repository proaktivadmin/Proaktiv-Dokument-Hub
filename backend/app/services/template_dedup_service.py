"""
Template Deduplication Service — identifies merge candidates, analyzes
differences, and produces merged templates using vitec-if conditional logic.
"""

import hashlib
import logging
import re
from difflib import SequenceMatcher
from uuid import UUID

from bs4 import BeautifulSoup, Tag
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.template import Template
from app.schemas.template_dedup import (
    ContentSection,
    MergeAnalysis,
    MergeCandidate,
    MergeCandidateGroup,
    MergePreview,
    MergeResult,
)
from app.services.sanitizer_service import get_sanitizer_service

logger = logging.getLogger(__name__)

PROPERTY_TYPE_SUFFIXES = [
    "Bruktbolig",
    "Nybygg",
    "Fritid",
    "Tomt",
    "Borettslag",
    "Aksjeleilighet",
    "Obligasjonsleilighet",
    "Næring",
]

PROPERTY_TYPE_SUFFIX_PATTERN = re.compile(
    r"\s*(" + "|".join(re.escape(s) for s in PROPERTY_TYPE_SUFFIXES) + r").*$",
    re.IGNORECASE,
)

NO_TOUCH_TITLE_PATTERNS = re.compile(
    r"(Skj\u00f8te|Pantedokument|Hjemmelserkl\u00e6ring|Hjemmelsoverf\u00f8ring"
    r"|konsesjonsfrihet|konsesjon|Tvangssalg|pantefrafall"
    r"|Seksjoneringsbegj\u00e6ring|Kartverket|Grunnboksutskrift)",
    re.IGNORECASE,
)


TITLE_NOISE_PATTERN = re.compile(
    r"\s*(?:"
    r"//\s*Proaktiv\s+QA[^/]*"
    r"|V\.\d+(?:\.\d+)*"
    r")\s*$",
    re.IGNORECASE,
)

MIN_PREFIX_LENGTH = 15
SIMILARITY_THRESHOLD = 0.55


def _extract_base_title(title: str) -> str:
    """Strip property type suffixes and noise to get a normalised base title."""
    cleaned = title
    cleaned = PROPERTY_TYPE_SUFFIX_PATTERN.sub("", cleaned).strip()
    cleaned = TITLE_NOISE_PATTERN.sub("", cleaned).strip()
    cleaned = cleaned.rstrip(" -\u2013\u2014")
    return cleaned


def _extract_title_prefix(title: str) -> str:
    """Extract the leading phrase of a title for prefix-based grouping.

    Splits on common delimiters (-, //, fra, from) and returns the first
    segment if it's long enough to be meaningful.
    """
    cleaned = TITLE_NOISE_PATTERN.sub("", title).strip()
    split = re.split(r"\s+[-\u2013\u2014]\s+|\s*//\s*|\s+fra\s+", cleaned, maxsplit=1)
    prefix = split[0].strip()
    if len(prefix) >= MIN_PREFIX_LENGTH:
        return prefix
    return cleaned


def _extract_property_type(title: str) -> str | None:
    """Return the canonical property type suffix from a title, or None."""
    m = PROPERTY_TYPE_SUFFIX_PATTERN.search(title)
    if m:
        captured = m.group(1)
        for canonical in PROPERTY_TYPE_SUFFIXES:
            if canonical.lower() == captured.lower():
                return canonical
        return captured
    return None


def _is_no_touch(title: str, origin: str | None) -> bool:
    """Return True if the template must never appear as a merge candidate."""
    if origin and origin == "vitec_system" and NO_TOUCH_TITLE_PATTERNS.search(title):
        return True
    if NO_TOUCH_TITLE_PATTERNS.search(title):
        return True
    return False


def _normalize_html(html: str) -> str:
    """Normalize HTML for structural comparison — strip whitespace, sort attrs."""
    soup = BeautifulSoup(html, "lxml")
    for el in soup.find_all(string=True):
        if isinstance(el, str):
            collapsed = " ".join(el.split())
            if collapsed != el:
                el.replace_with(collapsed)
    return str(soup)


def _content_similarity(a: str, b: str) -> float:
    """Return 0-1 similarity ratio between two HTML strings."""
    norm_a = _normalize_html(a)
    norm_b = _normalize_html(b)
    return SequenceMatcher(None, norm_a, norm_b).ratio()


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def _extract_top_level_sections(html: str) -> list[dict]:
    """
    Break an HTML template into top-level sections for comparison.

    Returns a list of dicts with keys: tag, path, content, hash.
    """
    soup = BeautifulSoup(html, "lxml")
    wrapper = soup.find(id="vitecTemplate")
    target = wrapper if wrapper else (soup.body or soup)

    sections: list[dict] = []
    idx = 0
    for child in target.children:
        if isinstance(child, Tag):
            content_str = str(child)
            sections.append(
                {
                    "tag": child.name,
                    "path": f"{child.name}[{idx}]",
                    "content": content_str,
                    "hash": _hash_text(content_str),
                }
            )
            idx += 1
    return sections


def _vitec_if_property_type(prop_type: str) -> str:
    """
    Build a vitec-if attribute value for a property type comparison.

    Uses the escaping rules from the ruleset:
    - &quot; for quotes
    - \\xE6 for æ, \\xF8 for ø, \\xE5 for å (and uppercase variants)
    """
    escaped = prop_type
    replacements = {
        "æ": "\\xE6",
        "Æ": "\\xC6",
        "ø": "\\xF8",
        "Ø": "\\xD8",
        "å": "\\xE5",
        "Å": "\\xC5",
    }
    for char, esc in replacements.items():
        escaped = escaped.replace(char, esc)
    return f"oppdrag.oppdragstype.key == &quot;{escaped}&quot;"


def _build_candidate_group(base_title: str, group_templates: list[Template]) -> MergeCandidateGroup:
    """Build a MergeCandidateGroup from a list of templates with shared purpose."""
    primary = group_templates[0]
    candidates: list[MergeCandidate] = []
    for t in group_templates:
        sim = 1.0 if t.id == primary.id else _content_similarity(primary.content or "", t.content or "")
        candidates.append(
            MergeCandidate(
                template_id=t.id,
                title=t.title,
                property_type=_extract_property_type(t.title),
                content_length=len(t.content or ""),
                similarity_score=round(sim, 3),
            )
        )

    cat_name: str | None = None
    for t in group_templates:
        cats = getattr(t, "categories", [])
        if cats:
            cat_name = cats[0].name
            break

    return MergeCandidateGroup(
        base_title=base_title,
        candidates=candidates,
        category=cat_name,
        estimated_reduction=len(group_templates) - 1,
    )


class TemplateDedupService:
    """Service for template deduplication analysis and merge operations."""

    @staticmethod
    async def find_candidates(db: AsyncSession) -> list[MergeCandidateGroup]:
        """Scan the library and identify groups of templates that serve the same purpose.

        Uses two strategies:
        1. Exact base title match (after stripping property type suffixes)
        2. Prefix-based grouping with content similarity for templates that
           share a common leading phrase (e.g. "Innhenting av opplysninger")
        """
        result = await db.execute(
            select(Template).where(
                Template.content.isnot(None),
                Template.content != "",
                Template.file_type.in_(["html", "htm"]),
            )
        )
        templates = list(result.scalars().all())

        eligible = [t for t in templates if not _is_no_touch(t.title, getattr(t, "origin", None))]

        # Pass 1: group by exact base title (property type suffix stripping)
        base_groups: dict[str, list[Template]] = {}
        for t in eligible:
            base = _extract_base_title(t.title)
            if base not in base_groups:
                base_groups[base] = []
            base_groups[base].append(t)

        grouped_ids: set[str] = set()
        candidate_groups: list[MergeCandidateGroup] = []

        for base_title, group_templates in base_groups.items():
            if len(group_templates) < 2:
                continue
            group = _build_candidate_group(base_title, group_templates)
            candidate_groups.append(group)
            for t in group_templates:
                grouped_ids.add(str(t.id))

        # Pass 2: prefix-based grouping for remaining templates
        remaining = [t for t in eligible if str(t.id) not in grouped_ids]
        prefix_groups: dict[str, list[Template]] = {}
        for t in remaining:
            prefix = _extract_title_prefix(t.title)
            if prefix not in prefix_groups:
                prefix_groups[prefix] = []
            prefix_groups[prefix].append(t)

        for prefix, group_templates in prefix_groups.items():
            if len(group_templates) < 2:
                continue

            primary = group_templates[0]
            similar: list[Template] = [primary]
            for t in group_templates[1:]:
                sim = _content_similarity(primary.content or "", t.content or "")
                if sim >= SIMILARITY_THRESHOLD:
                    similar.append(t)

            if len(similar) >= 2:
                group = _build_candidate_group(prefix, similar)
                candidate_groups.append(group)
                for t in similar:
                    grouped_ids.add(str(t.id))

        candidate_groups.sort(key=lambda g: len(g.candidates), reverse=True)
        return candidate_groups

    @staticmethod
    async def analyze_group(db: AsyncSession, template_ids: list[UUID]) -> MergeAnalysis:
        """Deep-compare a group of templates to identify shared vs divergent content."""
        result = await db.execute(select(Template).where(Template.id.in_([str(tid) for tid in template_ids])))
        templates = list(result.scalars().all())

        if len(templates) < 2:
            raise ValueError("Need at least 2 templates to analyze")

        candidates = [
            MergeCandidate(
                template_id=t.id,
                title=t.title,
                property_type=_extract_property_type(t.title),
                content_length=len(t.content or ""),
                similarity_score=0.0,
            )
            for t in templates
        ]

        primary = templates[0]
        for c in candidates:
            if c.template_id == primary.id:
                c.similarity_score = 1.0
            else:
                match_t = next((t for t in templates if t.id == c.template_id), None)
                if match_t:
                    c.similarity_score = round(_content_similarity(primary.content or "", match_t.content or ""), 3)

        # Extract sections per template
        all_sections: dict[UUID, list[dict]] = {}
        for t in templates:
            all_sections[t.id] = _extract_top_level_sections(t.content or "")

        # Build hash-to-templates map for each section index
        max_sections = max(len(s) for s in all_sections.values()) if all_sections else 0
        shared: list[ContentSection] = []
        divergent: list[ContentSection] = []
        unique: list[ContentSection] = []

        for idx in range(max_sections):
            hashes: dict[str, list[str]] = {}  # hash -> list of template IDs
            section_content: dict[str, str] = {}  # hash -> content preview
            section_path = ""

            for tid, sections in all_sections.items():
                if idx < len(sections):
                    sec = sections[idx]
                    h = sec["hash"]
                    section_path = sec["path"]
                    if h not in hashes:
                        hashes[h] = []
                    hashes[h].append(str(tid))
                    section_content[h] = sec["content"][:100]

            template_count = sum(1 for tid, secs in all_sections.items() if idx < len(secs))

            if len(hashes) == 1 and template_count == len(templates):
                the_hash = next(iter(hashes))
                shared.append(
                    ContentSection(
                        path=section_path,
                        content_hash=the_hash,
                        is_shared=True,
                        differs_in=[],
                        preview=section_content.get(the_hash, ""),
                    )
                )
            elif template_count == 1:
                the_hash = next(iter(hashes))
                unique.append(
                    ContentSection(
                        path=section_path,
                        content_hash=the_hash,
                        is_shared=False,
                        differs_in=list(hashes.values())[0],
                        preview=section_content.get(the_hash, ""),
                    )
                )
            else:
                all_tids: list[str] = []
                for tids in hashes.values():
                    all_tids.extend(tids)
                first_hash = next(iter(hashes))
                divergent.append(
                    ContentSection(
                        path=section_path,
                        content_hash=first_hash,
                        is_shared=False,
                        differs_in=all_tids,
                        preview=section_content.get(first_hash, ""),
                    )
                )

        # Determine complexity
        avg_sim = sum(c.similarity_score for c in candidates) / len(candidates)
        if avg_sim > 0.9 and len(divergent) <= 2:
            complexity: str = "simple"
        elif avg_sim > 0.7:
            complexity = "moderate"
        else:
            complexity = "complex"

        auto_merge = complexity == "simple" and all(
            c.property_type is not None for c in candidates if c.template_id != primary.id
        )

        warnings: list[str] = []
        if complexity == "complex":
            warnings.append("Stor variasjon mellom malene — manuell gjennomgang anbefales")
        if any(c.property_type is None for c in candidates):
            warnings.append("Noen maler mangler eiendomstype i tittelen")

        base_title = _extract_base_title(primary.title)

        return MergeAnalysis(
            group_title=base_title,
            templates=candidates,
            shared_sections=shared,
            divergent_sections=divergent,
            unique_sections=unique,
            merge_complexity=complexity,
            auto_mergeable=auto_merge,
            warnings=warnings,
        )

    @staticmethod
    async def preview_merge(db: AsyncSession, template_ids: list[UUID], primary_id: UUID) -> MergePreview:
        """Generate a preview of the merged template using vitec-if logic."""
        result = await db.execute(select(Template).where(Template.id.in_([str(tid) for tid in template_ids])))
        templates = list(result.scalars().all())

        primary = next((t for t in templates if t.id == primary_id), None)
        if not primary:
            raise ValueError(f"Primary template {primary_id} not found")

        others = [t for t in templates if t.id != primary_id]
        if not others:
            raise ValueError("Need at least one non-primary template")

        primary_sections = _extract_top_level_sections(primary.content or "")
        other_sections_map: dict[UUID, list[dict]] = {}
        for t in others:
            other_sections_map[t.id] = _extract_top_level_sections(t.content or "")

        merged_parts: list[str] = []
        conditions_added = 0
        warnings: list[str] = []

        primary_prop = _extract_property_type(primary.title)
        other_props: dict[UUID, str | None] = {t.id: _extract_property_type(t.title) for t in others}

        for idx, p_sec in enumerate(primary_sections):
            # Check if all others have the same content at this position
            all_same = True
            for _tid, o_secs in other_sections_map.items():
                if idx >= len(o_secs) or o_secs[idx]["hash"] != p_sec["hash"]:
                    all_same = False
                    break

            if all_same:
                merged_parts.append(p_sec["content"])
            else:
                # Divergent section — wrap each variant in vitec-if
                if primary_prop:
                    condition = _vitec_if_property_type(primary_prop)
                    merged_parts.append(f'<div vitec-if="{condition}">\n{p_sec["content"]}\n</div>')
                    conditions_added += 1
                else:
                    merged_parts.append(p_sec["content"])
                    warnings.append(f"Primærmal mangler eiendomstype — seksjon {idx} ikke betinget")

                for t in others:
                    o_secs = other_sections_map.get(t.id, [])
                    prop = other_props.get(t.id)
                    if idx < len(o_secs) and prop:
                        condition = _vitec_if_property_type(prop)
                        merged_parts.append(f'<div vitec-if="{condition}">\n{o_secs[idx]["content"]}\n</div>')
                        conditions_added += 1
                    elif idx < len(o_secs):
                        warnings.append(
                            f"Mal '{next((t2.title for t2 in others if t2.id == t.id), '')}' "
                            f"mangler eiendomstype — seksjon {idx} hoppet over"
                        )

        # Handle extra sections that only exist in other templates
        for t in others:
            o_secs = other_sections_map.get(t.id, [])
            for idx in range(len(primary_sections), len(o_secs)):
                prop = other_props.get(t.id)
                if prop:
                    condition = _vitec_if_property_type(prop)
                    merged_parts.append(f'<div vitec-if="{condition}">\n{o_secs[idx]["content"]}\n</div>')
                    conditions_added += 1

        merged_html = "\n".join(merged_parts)

        # Validate with sanitizer
        sanitizer = get_sanitizer_service()
        validation = sanitizer.validate_structure(merged_html)

        return MergePreview(
            merged_html=merged_html,
            primary_template_id=primary_id,
            templates_to_archive=[t.id for t in others],
            vitec_if_conditions_added=conditions_added,
            warnings=warnings,
            validation_passed=validation.get("has_vitec_wrapper", False),
        )

    @staticmethod
    async def execute_merge(
        db: AsyncSession,
        template_ids: list[UUID],
        primary_id: UUID,
        merged_html: str,
    ) -> MergeResult:
        """
        Apply the merge: update primary template with merged content,
        archive all others.
        """
        result = await db.execute(select(Template).where(Template.id.in_([str(tid) for tid in template_ids])))
        templates = list(result.scalars().all())

        primary = next((t for t in templates if t.id == primary_id), None)
        if not primary:
            raise ValueError(f"Primary template {primary_id} not found")

        others = [t for t in templates if t.id != primary_id]

        # Collect property types covered
        all_prop_types: list[str] = []
        for t in templates:
            pt = _extract_property_type(t.title)
            if pt and pt not in all_prop_types:
                all_prop_types.append(pt)

        # Update primary template
        primary.content = merged_html
        primary.version = (primary.version or 1) + 1
        primary.title = _extract_base_title(primary.title)
        if all_prop_types:
            primary.property_types = all_prop_types

        # Archive others
        archived_ids: list[UUID] = []
        for t in others:
            t.status = "archived"
            t.workflow_status = "archived"
            archived_ids.append(t.id)

        await db.flush()

        return MergeResult(
            primary_template_id=primary_id,
            archived_template_ids=archived_ids,
            new_version=primary.version,
            property_types_covered=all_prop_types,
        )
