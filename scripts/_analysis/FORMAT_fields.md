# Field Mapping Output Format

The Field Mapper subagent must produce a file matching this format.
Save to: `scripts/_analysis/{template_name}/fields.md`

---

## Example Output

```markdown
# Field Mapping: [Template Name]

## Source
- **File:** [path to source document]
- **Registry used:** .planning/field-registry.md

## Summary
- **Total placeholders found:** [count]
- **Mapped successfully:** [count]
- **Unmapped (need review):** [count]
- **Monetary (need $.UD):** [count]
- **Optional (need vitec-if guard):** [count]

## Field Mapping Table

| # | Source Text / Placeholder | Modern Path | $.UD | Guard | Notes |
|---|--------------------------|-------------|------|-------|-------|
| 1 | #oppdrag.nr¤ | [[oppdrag.nr]] | — | — | Always present |
| 2 | #kontrakt.kjopesum¤ | [[kontrakt.kjopesum]] | YES | — | Monetary |
| 3 | #eiendom.adresse¤ | [[eiendom.adresse]] | — | — | Always present |
| 4 | #kjoper.fullmektig.navn¤ | [[kjoper.fullmektig.navn]] | — | != "" | Optional field |
| 5 | (implied: seller party) | [[*selger.navnutenfullmektigogkontaktperson]] | — | foreach | Inside loop |
| ... | ... | ... | ... | ... | ... |

$.UD values: `YES` (wrap in $.UD()), `—` (not monetary)

Guard values:
- `—` — always present, no guard needed
- `!= ""` — optional, hide when empty
- `!= "Mangler data"` — optional, hide when "Mangler data"
- `!= "" && != "Mangler data"` — double guard
- `foreach` — inside a vitec-foreach loop, use [[*field]]

## Collections (vitec-foreach candidates)

| Collection Path | Loop Variable | Fields Inside | Guard |
|----------------|---------------|---------------|-------|
| Model.selgere | selger | navnutenfullmektigogkontaktperson, adresse, postnrogsted, kontaktperson, telefon, epost | Count > 0 |
| Model.kjopere | kjoper | navnutenfullmektigogkontaktperson, adresse, postnrogsted, kontaktperson, telefon, epost | Count > 0 |
| Model.kontrakt.omkostninger | kostnad | navn, belop | Count > 0 |
| ... | ... | ... | ... |

## Monetary Fields ($.UD required)

| Field Path | Context |
|-----------|---------|
| [[kontrakt.kjopesum]] | Purchase price |
| [[kontrakt.totaleomkostninger]] | Total costs |
| [[kontrakt.kjopesumogomkostn]] | Grand total |
| [[*kostnad.belop]] | Cost item amount (inside foreach) |
| [[eiendom.fellesutgifter]] | Common expenses |
| ... | ... |

## Unmapped Fields (NEED HUMAN REVIEW)

| # | Source Text | Context in Document | Attempted Match | Confidence |
|---|-----------|--------------------|-----------------|----|
| 1 | #some.unknown.field¤ | Section 7, after "Forsikring" | — | — |
| ... | ... | ... | ... | ... |

If no unmapped fields: "All fields mapped successfully."
```

## Rules for the Field Mapper

1. Do NOT determine vitec-if condition expressions — that is the Logic Mapper's job
2. Do NOT analyze document structure — that is the Structure Analyzer's job
3. Map EVERY placeholder/field found in the source to a modern [[path]]
4. Use field-registry.md as the primary lookup source
5. Flag ALL monetary fields for $.UD() wrapping
6. Flag ALL optional fields that need vitec-if guards
7. Identify ALL collection patterns that need vitec-foreach
8. If a field cannot be mapped, flag it clearly — do NOT guess
9. Inside foreach loops, all fields must use [[*variable.field]] syntax
