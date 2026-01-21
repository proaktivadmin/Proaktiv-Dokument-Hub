"""
Seed Code Patterns Script

Populates the database with Vitec logic patterns and layout snippets.
Based on .cursor/vitec-reference.md

Run with: python -m scripts.seed_code_patterns
Or remotely: python backend/scripts/seed_code_patterns.py --api-url <URL>
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
# VITEC CODE PATTERNS DATA
# Based on .cursor/vitec-reference.md
# =============================================================================

CODE_PATTERNS: list[dict[str, Any]] = [
    # ----- VITEC-IF PATTERNS -----
    {
        "name": "vitec-if - Enkel betingelse",
        "category": "Vitec Logic",
        "description": "Vis element basert pa en enkel betingelse",
        "html_code": """<span vitec-if="Model.felt == &quot;verdi&quot;">
    Innhold som vises hvis betingelsen er sann
</span>""",
        "variables_used": ["felt"],
        "created_by": "system",
        "updated_by": "system",
    },
    {
        "name": "vitec-if - Negert betingelse",
        "category": "Vitec Logic",
        "description": "Vis element hvis betingelsen IKKE er sann",
        "html_code": """<span vitec-if="!Model.felt == &quot;verdi&quot;">
    Vises hvis betingelsen er usann
</span>""",
        "variables_used": ["felt"],
        "created_by": "system",
        "updated_by": "system",
    },
    {
        "name": "vitec-if - Contains sjekk",
        "category": "Vitec Logic",
        "description": "Sjekk om en streng inneholder en verdi",
        "html_code": """<span vitec-if="Model.oppdrag.type.Contains(&quot;tleie&quot;)">
    Dette er et utleieoppdrag
</span>""",
        "variables_used": ["oppdrag.type"],
        "created_by": "system",
        "updated_by": "system",
    },
    {
        "name": "vitec-if - StartsWith sjekk",
        "category": "Vitec Logic",
        "description": "Sjekk om en streng starter med en verdi",
        "html_code": """<span vitec-if="Model.referanse.StartsWith(&quot;2024&quot;)">
    Referanse fra 2024
</span>""",
        "variables_used": ["referanse"],
        "created_by": "system",
        "updated_by": "system",
    },
    {
        "name": "vitec-if - Numerisk sammenligning",
        "category": "Vitec Logic",
        "description": "Sammenlign tall med storre/mindre enn",
        "html_code": """<span vitec-if="Model.oppdrag.prisantydning > 5000000">
    Eiendom over 5 millioner
</span>""",
        "variables_used": ["oppdrag.prisantydning"],
        "created_by": "system",
        "updated_by": "system",
    },
    {
        "name": "vitec-if - OG logikk (&&)",
        "category": "Vitec Logic",
        "description": "Kombiner flere betingelser med OG",
        "html_code": """<span vitec-if="Model.eiendom.eieform == &quot;Andel&quot; && Model.oppdrag.prisantydning > 0">
    Andel med prisantydning
</span>""",
        "variables_used": ["eiendom.eieform", "oppdrag.prisantydning"],
        "created_by": "system",
        "updated_by": "system",
    },
    {
        "name": "vitec-if - ELLER logikk (||)",
        "category": "Vitec Logic",
        "description": "Kombiner flere betingelser med ELLER",
        "html_code": """<span vitec-if="Model.eiendom.eieform == &quot;Aksje&quot; || Model.eiendom.eieform == &quot;Andel&quot;">
    Aksje eller andel
</span>""",
        "variables_used": ["eiendom.eieform"],
        "created_by": "system",
        "updated_by": "system",
    },
    {
        "name": "vitec-if - Salg vs Utleie",
        "category": "Vitec Logic",
        "description": "Betinget tekst for salg/utleie oppdrag",
        "html_code": """<span vitec-if="!Model.oppdrag.type.Contains(&quot;tleie&quot;)">Selger</span>
<span vitec-if="Model.oppdrag.type.Contains(&quot;tleie&quot;)">Utleier</span>""",
        "variables_used": ["oppdrag.type"],
        "created_by": "system",
        "updated_by": "system",
    },
    {
        "name": "vitec-if - Eieform sjekk",
        "category": "Vitec Logic",
        "description": "Betinget tekst basert pa eieform",
        "html_code": """<span vitec-if="Model.eiendom.eieform == &quot;Andel&quot;">andel i borettslag</span>
<span vitec-if="Model.eiendom.eieform != &quot;Andel&quot;">fast eiendom</span>""",
        "variables_used": ["eiendom.eieform"],
        "created_by": "system",
        "updated_by": "system",
    },
    # ----- VITEC-FOREACH PATTERNS -----
    {
        "name": "vitec-foreach - Selgere tabell",
        "category": "Vitec Logic",
        "description": "Loop over selgere i en tabell",
        "html_code": """<table>
  <tbody vitec-foreach="s in Model.selgere">
    <tr>
      <td>[[s.navn]]</td>
      <td>[[s.fodselsnr]]</td>
      <td>[[s.adresse]], [[s.postnr]] [[s.poststed]]</td>
    </tr>
  </tbody>
</table>""",
        "variables_used": ["selgere"],
        "created_by": "system",
        "updated_by": "system",
    },
    {
        "name": "vitec-foreach - Kjopere liste",
        "category": "Vitec Logic",
        "description": "Loop over kjopere i en liste",
        "html_code": """<div vitec-foreach="k in Model.kjopere">
  <p><strong>[[k.navn]]</strong></p>
  <p>[[k.adresse]], [[k.postnr]] [[k.poststed]]</p>
  <p>Andel: [[k.andel]]%</p>
</div>""",
        "variables_used": ["kjopere"],
        "created_by": "system",
        "updated_by": "system",
    },
    {
        "name": "vitec-foreach - Visninger",
        "category": "Vitec Logic",
        "description": "Vis alle planlagte visninger",
        "html_code": """<ul vitec-foreach="v in Model.visninger">
  <li>[[v.dato]] kl [[v.startklokken]]-[[v.sluttklokken]]</li>
</ul>""",
        "variables_used": ["visninger"],
        "created_by": "system",
        "updated_by": "system",
    },
    {
        "name": "vitec-foreach - Posteringer",
        "category": "Vitec Logic",
        "description": "Loop over posteringer i oppgjor",
        "html_code": """<table>
  <tbody vitec-foreach="p in Model.posteringer">
    <tr>
      <td>[[p.tekst]]</td>
      <td style="text-align:right">[[p.belop]]</td>
    </tr>
  </tbody>
</table>""",
        "variables_used": ["posteringer"],
        "created_by": "system",
        "updated_by": "system",
    },
    {
        "name": "vitec-foreach - Med Where filter",
        "category": "Vitec Logic",
        "description": "Filtrer liste med Where",
        "html_code": """<div vitec-foreach="p in Model.posteringer.Where(x => x.kode == &quot;HONORAR&quot;)">
  [[p.tekst]]: [[p.belop]]
</div>""",
        "variables_used": ["posteringer"],
        "created_by": "system",
        "updated_by": "system",
    },
    {
        "name": "vitec-foreach - Med Take begrensning",
        "category": "Vitec Logic",
        "description": "Begrens antall elementer med Take",
        "html_code": """<div vitec-foreach="v in Model.visninger.Take(3)">
  [[v.dato]] - [[v.tidspunkt]]
</div>""",
        "variables_used": ["visninger"],
        "created_by": "system",
        "updated_by": "system",
    },
    {
        "name": "vitec-if - Any sjekk",
        "category": "Vitec Logic",
        "description": "Sjekk om minst ett element matcher",
        "html_code": """<div vitec-if="Model.selgere.Any(x => x.type == &quot;Juridisk&quot;)">
  Minst en juridisk selger
</div>""",
        "variables_used": ["selgere"],
        "created_by": "system",
        "updated_by": "system",
    },
    # ----- VITEC FUNCTIONS -----
    {
        "name": "$.UD - Uten desimaler",
        "category": "Vitec Functions",
        "description": "Formater tall uten desimaler",
        "html_code": """<span>Pris: $.UD([[oppdrag.prisantydning]]) kr</span>""",
        "variables_used": ["oppdrag.prisantydning"],
        "created_by": "system",
        "updated_by": "system",
    },
    {
        "name": "$.BOKST - Tall til bokstaver",
        "category": "Vitec Functions",
        "description": "Konverter tall til ord",
        "html_code": """<span>Belop: $.BOKST([[pant.belopskr]]) kroner</span>""",
        "variables_used": ["pant.belopskr"],
        "created_by": "system",
        "updated_by": "system",
    },
    {
        "name": "$.CALC - Beregning",
        "category": "Vitec Functions",
        "description": "Utfor matematisk beregning",
        "html_code": """<span>Meglerhonorar: $.CALC([[oppdrag.salgssum]] * 0.025) kr</span>""",
        "variables_used": ["oppdrag.salgssum"],
        "created_by": "system",
        "updated_by": "system",
    },
    {
        "name": "$.CALCHOURS - Summer timer",
        "category": "Vitec Functions",
        "description": "Summer timeforbruk",
        "html_code": """<span>Totalt: $.CALCHOURS([[timer]]) timer</span>""",
        "variables_used": ["timer"],
        "created_by": "system",
        "updated_by": "system",
    },
    {
        "name": "$.CALCBOKST - Beregning til bokstaver",
        "category": "Vitec Functions",
        "description": "Beregn og konverter til ord",
        "html_code": """<span>$.CALCBOKST([[sum]]) kroner</span>""",
        "variables_used": ["sum"],
        "created_by": "system",
        "updated_by": "system",
    },
    # ----- LAYOUT PATTERNS -----
    {
        "name": "2 Kolonner Grid",
        "category": "Layout",
        "description": "To-kolonners layout med grid",
        "html_code": """<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
  <div>Venstre kolonne</div>
  <div>Hoyre kolonne</div>
</div>""",
        "variables_used": [],
        "created_by": "system",
        "updated_by": "system",
    },
    {
        "name": "3 Kolonner Grid",
        "category": "Layout",
        "description": "Tre-kolonners layout med grid",
        "html_code": """<div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px;">
  <div>Kolonne 1</div>
  <div>Kolonne 2</div>
  <div>Kolonne 3</div>
</div>""",
        "variables_used": [],
        "created_by": "system",
        "updated_by": "system",
    },
    {
        "name": "Data Tabell",
        "category": "Layout",
        "description": "Standard tabell med header og border",
        "html_code": """<table style="width: 100%; border-collapse: collapse;">
  <thead>
    <tr>
      <th style="border-bottom: 1px solid #000; text-align: left; padding: 8px;">Felt</th>
      <th style="border-bottom: 1px solid #000; text-align: left; padding: 8px;">Verdi</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="padding: 8px;">Navn</td>
      <td style="padding: 8px;">[[selger.navn]]</td>
    </tr>
  </tbody>
</table>""",
        "variables_used": ["selger.navn"],
        "created_by": "system",
        "updated_by": "system",
    },
    {
        "name": "Signaturblokk - 2 parter",
        "category": "Layout",
        "description": "Signaturomrade for 2 parter",
        "html_code": """<table style="width: 100%; margin-top: 50px;">
  <tr>
    <td style="width: 45%; text-align: center;">
      <div style="border-top: solid 1px #000; padding-top: 10px; width: 80%; margin: 0 auto;">
        Selgers underskrift
      </div>
    </td>
    <td style="width: 10%;"></td>
    <td style="width: 45%; text-align: center;">
      <div style="border-top: solid 1px #000; padding-top: 10px; width: 80%; margin: 0 auto;">
        Meglers underskrift
      </div>
    </td>
  </tr>
</table>""",
        "variables_used": [],
        "created_by": "system",
        "updated_by": "system",
    },
    {
        "name": "Signaturblokk - 3 parter",
        "category": "Layout",
        "description": "Signaturomrade for selger, kjoper, megler",
        "html_code": """<table style="width: 100%; margin-top: 50px;">
  <tr>
    <td style="width: 30%; text-align: center;">
      <div style="border-top: solid 1px #000; padding-top: 10px;">
        Selger
      </div>
    </td>
    <td style="width: 5%;"></td>
    <td style="width: 30%; text-align: center;">
      <div style="border-top: solid 1px #000; padding-top: 10px;">
        Kjoper
      </div>
    </td>
    <td style="width: 5%;"></td>
    <td style="width: 30%; text-align: center;">
      <div style="border-top: solid 1px #000; padding-top: 10px;">
        Megler
      </div>
    </td>
  </tr>
</table>""",
        "variables_used": [],
        "created_by": "system",
        "updated_by": "system",
    },
    {
        "name": "Sideskift",
        "category": "Layout",
        "description": "Tving ny side i PDF",
        "html_code": """<div style="page-break-before: always;"></div>""",
        "variables_used": [],
        "created_by": "system",
        "updated_by": "system",
    },
    {
        "name": "Unnga sideskift",
        "category": "Layout",
        "description": "Hold elementer sammen pa samme side",
        "html_code": """<div style="page-break-inside: avoid;">
  <!-- Innhold som skal holdes sammen -->
</div>""",
        "variables_used": [],
        "created_by": "system",
        "updated_by": "system",
    },
    {
        "name": "A4 Bredde Tabell",
        "category": "Layout",
        "description": "Tabell med A4 bredde (21cm)",
        "html_code": """<table style="width: 21cm; table-layout: fixed; border-collapse: collapse;">
  <tbody>
    <tr>
      <td style="padding: 1cm;">Innhold</td>
    </tr>
  </tbody>
</table>""",
        "variables_used": [],
        "created_by": "system",
        "updated_by": "system",
    },
    {
        "name": "data-label Felt",
        "category": "Layout",
        "description": "Input-felt med flytende label",
        "html_code": """<style>
td[data-label] {
  padding: 16px 2px 4px 3px;
  position: relative;
}
td[data-label]:before {
  content: attr(data-label);
  font-size: 7pt;
  text-transform: uppercase;
  position: absolute;
  top: 1px;
}
</style>
<table>
  <tr>
    <td data-label="Dato">&nbsp;</td>
    <td data-label="Underskrift">&nbsp;</td>
  </tr>
</table>""",
        "variables_used": [],
        "created_by": "system",
        "updated_by": "system",
    },
    # ----- TEMPLATE STRUCTURE -----
    {
        "name": "Vitec Template Wrapper",
        "category": "Structure",
        "description": "Standard wrapper for Vitec-maler",
        "html_code": """<div id="vitecTemplate">
  <span vitec-template="resource:Vitec Stilark">&nbsp;</span>

  <!-- Mal-innhold her -->

</div>""",
        "variables_used": [],
        "created_by": "system",
        "updated_by": "system",
    },
    {
        "name": "Inkluder Stilark",
        "category": "Structure",
        "description": "Inkluder Vitec Stilark i mal",
        "html_code": """<span vitec-template="resource:Vitec Stilark">&nbsp;</span>""",
        "variables_used": [],
        "created_by": "system",
        "updated_by": "system",
    },
    {
        "name": "Contenteditable false",
        "category": "Structure",
        "description": "Forhindre redigering i editor",
        "html_code": """<tr contenteditable="false">
  <td>Denne raden kan ikke redigeres i Vitec</td>
</tr>""",
        "variables_used": [],
        "created_by": "system",
        "updated_by": "system",
    },
    {
        "name": "Sidetall Bunntekst",
        "category": "Structure",
        "description": "Standard sidetall-visning",
        "html_code": """<div style="text-align: center;">
  <small>Side [[p]] av [[P]]</small>
</div>""",
        "variables_used": ["p", "P"],
        "created_by": "system",
        "updated_by": "system",
    },
]


async def seed_code_patterns_local():
    """Seed code patterns to local database."""
    from app.database import async_session_factory
    from app.services.code_pattern_service import CodePatternService

    print("Seeding code patterns to local database...")

    async with async_session_factory() as db:
        created = 0
        skipped = 0

        for pattern_data in CODE_PATTERNS:
            try:
                await CodePatternService.create(db, **pattern_data)
                created += 1
                print(f"  [OK] Created: {pattern_data['name']}")
            except ValueError as e:
                if "already exists" in str(e).lower():
                    skipped += 1
                    print(f"  [--] Exists: {pattern_data['name']}")
                else:
                    print(f"  [ERROR] {pattern_data['name']}: {e}")
            except Exception as e:
                print(f"  [ERROR] {pattern_data['name']}: {e}")

        await db.commit()
        print(f"\nDone! Created {created}, Skipped {skipped}")


def seed_code_patterns_remote(api_url: str):
    """Seed code patterns to remote API."""
    endpoint = f"{api_url.rstrip('/')}/api/code-patterns"
    print(f"Seeding code patterns to {endpoint}...")

    created = 0
    skipped = 0
    errors = 0

    for pattern_data in CODE_PATTERNS:
        try:
            response = requests.post(endpoint, json=pattern_data, timeout=30)
            if response.status_code == 201:
                created += 1
                print(f"  [OK] Created: {pattern_data['name']}")
            elif response.status_code in [400, 409] and "exists" in response.text.lower():
                skipped += 1
                print(f"  [--] Exists: {pattern_data['name']}")
            else:
                errors += 1
                print(f"  [ERROR] {pattern_data['name']}: {response.status_code} - {response.text[:100]}")
        except Exception as e:
            errors += 1
            print(f"  [ERROR] {pattern_data['name']}: {e}")

    print(f"\nDone! Created {created}, Skipped {skipped}, Errors {errors}")


def main():
    parser = argparse.ArgumentParser(description="Seed Vitec code patterns to database")
    parser.add_argument("--api-url", help="Remote API URL (if not provided, uses local database)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be seeded")

    args = parser.parse_args()

    if args.dry_run:
        print(f"Would seed {len(CODE_PATTERNS)} code patterns:")
        categories = {}
        for p in CODE_PATTERNS:
            cat = p["category"]
            categories[cat] = categories.get(cat, 0) + 1
        for cat, count in sorted(categories.items()):
            print(f"  {cat}: {count} patterns")
        return

    if args.api_url:
        seed_code_patterns_remote(args.api_url)
    else:
        asyncio.run(seed_code_patterns_local())


if __name__ == "__main__":
    main()
