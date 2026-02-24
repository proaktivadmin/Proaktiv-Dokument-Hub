# Knowledge Base Changelog

Reverse-chronological log of every change to the Vitec Template Builder knowledge base.
Covers: LESSONS.md, PATTERNS.md, SKILL.md, `validate_vitec_template.py`, `post_process_template.py`.

**Rule:** Any agent that modifies LESSONS.md, PATTERNS.md, SKILL.md, the validator, or the
post-processor MUST append a dated entry to this file describing what changed and why.

---

## [2026-02-24] Transcript mining: 24 undocumented lessons extracted

**Files changed:** LESSONS.md
**Trigger:** Systematic audit of 3 agent transcripts (1,859 KB total) from Feb 21-23 build sessions

**Changes:**
- Added 24 new lessons across 8 categories (including 1 new category):
  - **E4:** Word HTM exports use Windows-1252 encoding (not UTF-8)
  - **E5:** CSS attribute selectors use `\00f8` unicode escapes (distinct from vitec-if `\xF8`)
  - **E6:** Lambda `=>` must be HTML-encoded as `=&gt;` in vitec attributes
  - **CB7:** Checkbox count parity tracking between Word source and output
  - **S15:** Only use standard Vitec CSS classes — no custom class names
  - **S16:** vitec-foreach valid on `<div>`, not just `<tbody>`
  - **S17:** Three insert field CSS variants (insert-table, insert-textbox, insert-textarea)
  - **S18:** `data-choice` attribute for floating choice labels via CSS `::after`
  - **S19:** `@functions` C# blocks live in separate support templates
  - **S20:** Combined vitec-if + vitec-foreach valid on same element
  - **S21:** System templates use custom CSS IDs for scoping
  - **S22:** Multiple resource template spans can coexist
  - **MF9:** Loop variable fields omit `Model.` prefix inside foreach
  - **MF10:** "Mangler data" used for branching to alternative content
  - **MF11:** `Model.dokumentoutput` discriminates PDF vs email rendering
  - **MF12:** Contact field separators need compound vitec-if checking both sides
  - **VIF1:** Implicit boolean — no `== true` required
  - **VIF2:** `.ToString().Length` valid for ID type detection
  - **VIF3:** Chained LINQ `.Where().Take()` valid in vitec-foreach
  - **VIF4:** vitec-if safe on `<p>`, `<article>`, `<li>`, `<ol>` elements
  - **VIF5:** Custom method calls — `@` prefix rules differ by context
  - **VIF6:** `$.CALC()` supports mixed merge field + method operands
  - **CF4:** Word "q" characters are checkbox placeholders
  - **V3:** Validator check count is 35 static + N dynamic per foreach
  - **PP4:** Pipeline reference docs must be validated against golden standards
  - **PP5:** Builder agents must verify source file identity
  - **PP6:** Headers/footers assigned via admin UI, not template HTML
  - **PP7:** Kartverket protected templates — 4-tier classification, never modify core forms
- New category **VIF (vitec-if Syntax)** created for expression-level edge cases
- Updated "How to Use" section to reference VIF category

**Impact:** Covers loop variable scoping (MF9 — previously caused silent bugs), LINQ chaining patterns (VIF3/VIF5), Kartverket protection rules (PP7), Word conversion pipeline specifics (E4, CF4, CB7), and admin deployment workflow (PP6). Total knowledge base now at 52 lessons across 8 categories.

---

## [2026-02-24] Library mining: 234 templates analyzed, knowledge base updated

**Files changed:** LESSONS.md, PATTERNS.md
**Trigger:** Template Library Mining script analyzed 234/249 templates from `templates/master/`
**Changes:**
- CORRECTED MF6: `!` negation DOES work (5 production templates use it); `not` keyword NOT used (0 templates)
- CONFIRMED SVG encoding: 74/75 templates use `;utf8,<svg>` inline format
- Added S13: H2 margin has two valid patterns (30px 0 0 -20px recommended)
- Added S14: H1 font size varies by template type (14pt default for contracts)
- Added MF7: Most common field paths quick reference
- Added MF8: Vitec template resources catalog
- Added empirical confirmation notes to S2, S8, S9, S10, MF1, MF4, V2
**Impact:** Knowledge base now backed by empirical data from 234 templates instead of 3-4 manually analyzed references.

---

## [2026-02-24] Chromium insert-table fix codified as production standard

**Files changed:** PATTERNS.md, LESSONS.md (S8-S12), SKILL.md, validate_vitec_template.py, post_process_template.py
**Trigger:** Production comparison of Kjøpekontrakt Bruktbolig + FORBRUKER templates

**Changes:**
- Core CSS updated to match production (article padding `20px` not `26px`, h2 margin `-20px` not `-26px`, counter `::before` simplified to `content:` only — no `display`/`width`)
- Insert-table Chromium fix documented as S10 (`.insert-table { display: inline-table }` with unscoped selectors)
- `.borders` table class added to core CSS (S11)
- `.liste` rule reduced to single last-child separator rule (S12)
- Validator gained 3 new checks: article padding 20px, h2 margin -20px, insert-table CSS present
- Post-processor auto-fixes `26px` → `20px` (S8), warns on missing insert-table CSS (S10)
- 5 new lessons added: S8 (article padding), S9 (counter ::before), S10 (insert-table), S11 (.borders), S12 (.liste)

**Impact:** All future T3+ builds use correct production values. Validator and post-processor enforce the new standards automatically.

---

## [2026-02-24] Source of truth hierarchy established

**Files changed:** LESSONS.md (header), PATTERNS.md (header), SKILL.md, CLAUDE.md, process-template-requests.md, SUBAGENT-PROMPTS.md, PRODUCTION-TEMPLATE-PIPELINE.md
**Trigger:** User clarification that the old vitec-html-ruleset-FULL.md was based on 133 Proaktiv-customized DB templates, not the Vitec standard

**Changes:**
- Added Source of Truth Hierarchy to LESSONS.md: working reference templates > master library > Vitec Stilark > builder KB > old ruleset
- Updated all pipeline docs to mark old ruleset as supplementary only
- Added "Template Source of Truth" section to CLAUDE.md
- Demoted vitec-html-ruleset references across orchestrator and subagent prompts
- Confirmed `proaktiv-theme` class is NOT used by 0/249 official templates
- Added explicit "Do NOT use" warning for `.planning/vitec-html-ruleset-FULL.md` in SKILL.md

**Impact:** All agents now follow correct authority chain; old ruleset no longer treated as primary reference.

---

## [2026-02-24] V2 Analysis and VITEC-IF Deep Analysis findings integrated

**Files changed:** LESSONS.md (S5-S7, CB4-CB6, MF4-MF6), validate_vitec_template.py
**Trigger:** V2 Analysis Report and VITEC-IF Deep Analysis review

**Changes:**
- Added 9 new lessons:
  - S5: CSS selector specificity — scoped vs unscoped rules with exact reference scoping pattern
  - S6: Two separate style blocks (template CSS + checkbox CSS)
  - S7: roles-table — only the hide-last-row rule (Stilark handles base styles)
  - CB4: SVG viewBox must be 512x512 (not 0 0 16 16)
  - CB5: Checkbox CSS must have all 12 reset properties
  - CB6: Radio button SVG pattern (circular SVG, `<input type="radio">` after span)
  - MF4: "Mangler data" sentinel checks (Vitec sets empty fields to this string)
  - MF5: Entity-level vs property-level field access patterns
  - MF6: vitec-if negation patterns (`not` keyword, not `!` prefix)
- Validator updated with checks for new patterns

**Impact:** Builder agent now handles checkbox specifics, CSS scoping, and conditional logic edge cases correctly.

---

## [2026-02-23] One-shot perfection stack created

**Files changed:** LESSONS.md (created, 18 lessons), PATTERNS.md (created, 14 patterns), SKILL.md (updated), post_process_template.py (created), validate_vitec_template.py (updated to 61 checks), process-template-requests.md (updated)
**Trigger:** User request to build optimal stack for one-shot template builds with zero flaws

**Changes:**
- Created LESSONS.md registry with 18 lessons across categories: Encoding (E1-E3), Checkboxes (CB1-CB3), Structure (S1-S4), Merge Fields (MF1-MF3), Content Fidelity (CF1-CF3), Validation (V1-V2), Pipeline Process (PP1-PP3)
- Created PATTERNS.md library with 14 copy-pasteable code blocks (template shell, CSS blocks, checkboxes, party loops, safe fallbacks, article sections, costs tables, signature blocks, conditional patterns, entity encoding reference, hjemmelshaver fallback)
- Created post_process_template.py — auto-fixes entity encoding, proaktiv-theme removal; warns on checkboxes, monetary fields, foreach guards, missing table wrapper, wrong title level
- Enhanced validator from 58 to 61 checks
- Updated orchestrator (process-template-requests.md) to mandate reading LESSONS.md and PATTERNS.md before builds
- Added mandatory post-processor step to SKILL.md pipeline

**Impact:** Foundation of the self-improving builder pipeline. All future builds start from verified patterns and apply all known fixes automatically.
