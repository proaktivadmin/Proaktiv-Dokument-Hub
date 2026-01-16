---
name: Puncheveiledning Production Ready
overview: Ferdigstille to HTML-filer (puncheguide_bruktbolig.html og puncheguide_naering_prosjekt.html) som selvstendige, distribuerbare applikasjoner med Base64-innbyggede bilder, hybrid visning (interaktiv/print), design-opprydding, og A4-optimalisert print.
todos:
  - id: read_images
    content: Les alle bilder fra images-mappen og konverter til Base64. Mappe bildene til HTML-referanser basert på innhold/rekkefølge.
    status: completed
  - id: read_logos
    content: Les logo-filene (Lilje_Hel_WarmGrey.1.0.png og logo.svg) fra Utkast-mappen og konverter til Base64.
    status: completed
  - id: fix_bruktbolig
    content: "Oppdater puncheguide_bruktbolig.html: fjern bracket-divs, fiks watermark, erstatte alle bildereferanser med Base64, oppdater logoer."
    status: completed
  - id: fix_naering
    content: "Oppdater puncheguide_naering_prosjekt.html: fjern bracket-divs, fiks watermark, oppdater logoer, legg til accordion-system hvis mangler."
    status: completed
  - id: fix_print_styles
    content: "Forbedre print-stiler: legg til break-inside: avoid på alle relevante elementer, optimaliser A4 page breaks, test i Edge."
    status: completed
  - id: verify_standalone
    content: "Verifiser at begge filer fungerer helt standalone: test offline, test print preview, sjekk at ingen eksterne ressurser mangler."
    status: completed
---

# Proaktiv Puncheveiledninger - Full Production Plan

## Oversikt

Ferdigstille to HTML-filer slik at de fungerer som selvstendige, distribuerbare applikasjoner uten eksterne avhengigheter.

## Filstruktur

- **Input:** 
- `C:\Users\Adrian\Documents\.cursor\puncheveiledning\puncheguide_bruktbolig.html`
- `C:\Users\Adrian\Documents\.cursor\puncheveiledning\puncheguide_naering_prosjekt.html`
- `C:\Users\Adrian\Documents\.cursor\puncheveiledning\images\` (30 PNG-filer)
- `C:\Users\Adrian\Documents\.cursor\puncheveiledning\Utkast\Lilje_Hel_WarmGrey.1.0.png`
- `C:\Users\Adrian\Documents\.cursor\puncheveiledning\Utkast\logo.svg`

## Oppgaver

### 1. Bilde-integrasjon (Base64)

**Mål:** Alle bilder skal være inline Base64, ingen eksterne filer.**For puncheguide_bruktbolig.html:**

- Mappe 30 bilder fra `images/` til referanser i HTML (manuell mapping basert på innhold/rekkefølge)
- Konverter alle bilder til Base64 og erstatte `src="images/..."` med `src="data:image/png;base64,..."`
- Inkluder logoer:
- `Lilje_Hel_WarmGrey.1.0.png` → watermark-lily
- `logo.svg` → cover-logo

**For puncheguide_naering_prosjekt.html:**

- Samme logoer som bruktbolig
- Screenshot-placeholders kan forblir som placeholders eller fjernes (avhengig av om bilder skal legges til)

**Teknisk:**

- Bruk Python script eller direkte konvertering
- Behold bildenes opprinnelige kvalitet
- Alle referanser i både `.img-container img` og `.appendix-img` skal oppdateres

### 2. Hybrid Visning (Interaktiv vs. Print)

**Skjermvisning:**

- Accordion-funksjonalitet eksisterer allerede (`toggleImg()` funksjon)
- Bekreft at alle `.img-toggle` knapper fungerer
- Skjul `.img-container` som standard (max-height: 0)
- Vis kun når `.open` class er aktiv

**Print-visning:**

- Skjul alle `.img-toggle` knapper (`display: none !important`)
- Skjul alle `.img-container` (inline bilder)
- Vis `.img-ref` referanser i stedet (f.eks. "[Bilde 1]")
- Vis hele `.print-only` appendix-seksjonen med alle bilder i full størrelse
- Hver bilde i appendix skal ha figurnummer og beskrivelse

**CSS-endringer:**

```css
@media screen {
    .print-only { display: none; }
    .img-ref { display: none; }
}

@media print {
    .img-toggle, .img-container { display: none !important; }
    .img-ref { display: inline-block !important; }
    .print-only { display: block !important; }
}
```

### 3. Design-opprydding (Forside)

**Fjern bracket-divs:**

- Slett alle `<div class="bracket bracket-tl"></div>` og `<div class="bracket bracket-br"></div>` elementer
- Fjern relatert CSS (`.bracket`, `.bracket-tl`, `.bracket-br`)

**Fiks lilje-logo watermark:**

- Fjern `filter: brightness(0.75) sepia(0.05);` fra `.watermark-lily`
- Juster kun `opacity` (f.eks. `opacity: 0.08-0.12`) for subtil blending
- Sørg for at watermark ikke skaper grå boks ved utskrift
- Test at den blender naturlig inn i hvit bakgrunn

**CSS-endring:**

```css
.watermark-lily {
    /* Fjern filter, kun opacity */
    opacity: 0.10;
    /* Ingen filter-egenskaper */
}
```

### 4. Sideskift og A4-kontroll

**A4-størrelse:**

- `.page` skal være `210mm × 297mm` (A4)
- `overflow: hidden` for skjermvisning
- `page-break-after: always;` på hver `.page` (unntatt siste)

**Page-break-regler:**

- `break-inside: avoid;` på:
- `.step` (hele steg skal være sammenhengende)
- `.info-box` (ikke del info-boxer på to sider)
- `.img-container` (bilder skal ikke kuttes)
- `.appendix-item` (hele appendix-elementer skal være sammenhengende)
- `.critical-box` (viktige bokser skal være sammenhengende)

**Print-optimalisering:**

- `@page { size: A4; margin: 0; }`
- `.page:last-child { page-break-after: auto; }`
- Test i Microsoft Edge print preview

**CSS-tillegg:**

```css
@page {
    size: A4;
    margin: 0;
}

.step, .info-box, .img-container, .appendix-item, .critical-box {
    break-inside: avoid;
    page-break-inside: avoid;
}
```

### 5. Output-format

**Krav:**

- Hele koden for hver fil i én fil
- All CSS inline i `<head>`
- All JavaScript inline i `<body>` (eller `<head>`)
- Ingen eksterne lenker (unntatt Google Fonts - kan også embeddes hvis nødvendig)
- Filene skal fungere offline og kunne sendes på e-post

**Validering:**

- Test at alle bilder vises korrekt
- Test accordion-funksjonalitet
- Test print preview i Edge
- Verifiser at ingen eksterne ressurser trengs

## Implementasjonsrekkefølge

1. **Forberedelse:** Les alle bilder og konverter til Base64
2. **puncheguide_bruktbolig.html:**

- Fjern bracket-divs
- Fiks watermark CSS
- Erstatt alle bildereferanser med Base64
- Oppdater logoer
- Test accordion og print

3. **puncheguide_naering_prosjekt.html:**

- Fjern bracket-divs
- Fiks watermark CSS
- Legg til accordion-system (hvis ikke allerede)
- Oppdater logoer
- Legg til print appendix (hvis nødvendig)

4. **Finalisering:**

- Verifiser A4 page breaks
- Test i Edge print preview
- Sjekk at alle bilder er inline

## Notater