# Mass Migration Strategy: Vitec Next Template Modernization

## 1. Goal
Update approximately 100-300 existing Vitec document templates to utilize the new "Vitec Stilark Premium Gold Navy" modular CSS system. This ensures consistent branding, easier maintenance, and "premium" aesthetics across all company documents.

## 2. Technical Challenge
*   **Volume:** 100-300 files make manual editing error-prone and tedious.
*   **Legacy Code:** Existing templates likely contain:
    *   Hardcoded inline styles (e.g., `style="font-family: Arial; color: #000;"`).
    *   Deprecated HTML tags (e.g., `<font>`, `<center>`).
    *   Table-heavy layouts that might fight with modern CSS.
*   **Vitec Constraint:** Vitec Next templates must be edited individually in the browser or via copy-paste. There is no known "bulk upload" API for templates.

## 3. Proposed Hub Workflow

We will transform the **Proaktiv Document Hub** into a "Migration Factory".

### Phase 1: Ingestion (Getting templates INTO the Hub)
Since Vitec doesn't support bulk export easily, we have two options:
1.  **Browser Automation (Agentic):** I (the AI agent) can navigate to Vitec, open each template, copy the source, and save it to the Hub's `library/Legacy_Import/` folder.
2.  **Manual Export (Batch):** You manually copy source codes into text files in a local folder which the Hub reads.

### Phase 2: Automated Refactoring (The "Sanitizer")
We will build a Node.js script (triggered via Hub UI) that processes files in `library/Legacy_Import/`:
1.  **Resource Update:** Automatically finds `<span class="vitec-resource" ...>` and changes it to `vitec-template="resource:Vitec Stilark Premium Gold Navy"`.
2.  **Style Stripping:**
    *   Removes `font-family`, `color`, and `font-size` from `style="..."` attributes (letting the CSS class handle it).
    *   Converts `<font color="...">` tags to `<span>` or strips them.
3.  **Structure Normalization:** Adds the standard `<div id="vitecTemplate" class="proaktiv-theme">` wrapper if missing.
4.  **Output:** Saves the cleaned file to `library/Ready_For_Export/`.

### Phase 3: Validation (Hub Preview)
Use the existing **HTML Hub Preview** to visually verify the batch.
*   We can add a "Batch Preview" mode to quickly cycle through the `Ready_For_Export` folder.
*   Compare "Legacy" vs "Refactored" side-by-side.

### Phase 4: Deployment (Getting templates BACK into Vitec)
1.  **Browser Automation (Bot):** The AI Agent runs a script to:
    *   Read a file from `Ready_For_Export`.
    *   Open the corresponding template in Vitec Next (by name match).
    *   Paste the new code.
    *   Save.
2.  **Manual Override:** For critical templates, you can copy-paste manually from the Hub's "Export" view.

## 4. Required Tooling Upgrades
1.  **Sanitization Script:** A regex/DOM-based cleaner in `server.js` or a new utility module.
2.  **Batch Processing UI:** A new "Migration" tab in the Hub to trigger the clean-up and see status (e.g., "10 Pending, 50 Cleaned").
3.  **Vitec Navigator:** A mapped list of Template Names <-> Vitec IDs (if possible) or Search Terms to help the bot find the right template.

## 5. Risk Mitigation
*   **Backup:** Always keep the original "Legacy" source in a git branch before overwriting.
*   **Pilot:** Run the full process on 5 non-critical templates first.
*   **Visual Regression:** Use screenshots (as we did today) to confirm nothing broke layout-wise.
