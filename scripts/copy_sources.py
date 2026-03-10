"""Copy source HTM files to the converted_html directory for side-by-side preview."""
import shutil
import os
from pathlib import Path

SRC_DIR = Path(r"C:\Users\Adrian\Downloads\OneDrive_2026-02-21") / "maler vi m\u00e5 f\u00e5 produsert"
DST_DIR = Path(r"C:\Users\Adrian\Documents\Proaktiv-Dokument-Hub\scripts\converted_html")

copies = [
    ("Kj\u00f8pekontrakt prosjekt (enebolig med delinnbetalinger).htm", "SOURCE_enebolig.htm"),
    ("Kj\u00f8pekontrakt prosjekt selveier.htm", "SOURCE_selveier_leilighet.htm"),
    ("Kj\u00f8pekontrakt prosjekt profesjonell kj\u00f8per.htm", "SOURCE_profesjonell_kjoper.htm"),
    ("Kj\u00f8pekontrakt prosjekt Borettslag.htm", "SOURCE_borettslag.htm"),
]

for src_name, dst_name in copies:
    src = SRC_DIR / src_name
    dst = DST_DIR / dst_name
    if src.exists():
        shutil.copy2(src, dst)
        print(f"OK: {src_name} -> {dst_name} ({src.stat().st_size:,} bytes)")
    else:
        print(f"MISSING: {src_name}")
