## 13. Vitec Next Template Admin Interface

This section documents the built-in system features of the Vitec Next template editor and management interface, based on screenshots of the production admin UI.

### CKEditor toolbar

Templates are edited using CKEditor 4 with the following toolbar:

| Button/Group | Function |
|-------------|----------|
| **Testfletting** | Test merge — renders the template with sample data to preview the output |
| **Normal (...)** | Paragraph style dropdown (Normal, Heading 1–5, etc.) |
| **Skrift** | Font family dropdown |
| **Størrelse** | Font size dropdown |
| **B I U S T** | Bold, Italic, Underline, Strikethrough, and text formatting |
| List buttons | Ordered and unordered lists |
| Indent buttons | Increase/decrease indent |
| Alignment | Left, Center, Right, Justify |
| **Q** (magnifier) | Find/Replace |
| **A** / **A** (colored) | Text color / Background color pickers |
| Table icon | Insert/edit tables |
| Link/Unlink | Insert/remove hyperlinks |
| **[P]** | Insert page break |
| **[d]** | Insert merge field / data field |
| **Kilde** | Source view — switch to raw HTML editing mode |

The editor shows the current template name at the bottom: `Dokumentmal: [Template Name]`.

**Key workflow:** Editors typically work in the visual WYSIWYG view. The "Kilde" (Source) button switches to raw HTML where `vitec-if`, `vitec-foreach`, and merge fields can be edited directly. "Testfletting" previews how the template will look with real data.

### Template categorization settings

Each template has a "Kategorisering" (Categorization) panel with the following configurable fields:

#### Core metadata

| Field | Norwegian label | Description | Example |
|-------|----------------|-------------|---------|
| Template type | MALTYPE | `Objekt/Kontakt` (document) or `System` (system template) | `Objekt/Kontakt` |
| Objects | OBJEKTER | Link to specific property/contact objects | `Finn objekt` (search) |
| Template name | MALNAVN | Display name of the template | `Kjøpekontrakt Bruktbolig` |
| Receiver type | MOTTAKERTYPE | Who receives this document | `Systemstandard` |
| Receiver | MOTTAKER | Specific receiver selection | `Ingen valgt` |
| Extra receivers | EKSTRA MOTTAKERE | Additional receivers | `Ingen valgt` |

#### Filtering and classification

| Field | Norwegian label | Description | Example |
|-------|----------------|-------------|---------|
| Access restrictions | FILTRERING | Restrict who can use this template | (configurable) |
| Channels | KANALER | Output channels | `PDF og e-post`, `Kun SMS`, `Kun e-post` |
| Category | KATEGORI | Document category | `Kontrakt`, `Oppdragsavtale`, `Akseptbrev kjøper`, etc. |
| Assignment category groups | OPPDRAGSKATEGORIGRUPPER | Which assignment categories this applies to | `Oppgjørsoppdrag (Bolig, Fritid, Tomt), Salg (Bolig, Fritid, Tomt)` |
| Assignment types | OPPDRAGSTYPER | Specific assignment types | `Oppgjørsoppdrag (Bolig, Fritid, Tomt), Salg (Bruktbolig, Fritid, Tomt)` |
| Depot journal groups | DEPOTJOURNALGRUPPER | Depot journal classification | `Ingen valgt` |
| Depot journal types | DEPOTJOURNALTYPER | Specific depot journal types | `Ingen valgt` |
| Phases | FASER | Which workflow phases | `Innsalg`, `Til salgs`, `Kontrakt`, `Oppgjør`, etc. |
| Ownership types | EIERFORMER | Property ownership filter | `Ingen valgt` (all) or specific types |
| Departments | AVDELINGER | Office/department filter | `Ingen valgt` (all) |

#### Email settings

| Field | Norwegian label | Description | Example |
|-------|----------------|-------------|---------|
| Subject | EMNE | Email subject line — supports merge fields! | `Kjøpekontrakt - [[oppdrag.nr]]` |

This confirms that `[[merge.fields]]` work in email subject lines, not just in template body content.

#### PDF settings — Header, footer, and margins

This is the critical section that controls how headers and footers are attached:

| Field | Norwegian label | Description | Example |
|-------|----------------|-------------|---------|
| Header template | TOPPTEKST | Dropdown to select header template (or "Ingen" = none) | `Ingen`, `Vitec Topptekst` |
| Footer template | BUNNTEKST | Dropdown to select footer template (or "Ingen" = none) | `Vitec Bunntekst Kontrakt` |

**Page margins** are configured per template with a visual A4 diagram:

| Margin | Norwegian label | Unit | Max | Example (Kjøpekontrakt) |
|--------|----------------|------|-----|------------------------|
| Top | TOPP | cm | 10 | `1,5` |
| Left | VENSTRE | cm | 10 | `1` |
| Right | HØYRE | cm | 10 | `1,2` |
| Bottom | BUNN | cm | 10 | `1` |

Note: "Angi marger i cm (eks. 2.25). Maksimalt 10 cm." — Margins are specified in cm with decimal values (Norwegian comma separator), maximum 10 cm.

**Example: Kjøpekontrakt Bruktbolig PDF settings:**
- Topptekst: **Ingen** (no header — the contract has its own header content)
- Bunntekst: **Vitec Bunntekst Kontrakt** (contract footer with signature lines)
- Margins: Top 1.5cm, Left 1cm, Right 1.2cm, Bottom 1cm

This confirms that the Kjøpekontrakt does NOT use a header template — the org number, assignment number, and title ("Kjøpekontrakt") at the top of the template are part of the body content itself.

### Template management sidebar

Each template has a "Dokumentmal" sidebar with:

| Section | Norwegian label | Description |
|---------|----------------|-------------|
| Categorization | Kategorisering | All metadata fields (expandable) |
| PDF attachments | PDF-vedlegg | Attach additional PDF documents to the template output |
| Copy as new | Kopier som ny mal | Duplicate the template as a starting point |
| History | Historikk | Version history of changes |
| Activate | AKTIVER MALEN | Toggle template active/inactive (green = active) |
| Delete | SLETT | Toggle to mark for deletion |
| Document concerns | DOKUMENTET OMHANDLER | What the document is about |
| Relations | VELG RELASJONER | Link to related templates |

### Template list view

The template list shows all templates with the following columns:

| Column | Norwegian | Description |
|--------|-----------|-------------|
| Template name | MALNAVN | Template display name |
| Type | TYPE | `Objekt/Kontakt` or `System` |
| Phase | FASE | Workflow phase(s) |
| Receiver | MOTTAKER | Receiver type |
| Category | KATEGORI | Document category |
| Header/Footer | TOPP/BUNN... | Cloud icons indicating header/footer assignment |
| Assignment type | OPPDRAGSTYPE | Assignment type filter |
| Depot journal | DEPO JOURNAL... | Journal classification |
| Posting code | POSTERINGSKOD... | Accounting code |
| Icons | IKONER | Status indicators (active, published, channels) |
| Departments | AVDELINGER | Department restrictions |
| Last modified | SIST ENDRET | Date and time of last edit |
| Modified by | ENDRET AV | User code who last edited |

Icon indicators visible in the list:
- Green checkmark — template is active/published
- Cloud icon — has header or footer assigned
- Email icon (@) — available for email channel
- Document icon — available for PDF channel

### Action menu (Utfør)

The gear icon "Utfør" menu provides:

| Action | Norwegian | Description |
|--------|-----------|-------------|
| New document template | Ny dokumentmal | Create a new HTML template from scratch |
| New Word template | Ny Word-mal | Create a Word document template |
| Select standard templates | Velg standardmaler | Import Vitec's default standard templates |
| Select function templates | Velg funksjonsmaler | Import function-specific templates (Saldoforespørsel, etc.) |
| Vitec templates | Vitecmaler | Browse all available Vitec system templates |
| Import template | Importer mal | Import a template from file |
| Filter | Filter | Open filter panel |
| View as cards | Vis som kort | Switch from list view to card view |

### Filter panel

The filter panel allows narrowing the template list:

| Filter | Norwegian | Options |
|--------|-----------|---------|
| Show inactive | VIS INAKTIVE MALER | Toggle — shows deactivated templates |
| System only | VIS KUN SYSTEMMALER | Toggle — filter to system templates only |
| Selection | UTVALG | `KUNDEMALER` (customer/custom) or `VITECMALER` (Vitec defaults) |
| Channel | KANAL | `KUN SMS` (SMS only) or `KUN E-POST` (email only) |
| Content search | INNHOLD | Free text search within template HTML content |

The "KUNDEMALER" vs "VITECMALER" distinction is important:
- **Vitecmaler** — Default templates provided by Vitec (cannot be modified directly, must be copied first)
- **Kundemaler** — Company-customized templates (copies of Vitecmaler or newly created)

### Confirmed from UI: Boligkjøperforsikring is a System template

The template list screenshot confirms that **Boligkjøperforsikring** is categorized as a `System` template type (last modified 16.02.2026). This is the support template containing the `@functions` block, referenced by the Kjøpekontrakt via `<span vitec-template="resource:Boligkjøperforsikring">`.

**(Evidence: Vitec Next admin UI screenshots from Proaktiv production environment, 2026-02-21)**

---
