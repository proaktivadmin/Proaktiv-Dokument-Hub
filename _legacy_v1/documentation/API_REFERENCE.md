# API Reference

**Base URL:** `http://localhost:5000`

## 1. System Initialization
### `GET /api/init`
Starts the application session.
-   **Actions:**
    -   Recursively scans `library/` for `.html`, `.txt`, `.css`.
    -   Checks Git status for the repository.
    -   Reads metadata from `library/meta.json` (if exists).
-   **Returns:** JSON object with `filePaths`, `gitStatus`, `meta`, `cssFiles`, `htmlFiles`.

## 2. File Operations
### `POST /api/files/read`
Reads a file's content.
-   **Body:** `{ path: "Relative/Path/To/File.html" }`
-   **Returns:** `{ content: "..." }`

### `POST /api/files/save`
Saves content to a file.
-   **Body:** `{ path: "...", content: "..." }`
-   **Returns:** `{ success: true }`

### `POST /api/export/save-to-disk`
Saves a bundled CSS export to the filesystem.
-   **Body:** `{ filename: "...", content: "..." }`
-   **Returns:** `{ success: true, path: "..." }`

## 3. Migration Factory (Sanitizer)
### `POST /api/sanitize/preview`
Runs the sanitizer logic on a raw HTML string without saving.
-   **Body:** `{ content: "Raw HTML..." }`
-   **Returns:** `{ sanitized: "Cleaned HTML..." }`

### `POST /api/sanitize/batch`
Triggers the mass migration process.
-   **Actions:**
    1.  Scans `library/Legacy_Import` for all `.html`/`.txt` files.
    2.  Sanitizes each file using `sanitizer.js`.
    3.  Saves output to `library/Ready_For_Export`.
-   **Body:** `{}` (Empty)
-   **Returns:** `{ results: [ { file: "name", success: true, ... } ] }`

## 4. Resources
### `GET /resources/*`
Serves static assets from the `company-portal/resources` directory.
