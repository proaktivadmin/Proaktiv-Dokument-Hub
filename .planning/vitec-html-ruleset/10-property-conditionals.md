## 10. Property Type Conditional Patterns

These patterns use `vitec-if` to branch content based on property type, ownership form, and assignment type. They are the foundation for template merging work.

### Ownership form (eieform) branching

```html
<span vitec-if="Model.eiendom.eieform == &quot;Andel&quot;">andel i borettslag</span>
<span vitec-if="Model.eiendom.eieform != &quot;Andel&quot;">fast eiendom</span>
```

Known eieform values: `Andel`, `Eiet`, `Aksje`, `Obligasjon`, `Eierseksjon`.

**Evidence:** `vitec-reference.md` lines 868–869 (Sikring footer).

### Sale vs rental branching

```html
<span vitec-if="!Model.oppdrag.type.Contains(&quot;tleie&quot;)">Selger</span>
<span vitec-if="Model.oppdrag.type.Contains(&quot;tleie&quot;)">Utleier</span>
```

The string `"tleie"` (a substring of "Utleie") is used as the discriminator.

| Condition | Assignment type |
|-----------|----------------|
| Contains "tleie" | Rental (Utleie) |
| Does NOT contain "tleie" | Sale (Salg) |

**Evidence:** `vitec-reference.md` lines 735–746 (Kontrakt footer).

### Assignment category branching

```html
<span vitec-if="Model.oppdrag.hovedtype == &quot;Oppgj\xF8rsoppdrag&quot;">Ja</span>
<span vitec-if="Model.oppdrag.hovedtype != &quot;Oppgj\xF8rsoppdrag&quot;">Nei</span>
```

Note the `\xF8` escape for `ø`.

**Evidence:** Line 6418.

### Property base type branching

```html
<span vitec-if="Model.eiendom.grunntype == &quot;N\xE6ring&quot;">Ja</span>
<span vitec-if="Model.eiendom.grunntype != &quot;N\xE6ring&quot;">Nei</span>
```

Known grunntype values: `bolig`, `fritid`, `tomt`, `Næring` (note: `\xE6` escape needed for æ).

**Evidence:** Line 6408.

### Output channel branching

```html
<tr vitec-if="Model.dokumentoutput == &quot;pdf&quot;">
  <!-- PDF-specific content -->
</tr>
<tr vitec-if="Model.dokumentoutput == &quot;email&quot;">
  <!-- Email-specific content -->
</tr>
```

**Evidence:** Lines 6160–6167. The `dokumentoutput` field determines whether the template is being rendered for PDF (document creation) or email (send-as-email flow).

### Boolean property flags

```html
<span vitec-if="Model.oppdrag.vederlagtypeprovisjon == true">JA</span>
<span vitec-if="Model.oppdrag.vederlagtypeprovisjon == false">NEI</span>
```

Other boolean flags observed:
- `Model.oppdrag.vederlagtypetimepris`
- `Model.oppdrag.vederlagtypefastpris`
- `Model.oppdrag.boligselgerforsikringbestilt` (DB evidence: "Oppdragsavtale")
- `Model.oppdrag.erdetforkjopsfrist` (DB evidence: multiple)
- `Model.kjoper.erfirma` / `Model.selger.erfirma`
- `Model.kjoper.fullmektig.erfirma`
- `Model.megler2.erstudent`
- `Model.medhjelper.erstudent`
- `Model.eiendom.erprosjektmaster`
- `Model.kjoper.fullmektig_er_gruppe`
- `Model.pant.ertypefrivilligpant` (DB evidence: "Pantedokument (sikring)")
- `Model.pant.ertypelegalpant` (DB evidence: "Pantedokument (sikring)")
- `selger.ergift` — implicit boolean on loop variable (DB evidence: "Hjemmelserklæring")

**Evidence:** Lines 2482–2652 (fee type branching), 1649 (company flag), 952/991 (student flag).

### Razor `@{}` code blocks for dynamic CSS classes

Complex templates use Razor C# code blocks to compute CSS class values at render time. This is a server-side pattern distinct from `vitec-if`:

```html
@{
    var erGrunntypeBolig = "";
    var erGrunntypeFritid = "";
    var erGrunntypeNaering = "";
    var erGrunntypeTomt = "";
    if (Model.eiendom.grunntype == "Bolig") {
        erGrunntypeBolig = "active";
    }
    if (Model.eiendom.grunntype == "Fritid") {
        erGrunntypeFritid = "active";
    }
    // ... etc
}

<label class="btn @erGrunntypeBolig" contenteditable="false" data-toggle="button">
  <span class="checkbox svg-toggle"></span> Bolig
</label>
<label class="btn @erGrunntypeFritid" contenteditable="false" data-toggle="button">
  <span class="checkbox svg-toggle"></span> Fritid
</label>
```

When the Razor variable is `"active"`, the label gets `class="btn active"` which triggers the checked SVG toggle state. When empty, it stays as `class="btn "` (unchecked).

Known Razor class variables:

| Variable | Condition field | Templates |
|----------|----------------|-----------|
| `@erGrunntypeBolig` | `Model.eiendom.grunntype == "Bolig"` | "Hjemmelsoverføring" |
| `@erGrunntypeFritid` | `Model.eiendom.grunntype == "Fritid"` | "Hjemmelsoverføring" |
| `@erGrunntypeNaering` | `Model.eiendom.grunntype == "Næring"` | "Hjemmelsoverføring" |
| `@erGrunntypeTomt` | `Model.eiendom.grunntype == "Tomt"` | "Hjemmelsoverføring" |
| `@erTomtetypeEiertomt` | `Model.eiendom.tomtetype == "eiertomt"` | "Hjemmelserklæring", "Skjøte" |
| `@erTomtetypeFestetomt` | `Model.eiendom.tomtetype == "festetomt"` | "Hjemmelserklæring", "Skjøte" |
| `@erHovedtypeSalg` | `Model.eiendom.grunntype == "Salg"` | "Kundeopplysningsskjema kjøper/selger" |
| `@erHovedtypeProsjektsalg` | Prosjektsalg type | "Kundeopplysningsskjema" |
| `@erHovedtypeUtleie` | Utleie type | "Kundeopplysningsskjema" |
| `@erHovedtypeOppgjorsOppdrag` | Oppgjørsoppdrag type | "Kundeopplysningsskjema" |
| `@erHovedtypeVerdivurdering` | Verdivurdering type | "Kundeopplysningsskjema" |
| `@erSalg` / `@erKjop` / `@erUtleie` | Assignment type | "Oppdragsavtale" |
| `@erOppgjorsoppdrag` | Oppgjørsoppdrag type | "Oppdragsavtale" |
| `@erTvangssalg` / `@erIkkeTvangssalg` | Forced sale flag | Multiple |
| `@erIkkeOppgjorsOppdrag` | Not oppgjørsoppdrag | Multiple |
| `@erTypeGrunnBoligeiendom` | `Model.eiendom.typegrunn == "Boligeiendom"` | "Skjøte" (Kartverket code **B**) |
| `@erTypeGrunnFritidseiendom` | `Model.eiendom.typegrunn == "Fritidseiendom"` | "Skjøte" (Kartverket code **F**) |
| `@erTypeGrunnForretningKontor` | `Model.eiendom.typegrunn == "Forretning - kontor"` | "Skjøte" (Kartverket code **V**) |
| `@erTypeGrunnIndustriBergverk` | `Model.eiendom.typegrunn == "Industri - bergverk"` | "Skjøte" (Kartverket code **I**) |
| `@erTypeGrunnLandbrukFiske` | `Model.eiendom.typegrunn == "Landbruk - fiske"` | "Skjøte" (Kartverket code **L**) |
| `@erTypeGrunnOffentligVei` | `Model.eiendom.typegrunn == "Offentlig vei"` | "Skjøte" (Kartverket code **K**) |
| `@erTypeGrunnAnnet` | `Model.eiendom.typegrunn == "Annet"` | "Skjøte" (Kartverket code **A**) |
| `@erTypeBoligFrittliggendeEnebolig` | `Model.eiendom.typebolig == "Frittliggende enebolig"` | "Skjøte" (Kartverket code **FB**) |
| `@erTypeBoligTomannsbolig` | `Model.eiendom.typebolig == "Tomannsbolig"` | "Skjøte" (Kartverket code **TB**) |
| `@erTypeBoligRekkehusKjede` | `Model.eiendom.typebolig == "Rekkehus/Kjede"` | "Skjøte" (Kartverket code **RK**) |
| `@erTypeBoligBlokkleilighet` | `Model.eiendom.typebolig == "Blokkleilighet"` | "Skjøte" (Kartverket code **BL**) |
| `@erTypeBoligAnnet` | `Model.eiendom.typebolig == "Annet"` | "Skjøte" (Kartverket code **AN**) |

**(DB evidence: "Hjemmelsoverføring", "Hjemmelserklæring", "Kundeopplysningsskjema kjøper", "Kundeopplysningsskjema selger", "Oppdragsavtale", "Skjøte")**

### ID number type detection (personal vs. organization)

```html
<span vitec-if="kjoper.idnummer.ToString().Length == 11">
  <!-- Personal ID (fødselsnummer: 11 digits) -->
</span>
<span vitec-if="kjoper.idnummer.ToString().Length == 12">
  <!-- Organization number (12 digits with dash) -->
</span>
```

Uses `.ToString().Length` to distinguish between personal ID numbers (11 digits) and organization numbers (12 digits). Also used for `Model.selger.idnummer.ToString().Length`.

**(DB evidence: "Egenerklæring om konsesjonsfrihet", "Oppdragsavtale")**

### Count-based branching

```html
<em vitec-if="Model.selgere.Count == 0">Ingen registrert</em>
<table vitec-if="Model.selgere.Count &gt; 0">
  <!-- content -->
</table>
```

### String value branching

```html
<span vitec-if="Model.mottaker.visning.dato != &quot;Mangler data&quot;">
  [[mottaker.visning.dato]] [[mottaker.visning.tidsrom]]
</span>
<span vitec-if="Model.mottaker.visning.dato == &quot;Mangler data&quot;">
  Ingen visning registrert på mottakeren.
</span>
```

**Evidence:** Lines 2332–2333. The string `"Mangler data"` is Vitec's placeholder for missing data.

### Numeric comparison with negated greater-than

For "less than or equal" comparisons, Vitec uses negated `>`:

```html
<span vitec-if="!(Model.oppdrag.prosjektenhet.antallgarasjeplasser &gt; 4)">3 or fewer</span>
<span vitec-if="Model.oppdrag.prosjektenhet.antallgarasjeplasser &gt; 3">More than 3</span>
```

**Evidence:** Lines 6469–6470.

---
