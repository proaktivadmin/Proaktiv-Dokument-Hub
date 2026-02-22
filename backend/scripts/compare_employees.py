"""Compare Vitec employee list with dashboard database."""

import os

from sqlalchemy import create_engine, text

DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(DATABASE_URL)

# Vitec employee emails (extracted from the list)
vitec_emails = [
    "froyland@proaktiv.no",
    "marthinsen@proaktiv.no",
    "alexander.abelseth@proaktiv.no",
    "alexander.bergheim@proaktiv.no",
    "am@proaktiv.no",
    "an@proaktiv.no",
    "amalie@proaktiv.no",
    "abo@proaktiv.no",
    "aw@proaktiv.no",
    "ab@proaktiv.no",
    "ae@proaktiv.no",
    "ommundsen@proaktiv.no",
    "alo@proaktiv.no",
    "amh@proaktiv.no",
    "mjolne@proaktiv.no",
    "aaf@proaktiv.no",
    "aj@proaktiv.no",
    "asbjorn@proaktiv.no",
    "aurora@proaktiv.no",
    "bendik@proaktiv.no",
    "edland@proaktiv.no",
    "bh@proaktiv.no",
    "camilla@proaktiv.no",
    "cr@proaktiv.no",
    "celine.olsen@proaktiv.no",
    "cas@proaktiv.no",
    "cap@proaktiv.no",
    "cs@proaktiv.no",
    "christian@proaktiv.no",
    "ca@proaktiv.no",
    "cp@proaktiv.no",
    "en@proaktiv.no",
    "ed@proaktiv.no",
    "edl@proaktiv.no",
    "elisabeth@proaktiv.no",
    "erik.andre.engebretsen@proaktiv.no",
    "el@proaktiv.no",
    "fredrik.e@proaktiv.no",
    "fj@proaktiv.no",
    "frida@proaktiv.no",
    "geir@proaktiv.no",
    "geir.johannessen@proaktiv.no",
    "gag@proaktiv.no",
    "hans@proaktiv.no",
    "hege@proaktiv.no",
    "hjh@proaktiv.no",
    "hakon.gronlund@proaktiv.no",
    "ial@proaktiv.no",
    "inge@proaktiv.no",
    "ihb@proaktiv.no",
    "id@proaktiv.no",
    "jas@proaktiv.no",
    "jon@proaktiv.no",
    "jk@proaktiv.no",
    "jonas.maalo@proaktiv.no",
    "jt@proaktiv.no",
    "julia@proaktiv.no",
    "julianne@proaktiv.no",
    "justyna.szabla@proaktiv.no",
    "jorgen@proaktiv.no",
    "jorgen.ranum@proaktiv.no",
    "kai.roger.hagen@proaktiv.no",
    "karianne@proaktiv.no",
    "karina.vonmehren@proaktiv.no",
    "kse@proaktiv.no",
    "kmw@proaktiv.no",
    "kv@proaktiv.no",
    "kine@proaktiv.no",
    "birkeland@proaktiv.no",
    "ktd@proaktiv.no",
    "kbh@proaktiv.no",
    "kg@proaktiv.no",
    "ks@proaktiv.no",
    "km@proaktiv.no",
    "lofthus@proaktiv.no",
    "lasse@proaktiv.no",
    "lu@proaktiv.no",
    "lck@proaktiv.no",
    "liba@proaktiv.no",
    "lk@proaktiv.no",
    "madelen@proaktiv.no",
    "mk@proaktiv.no",
    "mu@proaktiv.no",
    "msk@proaktiv.no",
    "mae@proaktiv.no",
    "langeland@proaktiv.no",
    "marcus@proaktiv.no",
    "mjolhus@proaktiv.no",
    "mgi@proaktiv.no",
    "mry@proaktiv.no",
    "markus.thoen@proaktiv.no",
    "msy@proaktiv.no",
    "mml@proaktiv.no",
    "ml@proaktiv.no",
    "nina.aamodt@proaktiv.no",
    "ola@proaktiv.no",
    "olav@proaktiv.no",
    "owl@proaktiv.no",
    "omm@proaktiv.no",
    "oliver@proaktiv.no",
    "of@proaktiv.no",
    "ok@proaktiv.no",
    "paa@proaktiv.no",
    "rhs@proaktiv.no",  # Note: appears twice in Vitec list (Rakel Hvidsten Søvik and Rakel Søvik)
    "re@proaktiv.no",
    "sander@proaktiv.no",
    "sj@proaktiv.no",
    "sebastian@proaktiv.no",
    "sbs@proaktiv.no",
    "sg@proaktiv.no",
    "svb@proaktiv.no",
    "sf@proaktiv.no",
    "sdj@proaktiv.no",
    "lie@proaktiv.no",
    "steinar@proaktiv.no",
    "erichsen@proaktiv.no",
    "sv@proaktiv.no",
    "svein.eng@proaktiv.no",
    "svein.gunnar.hansen@proaktiv.no",
    "skb@proaktiv.no",
    "terje.nicolaysen@proaktiv.no",
    "tls@proaktiv.no",
    "mannes@proaktiv.no",
    "tore@proaktiv.no",
    "ts@proaktiv.no",
    "trude@proaktiv.no",
    "th@proaktiv.no",
    "vvi@proaktiv.no",
    "vs@proaktiv.no",
    "zuzanna@proaktiv.no",
    "oystein@proaktiv.no",
    "rege@proaktiv.no",
]

# Normalize emails to lowercase
vitec_emails_lower = {e.lower() for e in vitec_emails}

with engine.connect() as conn:
    # Get all employees from database
    result = conn.execute(
        text("""
        SELECT first_name, last_name, email, status
        FROM employees
        ORDER BY email
    """)
    )

    db_employees = list(result)
    db_emails_lower = {row.email.lower(): row for row in db_employees if row.email}

    print("=" * 80)
    print("EMPLOYEE COMPARISON: Vitec vs Dashboard")
    print("=" * 80)
    print()

    # Find employees in Vitec but NOT in dashboard
    missing_in_db = []
    for email in vitec_emails_lower:
        if email not in db_emails_lower:
            missing_in_db.append(email)

    print(f"MISSING IN DASHBOARD (in Vitec but not in DB): {len(missing_in_db)}")
    print("-" * 60)
    if missing_in_db:
        for email in sorted(missing_in_db):
            print(f"  - {email}")
    else:
        print("  None - all Vitec employees are in the dashboard!")
    print()

    # Find employees in dashboard but NOT in Vitec
    extra_in_db = []
    for email in db_emails_lower:
        if email not in vitec_emails_lower:
            row = db_emails_lower[email]
            extra_in_db.append((email, row.first_name, row.last_name, row.status))

    print(f"EXTRA IN DASHBOARD (in DB but not in Vitec list): {len(extra_in_db)}")
    print("-" * 60)
    if extra_in_db:
        for email, first, last, status in sorted(extra_in_db):
            print(f"  - {first} {last} ({email}) [{status}]")
    else:
        print("  None - dashboard matches Vitec exactly!")
    print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Vitec employees:    {len(vitec_emails_lower)}")
    print(f"Dashboard employees: {len(db_emails_lower)}")
    print(f"Missing in dashboard: {len(missing_in_db)}")
    print(f"Extra in dashboard:   {len(extra_in_db)}")

    if len(missing_in_db) == 0 and len(extra_in_db) == 0:
        print("\n*** PERFECT MIRROR ***")
    elif len(missing_in_db) == 0:
        print(f"\n*** All Vitec employees present, but {len(extra_in_db)} extra in dashboard ***")
