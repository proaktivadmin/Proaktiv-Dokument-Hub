# Firebase Deployment Strategy for Proaktiv Document Hub

## Overview
The current "Proaktiv Document Hub" is designed as a **Local filesystem-based application**. It reads and writes directly to your computer's `library` folder.

**Firebase Functions are serverless and ephemeral**, meaning they do not have a persistent filesystem. If you deploy the current `server.js` to Firebase:
1.  **Reading files** will work (if bundled with the deployment).
2.  **Saving/Editing files** will appear to work but changes **will be lost** immediately after the function execution finishes.
3.  **New files** cannot be permanently created.

To make the Hub work on Firebase, we must **Refactor the Storage Layer** to use cloud services instead of the local disk.

---

## Required Changes

### 1. Architecture Shift
We need to move from **Local FS** -> **Cloud Storage + Firestore**.
- **HTML Templates:** Store in **Firebase Cloud Storage** buckets.
- **Metadata (Categories, Tags):** Store in **Firestore Database** for fast querying.
- **Backend API:** Migrate `server.js` to **Firebase Cloud Functions**.

### 2. Code Refactoring (The "Adapter" Pattern)
We need to rewrite the file operations in `server.js`.

| Current Operation (`fs`) | New Cloud Operation (Admin SDK) |
| :--- | :--- |
| `fs.readdir(LIBRARY_PATH)` | Iterate Firestore collection `templates` |
| `fs.readFile(path)` | Download stream from Cloud Storage bucket |
| `fs.writeFile(path)` | Upload stream to Cloud Storage bucket |
| `fs.mkdir(category)` | Just a metadata field `category` in Firestore |

### 3. Configuration Setup
You will need to add these files to your project root:

**`firebase.json`** (Routing)
```json
{
  "hosting": {
    "public": "client/dist",
    "rewrites": [
      {
        "source": "/api/**",
        "function": "api"
      },
      {
        "source": "**",
        "destination": "/index.html"
      }
    ]
  },
  "functions": {
    "source": "functions"
  }
}
```

**`functions/index.js`** (The Wrapper)
```javascript
const functions = require('firebase-functions');
const expressApp = require('./server'); // Your existing server.js (modified)

exports.api = functions.https.onRequest(expressApp);
```

### 4. Why this is necessary
If you simply "launch" it now, you will likely get errors about "Read-only file system" or your saved changes will vanish instantly. To have a functional "Hub" accessible from anywhere (including your work computer), the data must live in the cloud, not on your laptop's hard drive.

## Immediate Alternative (Low Effort)
If refactoring the entire storage layer is too much for today, you could:
1.  **Deploy for "View Only":** Deploy to Firebase, but disable the "Save" buttons. You can browse and copy code, but not edit.
2.  **Use a VPS:** Host it on a virtual machine (like DigitalOcean, Linode, or even a persistent Replit) instead of Firebase. A VPS has a persistent disk, so the current code would work with almost zero changes.
