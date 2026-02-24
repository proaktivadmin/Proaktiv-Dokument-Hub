"""
Template Library Mining Script

Parses all HTML templates in templates/master/ and extracts structured data
across three focus areas: CSS patterns, merge fields, and conditional logic.

Outputs:
  - scripts/qa_artifacts/LIBRARY-MINING-REPORT.md (human-readable)
  - scripts/qa_artifacts/library-mining-data.json (machine-readable)

Usage:
    python scripts/tools/mine_template_library.py
    python scripts/tools/mine_template_library.py --min-size 1024
    python scripts/tools/mine_template_library.py --json-only
"""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

TEMPLATES_ROOT = Path(__file__).resolve().parent.parent.parent / "templates" / "master"
OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "scripts" / "qa_artifacts"

STYLE_BLOCK_RE = re.compile(r"<style[^>]*>(.*?)</style>", re.DOTALL | re.IGNORECASE)
MERGE_FIELD_RE = re.compile(r"\[\[(\*?)([^\]]+)\]\]")
UD_FIELD_RE = re.compile(r"\$\.UD\(\[\[(\*?)([^\]]+)\]\]\)")
VITEC_IF_RE = re.compile(r'vitec-if="([^"]*)"')
VITEC_FOREACH_RE = re.compile(r'vitec-foreach="(\w+)\s+in\s+([\w.()]+)"')
DATA_LABEL_RE = re.compile(r'data-label="([^"]*)"')
VITEC_TEMPLATE_RE = re.compile(r'vitec-template="resource:([^"]*)"')

CSS_SELECTOR_RE = re.compile(r"([^{]+)\{([^}]*)\}", re.DOTALL)
CSS_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)

PADDING_LEFT_RE = re.compile(r"padding-left:\s*([\d.]+(?:px|em|pt))")
MARGIN_RE = re.compile(r"margin:\s*([^;]+)")
FONT_SIZE_RE = re.compile(r"font-size:\s*([\d.]+(?:px|em|pt))")
COUNTER_RESET_RE = re.compile(r"counter-reset:\s*([^;]+)")
COUNTER_INCREMENT_RE = re.compile(r"counter-increment:\s*([^;]+)")
COUNTER_CONTENT_RE = re.compile(r'content:\s*counter\(([^)]+)\)\s*"([^"]*)"')


def read_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1")


def detect_svg_encoding(html: str) -> str | None:
    """Detect SVG data URI encoding from raw HTML (not just style blocks)."""
    if "data:image/svg" not in html:
        return None
    if ";utf8," in html or ";utf-8," in html or "charset=utf8" in html or "charset=utf-8" in html:
        return "utf8"
    if "%3Csvg" in html or "%3csvg" in html:
        return "percent"
    return "unknown"


def extract_css(html: str) -> dict:
    """Extract CSS pattern data from all style blocks."""
    style_blocks = STYLE_BLOCK_RE.findall(html)
    result = {
        "style_block_count": len(style_blocks),
        "has_checkbox_css": False,
        "has_insert_css": False,
        "has_counter_css": False,
        "scoped_selectors": [],
        "unscoped_selectors": [],
        "article_padding": None,
        "h1_font_size": None,
        "h2_font_size": None,
        "h2_margin": None,
        "h3_font_size": None,
        "counter_names": [],
        "counter_before_format": [],
        "counter_before_has_display": False,
        "counter_before_has_width": False,
        "svg_encoding": None,
        "has_insert_table_inline_table": False,
        "has_roles_table": False,
        "has_bookmark": False,
        "has_liste": False,
        "has_borders_class": False,
        "has_avoid_page_break": False,
    }

    all_css = "\n".join(style_blocks)
    cleaned = CSS_COMMENT_RE.sub("", all_css)

    if "label.btn" in all_css or "svg-toggle" in all_css:
        result["has_checkbox_css"] = True

    if "span.insert:empty" in all_css or "insert-table" in all_css:
        result["has_insert_css"] = True

    if "counter-reset" in all_css:
        result["has_counter_css"] = True

    if "display: inline-table" in all_css or "display:inline-table" in all_css:
        result["has_insert_table_inline_table"] = True

    if "roles-table" in all_css:
        result["has_roles_table"] = True

    if "a.bookmark" in all_css:
        result["has_bookmark"] = True

    if ".liste" in all_css:
        result["has_liste"] = True

    if ".borders" in all_css:
        result["has_borders_class"] = True

    if "avoid-page-break" in all_css or "page-break-inside" in all_css:
        result["has_avoid_page_break"] = True

    result["svg_encoding"] = detect_svg_encoding(html)

    for match in CSS_SELECTOR_RE.finditer(cleaned):
        selector = match.group(1).strip()
        props = match.group(2).strip()

        norm_sel = " ".join(selector.split())
        if "#vitecTemplate" in norm_sel:
            result["scoped_selectors"].append(norm_sel)
        elif norm_sel and not norm_sel.startswith("@"):
            result["unscoped_selectors"].append(norm_sel)

        if "article" in selector and "article article" not in selector:
            pad = PADDING_LEFT_RE.search(props)
            if pad:
                result["article_padding"] = pad.group(1)

        if selector.strip().endswith("h1") or "h1 {" in selector:
            fs = FONT_SIZE_RE.search(props)
            if fs:
                result["h1_font_size"] = fs.group(1)

        if selector.strip().endswith("h2") or "h2 {" in selector:
            fs = FONT_SIZE_RE.search(props)
            if fs:
                result["h2_font_size"] = fs.group(1)
            mg = MARGIN_RE.search(props)
            if mg:
                result["h2_margin"] = mg.group(1).strip()

        if selector.strip().endswith("h3") or "h3 {" in selector:
            fs = FONT_SIZE_RE.search(props)
            if fs:
                result["h3_font_size"] = fs.group(1)

        if "::before" in selector:
            if "display" in props:
                result["counter_before_has_display"] = True
            if "width" in props:
                result["counter_before_has_width"] = True
            cm = COUNTER_CONTENT_RE.search(props)
            if cm:
                result["counter_before_format"].append(
                    f'counter({cm.group(1)}) "{cm.group(2)}"'
                )

    for cr in COUNTER_RESET_RE.findall(all_css):
        for name in cr.strip().rstrip(";").split():
            if name and name not in result["counter_names"]:
                result["counter_names"].append(name)

    result["scoped_selectors"] = list(set(result["scoped_selectors"]))
    result["unscoped_selectors"] = list(set(result["unscoped_selectors"]))

    return result


def extract_merge_fields(html: str) -> dict:
    """Extract merge field data."""
    all_fields = MERGE_FIELD_RE.findall(html)
    ud_fields = UD_FIELD_RE.findall(html)
    data_labels = DATA_LABEL_RE.findall(html)
    resources = VITEC_TEMPLATE_RE.findall(html)

    fields_list = []
    for required, path in all_fields:
        fields_list.append({
            "path": path.strip(),
            "required": bool(required),
        })

    ud_set = set()
    for _, path in ud_fields:
        ud_set.add(path.strip())

    foreach_blocks = VITEC_FOREACH_RE.findall(html)
    foreach_iterators = set()
    for iterator, _ in foreach_blocks:
        foreach_iterators.add(iterator)

    fields_in_foreach = []
    fields_outside_foreach = []
    for f in fields_list:
        parts = f["path"].split(".")
        if parts[0] in foreach_iterators:
            fields_in_foreach.append(f)
        else:
            fields_outside_foreach.append(f)

    return {
        "total_fields": len(fields_list),
        "unique_fields": list(set(f["path"] for f in fields_list)),
        "required_fields": [f["path"] for f in fields_list if f["required"]],
        "optional_fields": [f["path"] for f in fields_list if not f["required"]],
        "ud_wrapped": list(ud_set),
        "data_labels": list(set(data_labels)),
        "resources": list(set(resources)),
        "fields_in_foreach": [f["path"] for f in fields_in_foreach],
        "fields_outside_foreach": list(set(f["path"] for f in fields_outside_foreach)),
    }


def extract_conditions(html: str) -> dict:
    """Extract conditional logic data."""
    vitec_ifs = VITEC_IF_RE.findall(html)
    foreachs = VITEC_FOREACH_RE.findall(html)

    has_count_guard = ".Count" in html
    has_mangler_data = "Mangler data" in html
    has_negation_not = bool(re.search(r'vitec-if="not\s', html, re.IGNORECASE))
    has_negation_bang = bool(re.search(r'vitec-if="[^"]*![^=]', html))

    collection_paths = [coll for _, coll in foreachs]

    guard_patterns = []
    for cond in vitec_ifs:
        if ".Count" in cond:
            guard_patterns.append(cond)

    model_prefix_in_foreach = []
    iterator_prefix_in_foreach = []
    foreach_iterators = {it for it, _ in foreachs}
    for cond in vitec_ifs:
        for it in foreach_iterators:
            if f"{it}." in cond:
                iterator_prefix_in_foreach.append(cond)
                break
        if "Model." in cond and cond not in iterator_prefix_in_foreach:
            model_prefix_in_foreach.append(cond)

    return {
        "vitec_if_count": len(vitec_ifs),
        "vitec_if_unique": list(set(vitec_ifs)),
        "foreach_count": len(foreachs),
        "foreach_expressions": [f"{it} in {coll}" for it, coll in foreachs],
        "collection_paths": collection_paths,
        "has_count_guard": has_count_guard,
        "has_mangler_data": has_mangler_data,
        "has_negation_not": has_negation_not,
        "has_negation_bang": has_negation_bang,
        "guard_patterns": list(set(guard_patterns)),
        "model_prefix_conditions": len(model_prefix_in_foreach),
        "iterator_prefix_conditions": len(iterator_prefix_in_foreach),
    }


def mine_template(path: Path, origin: str) -> dict:
    """Mine a single template and return structured data."""
    html = read_file(path)
    return {
        "filename": path.name,
        "origin": origin,
        "size_bytes": len(html.encode("utf-8")),
        "has_vitec_id": 'id="vitecTemplate"' in html,
        "has_proaktiv_theme": 'class="proaktiv-theme"' in html,
        "css": extract_css(html),
        "fields": extract_merge_fields(html),
        "conditions": extract_conditions(html),
    }


def aggregate(templates: list[dict]) -> dict:
    """Aggregate data across all templates."""
    css_agg = {
        "style_block_counts": Counter(),
        "article_paddings": Counter(),
        "h1_font_sizes": Counter(),
        "h2_font_sizes": Counter(),
        "h2_margins": Counter(),
        "h3_font_sizes": Counter(),
        "has_checkbox_css": 0,
        "has_insert_css": 0,
        "has_counter_css": 0,
        "has_insert_table_inline_table": 0,
        "has_roles_table": 0,
        "has_bookmark": 0,
        "has_liste": 0,
        "has_borders_class": 0,
        "has_avoid_page_break": 0,
        "svg_encodings": Counter(),
        "counter_before_has_display": 0,
        "counter_before_has_width": 0,
        "counter_names": Counter(),
        "has_proaktiv_theme": 0,
        "all_scoped_selectors": Counter(),
        "all_unscoped_selectors": Counter(),
    }

    field_agg = {
        "field_frequency": Counter(),
        "required_frequency": Counter(),
        "ud_frequency": Counter(),
        "data_label_frequency": Counter(),
        "resource_frequency": Counter(),
        "foreach_field_frequency": Counter(),
    }

    cond_agg = {
        "collection_path_frequency": Counter(),
        "foreach_expr_frequency": Counter(),
        "condition_frequency": Counter(),
        "guard_frequency": Counter(),
        "has_count_guard": 0,
        "has_mangler_data": 0,
        "has_negation_not": 0,
        "has_negation_bang": 0,
        "total_model_prefix": 0,
        "total_iterator_prefix": 0,
    }

    for t in templates:
        css = t["css"]
        css_agg["style_block_counts"][css["style_block_count"]] += 1
        if css["article_padding"]:
            css_agg["article_paddings"][css["article_padding"]] += 1
        if css["h1_font_size"]:
            css_agg["h1_font_sizes"][css["h1_font_size"]] += 1
        if css["h2_font_size"]:
            css_agg["h2_font_sizes"][css["h2_font_size"]] += 1
        if css["h2_margin"]:
            css_agg["h2_margins"][css["h2_margin"]] += 1
        if css["h3_font_size"]:
            css_agg["h3_font_sizes"][css["h3_font_size"]] += 1
        if css["has_checkbox_css"]:
            css_agg["has_checkbox_css"] += 1
        if css["has_insert_css"]:
            css_agg["has_insert_css"] += 1
        if css["has_counter_css"]:
            css_agg["has_counter_css"] += 1
        if css["has_insert_table_inline_table"]:
            css_agg["has_insert_table_inline_table"] += 1
        if css["has_roles_table"]:
            css_agg["has_roles_table"] += 1
        if css["has_bookmark"]:
            css_agg["has_bookmark"] += 1
        if css["has_liste"]:
            css_agg["has_liste"] += 1
        if css["has_borders_class"]:
            css_agg["has_borders_class"] += 1
        if css["has_avoid_page_break"]:
            css_agg["has_avoid_page_break"] += 1
        if css["svg_encoding"]:
            css_agg["svg_encodings"][css["svg_encoding"]] += 1
        if css["counter_before_has_display"]:
            css_agg["counter_before_has_display"] += 1
        if css["counter_before_has_width"]:
            css_agg["counter_before_has_width"] += 1
        for name in css["counter_names"]:
            css_agg["counter_names"][name] += 1
        if t["has_proaktiv_theme"]:
            css_agg["has_proaktiv_theme"] += 1
        for sel in css["scoped_selectors"]:
            css_agg["all_scoped_selectors"][sel] += 1
        for sel in css["unscoped_selectors"]:
            css_agg["all_unscoped_selectors"][sel] += 1

        fields = t["fields"]
        for f in fields["unique_fields"]:
            field_agg["field_frequency"][f] += 1
        for f in fields["required_fields"]:
            field_agg["required_frequency"][f] += 1
        for f in fields["ud_wrapped"]:
            field_agg["ud_frequency"][f] += 1
        for dl in fields["data_labels"]:
            field_agg["data_label_frequency"][dl] += 1
        for r in fields["resources"]:
            field_agg["resource_frequency"][r] += 1
        for f in fields["fields_in_foreach"]:
            field_agg["foreach_field_frequency"][f] += 1

        conds = t["conditions"]
        for path in conds["collection_paths"]:
            cond_agg["collection_path_frequency"][path] += 1
        for expr in conds["foreach_expressions"]:
            cond_agg["foreach_expr_frequency"][expr] += 1
        for cond in conds["vitec_if_unique"]:
            cond_agg["condition_frequency"][cond] += 1
        for g in conds["guard_patterns"]:
            cond_agg["guard_frequency"][g] += 1
        if conds["has_count_guard"]:
            cond_agg["has_count_guard"] += 1
        if conds["has_mangler_data"]:
            cond_agg["has_mangler_data"] += 1
        if conds["has_negation_not"]:
            cond_agg["has_negation_not"] += 1
        if conds["has_negation_bang"]:
            cond_agg["has_negation_bang"] += 1
        cond_agg["total_model_prefix"] += conds["model_prefix_conditions"]
        cond_agg["total_iterator_prefix"] += conds["iterator_prefix_conditions"]

    return {"css": css_agg, "fields": field_agg, "conditions": cond_agg}


def counter_to_sorted(c: Counter, limit: int = 0) -> list[tuple]:
    items = c.most_common()
    if limit:
        items = items[:limit]
    return items


def generate_report(templates: list[dict], agg: dict, total: int, skipped: int) -> str:
    """Generate the markdown report."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    css = agg["css"]
    fields = agg["fields"]
    conds = agg["conditions"]

    vitec_count = sum(1 for t in templates if t["origin"] == "vitec-system")
    kundemal_count = sum(1 for t in templates if t["origin"] == "kundemal")
    total_fields = sum(t["fields"]["total_fields"] for t in templates)
    total_conditions = sum(t["conditions"]["vitec_if_count"] for t in templates)
    total_foreach = sum(t["conditions"]["foreach_count"] for t in templates)

    lines = []
    lines.append(f"# Template Library Mining Report")
    lines.append(f"")
    lines.append(f"**Generated:** {now}")
    lines.append(f"**Templates analyzed:** {len(templates)} (of {total} total, {skipped} skipped below size threshold)")
    lines.append(f"**Vitec system:** {vitec_count} | **Kundemal:** {kundemal_count}")
    lines.append(f"")
    lines.append(f"## Executive Summary")
    lines.append(f"")
    lines.append(f"| Metric | Count |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Templates analyzed | {len(templates)} |")
    lines.append(f"| Total merge fields (instances) | {total_fields} |")
    lines.append(f"| Unique merge field paths | {len(fields['field_frequency'])} |")
    lines.append(f"| Total vitec-if conditions | {total_conditions} |")
    lines.append(f"| Unique conditions | {len(conds['condition_frequency'])} |")
    lines.append(f"| Total vitec-foreach loops | {total_foreach} |")
    lines.append(f"| Unique collection paths | {len(conds['collection_path_frequency'])} |")
    lines.append(f"| Templates with proaktiv-theme | {css['has_proaktiv_theme']} |")
    lines.append(f"")

    lines.append(f"---")
    lines.append(f"")
    lines.append(f"## 1. CSS Patterns")
    lines.append(f"")

    lines.append(f"### Style Block Counts")
    lines.append(f"| Blocks | Templates |")
    lines.append(f"|--------|-----------|")
    for count, freq in sorted(css["style_block_counts"].items()):
        lines.append(f"| {count} | {freq} |")
    lines.append(f"")

    lines.append(f"### Article Padding Values")
    lines.append(f"| Value | Templates |")
    lines.append(f"|-------|-----------|")
    for val, freq in counter_to_sorted(css["article_paddings"]):
        lines.append(f"| `{val}` | {freq} |")
    if not css["article_paddings"]:
        lines.append(f"| (none found) | - |")
    lines.append(f"")

    lines.append(f"### H2 Margin Values")
    lines.append(f"| Value | Templates |")
    lines.append(f"|-------|-----------|")
    for val, freq in counter_to_sorted(css["h2_margins"]):
        lines.append(f"| `{val}` | {freq} |")
    if not css["h2_margins"]:
        lines.append(f"| (none found) | - |")
    lines.append(f"")

    lines.append(f"### Font Sizes")
    lines.append(f"| Element | Value | Templates |")
    lines.append(f"|---------|-------|-----------|")
    for val, freq in counter_to_sorted(css["h1_font_sizes"]):
        lines.append(f"| h1 | `{val}` | {freq} |")
    for val, freq in counter_to_sorted(css["h2_font_sizes"]):
        lines.append(f"| h2 | `{val}` | {freq} |")
    for val, freq in counter_to_sorted(css["h3_font_sizes"]):
        lines.append(f"| h3 | `{val}` | {freq} |")
    lines.append(f"")

    lines.append(f"### CSS Feature Presence")
    lines.append(f"| Feature | Templates | % |")
    lines.append(f"|---------|-----------|---|")
    n = len(templates)
    for label, key in [
        ("Checkbox CSS (label.btn / svg-toggle)", "has_checkbox_css"),
        ("Insert field CSS (span.insert:empty)", "has_insert_css"),
        ("Counter CSS (counter-reset)", "has_counter_css"),
        (".insert-table { display: inline-table }", "has_insert_table_inline_table"),
        (".roles-table rule", "has_roles_table"),
        ("a.bookmark rule", "has_bookmark"),
        (".liste rule", "has_liste"),
        (".borders class", "has_borders_class"),
        ("avoid-page-break / page-break-inside", "has_avoid_page_break"),
        ("proaktiv-theme class", "has_proaktiv_theme"),
    ]:
        val = css[key]
        pct = round(val / n * 100) if n else 0
        lines.append(f"| {label} | {val} | {pct}% |")
    lines.append(f"")

    lines.append(f"### Counter ::before Properties")
    lines.append(f"| Property | Templates |")
    lines.append(f"|----------|-----------|")
    lines.append(f"| has `display` on ::before | {css['counter_before_has_display']} |")
    lines.append(f"| has `width` on ::before | {css['counter_before_has_width']} |")
    lines.append(f"")

    lines.append(f"### Counter Names Used")
    lines.append(f"| Name | Templates |")
    lines.append(f"|------|-----------|")
    for name, freq in counter_to_sorted(css["counter_names"]):
        lines.append(f"| `{name}` | {freq} |")
    lines.append(f"")

    lines.append(f"### SVG Data URI Encoding")
    lines.append(f"| Encoding | Templates |")
    lines.append(f"|----------|-----------|")
    for enc, freq in counter_to_sorted(css["svg_encodings"]):
        lines.append(f"| {enc} | {freq} |")
    if not css["svg_encodings"]:
        lines.append(f"| (no SVG CSS found) | - |")
    lines.append(f"")

    lines.append(f"### Top 20 Unscoped CSS Selectors")
    lines.append(f"| Selector | Templates |")
    lines.append(f"|----------|-----------|")
    for sel, freq in counter_to_sorted(css["all_unscoped_selectors"], 20):
        lines.append(f"| `{sel}` | {freq} |")
    lines.append(f"")

    lines.append(f"---")
    lines.append(f"")
    lines.append(f"## 2. Merge Fields")
    lines.append(f"")

    lines.append(f"### Top 50 Most Common Fields")
    lines.append(f"| Field | Templates | Always Required |")
    lines.append(f"|-------|-----------|-----------------|")
    req_set = set(fields["required_frequency"].keys())
    for path, freq in counter_to_sorted(fields["field_frequency"], 50):
        is_req = "YES" if path in req_set else ""
        lines.append(f"| `[[{path}]]` | {freq} | {is_req} |")
    lines.append(f"")

    lines.append(f"### $.UD() Wrapped Fields (monetary formatting)")
    lines.append(f"| Field | Templates |")
    lines.append(f"|-------|-----------|")
    for path, freq in counter_to_sorted(fields["ud_frequency"]):
        lines.append(f"| `$.UD([[{path}]])` | {freq} |")
    if not fields["ud_frequency"]:
        lines.append(f"| (none found) | - |")
    lines.append(f"")

    lines.append(f"### Insert Field data-label Values")
    lines.append(f"| Label | Templates |")
    lines.append(f"|-------|-----------|")
    for label, freq in counter_to_sorted(fields["data_label_frequency"], 30):
        lines.append(f"| `{label}` | {freq} |")
    lines.append(f"")

    lines.append(f"### Vitec Template Resources")
    lines.append(f"| Resource | Templates |")
    lines.append(f"|----------|-----------|")
    for res, freq in counter_to_sorted(fields["resource_frequency"]):
        lines.append(f"| `{res}` | {freq} |")
    lines.append(f"")

    lines.append(f"### Fields Used Inside foreach Loops")
    lines.append(f"| Field | Templates |")
    lines.append(f"|-------|-----------|")
    for path, freq in counter_to_sorted(fields["foreach_field_frequency"], 30):
        lines.append(f"| `[[{path}]]` | {freq} |")
    lines.append(f"")

    lines.append(f"---")
    lines.append(f"")
    lines.append(f"## 3. Conditional Logic")
    lines.append(f"")

    lines.append(f"### Foreach Collection Paths")
    lines.append(f"| Collection Path | Templates |")
    lines.append(f"|-----------------|-----------|")
    for path, freq in counter_to_sorted(conds["collection_path_frequency"]):
        lines.append(f"| `{path}` | {freq} |")
    lines.append(f"")

    lines.append(f"### Foreach Expressions (Full)")
    lines.append(f"| Expression | Templates |")
    lines.append(f"|------------|-----------|")
    for expr, freq in counter_to_sorted(conds["foreach_expr_frequency"], 30):
        lines.append(f"| `{expr}` | {freq} |")
    lines.append(f"")

    lines.append(f"### Logic Feature Usage")
    lines.append(f"| Feature | Templates | % |")
    lines.append(f"|---------|-----------|---|")
    for label, key in [
        (".Count guard before foreach", "has_count_guard"),
        ("'Mangler data' sentinel check", "has_mangler_data"),
        ("'not' negation (vitec-if=\"not ...\")", "has_negation_not"),
        ("'!' negation (vitec-if=\"!...\")", "has_negation_bang"),
    ]:
        val = conds[key]
        pct = round(val / n * 100) if n else 0
        lines.append(f"| {label} | {val} | {pct}% |")
    lines.append(f"")

    lines.append(f"### Model. vs Iterator Prefix in Conditions")
    lines.append(f"| Prefix Type | Total Conditions |")
    lines.append(f"|-------------|-----------------|")
    lines.append(f"| Model. prefix (outside foreach) | {conds['total_model_prefix']} |")
    lines.append(f"| Iterator prefix (inside foreach) | {conds['total_iterator_prefix']} |")
    lines.append(f"")

    lines.append(f"### Top 50 Most Common Conditions")
    lines.append(f"| Condition | Templates |")
    lines.append(f"|-----------|-----------|")
    for cond, freq in counter_to_sorted(conds["condition_frequency"], 50):
        display = cond.replace("|", "\\|")
        lines.append(f"| `{display}` | {freq} |")
    lines.append(f"")

    lines.append(f"### Guard Patterns (.Count checks)")
    lines.append(f"| Guard | Templates |")
    lines.append(f"|-------|-----------|")
    for g, freq in counter_to_sorted(conds["guard_frequency"], 20):
        lines.append(f"| `{g}` | {freq} |")
    lines.append(f"")

    lines.append(f"---")
    lines.append(f"")
    lines.append(f"## Appendix: Per-Template Summary")
    lines.append(f"")
    lines.append(f"| Template | Origin | Size | Fields | Conditions | Foreach | Style Blocks | Checkboxes | Inserts |")
    lines.append(f"|----------|--------|------|--------|------------|---------|--------------|------------|---------|")
    for t in sorted(templates, key=lambda x: x["filename"]):
        name = t["filename"][:50]
        lines.append(
            f"| {name} | {t['origin']} | {t['size_bytes']:,} | "
            f"{t['fields']['total_fields']} | {t['conditions']['vitec_if_count']} | "
            f"{t['conditions']['foreach_count']} | {t['css']['style_block_count']} | "
            f"{'Y' if t['css']['has_checkbox_css'] else '-'} | "
            f"{'Y' if t['css']['has_insert_css'] else '-'} |"
        )
    lines.append(f"")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Mine template library for patterns")
    parser.add_argument("--min-size", type=int, default=500,
                        help="Skip templates smaller than this (bytes)")
    parser.add_argument("--json-only", action="store_true",
                        help="Only output JSON, skip markdown report")
    args = parser.parse_args()

    if not TEMPLATES_ROOT.exists():
        print(f"ERROR: Templates directory not found: {TEMPLATES_ROOT}", file=sys.stderr)
        sys.exit(1)

    templates = []
    skipped = 0
    total = 0

    for origin_dir, origin_name in [
        (TEMPLATES_ROOT / "vitec-system", "vitec-system"),
        (TEMPLATES_ROOT / "kundemal", "kundemal"),
    ]:
        if not origin_dir.exists():
            continue
        for html_file in sorted(origin_dir.glob("*.html")):
            total += 1
            if html_file.stat().st_size < args.min_size:
                skipped += 1
                continue
            try:
                data = mine_template(html_file, origin_name)
                templates.append(data)
            except Exception as e:
                print(f"  WARNING: Failed to parse {html_file.name}: {e}", file=sys.stderr)

    print(f"Parsed {len(templates)} templates ({skipped} skipped, {total} total)")

    agg = aggregate(templates)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    json_path = OUTPUT_DIR / "library-mining-data.json"
    json_data = {
        "generated": datetime.now().isoformat(),
        "templates_analyzed": len(templates),
        "total_templates": total,
        "skipped": skipped,
        "aggregated": {
            "css": {k: dict(v) if isinstance(v, Counter) else v for k, v in agg["css"].items()},
            "fields": {k: dict(v) if isinstance(v, Counter) else v for k, v in agg["fields"].items()},
            "conditions": {k: dict(v) if isinstance(v, Counter) else v for k, v in agg["conditions"].items()},
        },
        "templates": templates,
    }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False, default=str)
    print(f"JSON data written to: {json_path}")

    if not args.json_only:
        report = generate_report(templates, agg, total, skipped)
        report_path = OUTPUT_DIR / "LIBRARY-MINING-REPORT.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"Report written to: {report_path}")


if __name__ == "__main__":
    main()
