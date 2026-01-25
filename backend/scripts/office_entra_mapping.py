#!/usr/bin/env python3
"""
Direct mapping table from Entra M365 Group IDs to office identifiers.

This mapping was created based on analysis of:
- exportGroups_2026-1-25.csv (full group list)
- Groups (1).csv (mail-enabled security groups)
- Groups (2).csv (M365 groups)
- Mailboxes.csv (user mailbox data with CustomAttribute1 containing Vitec IDs)

The mapping uses M365 Group ID as the primary key and maps to office
by either:
- office_name: Match by Office.name field
- legal_name: Match by Office.legal_name field
- city: Match by Office.city field
- email_prefix: Match by email prefix in Office.email

Priority: office_name > legal_name > city > email_prefix
"""

from __future__ import annotations

# Mapping from M365 Group ID to office identifier
# Format: group_id -> {"match_type": "field_name", "value": "field_value"}
#
# Note: The 6-digit codes (139xxx) found in Exchange/M365 group names and email
# prefixes are internal Microsoft identifiers from legacy migrations, NOT Vitec
# office IDs. Vitec office IDs are 4 digits. There is no shared ID between the
# two systems, so we match by name/legal_name/city instead.
ENTRA_OFFICE_MAPPING: dict[str, dict[str, str]] = {
    # ========================
    # PRIMARY OFFICE GROUPS
    # ========================
    # ProAktiv Ålesund -> Ålesund office
    "944f022d-064c-45d2-b56d-326ce13bfeed": {
        "match_type": "office_name",
        "value": "Ålesund",
        "group_name": "ProAktiv Ålesund",
    },
    # ProAktiv Asker -> Asker office
    "58ee7095-6cf3-4a9f-bf13-f868a141cdf7": {
        "match_type": "office_name",
        "value": "Asker",
        "group_name": "ProAktiv Asker",
    },
    # ProAktiv Briskeby -> Briskeby office
    "7f9014b0-71ae-4078-a5b5-e8657cc5de6e": {
        "match_type": "office_name",
        "value": "Briskeby",
        "group_name": "ProAktiv Briskeby",
    },
    # ProAktiv Drammen og Lier -> Drammen & Lier office
    "0f590975-68c2-4cbf-b41a-6c7841629eae": {
        "match_type": "office_name",
        "value": "Drammen & Lier",
        "group_name": "ProAktiv Drammen og Lier",
    },
    # ProAktiv Eiendomsmegling (Bergen HQ) -> Bergen / Småstrandgaten office
    "4aa54665-bd55-4a94-835c-02f4cfb27229": {
        "match_type": "city",
        "value": "Bergen",
        "group_name": "ProAktiv Eiendomsmegling",
        "notes": "Main Bergen office - Småstrandgaten",
    },
    # ProAktiv Holmestrand -> Holmestrand office
    "85b3d368-26a1-4f2c-ac51-db3598e0f415": {
        "match_type": "office_name",
        "value": "Holmestrand",
        "group_name": "ProAktiv Holmestrand",
    },
    # Proaktiv Lillestrøm -> Lillestrøm office
    "3146d21c-609d-4cdf-9ab3-bbc604e0e9c6": {
        "match_type": "office_name",
        "value": "Lillestrøm",
        "group_name": "Proaktiv Lillestrøm",
    },
    # ProAktiv Lørenskog -> Lørenskog office
    "750c6a8a-14ef-4cf2-8d02-f426f7945e7e": {
        "match_type": "office_name",
        "value": "Lørenskog",
        "group_name": "ProAktiv Lørenskog",
    },
    # ProAktiv Moholt -> Moholt office (Trondheim area)
    "6cae4798-c8bf-4f59-ab21-e9cb7f6d267c": {
        "match_type": "office_name",
        "value": "Moholt",
        "group_name": "ProAktiv Moholt",
    },
    # ProAktiv Oppgjør -> Oppgjør office
    "207e6086-7cac-4db1-afb0-72b8c7393d97": {
        "match_type": "office_name",
        "value": "Oppgjør",
        "group_name": "ProAktiv Oppgjør",
    },
    # ProAktiv Sandviken -> Sandviken office
    "09159403-cf74-44e0-8bf1-1edce276554b": {
        "match_type": "office_name",
        "value": "Sandviken",
        "group_name": "ProAktiv Sandviken",
    },
    # ProAktiv Sarpsborg -> Sarpsborg office
    "e516e78d-47d7-41e6-a553-68b29ad9a05f": {
        "match_type": "office_name",
        "value": "Sarpsborg",
        "group_name": "ProAktiv Sarpsborg",
    },
    # ProAktiv Stavanger -> Stavanger office
    "1e56d097-ea2d-4236-82f5-dc18833cf809": {
        "match_type": "office_name",
        "value": "Stavanger",
        "group_name": "ProAktiv Stavanger",
    },
    # ProAktiv Voss -> Voss office
    "c625aa27-8074-4dac-a907-e01c7ec9e649": {
        "match_type": "office_name",
        "value": "Voss",
        "group_name": "ProAktiv Voss",
    },
    # DF-ProAktivTrondheimSentrum -> Trondheim Sentrum office
    "aa8ababb-26b4-4c48-b7e5-2b732e879b05": {
        "match_type": "office_name",
        "value": "Trondheim Sentrum",
        "group_name": "DF-ProAktivTrondheimSentrum",
        "notes": "Also known as Pacta Eiendom AS",
    },
    # Trondheim Syd Eiendom AS -> Heimdal office
    "73897280-9319-41d1-b48f-79269a1377b2": {
        "match_type": "legal_name",
        "value": "Trondheim Syd Eiendom AS",
        "group_name": "Trondheim Syd Eiendom AS",
        "notes": "Heimdal office",
    },
    # Edland, Mannes & Rege AS -> Jæren office
    "45f61d3c-faf4-4b44-b9d4-a22a755863c0": {
        "match_type": "legal_name",
        "value": "Edland, Mannes & Rege AS",
        "group_name": "Edland, Mannes & Rege AS",
        "notes": "Jæren/Sandnes office",
    },
    # Oslo bolig & prosjektmegling AS -> Oslo/Briskeby office
    "101ab74a-18a5-4df3-8307-91fb495029bd": {
        "match_type": "legal_name",
        "value": "Oslo bolig & prosjektmegling AS",
        "group_name": "Oslo bolig & prosjektmegling AS",
        "notes": "May map to Briskeby or separate Oslo office",
    },
    # ========================
    # REGIONAL / SPECIAL GROUPS
    # ========================
    # Proaktiv Trøndelag -> Regional group (Trondheim area)
    "92e99405-01c8-4263-a590-343db0c6cfa4": {
        "match_type": "skip",
        "value": "",
        "group_name": "Proaktiv Trøndelag",
        "notes": "Regional group - covers multiple offices",
    },
    # ProAktiv AS -> HQ / Corporate
    "2fa0c1cd-00fa-4eb5-b4da-f3222b6a363c": {
        "match_type": "skip",
        "value": "",
        "group_name": "ProAktiv AS",
        "notes": "Corporate/HQ group - not a specific office",
    },
    # ProAktiv Common Resources -> Shared resources
    "62793246-488e-40b6-98a8-c19430e2c6dc": {
        "match_type": "skip",
        "value": "",
        "group_name": "ProAktiv Common Resources",
        "notes": "Common resources - not a specific office",
    },
}


def get_office_for_group(group_id: str, offices: list) -> tuple[object | None, str]:
    """
    Find office matching a group ID using the mapping table.

    Args:
        group_id: The Entra M365 Group ID
        offices: List of Office objects from database

    Returns:
        Tuple of (Office object or None, match_reason string)
    """
    mapping = ENTRA_OFFICE_MAPPING.get(group_id)
    if not mapping:
        return None, "no_mapping"

    match_type = mapping.get("match_type")
    value = mapping.get("value", "").lower()

    if match_type == "skip":
        return None, "skipped"

    for office in offices:
        if match_type == "office_name":
            if office.name and office.name.lower() == value:
                return office, f"mapping:{match_type}"
        elif match_type == "legal_name":
            if office.legal_name and value in office.legal_name.lower():
                return office, f"mapping:{match_type}"
        elif match_type == "city":
            if office.city and office.city.lower() == value:
                return office, f"mapping:{match_type}"
        elif match_type == "email_prefix":
            if office.email and "@" in office.email:
                prefix = office.email.split("@")[0].lower()
                if prefix == value:
                    return office, f"mapping:{match_type}"

    return None, f"mapping_not_found:{match_type}={value}"


def print_mapping_summary() -> None:
    """Print a summary of the mapping table."""
    print("=" * 80)
    print("ENTRA M365 GROUP TO OFFICE MAPPING TABLE")
    print("=" * 80)

    active_mappings = [(gid, m) for gid, m in ENTRA_OFFICE_MAPPING.items() if m.get("match_type") != "skip"]
    skipped_mappings = [(gid, m) for gid, m in ENTRA_OFFICE_MAPPING.items() if m.get("match_type") == "skip"]

    print(f"\nActive Mappings ({len(active_mappings)}):")
    print("-" * 80)
    for _group_id, mapping in sorted(active_mappings, key=lambda x: x[1].get("group_name", "")):
        group_name = mapping.get("group_name", "Unknown")
        match_type = mapping.get("match_type")
        value = mapping.get("value")
        notes = mapping.get("notes", "")

        notes_str = f" ({notes})" if notes else ""

        print(f"  {group_name:<40} -> {match_type}={value}{notes_str}")

    print(f"\nSkipped Groups ({len(skipped_mappings)}):")
    print("-" * 80)
    for _group_id, mapping in sorted(skipped_mappings, key=lambda x: x[1].get("group_name", "")):
        group_name = mapping.get("group_name", "Unknown")
        notes = mapping.get("notes", "No reason")
        print(f"  {group_name:<40} - {notes}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    print_mapping_summary()
