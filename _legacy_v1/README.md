# Proaktiv Dokument Hub

**Proaktiv Dokument Hub** is a modern, high-performance dashboard for managing, editing, and previewing Vitec Next document templates. Built with **React**, **Node.js**, and **Tailwind CSS**, it provides a seamless "Glassmorphism" UI for real-time document editing.

## 🌟 Key Features

### 🖥️ Modern UI & Experience
*   **Glassmorphism Design:** A premium, dark-mode transparency effect (frosted glass) across the entire application.
*   **Swappable Layout:** Instantly toggle between "Editor First" and "Preview First" layouts using the `<->` toolbar button.
*   **Responsive Panels:** Draggable resizers for the file explorer, editor, and preview pane.

### 📝 Advanced Template Management
*   **Live Code Editor:** Monaco Editor (VS Code style) with HTML syntax highlighting and auto-completion.
*   **Smart Categorization:** Organize templates into categories (folders) with drag-and-drop support (via file system).
*   **Search & Filter:** Instant search for templates (`Ctrl+F`).
*   **Keyboard Shortcuts:**
    *   `Ctrl+S`: Save
    *   `Ctrl+Shift+S`: Save as New Version
    *   `Ctrl+D`: Duplicate Template

### 📱 Real-time Simulators
*   **Device Skins:** Preview how documents look on different devices:
    *   **Desktop:** "New Outlook" Web Interface styling.
    *   **Mobile:** Modern iOS Outlook App styling with Dynamic Island.
    *   **iPhone (SMS):** Valid iPhone iMessage bubble for SMS templates.
    *   **A4 Print:** Standard print layout.
*   **SMS Support:** Dedicated support for `.txt` and `.html` SMS templates in the `SMS` category, with automatic variable highlighting.

### ☁️ Cloud Architecture & Persistence
*   **Azure Hosted:** Deployed on Azure App Service (Linux).
*   **Persistent Library:** Templates are stored in an Azure File Share (`library`), separated from application code.
*   **Direct Saving:** Edits are saved immediately to the cloud storage. No Git Push required.

## 🚀 User Access (Production)
The application is live on Azure. No installation is required for general use.
*   **Live App:** [https://proaktiv-dokument-hub-eqa2d7hthcf7c9ej.norwayeast-01.azurewebsites.net/](https://proaktiv-dokument-hub-eqa2d7hthcf7c9ej.norwayeast-01.azurewebsites.net/)

## 👨‍💻 Developer Setup (Localhost)
Follow these steps ONLY if you are a developer extending the application's logic.

### Prerequisites
*   Node.js (v16+)
*   Git

### Installation
1.  Clone the repository:
    ```bash
    git clone https://github.com/your-repo/proaktiv-dokument-hub.git
    cd proaktiv-dokument-hub
    ```

2.  Install dependencies:
    ```bash
    npm install         # Server deps
    cd client && npm i  # Client deps
    ```

### Running Locally
You can run the full dashboard (Frontend + Backend) with a single command:

```bash
# From the root directory
npm run dev
```

*   **Frontend:** `http://localhost:5173`
*   **Backend:** `http://localhost:5000`

## 📂 Project Structure

*   `/client` - React frontend (Vite)
*   `/library` - Local folder where your HTML/SMS templates are stored.
*   `/server.js` - Express backend for file operations.

---

*Developed for Proaktiv Eiendomsmegling.*
