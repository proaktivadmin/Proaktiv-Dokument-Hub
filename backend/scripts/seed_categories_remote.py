"""
Seed categories via API.
Usage: python backend/scripts/seed_categories_remote.py
"""

import requests

API_URL = "https://proaktiv-dokument-hub-production.up.railway.app/api/categories"

CATEGORIES = [
    {"name": "Akseptbrev", "icon": "FileCheck", "description": "Akseptbrev og bekreftelser", "sort_order": 1},
    {
        "name": "AML",
        "icon": "Shield",
        "description": "Anti-hvitvaskingsdokumenter og risikovurderinger",
        "sort_order": 2,
    },
    {"name": "Bortefester", "icon": "Home", "description": "Dokumenter for bortefester", "sort_order": 3},
    {"name": "Følgebrev", "icon": "Mail", "description": "Følgebrev og tinglysningsdokumenter", "sort_order": 4},
    {"name": "Forkjøpsrett", "icon": "Scale", "description": "Forkjøpsrett og borettslag", "sort_order": 5},
    {
        "name": "Forretningsfører",
        "icon": "Building",
        "description": "Kommunikasjon med forretningsfører",
        "sort_order": 6,
    },
    {
        "name": "Informasjonsbrev",
        "icon": "Info",
        "description": "Informasjonsbrev til kjøper og selger",
        "sort_order": 7,
    },
    {"name": "Kontrakt", "icon": "FileText", "description": "Kontrakter og avtaler", "sort_order": 8},
    {"name": "Salgsmelding", "icon": "Megaphone", "description": "Salgsmeldinger", "sort_order": 9},
    {"name": "SMS", "icon": "MessageSquare", "description": "SMS-maler", "sort_order": 10},
    {"name": "Topptekst", "icon": "Type", "description": "Topptekster og bunntekster", "sort_order": 11},
]


def main():
    print(f"Seeding categories to {API_URL}...")

    for cat in CATEGORIES:
        resp = requests.post(API_URL, json=cat)
        if resp.status_code == 201:
            print(f"  [OK] Created: {cat['name']}")
        elif resp.status_code == 400:
            print(f"  [--] Exists: {cat['name']}")
        else:
            print(f"  [!!] Failed {cat['name']}: {resp.status_code} {resp.text}")

    print("\nDone!")


if __name__ == "__main__":
    main()
