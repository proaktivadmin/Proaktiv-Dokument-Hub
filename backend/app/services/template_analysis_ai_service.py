"""
Template Analysis AI Service — LLM-powered interpretation of structural diffs.

Takes structural comparison output and produces plain-language Norwegian analysis
using a configurable LLM provider (Google Gemini preferred, OpenAI, Anthropic).
Falls back to structural-only results when no API key is available.
"""

import json
import logging
import os
from typing import Literal

from app.schemas.template_comparison import (
    AnalysisReport,
    ComparisonResult,
)
from app.services.template_comparison_service import _is_no_touch

logger = logging.getLogger(__name__)

LLMProvider = Literal["google", "openai", "anthropic", "none"]

SYSTEM_PROMPT = """Du er en ekspert på Vitec Next HTML-maler for norsk eiendomsmegling.

Du analyserer strukturelle endringer mellom en lagret malversjon og en oppdatert versjon fra Vitec.
Brukeren er en prosjekteier som ikke leser HTML-kode — du må forklare endringer i klartekst på norsk.

Kontekst:
- Vitec Next er et forvaltningssystem for eiendomsmeglere i Norge
- Maler bruker «flettekoder» med syntaks [[felt.navn]] for dynamiske data
- Betingelser: vitec-if="uttrykk", løkker: vitec-foreach="element in samling"
- Maler kan være tilpasset (våre endringer) eller systemstandarder fra Vitec

Svar alltid på norsk bokmål. Vær konkret og praktisk.
"""


def _detect_provider() -> tuple[LLMProvider, str | None]:
    """Detect the best available LLM provider from environment variables."""
    explicit = os.environ.get("COMPARISON_LLM_PROVIDER", "").lower().strip()
    if explicit == "none":
        return "none", None

    if explicit == "google" or (not explicit and os.environ.get("GOOGLE_API_KEY")):
        key = os.environ.get("GOOGLE_API_KEY")
        if key:
            return "google", key

    if explicit == "openai" or (not explicit and os.environ.get("OPENAI_API_KEY")):
        key = os.environ.get("OPENAI_API_KEY")
        if key:
            return "openai", key

    if explicit == "anthropic" or (not explicit and os.environ.get("ANTHROPIC_API_KEY")):
        key = os.environ.get("ANTHROPIC_API_KEY")
        if key:
            return "anthropic", key

    return "none", None


def _build_prompt(comparison: ComparisonResult, template_title: str, template_category: str | None = None) -> str:
    """Build the LLM prompt with structured change data."""
    lines: list[str] = []
    lines.append(f"## Mal: «{template_title}»")
    if template_category:
        lines.append(f"Kategori: {template_category}")
    lines.append("")
    lines.append(f"Totalt {comparison.classification.total} endring(er) oppdaget:")
    lines.append(f"- Kosmetisk: {comparison.classification.cosmetic}")
    lines.append(f"- Strukturell: {comparison.classification.structural}")
    lines.append(f"- Innhold: {comparison.classification.content}")
    lines.append(f"- Flettekoder: {comparison.classification.merge_fields}")
    lines.append(f"- Logikk: {comparison.classification.logic}")
    lines.append(f"- Kritisk: {comparison.classification.breaking}")
    lines.append("")

    lines.append("### Detaljerte endringer:")
    for i, change in enumerate(comparison.changes[:30], 1):
        lines.append(f"{i}. [{change.category}] {change.description}")
        if change.before:
            lines.append(f"   Før: {change.before[:150]}")
        if change.after:
            lines.append(f"   Etter: {change.after[:150]}")
    if len(comparison.changes) > 30:
        lines.append(f"... og {len(comparison.changes) - 30} endringer til.")
    lines.append("")

    if comparison.conflicts:
        lines.append("### Konflikter:")
        for c in comparison.conflicts:
            lines.append(f"- [{c.severity}] {c.section}: {c.vitec_change}")
    lines.append("")

    lines.append("""Gi en analyse med følgende struktur (bruk NØYAKTIG disse JSON-nøklene):
{
  "summary": "2-3 setninger som oppsummerer oppdateringen",
  "changes_by_category": {
    "kosmetisk": ["endring 1", "endring 2"],
    "strukturell": ["..."],
    "innhold": ["..."],
    "flettekoder": ["..."],
    "logikk": ["..."],
    "kritisk": ["..."]
  },
  "impact": "Hva endringene betyr for vår tilpassede versjon",
  "recommendation": "ADOPT | IGNORE | PARTIAL_MERGE | REVIEW_REQUIRED",
  "suggested_actions": ["handling 1", "handling 2"]
}

Velg anbefaling basert på:
- ADOPT: Vitecs versjon bør overtas (ingen konflikter, nyttige endringer)
- IGNORE: Endringene er irrelevante eller rent kosmetiske
- PARTIAL_MERGE: Noen endringer bør tas, andre beholdes
- REVIEW_REQUIRED: For komplekst for automatisk anbefaling""")

    return "\n".join(lines)


def _build_fallback_report(comparison: ComparisonResult, template_title: str) -> AnalysisReport:
    """Build an analysis report without AI — structural diff only."""
    is_no_touch = _is_no_touch(template_title)

    if comparison.classification.total == 0:
        summary = f"«{template_title}» er identisk med Vitec-versjonen. Ingen endringer oppdaget."
        recommendation: Literal["ADOPT", "IGNORE", "PARTIAL_MERGE", "REVIEW_REQUIRED"] = "IGNORE"
    elif is_no_touch:
        summary = (
            f"«{template_title}» er et myndighetsskjema (no-touch). "
            f"Vitec har {comparison.classification.total} endring(er). "
            "Anbefaler å overta Vitecs versjon uten endringer."
        )
        recommendation = "ADOPT"
    elif comparison.classification.breaking > 0:
        summary = (
            f"Vitec har gjort {comparison.classification.total} endring(er) i «{template_title}», "
            f"inkludert {comparison.classification.breaking} kritisk(e) endring(er). Manuell gjennomgang anbefalt."
        )
        recommendation = "REVIEW_REQUIRED"
    elif comparison.classification.total <= 3 and comparison.classification.content == 0:
        summary = (
            f"Vitec har gjort {comparison.classification.total} mindre endring(er) i «{template_title}». "
            "Endringene er kosmetiske eller strukturelle uten innholdspåvirkning."
        )
        recommendation = "ADOPT"
    else:
        summary = (
            f"Vitec har oppdatert «{template_title}» med {comparison.classification.total} endring(er). "
            "Gjennomgå endringene for å vurdere om de bør overtas."
        )
        recommendation = "REVIEW_REQUIRED"

    changes_by_category: dict[str, list[str]] = {}
    category_labels = {
        "cosmetic": "kosmetisk",
        "structural": "strukturell",
        "content": "innhold",
        "merge_fields": "flettekoder",
        "logic": "logikk",
        "breaking": "kritisk",
    }
    for change in comparison.changes:
        label = category_labels.get(change.category, change.category)
        if label not in changes_by_category:
            changes_by_category[label] = []
        changes_by_category[label].append(change.description)

    impact = (
        "AI-analyse er ikke tilgjengelig. Se detaljerte endringer ovenfor for manuell vurdering."
        if not is_no_touch
        else "Dette er et myndighetsskjema — overta alltid Vitecs versjon."
    )

    return AnalysisReport(
        summary=summary,
        changes_by_category=changes_by_category,
        impact=impact,
        conflicts=comparison.conflicts,
        recommendation=recommendation,
        suggested_actions=[],
        ai_powered=False,
        raw_comparison=comparison,
    )


async def _call_google(api_key: str, prompt: str) -> str:
    """Call Google Gemini API using the google-generativeai package."""
    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")

        response = await model.generate_content_async(
            [
                {"role": "user", "parts": [{"text": SYSTEM_PROMPT + "\n\n" + prompt}]},
            ],
            generation_config=genai.GenerationConfig(
                temperature=0.2,
                response_mime_type="application/json",
            ),
        )

        text = response.text
        logger.info("Gemini response: %d chars, usage: %s", len(text), getattr(response, "usage_metadata", "N/A"))
        return text

    except ImportError:
        logger.warning("google-generativeai package not installed, falling back")
        raise
    except Exception:
        logger.exception("Google Gemini API call failed")
        raise


async def _call_openai(api_key: str, prompt: str) -> str:
    """Call OpenAI API via httpx (no openai package required)."""
    import httpx

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": "gpt-4o",
                "temperature": 0.2,
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
            },
        )
        resp.raise_for_status()
        data = resp.json()
        text = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        logger.info(
            "OpenAI response: %d chars, tokens: prompt=%s completion=%s",
            len(text),
            usage.get("prompt_tokens"),
            usage.get("completion_tokens"),
        )
        return text


async def _call_anthropic(api_key: str, prompt: str) -> str:
    """Call Anthropic API via httpx."""
    import httpx

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 2048,
                "temperature": 0.2,
                "system": SYSTEM_PROMPT,
                "messages": [{"role": "user", "content": prompt}],
            },
        )
        resp.raise_for_status()
        data = resp.json()
        text = data["content"][0]["text"]
        usage = data.get("usage", {})
        logger.info(
            "Anthropic response: %d chars, tokens: input=%s output=%s",
            len(text),
            usage.get("input_tokens"),
            usage.get("output_tokens"),
        )
        return text


def _parse_llm_response(raw: str, comparison: ComparisonResult) -> AnalysisReport:
    """Parse the JSON response from the LLM into an AnalysisReport."""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[-1]
        if cleaned.endswith("```"):
            cleaned = cleaned.rsplit("```", 1)[0]
        data = json.loads(cleaned.strip())

    valid_recommendations = {"ADOPT", "IGNORE", "PARTIAL_MERGE", "REVIEW_REQUIRED"}
    rec = data.get("recommendation", "REVIEW_REQUIRED").upper()
    if rec not in valid_recommendations:
        rec = "REVIEW_REQUIRED"

    return AnalysisReport(
        summary=data.get("summary", ""),
        changes_by_category=data.get("changes_by_category", {}),
        impact=data.get("impact", ""),
        conflicts=comparison.conflicts,
        recommendation=rec,  # type: ignore[arg-type]
        suggested_actions=data.get("suggested_actions", []),
        ai_powered=True,
        raw_comparison=comparison,
    )


class TemplateAnalysisAIService:
    """Generates human-readable analysis from structural comparison using an LLM."""

    async def analyze(
        self,
        comparison: ComparisonResult,
        template_title: str,
        template_category: str | None = None,
    ) -> AnalysisReport:
        """Generate human-readable analysis from structural comparison."""
        if _is_no_touch(template_title):
            report = _build_fallback_report(comparison, template_title)
            report.recommendation = "ADOPT"
            report.impact = "Dette er et myndighetsskjema som aldri skal tilpasses. Overta alltid Vitecs versjon."
            return report

        if comparison.hashes_match:
            return _build_fallback_report(comparison, template_title)

        provider, api_key = _detect_provider()
        if provider == "none" or not api_key:
            logger.info("No LLM provider configured — returning structural-only analysis")
            return _build_fallback_report(comparison, template_title)

        prompt = _build_prompt(comparison, template_title, template_category)

        try:
            if provider == "google":
                raw = await _call_google(api_key, prompt)
            elif provider == "openai":
                raw = await _call_openai(api_key, prompt)
            elif provider == "anthropic":
                raw = await _call_anthropic(api_key, prompt)
            else:
                return _build_fallback_report(comparison, template_title)

            report = _parse_llm_response(raw, comparison)

            if _is_no_touch(template_title):
                report.recommendation = "ADOPT"

            return report

        except Exception:
            logger.exception("LLM analysis failed for %s, falling back to structural-only", template_title)
            return _build_fallback_report(comparison, template_title)


_ai_service: TemplateAnalysisAIService | None = None


def get_ai_analysis_service() -> TemplateAnalysisAIService:
    global _ai_service
    if _ai_service is None:
        _ai_service = TemplateAnalysisAIService()
    return _ai_service
