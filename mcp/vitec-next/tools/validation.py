from __future__ import annotations

# NOTE: Validation logic in this module was ported from
# backend/app/services/sanitizer_service.py.
# When backend sanitizer rules change, review this module for rule drift.

import re
from typing import Any

from bs4 import BeautifulSoup
from mcp.server.fastmcp import FastMCP


MERGE_FIELD_PATTERN = re.compile(r"\[\[(\*?)([^\]]+)\]\]")
VITEC_IF_PATTERN = re.compile(r'vitec-if="([^"]+)"')
VITEC_FOREACH_PATTERN = re.compile(r'vitec-foreach="(\w+)\s+in\s+([^"]+)"')

_STYLE_PROP_PATTERN = re.compile(r"^\s*([a-zA-Z-]+)\s*:")
_VITEC_IF_ATTR_PATTERN = re.compile(r"vitec-if\s*=")
_VITEC_FOREACH_ATTR_PATTERN = re.compile(r"vitec-foreach\s*=")

VITEC_STILARK_RESOURCE = "resource:Vitec Stilark"
FORBIDDEN_TEMPLATE_CLASS = "proaktiv-theme"

ALLOWED_INLINE_STYLES: set[str] = {
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
    "border",
    "border-top",
    "border-bottom",
    "border-left",
    "border-right",
    "border-collapse",
    "border-spacing",
    "text-align",
    "vertical-align",
}


def _extract_forbidden_style_entries(html: str) -> tuple[list[dict[str, Any]], int]:
    soup = BeautifulSoup(html or "", "html.parser")
    issues: list[dict[str, Any]] = []
    elements_with_violations = 0

    for element in soup.find_all(style=True):
        style_value = str(element.get("style", "")).strip()
        if not style_value:
            continue

        bad_properties: list[str] = []
        for declaration in style_value.split(";"):
            decl = declaration.strip()
            if not decl:
                continue
            match = _STYLE_PROP_PATTERN.match(decl)
            if not match:
                continue
            prop = match.group(1).lower()
            if prop not in ALLOWED_INLINE_STYLES:
                bad_properties.append(prop)

        if bad_properties:
            elements_with_violations += 1
            issues.append(
                {
                    "tag": element.name,
                    "forbidden_properties": sorted(set(bad_properties)),
                }
            )

    return issues, elements_with_violations


def _has_stilark_reference(soup: BeautifulSoup) -> bool:
    for element in soup.find_all(attrs={"vitec-template": True}):
        value = str(element.get("vitec-template", "")).strip()
        if value == VITEC_STILARK_RESOURCE:
            return True
    return False


def _validate_vitec_if_syntax(html: str, soup: BeautifulSoup) -> tuple[bool, list[dict[str, Any]]]:
    issues: list[dict[str, Any]] = []

    raw_attr_count = len(_VITEC_IF_ATTR_PATTERN.findall(html or ""))
    regex_matches = list(VITEC_IF_PATTERN.finditer(html or ""))
    if raw_attr_count != len(regex_matches):
        issues.append(
            {
                "type": "format",
                "message": 'Malformed vitec-if attribute detected (expected format: vitec-if="expression").',
            }
        )

    for element in soup.find_all(attrs={"vitec-if": True}):
        expr = str(element.get("vitec-if", "")).strip()
        if not expr:
            issues.append({"type": "empty_expression", "tag": element.name})
            continue
        if expr.count("(") != expr.count(")"):
            issues.append(
                {
                    "type": "unbalanced_parentheses",
                    "tag": element.name,
                    "expression": expr,
                }
            )

    return len(issues) == 0, issues


def _validate_vitec_foreach_syntax(html: str, soup: BeautifulSoup) -> tuple[bool, list[dict[str, Any]]]:
    issues: list[dict[str, Any]] = []

    raw_attr_count = len(_VITEC_FOREACH_ATTR_PATTERN.findall(html or ""))
    regex_matches = list(VITEC_FOREACH_PATTERN.finditer(html or ""))
    if raw_attr_count != len(regex_matches):
        issues.append(
            {
                "type": "format",
                "message": 'Malformed vitec-foreach attribute detected (expected format: vitec-foreach="item in collection").',
            }
        )

    for element in soup.find_all(attrs={"vitec-foreach": True}):
        raw = str(element.get("vitec-foreach", "")).strip()
        match = re.fullmatch(r"(\w+)\s+in\s+(.+)", raw)
        if not match:
            issues.append({"type": "invalid_expression", "tag": element.name, "value": raw})
            continue
        variable, collection = match.groups()
        if not variable.strip() or not collection.strip():
            issues.append({"type": "missing_variable_or_collection", "tag": element.name, "value": raw})

    return len(issues) == 0, issues


def _score_from_checks(checks: list[dict[str, Any]]) -> int:
    if not checks:
        return 0
    passed = sum(1 for check in checks if check.get("passed"))
    return round((passed / len(checks)) * 100)


def _score_stilark(stilark_referenced: bool, forbidden_count: int, element_count: int) -> int:
    style_component = 100
    if element_count > 0:
        ratio = forbidden_count / element_count
        style_component = max(0, round((1 - ratio) * 100))

    reference_component = 100 if stilark_referenced else 0
    return round((reference_component * 0.5) + (style_component * 0.5))


def register_validation_tools(mcp: FastMCP) -> None:
    @mcp.tool()
    def validate_template(html: str) -> dict[str, Any]:
        soup = BeautifulSoup(html or "", "html.parser")

        wrapper = soup.find(id="vitecTemplate")
        has_wrapper = wrapper is not None

        has_stilark_reference = _has_stilark_reference(soup)

        has_forbidden_theme_class = bool(soup.find(class_=lambda value: value and FORBIDDEN_TEMPLATE_CLASS in str(value).split()))

        font_tags = soup.find_all("font")
        has_deprecated_font_tags = len(font_tags) > 0

        forbidden_style_issues, _ = _extract_forbidden_style_entries(html)
        has_forbidden_inline_styles = len(forbidden_style_issues) > 0

        valid_if_syntax, vitec_if_issues = _validate_vitec_if_syntax(html, soup)
        valid_foreach_syntax, vitec_foreach_issues = _validate_vitec_foreach_syntax(html, soup)

        checks = [
            {
                "name": "has_vitec_template_wrapper",
                "passed": has_wrapper,
                "details": "Template includes #vitecTemplate wrapper div.",
            },
            {
                "name": "has_stilark_reference",
                "passed": has_stilark_reference,
                "details": 'Template references vitec-template="resource:Vitec Stilark".',
            },
            {
                "name": "no_proaktiv_theme_class",
                "passed": not has_forbidden_theme_class,
                "details": "Template does not contain proaktiv-theme class.",
            },
            {
                "name": "no_deprecated_font_tags",
                "passed": not has_deprecated_font_tags,
                "details": "Template does not contain deprecated <font> tags.",
            },
            {
                "name": "no_forbidden_inline_styles",
                "passed": not has_forbidden_inline_styles,
                "details": "Inline styles only use allowed structural properties.",
            },
            {
                "name": "valid_vitec_if_syntax",
                "passed": valid_if_syntax,
                "details": 'All vitec-if attributes follow vitec-if="expression".',
            },
            {
                "name": "valid_vitec_foreach_syntax",
                "passed": valid_foreach_syntax,
                "details": 'All vitec-foreach attributes follow vitec-foreach="item in collection".',
            },
        ]

        suggestions: list[str] = []
        if not has_wrapper:
            suggestions.append('Wrap content in <div id="vitecTemplate">...</div>.')
        if not has_stilark_reference:
            suggestions.append('Add vitec-template="resource:Vitec Stilark" to the template.')
        if has_forbidden_theme_class:
            suggestions.append('Remove "proaktiv-theme" class; rely on Vitec Stilark styling.')
        if has_deprecated_font_tags:
            suggestions.append("Replace <font> tags with semantic HTML and Stilark-driven styles.")
        if has_forbidden_inline_styles:
            suggestions.append("Remove non-structural inline styles and keep only allowed layout properties.")
        if not valid_if_syntax:
            suggestions.append('Fix vitec-if expressions to use valid quoted syntax: vitec-if="expression".')
        if not valid_foreach_syntax:
            suggestions.append(
                'Fix vitec-foreach expressions to use valid syntax: vitec-foreach="item in collection".'
            )

        score = _score_from_checks(checks)
        return {
            "valid": all(check["passed"] for check in checks),
            "score": score,
            "checks": checks,
            "suggestions": suggestions,
            "forbidden_style_issues": forbidden_style_issues,
            "vitec_if_issues": vitec_if_issues,
            "vitec_foreach_issues": vitec_foreach_issues,
        }

    @mcp.tool()
    def check_stilark_compliance(html: str) -> dict[str, Any]:
        soup = BeautifulSoup(html or "", "html.parser")
        element_count = len(soup.find_all())
        stilark_referenced = _has_stilark_reference(soup)

        issues, elements_with_forbidden_styles = _extract_forbidden_style_entries(html)
        compliant = stilark_referenced and elements_with_forbidden_styles == 0
        score = _score_stilark(stilark_referenced, elements_with_forbidden_styles, element_count)

        if not stilark_referenced:
            issues.insert(
                0,
                {
                    "type": "missing_stilark_reference",
                    "message": 'Missing vitec-template="resource:Vitec Stilark" reference.',
                },
            )

        return {
            "compliant": compliant,
            "score": score,
            "stilark_referenced": stilark_referenced,
            "issues": issues,
            "element_count": element_count,
            "elements_with_forbidden_styles": elements_with_forbidden_styles,
        }
