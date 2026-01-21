"""
Seed Layout Partials Script

Populates the database with Vitec headers, footers, and signatures.
Based on .cursor/vitec-reference.md

Run with: python -m scripts.seed_layout_partials
Or remotely: python backend/scripts/seed_layout_partials.py --api-url <URL>
"""

import argparse
import asyncio
import os
import sys
from typing import Any

import requests

# Add parent directory to path for local execution
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# =============================================================================
# VITEC LAYOUT PARTIALS DATA
# Based on .cursor/vitec-reference.md
# =============================================================================

LAYOUT_PARTIALS: list[dict[str, Any]] = [
    # ----- HEADERS -----
    {
        "name": "Vitec Topptekst",
        "type": "header",
        "context": "pdf",
        "is_default": True,
        "html_content": """<div id="vitecTemplate">
  <span vitec-template="resource:Vitec Stilark">&nbsp;</span>
  <table style="width:21cm">
    <tbody>
      <tr>
        <td style="padding:1cm">
          <strong><small>[[meglerkontor.kjedenavn]]</small></strong>
        </td>
        <td style="padding:1cm; text-align:right">
          <img src="[[meglerkontor.firmalogourl]]" style="max-height:1.5cm; max-width:6cm" />
        </td>
      </tr>
    </tbody>
  </table>
</div>""",
        "created_by": "system",
        "updated_by": "system",
    },
    # ----- FOOTERS -----
    {
        "name": "Vitec Bunntekst",
        "type": "footer",
        "context": "pdf",
        "is_default": True,
        "html_content": """<div id="vitecTemplate">
  <span vitec-template="resource:Vitec Stilark">&nbsp;</span>
  <table cellspacing="0" style="border-collapse:collapse; table-layout:fixed; width:21cm">
    <tbody>
      <tr>
        <td colspan="30" style="padding-left:1cm">
          <small>[[meglerkontor.juridisknavn]]</small>
        </td>
        <td colspan="40" style="text-align:center">
          <small>[[meglerkontor.adresse]], [[meglerkontor.postnr]] [[meglerkontor.poststed]]</small>
        </td>
        <td colspan="30" style="padding-right:1cm; text-align:right">
          <small>Tlf: [[meglerkontor.tlf]]</small>
        </td>
      </tr>
      <tr>
        <td colspan="30" style="padding-left:1cm">
          <small>Org.nr: [[meglerkontor.orgnr]]</small>
        </td>
        <td colspan="40" style="text-align:center">
          <small>Besoksadresse: [[meglerkontor.besoksadresse]], [[meglerkontor.besokspostnr]] [[meglerkontor.besokspoststed]]</small>
        </td>
        <td colspan="30" style="padding-right:1cm; text-align:right">
          <small>[[meglerkontor.epost]]</small>
        </td>
      </tr>
    </tbody>
  </table>
</div>""",
        "created_by": "system",
        "updated_by": "system",
    },
    {
        "name": "Vitec Bunntekst Kontrakt",
        "type": "footer",
        "context": "pdf",
        "is_default": False,
        "html_content": """<div id="vitecTemplate">
  <span vitec-template="resource:Vitec Stilark">&nbsp;</span>
  <table style="height:1.5cm; table-layout:fixed; width:20cm">
    <tbody>
      <tr>
        <td style="font-size:8pt; padding:0.25cm 0.5cm 0.5cm 2cm; vertical-align:bottom">
          <div style="border-top:solid 1px #000000; text-align:center; width:3cm">
            <span vitec-if="!Model.oppdrag.type.Contains(&quot;tleie&quot;)">Selger</span>
            <span vitec-if="Model.oppdrag.type.Contains(&quot;tleie&quot;)">Utleier</span>
          </div>
        </td>
        <td style="padding:0.5cm; text-align:center">
          <span style="font-size:8pt">side [[p]] av [[P]]</span>
        </td>
        <td style="font-size:8pt; padding:0.25cm 1cm 0.5cm 0.5cm; text-align:right; vertical-align:bottom">
          <div style="border-top:solid 1px #000000; float:right; text-align:center; width:3cm">
            <span vitec-if="!Model.oppdrag.type.Contains(&quot;tleie&quot;)">Kjoper</span>
            <span vitec-if="Model.oppdrag.type.Contains(&quot;tleie&quot;)">Leietaker</span>
          </div>
        </td>
      </tr>
    </tbody>
  </table>
</div>""",
        "created_by": "system",
        "updated_by": "system",
    },
    {
        "name": "Vitec Bunntekst Sikring",
        "type": "footer",
        "context": "pdf",
        "is_default": False,
        "html_content": """<style type="text/css">
#vitecTemplate td[data-label] {
    padding: 16px 2px 4px 3px;
    position: relative;
}
#vitecTemplate td[data-label]:before {
    content: attr(data-label);
    text-align: left;
    color: #333;
    font-size: 7pt;
    line-height: 8pt;
    text-transform: uppercase;
    display: block;
    position: absolute;
    top: 1px;
}
#vitecTemplate tr th,
#vitecTemplate tr td {
    vertical-align: middle;
    border: solid 1px #000;
    font-family: 'Open sans', sans-serif;
    font-size: 8pt;
    line-height: 9pt;
}
#vitecTemplate td.no-border {
    border: none;
}
</style>

<div id="vitecTemplate" style="padding-left:1cm; padding-right:1cm">
  <table>
    <tbody>
      <tr>
        <td colspan="25" data-label="Dato">&nbsp;</td>
        <td colspan="75" data-label="Pantsetters underskrift">&nbsp;</td>
      </tr>
      <tr contenteditable="false">
        <td class="no-border" colspan="20">
          <small>Statens kartverk - rev 01/19</small>
        </td>
        <td class="no-border" colspan="60" style="text-align:center">
          <small>Pantedokument - Panterett i
            <span vitec-if="Model.eiendom.eieform != &quot;Andel&quot;">fast eiendom</span>
            <span vitec-if="Model.eiendom.eieform == &quot;Andel&quot;">andel i borettslag</span>
          </small>
        </td>
        <td class="no-border" colspan="20" style="text-align:right">
          <small>Side [[p]] av [[P]]</small>
        </td>
      </tr>
    </tbody>
  </table>
</div>""",
        "created_by": "system",
        "updated_by": "system",
    },
    {
        "name": "Vitec Bunntekst Skjote",
        "type": "footer",
        "context": "pdf",
        "is_default": False,
        "html_content": """<div id="vitecTemplate" style="padding-left:0.5cm; padding-right:0.5cm">
  <table>
    <tbody>
      <tr>
        <td colspan="25" data-label="Dato">&nbsp;</td>
        <td colspan="75" data-label="Utstederens underskrift">&nbsp;</td>
      </tr>
      <tr contenteditable="false">
        <td class="no-border" colspan="20"><small>GA-5400 B</small></td>
        <td class="no-border" colspan="60" style="text-align:center"><small>Skjote</small></td>
        <td class="no-border" colspan="20" style="text-align:right"><small>Side [[p]] av [[P]]</small></td>
      </tr>
    </tbody>
  </table>
</div>""",
        "created_by": "system",
        "updated_by": "system",
    },
    {
        "name": "Vitec Bunntekst Sidetall",
        "type": "footer",
        "context": "pdf",
        "is_default": False,
        "html_content": """<style type="text/css">
@import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;700&display=swap');

#vitecTemplate table {
    margin: 0;
    padding: 0;
    width: 100%;
    height: 1.5cm;
    border-collapse: collapse;
    font-family: 'Open sans', sans-serif;
    font-size: 8pt;
    line-height: 10pt;
    table-layout: fixed;
}

#vitecTemplate tr td {
    vertical-align: middle;
    text-align: center;
    font-family: 'Open sans', sans-serif;
    font-size: 8pt;
    line-height: 9pt;
}
</style>

<div id="vitecTemplate">
  <table>
    <tbody>
      <tr>
        <td>[[p]] av [[P]]</td>
      </tr>
    </tbody>
  </table>
</div>""",
        "created_by": "system",
        "updated_by": "system",
    },
    {
        "name": "Vitec Bunntekst Fremleiekontrakt",
        "type": "footer",
        "context": "pdf",
        "is_default": False,
        "html_content": """<div id="vitecTemplate">
  <span vitec-template="resource:Vitec Stilark">&nbsp;</span>
  <table style="height:1.5cm; table-layout:fixed; width:20cm">
    <tbody>
      <tr>
        <td style="font-size:8pt; padding:0.25cm 0.5cm 0.5cm 2cm; vertical-align:bottom">
          <div style="border-top:solid 1px #000000; text-align:center; width:3cm">Utleier</div>
        </td>
        <td style="font-size:8pt; padding:0.25cm 0.5cm 0.5cm 2cm; vertical-align:bottom">
          <div style="border-top:solid 1px #000000; text-align:center; width:3cm">Fremleier</div>
        </td>
        <td style="font-size:8pt; padding:0.25cm 0cm 0.5cm 0.5cm; text-align:right; vertical-align:bottom">
          <div style="border-top:solid 1px #000000; float:right; text-align:center; width:3cm">Fremleietaker</div>
        </td>
        <td style="padding:0.5cm; text-align:center">
          <span style="font-size:8pt">side [[p]] av [[P]]</span>
        </td>
      </tr>
    </tbody>
  </table>
</div>""",
        "created_by": "system",
        "updated_by": "system",
    },
    # ----- SIGNATURES -----
    {
        "name": "E-post signatur",
        "type": "signature",
        "context": "email",
        "is_default": True,
        "html_content": """<div>
  <span style="font-family:calibri,sans-serif; font-size:11pt">&nbsp;</span><br />
  <span style="font-family:calibri,sans-serif; font-size:11pt">&nbsp;</span><br />
  <span style="font-family:calibri,sans-serif; font-size:11pt">&nbsp;</span><br />
  <span style="font-family:calibri,sans-serif; font-size:11pt">Med vennlig hilsen</span><br />
  <span style="font-family:calibri,sans-serif; font-size:11pt">[[avsender.navn]]</span><br />
  <span style="font-family:calibri,sans-serif; font-size:11pt">&nbsp;</span><br />
  <span style="font-family:calibri,sans-serif; font-size:11pt">[[avsender.tittel]]</span><br />
  <span style="font-family:calibri,sans-serif; font-size:11pt">[[avsender.meglerkontor.navn]]</span><br />
  <span style="font-family:calibri,sans-serif; font-size:11pt">Mobil: [[avsender.mobiltlf]], e-post: [[avsender.epost]]</span><br />
  <span style="font-family:calibri,sans-serif; font-size:11pt">Besoksadresse: [[avsender.meglerkontor.besoksadresse]], [[avsender.meglerkontor.postnr]] [[avsender.meglerkontor.poststed]]</span>
</div>""",
        "created_by": "system",
        "updated_by": "system",
    },
    {
        "name": "SMS-signatur",
        "type": "signature",
        "context": "sms",
        "is_default": True,
        "html_content": """<div>Vennlig hilsen</div>
<div>[[avsender.navn]]</div>
<div>&nbsp;</div>
<div>[[avsender.tittel]]</div>
<div>[[avsender.meglerkontor.navn]]</div>""",
        "created_by": "system",
        "updated_by": "system",
    },
]


async def seed_layout_partials_local():
    """Seed layout partials to local database."""
    from app.database import async_session_factory
    from app.services.layout_partial_service import LayoutPartialService

    print("Seeding layout partials to local database...")

    async with async_session_factory() as db:
        created = 0
        skipped = 0

        for partial_data in LAYOUT_PARTIALS:
            try:
                await LayoutPartialService.create(db, **partial_data)
                created += 1
                print(f"  [OK] Created: {partial_data['name']}")
            except ValueError as e:
                if "already exists" in str(e).lower():
                    skipped += 1
                    print(f"  [--] Exists: {partial_data['name']}")
                else:
                    print(f"  [ERROR] {partial_data['name']}: {e}")
            except Exception as e:
                print(f"  [ERROR] {partial_data['name']}: {e}")

        await db.commit()
        print(f"\nDone! Created {created}, Skipped {skipped}")


def seed_layout_partials_remote(api_url: str):
    """Seed layout partials to remote API."""
    endpoint = f"{api_url.rstrip('/')}/api/layout-partials"
    print(f"Seeding layout partials to {endpoint}...")

    created = 0
    skipped = 0
    errors = 0

    for partial_data in LAYOUT_PARTIALS:
        try:
            response = requests.post(endpoint, json=partial_data, timeout=30)
            if response.status_code == 201:
                created += 1
                print(f"  [OK] Created: {partial_data['name']}")
            elif response.status_code in [400, 409] and "exists" in response.text.lower():
                skipped += 1
                print(f"  [--] Exists: {partial_data['name']}")
            else:
                errors += 1
                print(f"  [ERROR] {partial_data['name']}: {response.status_code} - {response.text[:100]}")
        except Exception as e:
            errors += 1
            print(f"  [ERROR] {partial_data['name']}: {e}")

    print(f"\nDone! Created {created}, Skipped {skipped}, Errors {errors}")


def main():
    parser = argparse.ArgumentParser(description="Seed Vitec layout partials to database")
    parser.add_argument("--api-url", help="Remote API URL (if not provided, uses local database)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be seeded")

    args = parser.parse_args()

    if args.dry_run:
        print(f"Would seed {len(LAYOUT_PARTIALS)} layout partials:")
        for p in LAYOUT_PARTIALS:
            print(f"  [{p['type']}] {p['name']} ({p['context']})")
        return

    if args.api_url:
        seed_layout_partials_remote(args.api_url)
    else:
        asyncio.run(seed_layout_partials_local())


if __name__ == "__main__":
    main()
