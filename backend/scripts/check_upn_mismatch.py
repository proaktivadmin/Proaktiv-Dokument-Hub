#!/usr/bin/env python3
"""
Check for UPN mismatches between database emails and Entra ID User Principal Names.

This script:
1. Fetches all active internal employees from the database
2. Connects to Microsoft Graph API
3. Compares UPN in Entra ID with email in database
4. Flags accounts where they don't match (these will fail SSO)

Usage:
    Set environment variables:
        DATABASE_URL - PostgreSQL connection string
        ENTRA_TENANT_ID - Azure AD tenant ID
        ENTRA_CLIENT_ID - App registration client ID
        ENTRA_CLIENT_SECRET - App client secret

    Then run:
        python check_upn_mismatch.py
"""

import csv
import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text

try:
    import requests
except ImportError:
    print("Installing requests...")
    os.system("pip install requests")
    import requests


def get_access_token(tenant_id: str, client_id: str, client_secret: str) -> str:
    """Get Microsoft Graph access token using client credentials."""
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "https://graph.microsoft.com/.default",
    }
    response = requests.post(url, data=data)
    response.raise_for_status()
    return response.json()["access_token"]


def find_entra_user(email: str, access_token: str) -> dict | None:
    """Find a user in Entra ID by email address."""
    headers = {"Authorization": f"Bearer {access_token}"}

    # Try UPN lookup first
    try:
        url = f"https://graph.microsoft.com/v1.0/users/{email}"
        response = requests.get(url, headers=headers, params={"$select": "id,userPrincipalName,mail,displayName"})
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass

    # Try mail filter
    try:
        url = "https://graph.microsoft.com/v1.0/users"
        response = requests.get(
            url,
            headers=headers,
            params={
                "$filter": f"mail eq '{email}'",
                "$select": "id,userPrincipalName,mail,displayName",
            },
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("value"):
                return data["value"][0]
    except Exception:
        pass

    # Try proxyAddresses filter
    try:
        url = "https://graph.microsoft.com/v1.0/users"
        response = requests.get(
            url,
            headers=headers,
            params={
                "$filter": f"proxyAddresses/any(p:p eq 'smtp:{email}')",
                "$select": "id,userPrincipalName,mail,displayName",
            },
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("value"):
                return data["value"][0]
    except Exception:
        pass

    return None


def main():
    print("\n" + "=" * 70)
    print("UPN MISMATCH CHECK - Entra ID vs Database")
    print("=" * 70)

    # Get configuration from environment
    database_url = os.environ.get("DATABASE_URL")
    tenant_id = os.environ.get("ENTRA_TENANT_ID")
    client_id = os.environ.get("ENTRA_CLIENT_ID")
    client_secret = os.environ.get("ENTRA_CLIENT_SECRET")

    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set")
        sys.exit(1)

    if not all([tenant_id, client_id, client_secret]):
        print("ERROR: ENTRA_TENANT_ID, ENTRA_CLIENT_ID, and ENTRA_CLIENT_SECRET must be set")
        sys.exit(1)

    # Step 1: Get employees from database
    print("\n[1/3] Fetching employees from database...")
    engine = create_engine(database_url)

    with engine.connect() as conn:
        result = conn.execute(
            text("""
            SELECT
                e.id,
                e.first_name,
                e.last_name,
                e.email,
                e.vitec_employee_id,
                e.employee_type,
                e.status,
                o.name as office_name
            FROM employees e
            LEFT JOIN offices o ON e.office_id = o.id
            WHERE e.email IS NOT NULL
              AND e.status = 'active'
              AND e.employee_type = 'internal'
            ORDER BY e.last_name, e.first_name
        """)
        )

        employees = []
        for row in result:
            employees.append(
                {
                    "id": str(row[0]),
                    "first_name": row[1],
                    "last_name": row[2],
                    "email": row[3],
                    "vitec_id": row[4],
                    "employee_type": row[5],
                    "status": row[6],
                    "office": row[7],
                }
            )

    print(f"  Found {len(employees)} active internal employees")

    # Step 2: Get access token
    print("\n[2/3] Connecting to Microsoft Graph...")
    try:
        access_token = get_access_token(tenant_id, client_id, client_secret)
        print("  Connected successfully")
    except Exception as e:
        print(f"ERROR: Failed to authenticate: {e}")
        sys.exit(1)

    # Step 3: Compare UPNs
    print("\n[3/3] Comparing UPNs with database emails...")

    results = []
    match_count = 0
    mismatch_count = 0
    not_found_count = 0

    for i, emp in enumerate(employees, 1):
        db_email = emp["email"].lower().strip()
        display_name = f"{emp['first_name']} {emp['last_name']}"

        print(f"  [{i}/{len(employees)}] {display_name} ({db_email})...", end="", flush=True)

        entra_user = find_entra_user(db_email, access_token)

        result = {
            "employee_id": emp["id"],
            "name": display_name,
            "database_email": db_email,
            "entra_upn": "",
            "entra_mail": "",
            "status": "",
            "issue": "",
            "office": emp["office"] or "",
            "vitec_id": emp["vitec_id"] or "",
        }

        if not entra_user:
            result["status"] = "NOT_FOUND"
            result["issue"] = "No Entra ID account found"
            print(" NOT FOUND")
            not_found_count += 1
        else:
            upn = entra_user.get("userPrincipalName", "").lower().strip()
            mail = (entra_user.get("mail") or "").lower().strip()

            result["entra_upn"] = entra_user.get("userPrincipalName", "")
            result["entra_mail"] = entra_user.get("mail", "") or ""

            if upn == db_email:
                result["status"] = "OK"
                print(" OK")
                match_count += 1
            elif mail == db_email:
                result["status"] = "UPN_MISMATCH"
                result["issue"] = f"UPN ({upn}) differs from DB email - SSO will FAIL"
                print(f" MISMATCH: UPN={upn}")
                mismatch_count += 1
            else:
                result["status"] = "UPN_MISMATCH"
                result["issue"] = f"Neither UPN ({upn}) nor Mail ({mail}) match DB email"
                print(" MISMATCH")
                mismatch_count += 1

        results.append(result)

    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"\n  Total employees checked:  {len(employees)}")
    print(f"  Matching (OK):            {match_count}")
    print(f"  Mismatched (SSO ISSUE):   {mismatch_count}")
    print(f"  Not found in Entra:       {not_found_count}")

    # Show affected users
    affected = [r for r in results if r["status"] == "UPN_MISMATCH"]
    if affected:
        print("\n" + "=" * 70)
        print("AFFECTED USERS (UPN != Database Email) - SSO WILL FAIL")
        print("=" * 70)

        for user in affected:
            print(f"\n  {user['name']}")
            print(f"    Office:         {user['office']}")
            print(f"    Database Email: {user['database_email']}")
            print(f"    Entra UPN:      {user['entra_upn']}")
            print(f"    Entra Mail:     {user['entra_mail']}")
            print(f"    Issue:          {user['issue']}")

    # Show not found
    not_found = [r for r in results if r["status"] == "NOT_FOUND"]
    if not_found:
        print("\n" + "=" * 70)
        print("NOT FOUND IN ENTRA ID")
        print("=" * 70)
        for user in not_found:
            print(f"  {user['name']} - {user['database_email']} ({user['office']})")

    # Update database with UPN mismatch flags
    print("\n[4/4] Updating database with UPN mismatch flags...")

    update_count = 0
    with engine.connect() as conn:
        for result in results:
            if result["status"] == "UPN_MISMATCH":
                conn.execute(
                    text("""
                    UPDATE employees
                    SET entra_upn = :upn, entra_upn_mismatch = TRUE
                    WHERE id = :id
                """),
                    {"id": result["employee_id"], "upn": result["entra_upn"]},
                )
                update_count += 1
            elif result["status"] == "OK":
                conn.execute(
                    text("""
                    UPDATE employees
                    SET entra_upn = :upn, entra_upn_mismatch = FALSE
                    WHERE id = :id
                """),
                    {"id": result["employee_id"], "upn": result["entra_upn"]},
                )
        conn.commit()

    print(f"  Updated {update_count} employees with UPN mismatch flag")

    # Export to CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = os.path.join(os.path.dirname(__file__), f"upn_mismatch_report_{timestamp}.csv")

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print(f"\nFull report exported to: {csv_path}")
    print("\nDone!")


if __name__ == "__main__":
    main()
