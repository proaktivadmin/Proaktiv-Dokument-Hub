const fs = require('fs');
const path = require('path');

const SOURCE_DIR = path.join(__dirname, 'library');
const DEST_DIR = path.join(__dirname, 'azure_upload');

// Folders to ignore
const IGNORE_DIRS = ['Legacy_Import', 'Ready_For_Export', '.git'];

if (!fs.existsSync(DEST_DIR)) {
    fs.mkdirSync(DEST_DIR);
}

function copyFiles(dir, rootDir) {
    const files = fs.readdirSync(dir);

    files.forEach(file => {
        const fullPath = path.join(dir, file);
        const stat = fs.statSync(fullPath);

        if (stat.isDirectory()) {
            if (IGNORE_DIRS.includes(file)) return;
            copyFiles(fullPath, rootDir);
        } else {
            // It's a file
            let destFileName = file;
            let destPath = path.join(DEST_DIR, destFileName);

            // Handle Collisions
            if (fs.existsSync(destPath)) {
                // If collision, pre-pend parent folder name
                const parentDir = path.basename(dir);
                destFileName = `${parentDir}_${file}`;
                destPath = path.join(DEST_DIR, destFileName);

                // If specific check for known collision or just double check
                if (fs.existsSync(destPath)) {
                    // if still exists, obscure collision (rare in this dataset)
                    destFileName = `${parentDir}_${Date.now()}_${file}`;
                    destPath = path.join(DEST_DIR, destFileName);
                }
            }

            fs.copyFileSync(fullPath, destPath);
            console.log(`Copied: ${file} -> ${destFileName}`);
        }
    });
}

console.log('Starting file flattening...');
copyFiles(SOURCE_DIR, SOURCE_DIR);
console.log('Done!');
