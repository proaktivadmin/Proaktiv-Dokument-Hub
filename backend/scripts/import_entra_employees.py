#!/usr/bin/env python3
"""
Import Entra ID employee data into the local database (read-only to Entra).

This script:
1. Fetches users from Microsoft Graph (GET only)
2. Matches users to existing employees by email/UPN/proxyAddresses
3. Stores Entra values in secondary `entra_*` columns
4. Computes mismatch fields without overwriting Vitec data

Vitec Next remains the source of truth for primary fields.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections.abc import Iterable
from datetime import UTC, datetime

import httpx
from sqlalchemy import create_engine
from sqlalchemy.orm import joinedload, sessionmaker

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.employee import Employee

GRAPH_SCOPE = "https://graph.microsoft.com/.default"
GRAPH_USERS_URL = "https://graph.microsoft.com/v1.0/users"
GRAPH_FIELDS = ",".join(
    [
        "id",
        "userPrincipalName",
        "mail",
        "displayName",
        "givenName",
        "surname",
        "jobTitle",
        "mobilePhone",
        "department",
        "officeLocation",
        "streetAddress",
        "postalCode",
        "country",
        "accountEnabled",
        "proxyAddresses",
    ]
)


def get_access_token(tenant_id: str, client_id: str, client_secret: str) -> str:
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": GRAPH_SCOPE,
    }
    response = httpx.post(url, data=data, timeout=30.0)
    response.raise_for_status()
    return response.json()["access_token"]


def fetch_entra_users(access_token: str) -> Iterable[dict]:
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"$select": GRAPH_FIELDS}
    url = GRAPH_USERS_URL

    while url:
        response = httpx.get(url, headers=headers, params=params, timeout=30.0)
        response.raise_for_status()
        payload = response.json()
        yield from payload.get("value", [])
        url = payload.get("@odata.nextLink")
        params = None


def normalize_text(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value.lower() if value else None


def normalize_phone(value: str | None) -> str | None:
    if value is None:
        return None
    digits = re.sub(r"[^\d+]", "", value)
    return digits or None


def build_mismatch_fields(employee: Employee, user: dict) -> list[str]:
    mismatches: list[str] = []

    def check(field: str, vitec_value: str | None, entra_value: str | None, normalizer=normalize_text) -> None:
        if not vitec_value or not entra_value:
            return
        if normalizer(vitec_value) != normalizer(entra_value):
            mismatches.append(field)

    display_name = f"{employee.first_name} {employee.last_name}".strip()
    office = employee.office
    department_value = None
    if office:
        department_value = office.legal_name or office.name

    check("display_name", display_name, user.get("displayName"))
    check("first_name", employee.first_name, user.get("givenName"))
    check("last_name", employee.last_name, user.get("surname"))
    check("title", employee.title, user.get("jobTitle"))
    check("email", employee.email, user.get("mail"))
    check("phone", employee.phone, user.get("mobilePhone"), normalizer=normalize_phone)
    check("office_name", department_value, user.get("department"))
    check("office_location", office.city if office else None, user.get("officeLocation"))
    check("office_street", office.street_address if office else None, user.get("streetAddress"))
    check("office_postal", office.postal_code if office else None, user.get("postalCode"))
    check("country", "NO", user.get("country"))

    return mismatches


def build_candidate_emails(user: dict) -> list[str]:
    candidates: list[str] = []
    for key in ("mail", "userPrincipalName"):
        value = user.get(key)
        if value:
            candidates.append(value.lower())
    for address in user.get("proxyAddresses") or []:
        if isinstance(address, str) and address.lower().startswith("smtp:"):
            candidates.append(address.split(":", 1)[1].lower())
    return list(dict.fromkeys(candidates))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import Entra ID users into local employee records.")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without updating the database.")
    parser.add_argument("--filter-email", help="Only update a specific employee email.")
    parser.add_argument("--json", action="store_true", help="Output a JSON summary only.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    quiet = args.json

    def log(message: str) -> None:
        if not quiet:
            print(message)

    def log_error(message: str) -> None:
        print(message, file=sys.stderr)

    database_url = os.environ.get("DATABASE_URL")
    tenant_id = os.environ.get("ENTRA_TENANT_ID")
    client_id = os.environ.get("ENTRA_CLIENT_ID")
    client_secret = os.environ.get("ENTRA_CLIENT_SECRET")

    if not database_url:
        log_error("ERROR: DATABASE_URL environment variable not set")
        sys.exit(1)
    if not all([tenant_id, client_id, client_secret]):
        log_error("ERROR: ENTRA_TENANT_ID, ENTRA_CLIENT_ID, and ENTRA_CLIENT_SECRET must be set")
        sys.exit(1)

    log("\n" + "=" * 70)
    log("ENTRA ID IMPORT - Read-only to Entra (DB updates only)")
    log("=" * 70)

    access_token = get_access_token(tenant_id, client_id, client_secret)
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)

    with Session() as db:
        query = db.query(Employee).options(joinedload(Employee.office)).filter(Employee.email.isnot(None))
        if args.filter_email:
            query = query.filter(Employee.email == args.filter_email)

        employees = query.all()
        employees_by_email = {e.email.lower(): e for e in employees if e.email}
        matched_ids: set[str] = set()

        updated = 0
        skipped = 0
        not_matched = 0

        log(f"Loaded {len(employees)} employees from database")
        log("Fetching users from Microsoft Graph...")

        for user in fetch_entra_users(access_token):
            candidate_emails = build_candidate_emails(user)
            employee = None
            for email in candidate_emails:
                employee = employees_by_email.get(email)
                if employee:
                    break

            if not employee:
                not_matched += 1
                continue

            matched_ids.add(str(employee.id))

            user_upn = user.get("userPrincipalName")
            mismatch_fields = build_mismatch_fields(employee, user)
            employee.entra_user_id = user.get("id")
            employee.entra_upn = user_upn
            employee.entra_mail = user.get("mail")
            employee.entra_display_name = user.get("displayName")
            employee.entra_given_name = user.get("givenName")
            employee.entra_surname = user.get("surname")
            employee.entra_job_title = user.get("jobTitle")
            employee.entra_mobile_phone = user.get("mobilePhone")
            employee.entra_department = user.get("department")
            employee.entra_office_location = user.get("officeLocation")
            employee.entra_street_address = user.get("streetAddress")
            employee.entra_postal_code = user.get("postalCode")
            employee.entra_country = user.get("country")
            employee.entra_account_enabled = user.get("accountEnabled")
            employee.entra_mismatch_fields = mismatch_fields
            employee.entra_last_synced_at = datetime.now(UTC)
            employee.entra_upn_mismatch = bool(
                employee.email and user_upn and employee.email.lower() != user_upn.lower()
            )

            updated += 1

        if args.dry_run:
            db.rollback()
        else:
            db.commit()

        skipped = len(employees) - len(matched_ids)

        summary = {
            "employees_loaded": len(employees),
            "matched_updated": updated,
            "employees_not_matched": skipped,
            "entra_users_not_matched": not_matched,
            "dry_run": args.dry_run,
        }

        if args.json:
            print(json.dumps(summary))
            return

        print("\n" + "-" * 70)
        print("SUMMARY")
        print("-" * 70)
        print(f"Employees loaded:     {summary['employees_loaded']}")
        print(f"Matched & updated:    {summary['matched_updated']}{' (dry-run)' if args.dry_run else ''}")
        print(f"Employees not matched: {summary['employees_not_matched']}")
        print(f"Entra users not matched: {summary['entra_users_not_matched']}")
        print("-" * 70)


if __name__ == "__main__":
    main()
