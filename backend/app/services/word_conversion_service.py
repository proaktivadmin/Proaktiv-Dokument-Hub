"""
Word Conversion Service — Converts .docx files to Vitec Next-ready HTML.

Uses mammoth for initial .docx→HTML conversion, then post-processes with
BeautifulSoup to enforce the rules from .planning/vitec-html-ruleset.md.
The output passes through SanitizerService for final Vitec Stilark compliance.
"""

import io
import logging
import re

import mammoth
from bs4 import BeautifulSoup, Tag

from app.schemas.word_conversion import ConversionResult, ValidationItem
from app.services.sanitizer_service import SanitizerService
from app.services.template_analyzer_service import TemplateAnalyzerService

logger = logging.getLogger(__name__)

MERGE_FIELD_PATTERN = re.compile(r"\[\[(\*?)([^\]]+)\]\]")

VITEC_STILARK_RESOURCE = "resource:Vitec Stilark"
WRAPPER_CLASS = "proaktiv-theme"
WRAPPER_ID = "vitecTemplate"


class WordConversionService:
    """Converts .docx files to CKEditor 4-compliant, Vitec Next-ready HTML."""

    def __init__(self) -> None:
        self._sanitizer = SanitizerService()

    async def convert(
        self,
        docx_bytes: bytes,
        filename: str = "upload.docx",
    ) -> ConversionResult:
        """Convert a .docx file to Vitec-ready HTML.

        Args:
            docx_bytes: Raw bytes of the .docx file.
            filename: Original filename (for logging/warnings).

        Returns:
            ConversionResult with cleaned HTML, warnings, validation, and merge fields.

        Raises:
            ValueError: If mammoth cannot parse the file.
        """
        warnings: list[str] = []

        # 1. Run mammoth conversion
        style_map = self._build_style_map()
        try:
            result = mammoth.convert_to_html(
                io.BytesIO(docx_bytes),
                style_map=style_map,
            )
        except Exception as exc:
            raise ValueError(f"mammoth could not parse '{filename}': {exc}") from exc

        raw_html: str = result.value
        for msg in result.messages:
            warnings.append(f"mammoth: {msg.message}")

        if not raw_html.strip():
            warnings.append("mammoth produced empty output")
            raw_html = "<p>&nbsp;</p>"

        # 2. Post-process to enforce ruleset
        html, post_warnings = self._post_process(raw_html)
        warnings.extend(post_warnings)

        # 3. Run through SanitizerService for Stilark compliance
        html = self._sanitizer.sanitize(html, update_resource=True)

        # 4. Extract merge fields
        merge_fields = TemplateAnalyzerService.extract_merge_fields(html)

        # 5. Validate against Section 12 checklist
        validation = self._validate_against_checklist(html)
        is_valid = all(item.passed for item in validation)

        return ConversionResult(
            html=html,
            warnings=warnings,
            validation=validation,
            merge_fields_detected=merge_fields,
            is_valid=is_valid,
        )

    # ------------------------------------------------------------------
    # Style map
    # ------------------------------------------------------------------

    def _build_style_map(self) -> str:
        """Build mammoth style map aligned with Vitec Stilark conventions.

        Maps Word paragraph/character styles to semantic HTML elements that
        are safe inside CKEditor 4 and compatible with the Vitec Stilark CSS.
        """
        return "\n".join(
            [
                # Paragraph styles → semantic elements
                "p[style-name='Heading 1'] => h1:fresh",
                "p[style-name='Heading 2'] => h2:fresh",
                "p[style-name='Heading 3'] => h3:fresh",
                "p[style-name='Heading 4'] => h4:fresh",
                "p[style-name='Heading 5'] => h5:fresh",
                "p[style-name='Title'] => h1:fresh",
                "p[style-name='Subtitle'] => h2:fresh",
                "p[style-name='Normal'] => p:fresh",
                "p[style-name='Body Text'] => p:fresh",
                "p[style-name='List Paragraph'] => p:fresh",
                # Character styles → inline elements
                "r[style-name='Strong'] => strong",
                "r[style-name='Emphasis'] => em",
                # Bold/italic runs → semantic tags (Vitec uses <strong>/<em>)
                "b => strong",
                "i => em",
                "u => u",
                # Small/footnote
                "p[style-name='Footnote Text'] => p > small",
                # Table of contents — flatten to paragraph
                "p[style-name='TOC Heading'] => h2:fresh",
                "p[style-name='toc 1'] => p:fresh",
                "p[style-name='toc 2'] => p:fresh",
                "p[style-name='toc 3'] => p:fresh",
            ]
        )

    # ------------------------------------------------------------------
    # Post-processing
    # ------------------------------------------------------------------

    def _post_process(self, html: str) -> tuple[str, list[str]]:
        """Apply ruleset-based cleanup to mammoth output.

        Returns:
            Tuple of (cleaned_html, warnings).
        """
        warnings: list[str] = []
        soup = BeautifulSoup(html, "html.parser")

        # A. Remove empty paragraphs (mammoth artifact)
        removed_empty = 0
        for p in soup.find_all("p"):
            text = p.get_text(strip=True)
            if not text and not p.find(["img", "br", "table", "span"]):
                # Keep if it contains only &nbsp; (intentional spacer)
                inner = p.decode_contents().strip()
                if inner and inner != "&nbsp;" and inner != "\xa0":
                    p.decompose()
                    removed_empty += 1
                elif not inner:
                    p.decompose()
                    removed_empty += 1
        if removed_empty:
            warnings.append(f"Removed {removed_empty} empty paragraph(s)")

        # B. Unwrap unnecessary nested spans (mammoth artifact)
        for span in soup.find_all("span"):
            if not span.attrs and span.string is not None:
                span.unwrap()

        # C. Convert tables to Vitec-safe structure
        table_warnings = self._process_tables(soup)
        warnings.extend(table_warnings)

        # D. Strip non-structural inline styles that the Stilark handles
        self._strip_appearance_styles(soup)

        # E. Unwrap deprecated tags (<font>, <center>)
        for tag_name in ("font", "center"):
            for tag in soup.find_all(tag_name):
                tag.unwrap()
                warnings.append(f"Unwrapped deprecated <{tag_name}> tag")

        # F. Ensure images have alt attributes
        for img in soup.find_all("img"):
            if not img.get("alt"):
                img["alt"] = ""

        # G. Wrap in vitecTemplate shell with Stilark reference
        wrapped_html = self._wrap_in_template_shell(str(soup))

        return wrapped_html, warnings

    def _process_tables(self, soup: BeautifulSoup) -> list[str]:
        """Enforce Vitec table conventions on all tables."""
        warnings: list[str] = []

        for table in soup.find_all("table"):
            # Ensure rows are inside <tbody> (not direct children of <table>)
            direct_trs = [child for child in table.children if isinstance(child, Tag) and child.name == "tr"]
            if direct_trs:
                tbody = soup.new_tag("tbody")
                for tr in direct_trs:
                    tbody.append(tr.extract())
                table.append(tbody)
                warnings.append("Wrapped bare <tr> elements in <tbody>")

            # Add structural styles for outer tables
            existing_style = table.get("style", "")
            if "width" not in existing_style:
                table["style"] = f"width:100%; table-layout:fixed; {existing_style}".strip().rstrip(";") + ";"
            if "table-layout" not in existing_style:
                if "table-layout" not in table.get("style", ""):
                    current = table.get("style", "")
                    if "table-layout" not in current:
                        table["style"] = current.rstrip(";") + "; table-layout:fixed;"

            # Normalize style attribute (deduplicate table-layout)
            style_str = table.get("style", "")
            style_str = self._deduplicate_css_props(style_str)
            table["style"] = style_str

        return warnings

    @staticmethod
    def _deduplicate_css_props(style: str) -> str:
        """Remove duplicate CSS properties, keeping the last occurrence."""
        if not style:
            return ""
        declarations: list[tuple[str, str]] = []
        seen: dict[str, int] = {}
        for decl in style.split(";"):
            decl = decl.strip()
            if not decl or ":" not in decl:
                continue
            prop = decl.split(":")[0].strip().lower()
            if prop in seen:
                declarations[seen[prop]] = (prop, decl)
            else:
                seen[prop] = len(declarations)
                declarations.append((prop, decl))
        return "; ".join(d[1] for d in declarations) + ";"

    def _strip_appearance_styles(self, soup: BeautifulSoup) -> None:
        """Remove non-structural inline styles that the Stilark handles."""
        strip_props = {
            "font-family",
            "font-size",
            "color",
            "background-color",
            "background",
            "font-weight",
            "font-style",
            "line-height",
            "font-variant-ligatures",
        }
        for el in soup.find_all(style=True):
            original = el.get("style", "")
            kept: list[str] = []
            for decl in original.split(";"):
                decl = decl.strip()
                if not decl or ":" not in decl:
                    continue
                prop = decl.split(":")[0].strip().lower()
                if prop not in strip_props:
                    kept.append(decl)
            if kept:
                el["style"] = "; ".join(kept) + ";"
            else:
                del el["style"]

    def _wrap_in_template_shell(self, inner_html: str) -> str:
        """Wrap content in the required #vitecTemplate shell (Section 1)."""
        return (
            f'<div class="{WRAPPER_CLASS}" id="{WRAPPER_ID}">\n'
            f'  <span vitec-template="{VITEC_STILARK_RESOURCE}">&nbsp;</span>\n'
            f"  {inner_html}\n"
            f"</div>"
        )

    # ------------------------------------------------------------------
    # Validation (Section 12 Conversion Checklist)
    # ------------------------------------------------------------------

    def _validate_against_checklist(self, html: str) -> list[ValidationItem]:
        """Run Section 12 conversion checklist items against the output HTML."""
        items: list[ValidationItem] = []
        soup = BeautifulSoup(html, "html.parser")

        # A. Template Shell
        wrapper = soup.find(id=WRAPPER_ID)
        items.append(
            ValidationItem(
                rule="A1: vitecTemplate wrapper present",
                passed=wrapper is not None,
                detail="<div id='vitecTemplate'> found" if wrapper else "Missing #vitecTemplate wrapper",
            )
        )

        has_class = False
        if wrapper and isinstance(wrapper, Tag):
            classes = wrapper.get("class", [])
            if isinstance(classes, str):
                classes = classes.split()
            has_class = WRAPPER_CLASS in classes
        items.append(
            ValidationItem(
                rule="A1: proaktiv-theme class on wrapper",
                passed=has_class,
                detail=f"class='{WRAPPER_CLASS}' present" if has_class else f"Missing '{WRAPPER_CLASS}' class",
            )
        )

        stilark_ref = soup.find(attrs={"vitec-template": VITEC_STILARK_RESOURCE})
        items.append(
            ValidationItem(
                rule="A2: Stilark resource reference present",
                passed=stilark_ref is not None,
                detail="Stilark <span> found" if stilark_ref else "Missing Stilark resource reference",
            )
        )

        stilark_has_nbsp = False
        if stilark_ref:
            content = stilark_ref.decode_contents().strip()
            stilark_has_nbsp = "\xa0" in content or "&nbsp;" in content
        items.append(
            ValidationItem(
                rule="A3: Stilark span contains &nbsp;",
                passed=stilark_has_nbsp,
                detail="Contains &nbsp;" if stilark_has_nbsp else "Stilark span is empty or missing &nbsp;",
            )
        )

        # B. Table Structure
        tables = soup.find_all("table")
        all_trs_wrapped = True
        for table in tables:
            direct_trs = [c for c in table.children if isinstance(c, Tag) and c.name == "tr"]
            if direct_trs:
                all_trs_wrapped = False
                break
        items.append(
            ValidationItem(
                rule="B3: All <tr> inside <tbody>/<thead>/<tfoot>",
                passed=all_trs_wrapped,
                detail="All rows properly wrapped" if all_trs_wrapped else "Found <tr> directly inside <table>",
            )
        )

        no_empty_tables = True
        for table in tables:
            if not table.find("tr"):
                no_empty_tables = False
                break
        items.append(
            ValidationItem(
                rule="B6: No empty tables",
                passed=no_empty_tables or len(tables) == 0,
                detail="No empty tables found" if no_empty_tables else "Found table(s) with no rows",
            )
        )

        # C. Inline Styles
        has_font_family = False
        has_font_size = False
        for el in soup.find_all(style=True):
            style = el.get("style", "").lower()
            if "font-family" in style:
                has_font_family = True
            if "font-size" in style:
                has_font_size = True
        items.append(
            ValidationItem(
                rule="C1: No font-family in inline styles",
                passed=not has_font_family,
                detail="Clean" if not has_font_family else "Found inline font-family (Stilark handles this)",
            )
        )
        items.append(
            ValidationItem(
                rule="C2: No font-size in inline styles",
                passed=not has_font_size,
                detail="Clean" if not has_font_size else "Found inline font-size (may be intentional override)",
            )
        )

        # D. Merge Fields
        merge_fields = MERGE_FIELD_PATTERN.findall(html)
        no_spaces = True
        for _asterisk, field_path in merge_fields:
            if field_path != field_path.strip():
                no_spaces = False
                break
        items.append(
            ValidationItem(
                rule="D5: No spaces inside merge field brackets",
                passed=no_spaces,
                detail="All merge fields properly formatted" if no_spaces else "Found spaces inside [[ ]]",
            )
        )

        # I. Text and Formatting
        has_font_tags = len(soup.find_all("font")) > 0
        items.append(
            ValidationItem(
                rule="I1: No <font> tags",
                passed=not has_font_tags,
                detail="No <font> tags" if not has_font_tags else "Found deprecated <font> tag(s)",
            )
        )

        has_center_tags = len(soup.find_all("center")) > 0
        items.append(
            ValidationItem(
                rule="I2: No <center> tags",
                passed=not has_center_tags,
                detail="No <center> tags" if not has_center_tags else "Found deprecated <center> tag(s)",
            )
        )

        # K. Final Validation
        has_event_handlers = False
        dangerous_attrs = ["onclick", "onload", "onerror", "onmouseover", "onmouseout"]
        for attr in dangerous_attrs:
            if soup.find(attrs={attr: True}):
                has_event_handlers = True
                break
        items.append(
            ValidationItem(
                rule="K2: No JavaScript event handlers",
                passed=not has_event_handlers,
                detail="No event handlers found" if not has_event_handlers else "Found prohibited event handler(s)",
            )
        )

        has_ext_stylesheets = len(soup.find_all("link", rel="stylesheet")) > 0
        items.append(
            ValidationItem(
                rule="K3: No external stylesheet links",
                passed=not has_ext_stylesheets,
                detail="No external stylesheets" if not has_ext_stylesheets else "Found external <link> stylesheet(s)",
            )
        )

        # Well-formed HTML check (basic)
        html_str = str(soup)
        well_formed = True
        detail = "HTML appears well-formed"
        for tag_name in ["div", "table", "tr", "td", "th", "tbody", "thead", "tfoot", "p", "span", "strong", "em"]:
            opens = len(soup.find_all(tag_name))
            close_count = html_str.count(f"</{tag_name}>")
            if opens != close_count:
                well_formed = False
                detail = f"Mismatched <{tag_name}>: {opens} opens vs {close_count} closes"
                break
        items.append(
            ValidationItem(
                rule="K1: HTML is well-formed",
                passed=well_formed,
                detail=detail,
            )
        )

        return items


_word_conversion_service: WordConversionService | None = None


def get_word_conversion_service() -> WordConversionService:
    """Get the singleton WordConversionService instance."""
    global _word_conversion_service
    if _word_conversion_service is None:
        _word_conversion_service = WordConversionService()
    return _word_conversion_service
