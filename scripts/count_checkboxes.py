"""Count checkboxes in production templates."""
import re
from pathlib import Path

DIR = Path(r"C:\Users\Adrian\Documents\Proaktiv-Dokument-Hub\scripts\converted_html")
for name in ["Kjopekontrakt_prosjekt_enebolig_PRODUCTION.html",
             "Kjopekontrakt_prosjekt_leilighet_PRODUCTION.html"]:
    html = (DIR / name).read_text(encoding="utf-8")
    entity_cb = len(re.findall(r"&#9744;|&#9745;|&#x2610;|&#x2611;", html))
    literal_cb = len(re.findall("[\u2610\u2611]", html))
    print(f"{name}:")
    print(f"  Entity checkboxes (&#xxxx;): {entity_cb}")
    print(f"  Literal Unicode checkboxes:  {literal_cb}")
    print(f"  Total checkboxes:            {entity_cb + literal_cb}")
