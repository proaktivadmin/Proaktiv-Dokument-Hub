#!/usr/bin/env python3
"""
Import Entra ID M365 Group data into local office records (read-only to Entra).

This script:
1. Fetches M365 Groups from Microsoft Graph (GET only)
2. Matches groups to existing offices by email/name patterns
3. Stores Entra values in secondary `entra_*` columns
4. Computes mismatch fields without overwriting Vitec data

Vitec Next remains the source of truth for primary fields.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Iterable
from datetime import UTC, datetime

import httpx
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.office import Office

GRAPH_SCOPE = "https://graph.microsoft.com/.default"
GRAPH_GROUPS_URL = "https://graph.microsoft.com/v1.0/groups"

# Select only Unified (M365) groups
GRAPH_FILTER = "groupTypes/any(c:c eq 'Unified')"
GRAPH_FIELDS = ",".join(
    [
        "id",
        "displayName",
        "mail",
        "description",
        "createdDateTime",
    ]
)


def get_access_token(tenant_id: str, client_id: str, client_secret: str) -> str:
    """Get OAuth2 access token using client credentials flow."""
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


def fetch_entra_groups(access_token: str) -> Iterable[dict]:
    """Fetch all M365 Groups from Microsoft Graph with pagination."""
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "$filter": GRAPH_FILTER,
        "$select": GRAPH_FIELDS,
        "$top": "100",
    }
    url = GRAPH_GROUPS_URL

    while url:
        response = httpx.get(url, headers=headers, params=params, timeout=30.0)
        response.raise_for_status()
        payload = response.json()
        yield from payload.get("value", [])
        url = payload.get("@odata.nextLink")
        params = None  # nextLink includes params


def fetch_group_member_count(access_token: str, group_id: str) -> int | None:
    """Fetch member count for a specific group."""
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"{GRAPH_GROUPS_URL}/{group_id}/members/$count"
    try:
        response = httpx.get(
            url,
            headers={**headers, "ConsistencyLevel": "eventual"},
            timeout=30.0,
        )
        response.raise_for_status()
        return int(response.text)
    except Exception:
        return None


def fetch_group_sharepoint_url(access_token: str, group_id: str) -> str | None:
    """Fetch SharePoint site URL for a group."""
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"{GRAPH_GROUPS_URL}/{group_id}/sites/root"
    try:
        response = httpx.get(url, headers=headers, timeout=30.0)
        response.raise_for_status()
        return response.json().get("webUrl")
    except Exception:
        return None


def normalize_text(value: str | None) -> str | None:
    """Normalize text for comparison."""
    if value is None:
        return None
    value = value.strip().lower()
    return value if value else None


def find_matching_office(group: dict, offices: list[Office]) -> Office | None:
    """Find the best matching office for a group using priority matching."""
    group_mail = group.get("mail", "").lower()
    group_name = group.get("displayName", "").lower()

    # 1. Email exact match (highest priority)
    if group_mail:
        for office in offices:
            if office.email and office.email.lower() == group_mail:
                return office

    # 2. Email prefix match
    if group_mail and "@" in group_mail:
        group_prefix = group_mail.split("@")[0]
        for office in offices:
            if office.email and "@" in office.email:
                office_prefix = office.email.split("@")[0].lower()
                if office_prefix == group_prefix:
                    return office

    # 3. City name in group name
    for office in offices:
        if office.city and normalize_text(office.city) in group_name:
            return office

    # 4. Office name in group name
    for office in offices:
        office_name_norm = normalize_text(office.name)
        if office_name_norm and office_name_norm in group_name:
            return office

    return None


def build_mismatch_fields(office: Office, group: dict) -> list[str]:
    """Compute which fields differ between Vitec (office) and Entra (group)."""
    mismatches: list[str] = []

    def check(field: str, vitec_value: str | None, entra_value: str | None) -> None:
        if not vitec_value or not entra_value:
            return
        if normalize_text(vitec_value) != normalize_text(entra_value):
            mismatches.append(field)

    check("name", office.name, group.get("displayName"))
    check("email", office.email, group.get("mail"))
    check("description", office.description, group.get("description"))

    return mismatches


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Import Entra ID M365 Groups into local office records.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without updating the database.",
    )
    parser.add_argument(
        "--filter-office-id",
        help="Only update a specific office by UUID.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output a JSON summary only.",
    )
    parser.add_argument(
        "--fetch-details",
        action="store_true",
        help="Fetch additional details (member count, SharePoint URL). Slower.",
    )
    return parser.parse_args()


def main() -> None:
    """Main entry point."""
    args = parse_args()
    quiet = args.json

    def log(message: str) -> None:
        if not quiet:
            print(message)

    def log_error(message: str) -> None:
        print(message, file=sys.stderr)

    # Get environment variables
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
    log("ENTRA ID OFFICE IMPORT - Read-only to Entra (DB updates only)")
    log("=" * 70)

    # Get access token
    access_token = get_access_token(tenant_id, client_id, client_secret)

    # Connect to database
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)

    with Session() as db:
        # Load offices
        query = db.query(Office).filter(Office.is_active == True)  # noqa: E712
        if args.filter_office_id:
            query = query.filter(Office.id == args.filter_office_id)

        offices = query.all()
        matched_ids: set[str] = set()

        updated = 0
        not_matched_groups = 0

        log(f"Loaded {len(offices)} active offices from database")
        log("Fetching M365 Groups from Microsoft Graph...")

        # Fetch and process groups
        groups_list = list(fetch_entra_groups(access_token))
        log(f"Found {len(groups_list)} M365 Groups")

        for group in groups_list:
            office = find_matching_office(group, offices)

            if not office:
                not_matched_groups += 1
                log(f"  No match: {group.get('displayName')} ({group.get('mail')})")
                continue

            matched_ids.add(str(office.id))

            # Fetch additional details if requested
            member_count = None
            sharepoint_url = None
            if args.fetch_details:
                member_count = fetch_group_member_count(access_token, group["id"])
                sharepoint_url = fetch_group_sharepoint_url(access_token, group["id"])

            # Compute mismatches
            mismatch_fields = build_mismatch_fields(office, group)

            # Update office with Entra data
            office.entra_group_id = group.get("id")
            office.entra_group_name = group.get("displayName")
            office.entra_group_mail = group.get("mail")
            office.entra_group_description = group.get("description")
            office.entra_sharepoint_url = sharepoint_url
            office.entra_member_count = member_count
            office.entra_mismatch_fields = mismatch_fields
            office.entra_last_synced_at = datetime.now(UTC)

            updated += 1
            log(f"  Matched: {group.get('displayName')} -> {office.name}")
            if mismatch_fields:
                log(f"    Mismatches: {', '.join(mismatch_fields)}")

        # Commit or rollback
        if args.dry_run:
            db.rollback()
        else:
            db.commit()

        offices_not_matched = len(offices) - len(matched_ids)

        # Build summary
        summary = {
            "offices_loaded": len(offices),
            "matched_updated": updated,
            "offices_not_matched": offices_not_matched,
            "groups_not_matched": not_matched_groups,
            "dry_run": args.dry_run,
        }

        if args.json:
            print(json.dumps(summary))
            return

        print("\n" + "-" * 70)
        print("SUMMARY")
        print("-" * 70)
        print(f"Offices loaded:       {summary['offices_loaded']}")
        print(f"Matched & updated:    {summary['matched_updated']}{' (dry-run)' if args.dry_run else ''}")
        print(f"Offices not matched:  {summary['offices_not_matched']}")
        print(f"Groups not matched:   {summary['groups_not_matched']}")
        print("-" * 70)


if __name__ == "__main__":
    main()
