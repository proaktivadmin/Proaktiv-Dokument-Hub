# Logic Mapping Output Format

The Logic Mapper subagent must produce a file matching this format.
Save to: `scripts/_analysis/{template_name}/logic.md`

---

## Example Output

```markdown
# Logic Mapping: [Template Name]

## Source
- **File:** [path to source document]
- **References used:** vitec-html-ruleset/03-conditional-logic.md, 10-property-conditionals.md, VITEC-IF-DEEP-ANALYSIS.md

## Summary
- **vitec-if conditions:** [count]
- **vitec-foreach loops:** [count]
- **Checkbox groups:** [count]
- **Mutually exclusive sections:** [count]
- **"Mangler data" guards:** [count]

## Conditional Branches

### Property-Type Conditionals

| # | Element | Condition | Scope | Notes |
|---|---------|-----------|-------|-------|
| 1 | div | Model.eiendom.eieform == "Selveier" | Section 1A (entire) | Show selveier variant |
| 2 | div | Model.eiendom.eieform == "Borettslag" | Section 1B (entire) | Show borettslag variant |
| 3 | span | Model.eiendom.grunntype == "Bolig" | Inline text swap | "Boligen" vs "Fritidsboligen" |
| ... | ... | ... | ... | ... |

### Optional Field Guards

| # | Element | Condition | Content When True | Content When False |
|---|---------|-----------|-------------------|-------------------|
| 1 | p | Model.selger.fullmektig.navn != "" && != "Mangler data" | Fullmektig paragraph | (hidden) |
| 2 | span | Model.kontrakt.tinglysningsdato != "" && != "Mangler data" | Date display | (hidden) |
| ... | ... | ... | ... | ... |

### Alternative Sections (Mutually Exclusive)

| Group | Option | Condition | Location |
|-------|--------|-----------|----------|
| Payment model | Alternativ 1 | (to be determined from source context) | Section 4 |
| Payment model | Alternativ 2 | (opposite of above) | Section 4 |
| ... | ... | ... | ... |

Note: If the exact condition expression cannot be determined from source + references,
write the intent clearly and flag for builder review.

## Checkbox State Logic

### Data-Driven Checkboxes

| # | Location | Checked Condition | Unchecked Condition | Label Text |
|---|----------|-------------------|---------------------|------------|
| 1 | Section 4 | Model.field == "value1" | Model.field != "value1" | Alternativ 1: Forskudd |
| 2 | Section 4 | Model.field == "value2" | Model.field != "value2" | Alternativ 2: Hele kjøpesummen |
| ... | ... | ... | ... | ... |

### Broker-Interactive Checkboxes

| # | Location | Label Text | Notes |
|---|----------|------------|-------|
| 1 | Section 15 | Ja | User confirmation |
| 2 | Section 15 | Nei | User confirmation |
| ... | ... | ... | ... |

## Loop Specifications

| # | Collection | Variable | Guard Condition | Fallback Text | Used In |
|---|-----------|----------|-----------------|---------------|---------|
| 1 | Model.selgere | selger | Model.selgere.Count > 0 | [Mangler selger] | Section 1, Signature |
| 2 | Model.kjopere | kjoper | Model.kjopere.Count > 0 | [Mangler kjøper] | Section 1, Signature |
| 3 | Model.kontrakt.omkostninger | kostnad | Model.kontrakt.omkostninger.Count > 0 | [Ingen omkostninger registrert] | Section 2 |
| ... | ... | ... | ... | ... | ... |

## "Mangler Data" Guard List

Fields that should be hidden (not just empty) when Vitec returns "Mangler data":

| Field Path | Guard Expression | Element to Hide |
|-----------|------------------|-----------------|
| kontrakt.tinglysningsdato | != "" && != "Mangler data" | Date paragraph |
| selger.fullmektig.navn | != "" && != "Mangler data" | Fullmektig section |
| kjoper.fullmektig.navn | != "" && != "Mangler data" | Fullmektig section |
| ... | ... | ... |

## Condition Expression Syntax Reference

All conditions in this document use the MODEL notation. When implementing in HTML:
- `"` in values → `&quot;`
- `>` in comparisons → `&gt;`
- `<` in comparisons → `&lt;`
- `&&` (AND) → `&amp;&amp;`
- Norwegian chars in string values → `\xF8` (ø), `\xE5` (å), `\xE6` (æ)

## Unresolved Logic (NEED REVIEW)

| # | Location | Intent | Why Unresolved |
|---|----------|--------|----------------|
| 1 | Section 4 | Payment model toggle | Source doesn't specify which field drives the choice |
| ... | ... | ... | ... |

If no unresolved items: "All logic fully mapped."
```

## Rules for the Logic Mapper

1. Do NOT map field paths — that is the Field Mapper's job
2. Do NOT analyze document structure — that is the Structure Analyzer's job
3. Determine the EXACT vitec-if condition expression for every conditional
4. Use VITEC-IF-DEEP-ANALYSIS.md patterns as reference for expression syntax
5. Identify ALL checkbox groups and determine what drives their state
6. Specify guard + fallback for every vitec-foreach loop
7. Flag ALL optional fields that need "Mangler data" double-guards
8. If a condition expression cannot be determined, describe the intent and flag for review
9. Write conditions in Model notation — the builder handles HTML escaping
