## 5. Merge Field Reference

### Standard merge field syntax

```
[[field.path]]
```

Double square brackets delimit a merge field. The field path uses dot notation to traverse the data model.

### Required fields (asterisk)

```
[[*field.path]]
```

The asterisk prefix marks a field as required. If the field has no value at render time, the rendered output will contain a visible placeholder or error marker instead of blank space. Used inside foreach loops to ensure loop items have the expected data.

**Evidence:** `[[*ansatt.navn]]` (line 504), `[[*selger.navn]]` (line 4844), `[[*pant.prioritet]]` (line 6484).

### Merge field paths

Fields follow a hierarchical path structure. Top-level objects include:
- `meglerkontor` — Office information
- `avsender` — Sender (logged-in user)
- `mottaker` — Recipient
- `eiendom` — Property
- `oppdrag` — Assignment/listing
- `selger` / `selgere` — Seller(s)
- `kjoper` / `kjopere` — Buyer(s)
- `kontrakt` — Contract
- `ansvarligmegler`, `megler1`, `megler2`, `medhjelper`, `salgsmegler` — Agents
- `oppgjorsansvarlig` — Settlement officer
- `borettslag` — Housing cooperative
- `pant` — Mortgage/lien
- `bud` / `budgivere` — Bid(s)
- `visning` / `visninger` — Showing(s)
- `dagsdato`, `dagensdato`, `dato`, `p`, `P` — Date and page numbers
- `timer` — Time tracking (`timer.paalopt.salg`, `.visning`, `.bud`, `.kontrakt`, `.oppgjor`)
- `tvangssalgrefnr` — Forced sale reference number
- `skjema` — Kartverket form data (`skjema.innsender.navn`, `.adresse`, `.postnr`, `.poststed`, `.orgnr`; `skjema.referansenr`)
- `sameie` — Co-ownership data (`sameie.sameiebrok`)
- `komplettmatrikkelutvidet` — Full cadastral reference (expanded format)
- `esignering` — E-signing (`esignering.dokumentnavn`, `.melding`, `.lenke`)

Full field listing: see `.cursor/vitec-reference.md` sections "Flettekoder (Merge Fields) — Komplett Oversikt".

### Additional merge field paths from database templates

| Path | Description | Evidence |
|------|-------------|----------|
| `oppgjorselger.sumdebet` | Settlement debit total | (DB: "Oppgjørsoppstilling Selger") |
| `oppgjorselger.sumkredit` | Settlement credit total | (DB: "Oppgjørsoppstilling Selger") |
| `oppgjorselger.summva` | Settlement VAT total | (DB: "Oppgjørsoppstilling Selger") |
| `oppgjorselger.saldo` | Settlement balance | (DB: "Oppgjørsoppstilling Selger") |
| `kontrakt.formidling.nr` | Transaction number | (DB: "Kjøpekontrakt FORBRUKER") |
| `kontrakt.dato` | Contract signing date | Kjøpekontrakt Aksje |
| `kontrakt.kjopesum` | Purchase price (numeric, format via `$.UD()`) | Kjøpekontrakt Aksje |
| `kontrakt.overtagelse.dato` | Agreed takeover date | Kjøpekontrakt Aksje |
| `oppdrag.nr` | Assignment/case number ("Vår ref:" in letters) | Grunnlag brevmal, Kjøpekontrakt Aksje |
| `eiendom.prosjektnavn` | Project name | (DB: "Oppgjørsoppstilling Selger") |
| `eiendom.alfanavn` | Unit alpha name | (DB: "Oppgjørsoppstilling Selger") |
| `eiendom.leilighetsnr` | Apartment number | (DB: "Oppgjørsoppstilling Selger") |
| `timer.paalopt.*` | Elapsed hours by phase (salg, visning, bud, kontrakt, oppgjor) | (DB: "Oppgjørsoppstilling Selger") |
| `avsender.navn` | Sender's full name | System signatures |
| `avsender.tittel` | Sender's job title | System signatures |
| `avsender.mobiltlf` | Sender's mobile phone | System signatures |
| `avsender.epost` | Sender's email | System signatures |
| `avsender.meglerkontor.navn` | Office name (legal) | E-post signatur |
| `avsender.meglerkontor.markedsforingsnavn` | Office marketing name (display name) | SMS-signatur, Avsender PDF |
| `avsender.meglerkontor.besoksadresse` | Office visit address | E-post signatur |
| `avsender.meglerkontor.postnr` | Office postal code | E-post signatur |
| `avsender.meglerkontor.poststed` | Office postal city | E-post signatur |
| `meglerkontor.kjedenavn` | Chain/franchise name | Vitec Topptekst |
| `meglerkontor.firmalogourl` | Company logo URL | Vitec Topptekst |
| `meglerkontor.juridisknavn` | Legal company name | Vitec Bunntekst |
| `meglerkontor.besokspostnr` | Visit address postal code | Vitec Bunntekst |
| `meglerkontor.besokspoststed` | Visit address postal city | Vitec Bunntekst |
| `mottaker.navn` | Recipient name | Mottaker resource |
| `mottaker.adresse` | Recipient street address | Mottaker resource |
| `mottaker.postnr` | Recipient postal code | Mottaker resource |
| `mottaker.poststed` | Recipient postal city | Mottaker resource |
| `dagensdato` | Today's date (at generation time) | Mottaker resource |
| `skjema.innsender.navn` | Form submitter name | "Skjøte" (Kartverket form header) |
| `skjema.innsender.adresse` | Form submitter address | "Skjøte" (Kartverket form header) |
| `skjema.innsender.postnr` | Form submitter postal code | "Skjøte" (Kartverket form header) |
| `skjema.innsender.poststed` | Form submitter postal city | "Skjøte" (Kartverket form header) |
| `skjema.innsender.orgnr` | Form submitter org/personal ID | "Skjøte" (Kartverket form header) |
| `skjema.referansenr` | Form reference number | "Skjøte" (Kartverket form header) |
| `eiendom.kommunenr` | Municipality number | "Skjøte" |
| `eiendom.kommunenavn` | Municipality name | "Skjøte" |
| `eiendom.typegrunn` | Ground use classification (7 Kartverket categories) | "Skjøte" |
| `eiendom.typebolig` | Housing type classification (5 Kartverket categories) | "Skjøte" |
| `kontrakt.avgiftsgrunnlag` | Tax basis / sales value | "Skjøte" |
| `kontrakt.kjopesumibokstaver` | Purchase price in words | "Skjøte" |
| `sameie.sameiebrok` | Co-ownership fraction | "Skjøte" |
| `selger.selgersektefelle.navnutenfullmektig` | Seller's spouse name (without fullmektig) | "Skjøte" |
| `oppdrag.prosjekt.saerskilteavtaler` | Special agreements (tinglysing) | "Skjøte" |
| `oppdrag.prosjekt.andreavtaler` | Other agreements (non-tinglysing) | "Skjøte" |
| `selger.ledetekst_fdato_orgnr` | Dynamic label: "Fødselsdato" or "Org.nr." depending on party type | Grunnlag brevmal |
| `selger.fdato_orgnr` | Combined birth date / org number value | Grunnlag brevmal |
| `kjoper.ledetekst_fdato_orgnr` | Dynamic label: "Fødselsdato" or "Org.nr." depending on party type | Grunnlag brevmal |
| `kjoper.fdato_orgnr` | Combined birth date / org number value | Grunnlag brevmal |
| `selger.firmanavn` | Seller company/firm name (vs `selger.navn` for person) | Kjøpekontrakt Næring |
| `selger.hovedkontakt.navn` | Seller's main contact person name | Kjøpekontrakt Næring |
| `selger.hovedgatenavnognr` | Seller's head office street address | Kjøpekontrakt Næring |
| `selger.hovedpostnr` | Seller's head office postal code | Kjøpekontrakt Næring |
| `selger.hovedpoststed` | Seller's head office postal city | Kjøpekontrakt Næring |
| `selger.hovedkontonummer` | Seller's main bank account number | Kjøpekontrakt Næring |
| `kjoper.firmanavn` | Buyer company/firm name | Kjøpekontrakt Næring |
| `kjoper.hovedkontakt.navn` | Buyer's main contact person name | Kjøpekontrakt Næring |
| `kjoper.hovedgatenavnognr` | Buyer's head office street address | Kjøpekontrakt Næring |
| `kjoper.hovedpostnr` | Buyer's head office postal code | Kjøpekontrakt Næring |
| `kjoper.hovedpoststed` | Buyer's head office postal city | Kjøpekontrakt Næring |
| `operativmegler.navn` | Operating broker's name | Kjøpekontrakt Næring |
| `operativmegler.epost` | Operating broker's email | Kjøpekontrakt Næring |
| `kontrakt.klientkonto` | Client escrow account number | Kjøpekontrakt Næring |
| `pant.navn` | Mortgage holder / bank name (foreach loop) | Kjøpekontrakt Næring |
| `pant.panthaverorgnr` | Mortgage holder org number (foreach loop) | Kjøpekontrakt Næring |
| `aksjeselskap.navn` | Company name (in share sale transactions) | Kjøpekontrakt Aksje |
| `aksjeselskap.orgnr` | Company org number | Kjøpekontrakt Aksje |
| `aksjeselskap.aksjenr` | Share numbers (e.g., "1-100") | Kjøpekontrakt Aksje |
| `hjemmelshaver.navn` | Title holder name (when different from seller) | Kjøpekontrakt Aksje |
| `hjemmelshaver.fdato_orgnr` | Title holder birth date / org number | Kjøpekontrakt Aksje |
| `selger.hovedepost` | Seller's main email address | Kjøpekontrakt Aksje |
| `selger.idnummer` | Seller's ID number (birth date or org number) | Kjøpekontrakt Aksje |
| `kjoper.hovedepost` | Buyer's main email address | Kjøpekontrakt Aksje |
| `komplettmatrikkelutvidet` | Full cadastral reference (expanded format) | Kjøpekontrakt Aksje |
| `komplettmatrikkel` | Short cadastral reference (compact format, used in Bilag) | Kjøpekontrakt Aksje |
| `selger.gatenavnognr` | Seller's street address (in foreach loop) | Grunnlag brevmal, Kjøpekontrakt Aksje |
| `selger.postnr` | Seller's postal code (in foreach loop) | Grunnlag brevmal, Kjøpekontrakt Aksje |
| `selger.poststed` | Seller's postal city (in foreach loop) | Grunnlag brevmal, Kjøpekontrakt Aksje |
| `selger.tlf` | Seller's phone number (in foreach loop) | Grunnlag brevmal, Kjøpekontrakt Aksje |
| `selger.emailadresse` | Seller's email address (in foreach loop) | Grunnlag brevmal, Kjøpekontrakt Aksje |
| `kjoper.gatenavnognr` | Buyer's street address (in foreach loop) | Grunnlag brevmal, Kjøpekontrakt Aksje |
| `kjoper.postnr` | Buyer's postal code (in foreach loop) | Grunnlag brevmal, Kjøpekontrakt Aksje |
| `kjoper.poststed` | Buyer's postal city (in foreach loop) | Grunnlag brevmal, Kjøpekontrakt Aksje |
| `kjoper.tlf` | Buyer's phone number (in foreach loop) | Grunnlag brevmal, Kjøpekontrakt Aksje |
| `kjoper.emailadresse` | Buyer's email address (in foreach loop) | Grunnlag brevmal, Kjøpekontrakt Aksje |

### Merge fields inside foreach loops

Inside a `vitec-foreach` block, merge fields use the loop variable instead of `Model`:

```html
<tbody vitec-foreach="selger in Model.selgere">
  <tr>
    <td>[[*selger.navn]]</td>
    <td>[[*selger.fodselsnr]]</td>
  </tr>
</tbody>
```

### Merge fields in attributes vs text nodes

**In text nodes (standard):**
```html
<td>[[meglerkontor.navn]]</td>
```

**In `src` attributes (images):**

Images use the `@Model.` Razor syntax instead of `[[...]]`:
```html
<img src="@Model.ansvarligmegler.hovedbilde" />
<img src="@Model.meglerkontor.firmalogourl" />
```

**Evidence:** Lines 6243–6292. All image `src` values use `@Model.` prefix, not `[[...]]`.

There is also a `[[...]]` variant for image URLs in some templates:
```html
<img src="[[meglerkontor.firmalogourl]]" style="max-height:1.5cm; max-width:6cm" />
```

**Evidence:** Header template in `vitec-reference.md` line 949. Both syntaxes appear to work.

**In vitec-if expressions:**
```html
vitec-if="Model.eiendom.eieform == &quot;Andel&quot;"
```

Note: vitec-if uses `Model.` prefix (no `@`), no `[[...]]` brackets.

### Function wrappers

| Function | Purpose | Syntax | Example |
|----------|---------|--------|---------|
| `$.UD()` | Format number without decimals | `$.UD([[field]])` | `$.UD([[eiendom.pris]])` → "5 000 000" |
| `$.BOKST()` | Number to Norwegian words | `$.BOKST([[field]])` | `$.BOKST([[kontraktsposisjon.totalpris]])` |
| `$.CALC()` | Mathematical calculation | `$.CALC(expression)` | `$.CALC([[oppdrag.timeprisinklmva]]/1,25)` |
| `$.CALC(UD:...)` | Calculation without decimals | `$.CALC(UD:expression)` | `$.CALC(UD:1 + 2 - 3)` |
| `$.CALCHOURS()` | Sum hours (HH:MM format) | `$.CALCHOURS(expr)` | `$.CALCHOURS([[timer.paalopt.salg]]+[[timer.paalopt.visning]]+[[timer.paalopt.bud]]+[[timer.paalopt.kontrakt]]+[[timer.paalopt.oppgjor]])` (DB evidence: "Oppgjørsoppstilling Selger") |
| `$.CALCBOKST()` | Calculation result as words | `$.CALCBOKST(expr)` | `$.CALCBOKST([[eiendom.pris]] + [[eiendom.fellesgjeld]])` |
| `$.SKALER()` | Scale image | `$.SKALER(@Model.url, h=px)` | `$.SKALER(@Model.eiendom.hovedbilde, h=100)` |

**Evidence:** Lines 6302–6367 document all functions with live examples.

**CALC operators:**
- Addition: `+`
- Subtraction: `-`
- Multiplication: `*` or `x`
- Division: `/`
- Parentheses: `(` `)`
- Decimal separator: comma `,` or period `.`

**CALC operands:** Expressions can mix merge fields and Razor method calls:
- Merge fields: `[[kontrakt.kjopesumogomkostn]]`
- Custom method calls: `@GetPosteringsVerdiForBoligkjoperforsikring()`
- Example: `$.CALC(UD:[[kontrakt.kjopesumogomkostn]]-@GetPosteringsVerdiForBoligkjoperforsikring())` — subtracts the boligkjøperforsikring amount from total, outputs with tusenskilletegn formatting.

**(Evidence: custom Proaktiv Kjøpekontrakt Bruktbolig)**

### Page numbering

| Field | Output |
|-------|--------|
| `[[p]]` | Current page number |
| `[[P]]` | Total page count |
| `[[dagensdato]]` | Today's date |

**Evidence:** Footer templates in `vitec-reference.md` lines 806–807; Alle-flettekoder line 284 uses `[[dagensdato]]` (note: slightly different from `[[dagsdato]]` in reference docs).

### Inline Razor expressions

Some templates use Razor syntax (`@Model.property`) directly in text nodes:

```html
<td>kr @Model.oppgjorkjoper.saldo.Remove(0,1)</td>
```

This is used for inline string manipulation (e.g., removing a minus sign). **This is not the same as `[[...]]` syntax** — Razor expressions are processed server-side before merge field substitution.

**Evidence:** Line 6306.

---
