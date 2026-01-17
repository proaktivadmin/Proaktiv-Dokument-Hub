"""
Vitec Normalizer Service - Normalizes Proaktiv-flavoured templates to Vitec style.

Goals:
- Preserve Vitec structural/functional CSS
- Remove Proaktiv brand styling and inline appearance styles
- Ensure Vitec wrapper + stilark resource marker
"""

from __future__ import annotations

import logging
import re
from typing import Dict, List, Tuple

from bs4 import BeautifulSoup, Tag

logger = logging.getLogger(__name__)


class VitecNormalizerService:
    """
    Normalize HTML templates to match Vitec Next structural conventions.
    """

    VITEC_STILARK_RESOURCE = "resource:Vitec Stilark"

    PROAKTIV_CLASS_MARKERS = ("proaktiv", "theme-proaktiv")

    # Selectors that indicate functional/structural CSS we should keep
    FUNCTIONAL_SELECTOR_PATTERNS = [
        re.compile(r"\b#vitecTemplate\b", re.IGNORECASE),
        re.compile(r"\bbody\b", re.IGNORECASE),
        re.compile(r"\bhtml\b", re.IGNORECASE),
        re.compile(r"\.no-border\b", re.IGNORECASE),
        re.compile(r"\btd\[data-label\]", re.IGNORECASE),
        re.compile(r"\btd\[data-choice\]", re.IGNORECASE),
        re.compile(r"\bspan\.insert\b", re.IGNORECASE),
        re.compile(r"\.insert-table\b", re.IGNORECASE),
        re.compile(r"\blabel\.btn\b", re.IGNORECASE),
        re.compile(r"\.svg-toggle\b", re.IGNORECASE),
        re.compile(r"\[data-toggle=['\"]buttons['\"]\]\s*input", re.IGNORECASE),
        re.compile(r"\[contenteditable=['\"]false['\"]\]", re.IGNORECASE),
    ]

    # Inline styles allowed (layout-only)
    INLINE_KEEP_PROPERTIES = {
        "width",
        "height",
        "max-width",
        "max-height",
        "min-width",
        "min-height",
        "margin",
        "margin-top",
        "margin-bottom",
        "margin-left",
        "margin-right",
        "padding",
        "padding-top",
        "padding-bottom",
        "padding-left",
        "padding-right",
        "text-align",
        "vertical-align",
        "table-layout",
        "page-break-before",
        "page-break-after",
        "page-break-inside",
    }

    BRAND_TOKENS = (
        "playfair",
        "georgia",
        "proaktiv",
        "#bcab8a",
        "#272630",
        "#e9e7dc",
        "#a4b5a8",
        "#3e3d4a",
    )

    INLINE_BORDER_KEEP = re.compile(
        r"\b1px\b.*\bsolid\b.*(black|#000|#000000)\b", re.IGNORECASE
    )

    def normalize(self, html: str) -> Tuple[str, Dict[str, int | bool]]:
        """
        Normalize template HTML to Vitec conventions.
        """
        report: Dict[str, int | bool] = {
            "removed_style_tags": 0,
            "kept_style_tags": 0,
            "removed_css_rules": 0,
            "kept_css_rules": 0,
            "removed_inline_styles": 0,
            "kept_inline_styles": 0,
            "removed_classes": 0,
            "ensured_wrapper": False,
            "ensured_stilark_marker": False,
        }

        if not html or not html.strip():
            empty_wrapper = self._create_wrapper_with_stilark("")
            report["ensured_wrapper"] = True
            report["ensured_stilark_marker"] = True
            return empty_wrapper, report

        soup = BeautifulSoup(html, "lxml")

        self._remove_proaktiv_classes(soup, report)
        self._normalize_style_tags(soup, report)
        self._normalize_inline_styles(soup, report)

        normalized_html = self._ensure_wrapper_and_marker(soup, report)
        return normalized_html, report

    def _remove_proaktiv_classes(self, soup: BeautifulSoup, report: Dict[str, int | bool]) -> None:
        for element in soup.find_all(class_=True):
            class_list = element.get("class", [])
            if isinstance(class_list, str):
                class_list = class_list.split()

            original_len = len(class_list)
            class_list = [cls for cls in class_list if not self._is_proaktiv_class(cls)]

            removed = original_len - len(class_list)
            if removed > 0:
                report["removed_classes"] = int(report["removed_classes"]) + removed
                if class_list:
                    element["class"] = class_list
                else:
                    del element["class"]

    def _is_proaktiv_class(self, class_name: str) -> bool:
        lowered = class_name.lower()
        return any(marker in lowered for marker in self.PROAKTIV_CLASS_MARKERS)

    def _normalize_style_tags(self, soup: BeautifulSoup, report: Dict[str, int | bool]) -> None:
        for style_tag in soup.find_all("style"):
            css_text = style_tag.string or style_tag.get_text() or ""
            cleaned_css, removed, kept = self._filter_css_rules(css_text)

            report["removed_css_rules"] = int(report["removed_css_rules"]) + removed
            report["kept_css_rules"] = int(report["kept_css_rules"]) + kept

            if cleaned_css.strip():
                style_tag.string = cleaned_css
                report["kept_style_tags"] = int(report["kept_style_tags"]) + 1
            else:
                style_tag.decompose()
                report["removed_style_tags"] = int(report["removed_style_tags"]) + 1

    def _filter_css_rules(self, css_text: str) -> Tuple[str, int, int]:
        """
        Keep only functional/structural CSS rules. Drop @import and branding rules.
        """
        rules = self._split_css_rules(css_text)
        kept_rules: List[str] = []
        removed_count = 0

        for rule in rules:
            trimmed = rule.strip()
            if not trimmed:
                continue

            if trimmed.startswith("@"):
                # Remove @import and other at-rules for strict Vitec normalization
                removed_count += 1
                continue

            selector, declarations = self._split_selector_declarations(trimmed)
            if not selector or not declarations:
                removed_count += 1
                continue

            if self._should_keep_rule(selector, declarations):
                kept_rules.append(trimmed)
            else:
                removed_count += 1

        return "\n".join(kept_rules).strip(), removed_count, len(kept_rules)

    def _split_css_rules(self, css_text: str) -> List[str]:
        rules: List[str] = []
        buffer: List[str] = []
        depth = 0

        for char in css_text:
            buffer.append(char)
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    rules.append("".join(buffer))
                    buffer = []

        # Discard incomplete rules safely
        return rules

    def _split_selector_declarations(self, rule: str) -> Tuple[str, str]:
        if "{" not in rule or "}" not in rule:
            return "", ""
        selector, remainder = rule.split("{", 1)
        declarations = remainder.rsplit("}", 1)[0]
        return selector.strip(), declarations.strip()

    def _should_keep_rule(self, selector: str, declarations: str) -> bool:
        selectors = [s.strip() for s in selector.split(",") if s.strip()]
        if not selectors:
            return False

        if self._contains_branding(declarations):
            return False

        for sel in selectors:
            if not self._is_functional_selector(sel):
                return False

        return True

    def _is_functional_selector(self, selector: str) -> bool:
        lowered = selector.lower()
        return any(pattern.search(lowered) for pattern in self.FUNCTIONAL_SELECTOR_PATTERNS)

    def _contains_branding(self, declarations: str) -> bool:
        lowered = declarations.lower()
        if any(token in lowered for token in self.BRAND_TOKENS):
            return True
        if "font-family" in lowered:
            return True
        if "box-shadow" in lowered or "border-radius" in lowered:
            return True
        if "text-transform" in lowered:
            return True
        if re.search(r"padding\s*:\s*\d+mm", lowered):
            return True
        if re.search(r"max-width\s*:\s*\d+mm", lowered):
            return True
        return False

    def _normalize_inline_styles(self, soup: BeautifulSoup, report: Dict[str, int | bool]) -> None:
        for element in soup.find_all(style=True):
            original_style = element.get("style", "")
            if not original_style:
                continue

            kept, removed = self._filter_inline_styles(original_style)
            report["removed_inline_styles"] = int(report["removed_inline_styles"]) + removed
            report["kept_inline_styles"] = int(report["kept_inline_styles"]) + len(kept)

            if kept:
                element["style"] = "; ".join(kept)
            else:
                del element["style"]

    def _filter_inline_styles(self, style_string: str) -> Tuple[List[str], int]:
        kept: List[str] = []
        removed = 0

        declarations = [d.strip() for d in style_string.split(";") if d.strip()]
        for declaration in declarations:
            if ":" not in declaration:
                removed += 1
                continue

            prop, value = [part.strip() for part in declaration.split(":", 1)]
            prop_lower = prop.lower()
            value_lower = value.lower()

            if prop_lower in self.INLINE_KEEP_PROPERTIES:
                kept.append(f"{prop}: {value}")
                continue

            if prop_lower.startswith("border"):
                if self.INLINE_BORDER_KEEP.search(value_lower):
                    kept.append(f"{prop}: {value}")
                else:
                    removed += 1
                continue

            # Remove typography/appearance
            removed += 1

        return kept, removed

    def _ensure_wrapper_and_marker(
        self, soup: BeautifulSoup, report: Dict[str, int | bool]
    ) -> str:
        wrapper = soup.find(id="vitecTemplate")
        if not wrapper:
            content = self._extract_content(soup)
            report["ensured_wrapper"] = True
            report["ensured_stilark_marker"] = True
            return self._create_wrapper_with_stilark(content)

        # Remove Proaktiv classes on wrapper if any
        self._remove_proaktiv_classes(wrapper, report)
        self._ensure_stilark_marker(wrapper, report)
        return self._extract_content(soup)

    def _ensure_stilark_marker(self, wrapper: Tag, report: Dict[str, int | bool]) -> None:
        # Remove any existing Stilark markers to avoid duplicates
        for tag in wrapper.find_all(attrs={"vitec-template": True}):
            if "vitec stilark" in str(tag.get("vitec-template", "")).lower():
                tag.decompose()

        marker = BeautifulSoup(
            f'<span vitec-template="{self.VITEC_STILARK_RESOURCE}" '
            f'contenteditable="false">&nbsp;</span>',
            "html.parser",
        ).find("span")

        if marker:
            wrapper.insert(0, marker)
            report["ensured_stilark_marker"] = True

    def _create_wrapper_with_stilark(self, content: str) -> str:
        return (
            f'<div id="vitecTemplate">'
            f'<span vitec-template="{self.VITEC_STILARK_RESOURCE}" '
            f'contenteditable="false">&nbsp;</span>{content}</div>'
        )

    def _extract_content(self, soup: BeautifulSoup) -> str:
        body = soup.find("body")
        if body:
            return "".join(str(child) for child in body.children).strip()
        if soup.html and soup.body:
            return "".join(str(child) for child in soup.body.children).strip()
        return str(soup).strip()

