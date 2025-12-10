const express = require('express');
const fs = require('fs');
const path = require('path');
const cors = require('cors');
const { exec } = require('child_process');
const sanitizer = require('./sanitizer');

const app = express();
const PORT = process.env.PORT || 5000;
const LIBRARY_PATH = process.env.LIBRARY_PATH || path.join(__dirname, 'library');
const RESOURCES_PATH = process.env.RESOURCES_PATH || path.join(__dirname, '../company-portal/resources');
const LEGACY_IMPORT_PATH = path.join(LIBRARY_PATH, 'Legacy_Import');
const READY_EXPORT_PATH = path.join(LIBRARY_PATH, 'Ready_For_Export');

// Ensure migration directories exist
[LEGACY_IMPORT_PATH, READY_EXPORT_PATH].forEach(dir => {
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
});

app.use(cors());
app.use(express.json());
app.use('/resources', express.static(RESOURCES_PATH));
app.use('/resources/library', express.static(LIBRARY_PATH));

[LIBRARY_PATH, RESOURCES_PATH].forEach(dir => { if (!fs.existsSync(dir)) fs.mkdirSync(dir); });

const getFilesRecursively = (dir, fileList = []) => {
    const files = fs.readdirSync(dir);
    files.forEach(file => {
        if (file === '.git') return;
        const filePath = path.join(dir, file);
        if (fs.statSync(filePath).isDirectory()) {
            getFilesRecursively(filePath, fileList);
        } else if (file.endsWith('.html') || file.endsWith('.txt') || file.endsWith('.css')) {
            fileList.push(path.relative(LIBRARY_PATH, filePath));
        }
    });
    return fileList;
};

app.get('/api/init', (req, res) => {
    try {
        try {
            const filePaths = getFilesRecursively(LIBRARY_PATH);

            // GIT STATUS INTEGRATION
            exec('git status --porcelain', { cwd: LIBRARY_PATH }, (err, stdout) => {
                const gitStatusMap = {};
                if (!err && stdout) {
                    stdout.split('\n').forEach(line => {
                        const trimmed = line.trim();
                        if (!trimmed) return;
                        // Status code is first 2 chars
                        const code = line.substring(0, 2);
                        const file = line.substring(3).trim();
                        // Map generic statuses: ?? = untracked (green), M = modified (green), else clean (blue)
                        // We only care if it's NOT clean.
                        gitStatusMap[file] = 'modified';
                    });
                }

                // Map files to objects with status
                const files = filePaths.map(p => {
                    // Determine git status
                    // Windows paths might need normalization for matching git output which uses forward slashes
                    const normalizedKey = p.replace(/\\/g, '/');
                    const status = gitStatusMap[normalizedKey] ? 'modified' : 'clean';
                    return { path: p, status };
                });

                const resourceFiles = fs.readdirSync(RESOURCES_PATH);

                // CSS: Legacy resources + library/System/Styles
                let cssFiles = resourceFiles.filter(f => f.endsWith('.css'));
                const systemStylesPath = path.join(LIBRARY_PATH, 'System', 'Styles');
                if (fs.existsSync(systemStylesPath)) {
                    const sysStyles = fs.readdirSync(systemStylesPath).filter(f => f.endsWith('.css')).map(f => `System/Styles/${f}`);
                    cssFiles = [...cssFiles, ...sysStyles];
                }

                // HTML (Headers/Footers): Legacy resources + Topptekst + Bunntekst
                let htmlFiles = resourceFiles.filter(f => f.endsWith('.html'));
                ['Topptekst', 'Bunntekst'].forEach(folder => {
                    const folderPath = path.join(LIBRARY_PATH, folder);
                    if (fs.existsSync(folderPath)) {
                        const folderFiles = fs.readdirSync(folderPath).filter(f => f.endsWith('.html')).map(f => `${folder}/${f}`);
                        htmlFiles = [...htmlFiles, ...folderFiles];
                    }
                });

                let testData = {}, snippets = [];
                try { testData = JSON.parse(fs.readFileSync(path.join(RESOURCES_PATH, 'test_data.json'), 'utf8')); } catch (e) { }
                try { snippets = JSON.parse(fs.readFileSync(path.join(RESOURCES_PATH, 'snippets.json'), 'utf8')); } catch (e) { }
                res.json({ files, cssFiles, htmlFiles, testData, snippets });
            });
        } catch (err) { console.error(err); res.status(500).json({ error: 'Init failed' }); }
    } catch (err) { console.error(err); res.status(500).json({ error: 'Init failed' }); }
});

app.post('/api/files/read', (req, res) => {
    const fullPath = path.join(LIBRARY_PATH, req.body.filepath);
    const metaPath = fullPath.replace('.html', '.meta.json');
    fs.readFile(fullPath, 'utf8', (err, content) => {
        if (err) return res.status(500).json({ error: 'Read failed' });
        let meta = {};
        try { meta = JSON.parse(fs.readFileSync(metaPath, 'utf8')); } catch (e) { }
        res.json({ content, meta });
    });
});

app.post('/api/resources/read', (req, res) => {
    if (!req.body.filename) return res.json({ content: '' });

    // Check if it's a library file (starts with known system folders)
    const isLibraryResource = ['System/', 'Topptekst/', 'Bunntekst/'].some(prefix => req.body.filename.startsWith(prefix));

    let filePath;
    if (isLibraryResource) {
        filePath = path.join(LIBRARY_PATH, req.body.filename);
    } else {
        filePath = path.join(RESOURCES_PATH, req.body.filename);
    }

    fs.readFile(filePath, 'utf8', (err, content) => {
        res.json({ content: err ? '' : content });
    });
});

app.post('/api/files/save', (req, res) => {
    const { filepath, content, meta } = req.body;
    const fullPath = path.join(LIBRARY_PATH, filepath);
    const metaPath = fullPath.replace('.html', '.meta.json');
    const folder = path.dirname(fullPath);
    if (!fs.existsSync(folder)) fs.mkdirSync(folder, { recursive: true });
    fs.writeFile(fullPath, content, () => {
        if (meta) fs.writeFile(metaPath, JSON.stringify(meta, null, 2), () => { });
        res.json({ message: 'Saved', filepath });
    });
});

// Create new file with category
app.post('/api/files/create', (req, res) => {
    const { filename, category, content } = req.body;
    if (!filename) return res.status(400).json({ error: 'Filename required' });

    const finalCategory = category || 'Uncategorized';
    const isUncategorized = finalCategory === 'Uncategorized';
    const filepath = isUncategorized ? filename : path.join(finalCategory, filename);
    const fullPath = path.join(LIBRARY_PATH, filepath);
    const metaPath = fullPath.replace('.html', '.meta.json');
    const folder = path.dirname(fullPath);

    if (!fs.existsSync(folder)) fs.mkdirSync(folder, { recursive: true });

    fs.writeFile(fullPath, content, () => {
        const meta = {
            category: finalCategory,
            createdAt: new Date().toISOString(),
            subject: 'Ny mal'
        };
        fs.writeFile(metaPath, JSON.stringify(meta, null, 2), () => { });
        res.json({ message: 'Created', filepath });
    });
});

app.post('/api/files/delete', (req, res) => {
    const fullPath = path.join(LIBRARY_PATH, req.body.filepath);
    if (!fullPath.startsWith(LIBRARY_PATH)) return res.status(403).json({ error: 'Forbidden' });
    fs.unlink(fullPath, () => {
        const metaPath = fullPath.replace('.html', '.meta.json');
        if (fs.existsSync(metaPath)) fs.unlinkSync(metaPath);
        res.json({ message: 'Deleted' });
    });
});

// Move file to new category
app.post('/api/files/move', (req, res) => {
    const { filepath, newCategory } = req.body;
    if (!filepath || !newCategory) return res.status(400).json({ error: 'Filepath and newCategory required' });

    const sourcePath = path.join(LIBRARY_PATH, filepath);
    const fileName = path.basename(filepath);
    const destFolder = newCategory === 'Uncategorized' ? LIBRARY_PATH : path.join(LIBRARY_PATH, newCategory);
    const destPath = path.join(destFolder, fileName);

    // Ensure destination does not exist
    if (fs.existsSync(destPath)) return res.status(400).json({ error: 'File already exists in destination' });

    // Validate paths
    if (!sourcePath.startsWith(LIBRARY_PATH) || !destFolder.startsWith(LIBRARY_PATH)) {
        return res.status(403).json({ error: 'Forbidden' });
    }

    // Ensure dest folder exists
    if (!fs.existsSync(destFolder)) fs.mkdirSync(destFolder, { recursive: true });

    // Move file
    fs.rename(sourcePath, destPath, (err) => {
        if (err) return res.status(500).json({ error: 'Move failed', details: err.message });

        // Move meta file if exists
        const sourceMeta = sourcePath.replace('.html', '.meta.json');
        const destMeta = destPath.replace('.html', '.meta.json');

        if (fs.existsSync(sourceMeta)) {
            // Update category in meta
            try {
                const metaContent = JSON.parse(fs.readFileSync(sourceMeta, 'utf8'));
                metaContent.category = newCategory;
                fs.writeFileSync(destMeta, JSON.stringify(metaContent, null, 2));
                fs.unlinkSync(sourceMeta);
            } catch (e) {
                // If meta read/write fails, just move it raw or ignore
                fs.renameSync(sourceMeta, destMeta);
            }
        }

        res.json({ message: 'Moved', from: filepath, to: path.join(newCategory, fileName) });
    });
});

app.post('/api/git/push', (req, res) => {
    exec(`git add . && git commit -m "Update ${new Date().toLocaleString()}" && git push`, { cwd: LIBRARY_PATH },
        (err, stdout, stderr) => {
            if (err) return res.status(500).json({ error: stderr || err.message, details: stdout });
            res.json({ message: 'Pushed to GitHub', output: stdout });
        });
});

app.post('/api/git/pull', (req, res) => {
    exec('git pull', { cwd: LIBRARY_PATH }, (err, stdout, stderr) => {
        if (err) return res.status(500).json({ error: stderr || err.message, details: stdout });
        res.json({ message: 'Pulled', output: stdout });
    });
});

// Add new variable to test_data.json
app.post('/api/variables/add', (req, res) => {
    const { key, value } = req.body;
    if (!key) return res.status(400).json({ error: 'Key required' });
    const testDataPath = path.join(RESOURCES_PATH, 'test_data.json');
    let testData = {};
    try { testData = JSON.parse(fs.readFileSync(testDataPath, 'utf8')); } catch (e) { }
    testData[key] = value || '';
    fs.writeFile(testDataPath, JSON.stringify(testData, null, 4), (err) => {
        if (err) return res.status(500).json({ error: 'Failed to save' });
        res.json({ message: 'Variable added', key, value });
    });
});

// Get all categories
app.get('/api/categories', (req, res) => {
    try {
        const items = fs.readdirSync(LIBRARY_PATH);
        const categories = items.filter(item => {
            const stat = fs.statSync(path.join(LIBRARY_PATH, item));
            return stat.isDirectory() && item !== '.git';
        });
        res.json({ categories });
    } catch (err) { res.status(500).json({ error: 'Failed to get categories' }); }
});

// Create new category (folder)
app.post('/api/categories/create', (req, res) => {
    const { name } = req.body;
    if (!name) return res.status(400).json({ error: 'Name required' });
    const catPath = path.join(LIBRARY_PATH, name);
    if (fs.existsSync(catPath)) return res.status(400).json({ error: 'Category exists' });
    fs.mkdirSync(catPath, { recursive: true });
    res.json({ message: 'Category created', name });
});

// Rename category (move folder)
app.post('/api/categories/rename', (req, res) => {
    const { oldName, newName } = req.body;
    if (!oldName || !newName) return res.status(400).json({ error: 'Names required' });
    const oldPath = path.join(LIBRARY_PATH, oldName);
    const newPath = path.join(LIBRARY_PATH, newName);
    if (!fs.existsSync(oldPath)) return res.status(404).json({ error: 'Category not found' });
    if (fs.existsSync(newPath)) return res.status(400).json({ error: 'New name exists' });
    fs.renameSync(oldPath, newPath);
    res.json({ message: 'Category renamed', oldName, newName });
});

// Delete category (move files to Uncategorized, then remove folder)
app.post('/api/categories/delete', (req, res) => {
    const { name } = req.body;
    if (!name) return res.status(400).json({ error: 'Name required' });
    const catPath = path.join(LIBRARY_PATH, name);
    if (!fs.existsSync(catPath)) return res.status(404).json({ error: 'Category not found' });

    // Move all files to Root (Uncategorized)
    const files = fs.readdirSync(catPath);
    files.forEach(file => {
        const oldFilePath = path.join(catPath, file);
        const newFilePath = path.join(LIBRARY_PATH, file);
        if (fs.statSync(oldFilePath).isFile()) {
            // Avoid overwriting if file exists in root? 
            // For now, let's append timestamp if exists or just rename (Windows might fail)
            if (fs.existsSync(newFilePath)) {
                const nameParts = file.split('.');
                const ext = nameParts.pop();
                const base = nameParts.join('.');
                const newName = `${base}_${Date.now()}.${ext}`;
                fs.renameSync(oldFilePath, path.join(LIBRARY_PATH, newName));
            } else {
                fs.renameSync(oldFilePath, newFilePath);
            }
        }
    });

    // Remove empty folder
    try { fs.rmdirSync(catPath); } catch (e) { }
    res.json({ message: 'Category deleted', name });
});

// Import template (single or batch)
app.post('/api/files/import', (req, res) => {
    const { files } = req.body; // Array of { filename, content, category, tags }
    if (!files || !Array.isArray(files)) return res.status(400).json({ error: 'Files array required' });

    const results = [];
    files.forEach(file => {
        const category = file.category || 'Uncategorized';
        const filename = file.filename.endsWith('.html') ? file.filename : `${file.filename}.html`;
        const isUncategorized = category === 'Uncategorized';
        const filepath = isUncategorized ? filename : path.join(category, filename);
        const fullPath = path.join(LIBRARY_PATH, filepath);
        const metaPath = fullPath.replace('.html', '.meta.json');
        const folder = path.dirname(fullPath);

        if (!fs.existsSync(folder)) fs.mkdirSync(folder, { recursive: true });

        fs.writeFileSync(fullPath, file.content);

        const meta = {
            category,
            tags: file.tags || [],
            importedAt: new Date().toISOString(),
            ...file.meta
        };
        fs.writeFileSync(metaPath, JSON.stringify(meta, null, 2));

        results.push({ filepath, status: 'imported' });
    });

    res.json({ message: `Imported ${results.length} file(s)`, results });
});

// Export template(s) - returns file content with metadata
app.post('/api/files/export', (req, res) => {
    const { filepaths } = req.body; // Array of filepaths
    if (!filepaths || !Array.isArray(filepaths)) return res.status(400).json({ error: 'Filepaths array required' });

    const exports = [];
    filepaths.forEach(filepath => {
        const fullPath = path.join(LIBRARY_PATH, filepath);
        const metaPath = fullPath.replace('.html', '.meta.json');

        if (!fs.existsSync(fullPath)) return;

        let content = '';
        let meta = {};
        try { content = fs.readFileSync(fullPath, 'utf8'); } catch (e) { }
        try { meta = JSON.parse(fs.readFileSync(metaPath, 'utf8')); } catch (e) { }

        const filename = path.basename(filepath);
        exports.push({ filename, filepath, content, meta });
    });

    res.json({ exports });
});

// NEW: Save bundled export to local disk (easier for user to find)
app.post('/api/export/save-to-disk', (req, res) => {
    const { filename, content } = req.body;
    if (!filename || !content) return res.status(400).json({ error: 'Filename and content required' });

    const EXPORT_DIR = path.join(__dirname, 'exports');
    if (!fs.existsSync(EXPORT_DIR)) fs.mkdirSync(EXPORT_DIR);

    const filePath = path.join(EXPORT_DIR, filename);

    fs.writeFile(filePath, content, (err) => {
        if (err) return res.status(500).json({ error: 'Failed to write file' });
        res.json({ message: 'Saved to exports', path: filePath });
    });
});

// --- SANITIZER ENDPOINTS ---

app.post('/api/sanitize/preview', (req, res) => {
    const { content } = req.body;
    if (!content) return res.status(400).send('No content provided');
    try {
        const sanitized = sanitizer.sanitizeTemplate(content);
        res.json({ sanitized });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

app.post('/api/sanitize/batch', (req, res) => {
    try {
        const files = fs.readdirSync(LEGACY_IMPORT_PATH);
        const results = [];

        files.forEach(file => {
            if (file.endsWith('.html') || file.endsWith('.txt')) {
                const inputPath = path.join(LEGACY_IMPORT_PATH, file);
                const result = sanitizer.processFile(inputPath, READY_EXPORT_PATH);
                results.push(result);
            }
        });

        res.json({
            message: `Processed ${files.length} files.`,
            results
        });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

app.listen(PORT, () => console.log(`Server v3.5 running on ${PORT}`));