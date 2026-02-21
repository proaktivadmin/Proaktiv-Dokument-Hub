"""
Template Comparison Service — structural HTML diff for Vitec template change analysis.

Compares stored template HTML against updated Vitec source using BeautifulSoup
to identify structural, content, and logic changes at the DOM level.
"""

import hashlib
import logging
import re
from uuid import UUID

from bs4 import BeautifulSoup, Tag

from app.schemas.template_comparison import (
    ChangeClassification,
    ComparisonResult,
    Conflict,
    StructuralChange,
)

logger = logging.getLogger(__name__)

NO_TOUCH_PATTERNS = [
    "Skjøte",
    "Pantedokument",
    "Hjemmelserklæring",
    "Hjemmelsoverføring",
    "konsesjonsfrihet",
    "konsesjon",
    "Tvangssalg",
    "pantefrafall",
    "Seksjoneringsbegjæring",
    "Grunnboksutskrift",
    "Konsesjonserklæring",
]

MERGE_FIELD_RE = re.compile(r"\[\[(\*?)([^\]]+)\]\]")
VITEC_IF_RE = re.compile(r'vitec-if="([^"]*)"')
VITEC_FOREACH_RE = re.compile(r'vitec-foreach="([^"]*)"')


def _is_no_touch(title: str) -> bool:
    title_lower = title.lower()
    return any(p.lower() in title_lower for p in NO_TOUCH_PATTERNS)


def _compute_hash(html: str) -> str:
    normalized = re.sub(r"\s+", " ", html).strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _truncate(text: str, max_len: int = 300) -> str:
    if len(text) <= max_len:
        return text
    return text[:max_len] + "…"


def _element_path(tag: Tag) -> str:
    """Build a CSS-like path for a DOM element."""
    parts: list[str] = []
    current: Tag | None = tag
    while current and isinstance(current, Tag):
        name = current.name
        if current.get("id"):
            parts.append(f"{name}#{current['id']}")
            break
        css_classes = current.get("class")
        if css_classes and isinstance(css_classes, list):
            parts.append(f"{name}.{'.'.join(css_classes[:2])}")
        else:
            siblings = [s for s in (current.previous_siblings if current.parent else []) if isinstance(s, Tag) and s.name == name]
            idx = len(siblings) + 1
            parts.append(f"{name}:nth({idx})" if idx > 1 else name)
        current = current.parent if current.parent and isinstance(current.parent, Tag) else None
    parts.reverse()
    return " > ".join(parts) if parts else "root"


def _get_text_blocks(soup: BeautifulSoup) -> dict[str, str]:
    """Extract text blocks keyed by approximate element path."""
    blocks: dict[str, str] = {}
    for tag in soup.find_all(["p", "td", "th", "li", "span", "div", "h1", "h2", "h3", "h4", "h5", "h6"]):
        text = tag.get_text(strip=True)
        if text and len(text) > 2:
            path = _element_path(tag)
            blocks[path] = text
    return blocks


def _get_merge_fields(html: str) -> set[str]:
    return {m.group(0) for m in MERGE_FIELD_RE.finditer(html)}


def _get_vitec_conditions(html: str) -> set[str]:
    return {m.group(1) for m in VITEC_IF_RE.finditer(html)}


def _get_vitec_loops(html: str) -> set[str]:
    return {m.group(1) for m in VITEC_FOREACH_RE.finditer(html)}


def _get_tag_structure(soup: BeautifulSoup) -> list[str]:
    """Get a list of tag names in document order for structural comparison."""
    return [tag.name for tag in soup.find_all(True)]


def _get_style_blocks(soup: BeautifulSoup) -> list[str]:
    return [style.get_text() for style in soup.find_all("style")]


def _get_attributes_map(soup: BeautifulSoup) -> dict[str, dict[str, str]]:
    """Get a map of element_path -> attributes for elements with vitec-* attrs or id/class."""
    result: dict[str, dict[str, str]] = {}
    for tag in soup.find_all(True):
        attrs = dict(tag.attrs)
        has_vitec = any(k.startswith("vitec-") for k in attrs)
        if has_vitec or tag.get("id") or tag.get("style"):
            path = _element_path(tag)
            serialized = {}
            for k, v in attrs.items():
                if isinstance(v, list):
                    serialized[k] = " ".join(v)
                else:
                    serialized[k] = str(v)
            result[path] = serialized
    return result


class TemplateComparisonService:
    """Performs structural HTML comparison for Vitec template change analysis."""

    async def compare(
        self,
        stored_html: str,
        updated_html: str,
        template_id: UUID | None = None,
        template_title: str | None = None,
        vitec_source_hash: str | None = None,
    ) -> ComparisonResult:
        """Compare stored template against updated Vitec source."""
        stored_hash = _compute_hash(stored_html)
        updated_hash = _compute_hash(updated_html)

        if stored_hash == updated_hash:
            return ComparisonResult(
                changes=[],
                classification=ChangeClassification(total=0),
                conflicts=[],
                stored_hash=stored_hash,
                updated_hash=updated_hash,
                hashes_match=True,
            )

        stored_soup = BeautifulSoup(stored_html, "html.parser")
        updated_soup = BeautifulSoup(updated_html, "html.parser")

        changes = self._structural_diff(stored_soup, updated_soup, stored_html, updated_html)
        classification = self._classify_changes(changes)
        conflicts = self._detect_conflicts(stored_html, vitec_source_hash, changes)

        return ComparisonResult(
            changes=changes,
            classification=classification,
            conflicts=conflicts,
            stored_hash=stored_hash,
            updated_hash=updated_hash,
            hashes_match=False,
        )

    def _structural_diff(
        self,
        stored_soup: BeautifulSoup,
        updated_soup: BeautifulSoup,
        stored_html: str,
        updated_html: str,
    ) -> list[StructuralChange]:
        """Identify structural changes between two parsed HTML trees."""
        changes: list[StructuralChange] = []

        # 1. Compare merge fields
        stored_fields = _get_merge_fields(stored_html)
        updated_fields = _get_merge_fields(updated_html)
        for field in sorted(stored_fields - updated_fields):
            changes.append(StructuralChange(
                category="merge_fields",
                element_path="merge_field",
                description=f"Flettekode fjernet: {field}",
                before=field,
                after=None,
            ))
        for field in sorted(updated_fields - stored_fields):
            changes.append(StructuralChange(
                category="merge_fields",
                element_path="merge_field",
                description=f"Ny flettekode lagt til: {field}",
                before=None,
                after=field,
            ))

        # 2. Compare vitec-if conditions
        stored_conds = _get_vitec_conditions(stored_html)
        updated_conds = _get_vitec_conditions(updated_html)
        for cond in sorted(stored_conds - updated_conds):
            changes.append(StructuralChange(
                category="logic",
                element_path="vitec-if",
                description=f"Betingelse fjernet: {_truncate(cond, 120)}",
                before=cond,
                after=None,
            ))
        for cond in sorted(updated_conds - stored_conds):
            changes.append(StructuralChange(
                category="logic",
                element_path="vitec-if",
                description=f"Ny betingelse lagt til: {_truncate(cond, 120)}",
                before=None,
                after=cond,
            ))

        # 3. Compare vitec-foreach loops
        stored_loops = _get_vitec_loops(stored_html)
        updated_loops = _get_vitec_loops(updated_html)
        for loop in sorted(stored_loops - updated_loops):
            changes.append(StructuralChange(
                category="logic",
                element_path="vitec-foreach",
                description=f"Løkke fjernet: {_truncate(loop, 120)}",
                before=loop,
                after=None,
            ))
        for loop in sorted(updated_loops - stored_loops):
            changes.append(StructuralChange(
                category="logic",
                element_path="vitec-foreach",
                description=f"Ny løkke lagt til: {_truncate(loop, 120)}",
                before=None,
                after=loop,
            ))

        # 4. Compare tag structure
        stored_tags = _get_tag_structure(stored_soup)
        updated_tags = _get_tag_structure(updated_soup)
        if stored_tags != updated_tags:
            stored_counts: dict[str, int] = {}
            updated_counts: dict[str, int] = {}
            for t in stored_tags:
                stored_counts[t] = stored_counts.get(t, 0) + 1
            for t in updated_tags:
                updated_counts[t] = updated_counts.get(t, 0) + 1

            all_tag_names = set(stored_counts.keys()) | set(updated_counts.keys())
            for tag_name in sorted(all_tag_names):
                old_count = stored_counts.get(tag_name, 0)
                new_count = updated_counts.get(tag_name, 0)
                if old_count != new_count:
                    diff = new_count - old_count
                    verb = "lagt til" if diff > 0 else "fjernet"
                    changes.append(StructuralChange(
                        category="structural",
                        element_path=f"<{tag_name}>",
                        description=f"{abs(diff)} <{tag_name}>-element(er) {verb}",
                        before=f"{old_count} stk",
                        after=f"{new_count} stk",
                    ))

        # 5. Compare text content blocks
        stored_texts = _get_text_blocks(stored_soup)
        updated_texts = _get_text_blocks(updated_soup)
        shared_paths = set(stored_texts.keys()) & set(updated_texts.keys())
        for path in sorted(shared_paths):
            old_text = stored_texts[path]
            new_text = updated_texts[path]
            if old_text != new_text:
                if MERGE_FIELD_RE.search(old_text) or MERGE_FIELD_RE.search(new_text):
                    continue
                changes.append(StructuralChange(
                    category="content",
                    element_path=path,
                    description=f"Tekstinnhold endret i {path.split(' > ')[-1] if ' > ' in path else path}",
                    before=_truncate(old_text),
                    after=_truncate(new_text),
                ))

        # 6. Compare style blocks
        stored_styles = _get_style_blocks(stored_soup)
        updated_styles = _get_style_blocks(updated_soup)
        if stored_styles != updated_styles:
            changes.append(StructuralChange(
                category="cosmetic",
                element_path="<style>",
                description=f"CSS-stilblokker endret ({len(stored_styles)} → {len(updated_styles)} blokk(er))",
                before=_truncate("\n".join(stored_styles)),
                after=_truncate("\n".join(updated_styles)),
            ))

        # 7. Compare vitec-specific attributes on key elements
        stored_attrs = _get_attributes_map(stored_soup)
        updated_attrs = _get_attributes_map(updated_soup)
        shared_attr_paths = set(stored_attrs.keys()) & set(updated_attrs.keys())
        for path in sorted(shared_attr_paths):
            old_a = stored_attrs[path]
            new_a = updated_attrs[path]
            if old_a != new_a:
                changed_keys = [k for k in set(old_a.keys()) | set(new_a.keys()) if old_a.get(k) != new_a.get(k)]
                vitec_keys = [k for k in changed_keys if k.startswith("vitec-")]
                style_keys = [k for k in changed_keys if k == "style"]

                if vitec_keys:
                    for k in vitec_keys:
                        changes.append(StructuralChange(
                            category="logic" if k in ("vitec-if", "vitec-foreach") else "structural",
                            element_path=path,
                            description=f"Attributt «{k}» endret på {path.split(' > ')[-1]}",
                            before=old_a.get(k),
                            after=new_a.get(k),
                        ))
                elif style_keys:
                    changes.append(StructuralChange(
                        category="cosmetic",
                        element_path=path,
                        description=f"Inline-stil endret på {path.split(' > ')[-1]}",
                        before=_truncate(old_a.get("style", "")),
                        after=_truncate(new_a.get("style", "")),
                    ))

        # 8. Detect whitespace-only differences if no other changes found
        if not changes:
            stored_norm = re.sub(r"\s+", " ", stored_html).strip()
            updated_norm = re.sub(r"\s+", " ", updated_html).strip()
            if stored_norm != updated_norm:
                changes.append(StructuralChange(
                    category="cosmetic",
                    element_path="document",
                    description="Endringer i mellomrom/formatering (ingen strukturelle endringer)",
                    before=None,
                    after=None,
                ))

        return changes

    def _classify_changes(self, changes: list[StructuralChange]) -> ChangeClassification:
        """Categorize changes by type and produce aggregate counts."""
        counts: dict[str, int] = {
            "cosmetic": 0,
            "structural": 0,
            "content": 0,
            "merge_fields": 0,
            "logic": 0,
            "breaking": 0,
        }
        for change in changes:
            counts[change.category] = counts.get(change.category, 0) + 1

        return ChangeClassification(
            cosmetic=counts["cosmetic"],
            structural=counts["structural"],
            content=counts["content"],
            merge_fields=counts["merge_fields"],
            logic=counts["logic"],
            breaking=counts["breaking"],
            total=len(changes),
        )

    def _detect_conflicts(
        self,
        stored_html: str,
        original_hash: str | None,
        changes: list[StructuralChange],
    ) -> list[Conflict]:
        """Identify where Vitec's changes overlap with our customizations.

        Without three-way comparison data (original Vitec source unavailable),
        we flag potential conflicts based on heuristics:
        - Breaking changes always produce high-severity conflicts
        - Content changes in sections with merge fields suggest customized areas
        """
        conflicts: list[Conflict] = []

        breaking_changes = [c for c in changes if c.category == "breaking"]
        for bc in breaking_changes:
            conflicts.append(Conflict(
                section=bc.element_path,
                our_change="Mulig tilpasning i denne seksjonen",
                vitec_change=bc.description,
                severity="high",
            ))

        content_changes = [c for c in changes if c.category == "content"]
        logic_changes = [c for c in changes if c.category == "logic"]

        if content_changes and logic_changes:
            conflicts.append(Conflict(
                section="Flere seksjoner",
                our_change="Innholdsendringer kan overlappe med tilpasninger",
                vitec_change=f"{len(content_changes)} innholdsendring(er) og {len(logic_changes)} logikkendring(er)",
                severity="medium",
            ))

        return conflicts


_comparison_service: TemplateComparisonService | None = None


def get_comparison_service() -> TemplateComparisonService:
    global _comparison_service
    if _comparison_service is None:
        _comparison_service = TemplateComparisonService()
    return _comparison_service
