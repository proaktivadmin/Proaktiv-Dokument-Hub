# Proaktiv Skin Specification

> **Created by:** Skin Architect Agent  
> **Date:** 2026-01-22  
> **Purpose:** Detailed specification for branding Vitec Bud Portal and Visning Portal with Proaktiv identity

---

## Table of Contents

1. [Brand Colors](#brand-colors)
2. [Fonts](#fonts)
3. [Color Mapping (DEFAULT → PROAKTIV)](#color-mapping-default--proaktiv)
4. [Bud Portal Configuration](#bud-portal-configuration)
5. [Visning Portal Configuration](#visning-portal-configuration)
6. [Email Template Changes](#email-template-changes)
7. [Note Template Changes](#note-template-changes)
8. [SMS Template Changes](#sms-template-changes)
9. [Merge Field Reference](#merge-field-reference)
10. [File Checklist](#file-checklist)
11. [Implementation Notes](#implementation-notes)

---

## Brand Colors

### Proaktiv Brand Palette (from vitec-theme.css)

| Token | Hex Value | CSS Variable | Usage |
|-------|-----------|--------------|-------|
| **Primary** | `#272630` | `--color-primary` | Main brand color (dark charcoal/navy) |
| **Primary Light** | `#3E3D4A` | `--color-primary-light` | Lighter primary for hover states |
| **Beige** | `#e9e7dc` | `--color-pg-beige` | Background color, cards |
| **Grønn (Green)** | `#a4b5a8` | `--color-pg-gronn` | Accent, success states |
| **Bronse (Bronze)** | `#bcab8a` | `--color-pg-bronse` | Accent gold, borders, highlights |
| **Text** | `#1d1d1d` | `--color-text` | Main text color |
| **Text Secondary** | `#5e6d82` | `--color-text-secondary` | Muted text |
| **Border** | `#D6D4CD` | `--border-color` | Light borders |
| **Border Dark** | `#272630` | `--border-color-dark` | Dark borders |

### Semantic Colors (Proaktiv Style)

| Semantic | Original DEFAULT | Proaktiv Replacement | Notes |
|----------|------------------|----------------------|-------|
| Success | `#338143` | `#a4b5a8` (gronn) | Softer, on-brand green |
| Danger | `#cd2026` | `#cd2026` | Keep red for critical errors |
| Warning | `#fdb81e` | `#bcab8a` (bronse) | Use bronze instead of yellow |
| Info | `#8ba6ca` | `#e9e7dc` (beige) | Muted info background |

---

## Fonts

### DEFAULT Skin Fonts
- **Import:** `https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700&display=swap`
- **Body:** `'Open Sans', sans-serif`

### Proaktiv Brand Fonts
- **Primary (Body):** `'Open Sans', sans-serif` ✅ Keep the same
- **Heading (Serif):** `'Playfair Display', serif` (for premium feel, optional)

### Font Import for PROAKTIV.scss
```scss
@import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700&display=swap');
```

**Note:** Keep Open Sans for portals to maintain readability. Playfair Display is optional for headings if the portal supports custom heading styles.

---

## Color Mapping (DEFAULT → PROAKTIV)

### SCSS Variable Replacements

| Original Variable | Original Value | New Value | Reason |
|-------------------|----------------|-----------|--------|
| `$primary` | `#205493` (blue) | `#272630` (charcoal) | Proaktiv primary brand color |
| `$secondary` | `#5b616b` (gray) | `#5e6d82` | Slightly adjusted gray |
| `$success` | `#338143` (green) | `#a4b5a8` | Proaktiv grønn |
| `$danger` | `#cd2026` (red) | `#cd2026` | Keep for errors |
| `$warning` | `#fdb81e` (yellow) | `#bcab8a` | Proaktiv bronse |
| `$info` | `#8ba6ca` (light blue) | `#e9e7dc` | Proaktiv beige |
| `$light` | `#f8f9fa` (lightgray) | `#f8f9fa` | Keep neutral |
| `$dark` | `#343a40` (darkgray) | `#272630` | Match primary |

### Derived Colors (Bud Portal)

| Selector | Original | New | Purpose |
|----------|----------|-----|---------|
| `body a` | `#205493` | `#272630` | Link color |
| `.bg-primary` | `#205493` | `#272630` | Primary backgrounds |
| `.btn-primary` | `#205493` | `#272630` | Primary buttons |
| `.circle.active` | `#205493` | `#272630` | Active step indicator |
| `.bid-done` | `#338143` | `#a4b5a8` | Completed bid status |
| `.bid-signing` | `#fdb81e` | `#bcab8a` | Signing in progress |
| `.bid-retrying` | `#8ba6ca` | `#e9e7dc` | Retry status |
| `.bid-failed` | `#cd2026` | `#cd2026` | Failed status (keep red) |

### Derived Colors (Visning Portal)

| Selector | Original | New | Purpose |
|----------|----------|-----|---------|
| `body` background | `lightgray` | `#f8f9fa` | Page background |
| `body a` | `#205493` | `#272630` | Link color |
| `.btn-primary` | `#205493` | `#272630` | Primary buttons |
| `.btn-primary:hover` | `#173f6f` | `#3E3D4A` | Button hover |
| `.btn-outline-primary` | `#205493` | `#272630` | Outline buttons |
| `.far` icons | `#007bff` | `#272630` | Icon color |

---

## Bud Portal Configuration

### DEFAULT.json Analysis

| Option | Current Value | New Value | Notes |
|--------|---------------|-----------|-------|
| `ShowConsentFinancing` | `true` | `false` | **DISABLED** - Global setting |
| `ShowConsentFollowup` | `true` | `true` | Verdivurdering - ENABLED |
| `ShowConsentNewsletter` | `true` | `false` | **HIDDEN** - Per requirements |
| `ShowConsentSearchProfile` | `true` | `true` | Keep enabled |
| `ConsentFinancingText` | "Finansiering" | "Finansiering" | (Hidden, text doesn't matter) |
| `ConsentFollowupText` | "Verdivurdering" | "Verdivurdering" | Keep |
| `ConsentNewsletterText` | "Nyhetsbrev" | "Nyhetsbrev" | (Hidden) |
| `ConsentSearchProfileText` | "Søkeprofil" | "Søkeprofil" | Keep |
| `ConsentFinancingHelp` | (long text) | (unchanged) | Hidden anyway |
| `ConsentFollowupHelp` | (long text) | "En av våre lokalkjente meglere kontakter deg for å avtale en tid for verdivurdering." | Proaktiv-styled |
| `ConsentNewsletterHelp` | "Nyhetsbrev" | "Nyhetsbrev" | (Hidden) |
| `ConsentSearchProfileHelp` | "Søkeprofil" | "Søkeprofil" | Keep |
| `SendConsentCofirmationSms` | `true` | `true` | Keep |
| `HelpIcon` | "help-icon" | "help-icon" | Keep |
| `ShowPersonvernButton` | `false` | `true` | **ENABLE** privacy link |
| `PersonvernButtonText` | "Hvorfor innhenter vi personopplysninger" | "Les om personvern" | Shorter |
| `PersonvernModalText` | (Vitec text) | See below | Update with Proaktiv link |
| `SendTipToBank` | `false` | `false` | Keep disabled |
| `SendTipToBankSource` | "Budportal" | "Budportal" | Keep |
| `UseGoogleTagManager` | `false` | `false` | **Placeholder only** |
| `GoogleTagManagerId` | "GTM-XXXX" | "GTM-XXXX" | Placeholder for future |
| `DownForMaintenance` | `false` | `false` | Keep |
| `DownForMaintenanceText` | (text) | (unchanged) | Keep |
| `UseSmsOrEmailValidation` | `true` | `true` | Keep |
| `DisableRadiobuttonsForProfessionalActor` | `false` | `false` | Keep |
| `UseStepInfo` | `false` | `false` | Keep |
| `StepInfoFillForm` | (text) | (unchanged) | Keep |
| `StepInfoSignBid` | (text) | (unchanged) | Keep |
| `StepInfoSendBidToBroker` | (text) | (unchanged) | Keep |
| `BidComplete` | "Budet er levert megler og journalført." | "Budet er levert megler og journalført." | Keep |
| `StepComplete` | "FULLFØRT!" | "FULLFØRT!" | Keep |
| `ServiceMessage` | "" | "" | Keep empty |
| `CookiesConsentBannerText` | (text) | (unchanged) | Keep |
| `CookiesConsentModalText` | (text) | (unchanged) | Keep |

### PersonvernModalText (Bud Portal)

**New value:**
```html
Eiendomsmeglerforetaket behandler personopplysninger som er nødvendige for å oppfylle avtalen med deg samt andre formål som selskapet har lov til å behandle opplysningene til i henhold til personvernforordningen. Les mer om hvordan vi behandler personopplysninger i <a rel="noopener" target="_blank" href="https://proaktiv.no/personvern">personvernerklæringen</a>.
```

---

## Visning Portal Configuration

### DEFAULT.json Analysis

| Option | Current Value | New Value | Notes |
|--------|---------------|-----------|-------|
| `showNewsletterBox` | `true` | `false` | **HIDDEN** - Per requirements |
| `showFinanceBox` | `true` | `false` | **DISABLED** - Global (Voss override in backend) |
| `showSellingOwnProperty` | `true` | `true` | Verdivurdering - ENABLED |
| `AutoTipToBank` | `false` | `false` | Keep disabled |
| `BankTipSourceViewingRegistration` | "" | "" | Keep empty |
| `BankTipSourceSalesDocument` | "" | "" | Keep empty |
| `propertyDescriptionText` | (text) | (unchanged) | Keep |
| `consentFinancingText` | "Jeg ønsker tilbud om finansiering" | (hidden, unchanged) | Hidden |
| `consentFollowupText` | "Jeg ønsker verdivurdering av min bolig" | "Jeg ønsker verdivurdering av min bolig" | Keep |
| `consentNewsletterText` | "Jeg ønsker å abonnere på nyhetsbrev" | (hidden) | Hidden |
| `consentBidInfoText` | "Jeg ønsker bli informert om bud på eiendommen" | "Jeg ønsker bli informert om bud på eiendommen" | **ENABLED** - Budvarsel |
| `consentFinancingHelp` | (text) | (hidden, unchanged) | Hidden |
| `consentFollowupHelp` | (text) | "En eiendomsmegler vil kontakte deg og avtale tid for verdivurdering." | Keep |
| `consentNewsletterHelp` | (text) | (hidden) | Hidden |
| `consentBidInfoHelp` | (text) | "Du vil bli registrert som interessent og varslet om bud frem til eiendommen er solgt." | Keep |
| `consentFinanceHelpButtonText` | "" | "" | Keep |
| `consentFollowHelpButtonText` | "" | "" | Keep |
| `consentNewsletterHelpButtonText` | "" | "" | Keep |
| `consentBidInfoHelpButtonText` | "" | "" | Keep |
| `SendConsentCofirmationSms` | `false` | `false` | Keep |
| `SendRegistrationCofirmationSms` | `true` | `true` | Keep |
| `SendRegistrationCofirmationEmail` | `true` | `true` | Keep |
| `AnnouncementEnabled` | `false` | `false` | Keep |
| `AnnouncementText` | "" | "" | Keep |
| `helpIcon` | "help-icon" | "help-icon" | Keep |
| `forceAcceptGdpr` | `false` | `false` | Keep |
| `showPersonvernButton` | `true` | `true` | Keep enabled |
| `personvernButtonText` | (HTML with icon) | `<span class="link-text">Les om personvern</span> <i aria-hidden="true" class='far fa-question-circle'></i>` | Simplified |
| `personvernModalText` | (Vitec text) | See below | Update with Proaktiv content |
| `consentWhyButtonText` | "" | "" | Keep |
| `consentWhyInfoText` | "" | "" | Keep |
| `VisningsPameldinNotifyBroker` | `["mainBroker"]` | `["mainBroker"]` | Keep |
| `VisningsPameldinNotifyEmails` | `[]` | `[]` | Keep |
| `SalgsoppgavenedlastetNotifyBroker` | `["mainBroker"]` | `["mainBroker"]` | Keep |
| `SalgsoppgavenedlastetNotifyEmails` | `[]` | `[]` | Keep |
| `useGoogleTagManager` | `false` | `false` | **Placeholder only** |
| `googleTagManagerId` | "GTM-XXXX" | "GTM-XXXX" | Placeholder |
| `DownForMaintenance` | `false` | `false` | Keep |
| `DownForMaintenanceText` | (HTML) | (unchanged) | Keep |
| `SendTipToBankProductId` | "0" | "0" | Keep |
| `CookiesConsentBannerText` | (text) | (unchanged) | Keep |
| `CookiesConsentModalText` | (text) | (unchanged) | Keep |

### personvernModalText (Visning Portal)

**New value:**
```html
<h2>Dine personopplysninger</h2><p>Hensikten med denne registreringen er å tilby deg relevant og ønsket informasjon fra Proaktiv Eiendomsmegling.</p><p>Vi plikter å oppbevare dine opplysninger på en forsvarlig måte og følge gjeldende lover og forskrifter om vern av personopplysninger.</p><p>Les mer i vår <a rel="noopener" target="_blank" href="https://proaktiv.no/personvern">personvernerklæring</a>.</p><p><strong>Er du allerede kunde?</strong><br />Har du nye kontaktopplysninger eller ønsker å endre valg? Benytt skjemaet for å registrere deg på visning, men informer også megler slik at dine opplysninger blir registrert korrekt.</p>
```

---

## Email Template Changes

### Summary of Changes Required

All email templates need:
1. **Remove "Mvh Vitec"** → Replace with broker name only
2. **Font family**: Change from Calibri to Open Sans (consistent with portal)
3. **No other content changes** (merge fields and conditionals stay the same)

### Template: `email_notifyinterestedparty_propertydescription.txt`

**Purpose:** Sent to interested party with property description link

**Changes:**
| Line | Original | New |
|------|----------|-----|
| 1 | `font-family: Calibri, Helvetica, sans-serif` | `font-family: 'Open Sans', Helvetica, sans-serif` |
| 7 | `<div>Mvh </div>` | `<div>Med vennlig hilsen,</div>` |

**Full new content:**
```html
<div style='font-family: "Open Sans", Helvetica, sans-serif'>
	<p>Hei, </p>

	<p>Takk for din interesse på [[oppdrag.adresse.adresse]].</p>
	<p><span><a href="[[oppdrag.salgsoppgavelink]]">Last ned salgsoppgaven</a></span>.</p>

	<div>Med vennlig hilsen,</div>
	<div>[[oppdrag.saksbehandler.navn]]</div>

	<span vitec-if="Model.oppdrag.saksbehandler.hartitel == true">
		<div>[[oppdrag.saksbehandler.titel]]</div>
	</span>
		
	<div>Telefon: [[oppdrag.saksbehandler.telefon]]</div>
</div>
```

### Template: `email_notifyinterestedparty_registrationconfirmation.txt`

**Purpose:** Registration confirmation to interested party

**Changes:**
| Line | Original | New |
|------|----------|-----|
| 1 | `font-family: Calibri, Helvetica, sans-serif` | `font-family: 'Open Sans', Helvetica, sans-serif` |
| 16 | `<span>Mvh, <br /></span>` | `<span>Med vennlig hilsen,<br /></span>` |

### Template: `email_notifyrealtor_newviewingparticipant.txt`

**Purpose:** Notify realtor of new viewing participant

**Changes:**
| Line | Original | New |
|------|----------|-----|
| 1 | `font-family: Calibri, Helvetica, sans-serif` | `font-family: 'Open Sans', Helvetica, sans-serif` |
| 57-58 | `<div>Mvh</div><div>Vitec</div>` | `<div>Med vennlig hilsen,</div><div>Proaktiv Eiendomsmegling</div>` |

### Template: `email_notifyrealtor_salgsoppgaverequested.txt`

**Purpose:** Notify realtor when sales document is requested

**Changes:**
| Line | Original | New |
|------|----------|-----|
| 1 | `font-family: Calibri, Helvetica, sans-serif` | `font-family: 'Open Sans', Helvetica, sans-serif` |
| 43-44 | `<div>Mvh</div><div>Vitec</div>` | `<div>Med vennlig hilsen,</div><div>Proaktiv Eiendomsmegling</div>` |

---

## Note Template Changes

### Template: `note_newviewingparticipant.txt`

**Purpose:** Internal note for new viewing participant

**Changes:** None required - this is an internal note without signatures.

### Template: `note_salgsoppgaverequested.txt`

**Purpose:** Internal note for sales document request

**Changes:** None required - this is an internal note without signatures.

---

## SMS Template Changes

### Template: `sms_notifyinterestedparty_registrationconfirmation.txt`

**Purpose:** SMS confirmation to interested party

**Changes:**
| Line | Original | New |
|------|----------|-----|
| 10-12 | `Mvh<br />[[oppdrag.saksbehandler.navn]]<br />[[oppdrag.saksbehandler.titel]] [[oppdrag.saksbehandler.telefon]]` | `[[oppdrag.saksbehandler.navn]]<br />[[oppdrag.saksbehandler.titel]]<br />[[oppdrag.saksbehandler.telefon]]` |

**Full new content:**
```html
Takk for påmelding til visning - [[oppdrag.adresse.adresse]].
<br /><br />
<span vitec-if="Model.visingspamelding == false">
Megler vil ta kontakt med deg for å avtale et tidspunkt.</span>
<span vitec-if="Model.visingspamelding == true">
Visningstid: [[visingsdato]].<br />
Antall personer: [[participants]]
</span>
<br /><br />
[[oppdrag.saksbehandler.navn]]<br />
[[oppdrag.saksbehandler.titel]]<br />
[[oppdrag.saksbehandler.telefon]]
```

### Template: `Smstemplate_forlegad.txt`

**Purpose:** Debug/legacy SMS template

**Changes:** None required - this appears to be a debug template with merge field references.

---

## Merge Field Reference

### Commonly Used Merge Fields

| Field | Description |
|-------|-------------|
| `[[oppdrag.adresse.adresse]]` | Property street address |
| `[[oppdrag.adresse.leilighetnummer]]` | Apartment number |
| `[[oppdrag.adresse.postnummer]]` | Postal code |
| `[[oppdrag.adresse.sted]]` | City/location |
| `[[oppdrag.oppdragsnummer]]` | Assignment number |
| `[[oppdrag.salgsoppgavelink]]` | Link to sales document |
| `[[oppdrag.saksbehandler.navn]]` | Broker name |
| `[[oppdrag.saksbehandler.titel]]` | Broker title |
| `[[oppdrag.saksbehandler.telefon]]` | Broker phone |
| `[[interestedparty.navn]]` | Interested party name |
| `[[interestedparty.telefon]]` | Interested party phone |
| `[[interestedparty.mail]]` | Interested party email |
| `[[interestedparty.nextlink]]` | Link to open in Vitec Next |
| `[[visingsdato]]` | Viewing date |
| `[[participants]]` | Number of participants |

### Conditional Expressions

| Condition | Description |
|-----------|-------------|
| `Model.visingspamelding == true` | Viewing registration is true |
| `Model.oppdrag.saksbehandler.harnavn == true` | Broker has name |
| `Model.oppdrag.saksbehandler.hartitel == true` | Broker has title |
| `Model.interestedparty.harmail == true` | Interested party has email |
| `Model.interestedparty.salgsoppgaverequested == true` | Sales document requested |
| `Model.interestedparty.consentscontactforownestate` | Consents to property valuation |
| `Model.interestedparty.consentscontactforfinance` | Consents to financing contact |
| `Model.tiptobankisexpected` | Bank tip is expected |
| `Model.tiptobankiscreated` | Bank tip was created |

---

## File Checklist

### Bud Portal Files

- [ ] `PROAKTIV.scss` - SCSS with Proaktiv variables
- [ ] `PROAKTIV.css` - Compiled CSS
- [ ] `PROAKTIV.min.css` - Minified CSS
- [ ] `PROAKTIV.json` - Configuration with disabled newsletter/financing

### Visning Portal Files

- [ ] `PROAKTIV.scss` - SCSS with Proaktiv variables
- [ ] `PROAKTIV.css` - Compiled CSS
- [ ] `PROAKTIV.min.css` - Minified CSS
- [ ] `PROAKTIV.json` - Configuration with disabled newsletter/financing
- [ ] `email_notifyinterestedparty_propertydescription.txt` - Updated signature
- [ ] `email_notifyinterestedparty_registrationconfirmation.txt` - Updated signature
- [ ] `email_notifyrealtor_newviewingparticipant.txt` - Updated signature
- [ ] `email_notifyrealtor_salgsoppgaverequested.txt` - Updated signature
- [ ] `note_newviewingparticipant.txt` - Copy as-is
- [ ] `note_salgsoppgaverequested.txt` - Copy as-is
- [ ] `sms_notifyinterestedparty_registrationconfirmation.txt` - Updated signature
- [ ] `Smstemplate_forlegad.txt` - Copy as-is (debug template)
- [ ] `blacklist.json` - Copy as-is (spam protection rules)

---

## Implementation Notes

### 1. SCSS Compilation

The SCSS files need to be compiled to CSS. Use:
```bash
sass PROAKTIV.scss PROAKTIV.css
sass PROAKTIV.scss PROAKTIV.min.css --style=compressed
```

### 2. Background Color Consideration

The Visning portal uses `background: lightgray` on body. Consider keeping this or changing to `#f8f9fa` (light neutral) for consistency.

### 3. Button Hover States

For Proaktiv, use:
- Primary: `#272630`
- Hover: `#3E3D4A` (lighter)

This is the **opposite** of the DEFAULT skin which darkens on hover. Proaktiv uses a lighter shade for hover to maintain the premium feel.

### 4. Financing Office Override

The Voss office has financing enabled in the Vitec backend. This spec disables financing **globally** in the skin. The Voss override is handled separately in Vitec Next administration, not in the skin files.

### 5. Google Tag Manager

Left as placeholder (`GTM-XXXX`). When Proaktiv gets a GTM ID, update the config and set `UseGoogleTagManager: true` / `useGoogleTagManager: true`.

### 6. Privacy URL

All privacy links should point to: **https://proaktiv.no/personvern**

### 7. CSS Specificity

Both portals use Bootstrap-based styling. The skin CSS overrides Bootstrap defaults. Ensure `!important` flags are used where the DEFAULT skin uses them.

### 8. Font Consistency

Keep `'Open Sans'` for all templates and portal UI. The serif font (`'Playfair Display'`) from Proaktiv brand guide is for document templates, not portal UI.

---

## Appendix: Full SCSS Templates

### PROAKTIV.scss (Bud Portal)

```scss
$primary: #272630; /* Proaktiv charcoal */
$secondary: #5e6d82; /* gray */
$success: #a4b5a8; /* Proaktiv grønn */
$danger: #cd2026; /* red - keep for errors */
$warning: #bcab8a; /* Proaktiv bronse */
$info: #e9e7dc; /* Proaktiv beige */
$light: #f8f9fa; /* lightgray */
$dark: #272630; /* Proaktiv primary */

@import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700&display=swap');

body {
    font-family: 'Open sans', sans-serif;

    a {
        color: $primary;
    }

    .bg-primary {
        background-color: $primary !important;
    }

    .bg-secondary {
        background-color: $secondary !important;
    }

    .bg-success {
        background-color: $success !important;
    }

    .bg-danger {
        background-color: $danger !important;
    }

    .bg-warning {
        background-color: $warning !important;
    }

    .bg-info {
        background-color: $info !important;
    }

    .bg-light {
        background-color: $light !important;
    }

    .bg-dark {
        background-color: $dark !important;
    }

    .btn-primary {
        background-color: $primary;
        border: none;

        &:not(:disabled):hover,
        &:not(:disabled):focus {
            background-color: #3E3D4A;
        }
    }

    .btn-secondary {
        background-color: $secondary;
        border: none;
    }

    .btn-success {
        background-color: $success;
        border: none;
    }

    .btn-danger {
        background-color: $danger;
        border: none;
    }

    .btn-warning {
        background-color: $warning;
        border: none;
    }

    .btn-info {
        background-color: $info;
        border: none;
    }

    .btn-light {
        background-color: $light;
        border: none;
    }

    .btn-dark {
        background-color: $dark;
        border: none;
    }

    .btn-outline-danger {
        border-color: $danger;

        &:not(:disabled):not(.disabled):active {
            border-color: $danger;
        }
    }

    main {
        .container {

            &.status {

                &.bid-signing {
                    background-color: $warning;
                }

                &.bid-done {
                    background-color: $success;
                    color: $primary;
                }

                &.bid-retrying {
                    background-color: $info;
                }

                &.bid-failed {
                    background-color: $danger;
                    color: white;
                }
            }

            .list-group {

                .list-group-item {

                    .link-text {
                        color: $primary;
                    }

                    .far {

                        &.fa-check {
                            color: $success;
                        }

                        &.fa-arrow-alt-square-down, &.fa-external-link-square-alt {
                            color: $primary;
                        }
                    }
                }
            }
        }

        .progress-article {
            .container {
                .bid-progress-container {
                    .circle {
                        &.active {
                            border-color: $primary;
                        }

                        &.completed, &.allStepsCompleted {
                            border-color: $success;
                            background-color: lighten($success, 15%);

                            i {
                                color: darken($success, 20%);
                            }
                        }

                        &.failed, &.failedButActive {
                            border-color: $danger;
                            background-color: lighten($danger, 30%);

                            i {
                                color: $danger;
                            }
                        }

                        &.waiting {
                            border-color: $warning;
                            background-color: lighten($warning, 20%);

                            i {
                                color: darken($warning, 20%);
                            }
                        }
                    }
                }
            }
        }
    }
}
```

### PROAKTIV.scss (Visning Portal)

```scss
@import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700&display=swap');

$primary: #272630;
$primary-hover: #3E3D4A;

body {
    background: #f8f9fa;
    font-family: 'Open sans', sans-serif;

    a {
        color: $primary;
    }

    .btn {

        &.btn-primary {
            background-color: $primary;
            border: none;

            &:not(:disabled):hover,
            &:not(:disabled):focus {
                background-color: $primary-hover;
            }
        }

        &.btn-outline-primary {
            border-color: $primary;
            color: $primary;

            &:not(:disabled):hover,
            &:not(:disabled):focus {
                border-color: $primary-hover;
                background-color: $primary-hover;
                color: #fff;
            }

            &.btn-primary {
                background-color: $primary;
                border: solid 1px $primary;
                color: #fff;

                &:not(:disabled):hover,
                &:not(:disabled):focus {
                    background-color: $primary-hover;
                    border: solid 1px $primary-hover;
                    color: #fff;
                }
            }
        }
    }

    .container {

        .list-group-item {

            .far {
                color: $primary;
            }
        }
    }
}
```

---

## Next Steps

1. **Phase 2 (Style Builder):** Create actual files from this spec
2. **Phase 3 (Testing):** Test in Vitec sandbox environment
3. **Phase 4 (Deployment):** Upload to Vitec production

---

*End of Specification*
