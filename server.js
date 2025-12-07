const express = require('express');
const fs = require('fs');
const path = require('path');
const cors = require('cors');
const { exec } = require('child_process');
const app = express();
const PORT = 5000;
const LIBRARY_PATH = path.join(__dirname, '../company-portal/library');
const RESOURCES_PATH = path.join(__dirname, '../company-portal/resources');

app.use(cors());
app.use(express.json());
app.use('/resources', express.static(RESOURCES_PATH));

[LIBRARY_PATH, RESOURCES_PATH].forEach(dir => { if (!fs.existsSync(dir)) fs.mkdirSync(dir); });

const getFilesRecursively = (dir, fileList = []) => {
    const files = fs.readdirSync(dir);
    files.forEach(file => {
        if (file === '.git') return;
        const filePath = path.join(dir, file);
        if (fs.statSync(filePath).isDirectory()) {
            getFilesRecursively(filePath, fileList);
        } else if (file.endsWith('.html')) {
            fileList.push(path.relative(LIBRARY_PATH, filePath));
        }
    });
    return fileList;
};

app.get('/api/init', (req, res) => {
    try {
        const files = getFilesRecursively(LIBRARY_PATH);
        const resourceFiles = fs.readdirSync(RESOURCES_PATH);
        const cssFiles = resourceFiles.filter(f => f.endsWith('.css'));
        const htmlFiles = resourceFiles.filter(f => f.endsWith('.html'));
        let testData = {}, snippets = [];
        try { testData = JSON.parse(fs.readFileSync(path.join(RESOURCES_PATH, 'test_data.json'), 'utf8')); } catch (e) { }
        try { snippets = JSON.parse(fs.readFileSync(path.join(RESOURCES_PATH, 'snippets.json'), 'utf8')); } catch (e) { }
        res.json({ files, cssFiles, htmlFiles, testData, snippets });
    } catch (err) { res.status(500).json({ error: 'Init failed' }); }
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
    fs.readFile(path.join(RESOURCES_PATH, req.body.filename), 'utf8', (err, content) => {
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

app.post('/api/files/delete', (req, res) => {
    const fullPath = path.join(LIBRARY_PATH, req.body.filepath);
    if (!fullPath.startsWith(LIBRARY_PATH)) return res.status(403).json({ error: 'Forbidden' });
    fs.unlink(fullPath, () => {
        const metaPath = fullPath.replace('.html', '.meta.json');
        if (fs.existsSync(metaPath)) fs.unlinkSync(metaPath);
        res.json({ message: 'Deleted' });
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

    const uncatPath = path.join(LIBRARY_PATH, 'Uncategorized');
    if (!fs.existsSync(uncatPath)) fs.mkdirSync(uncatPath, { recursive: true });

    // Move all files to Uncategorized
    const files = fs.readdirSync(catPath);
    files.forEach(file => {
        const oldFilePath = path.join(catPath, file);
        const newFilePath = path.join(uncatPath, file);
        if (fs.statSync(oldFilePath).isFile()) {
            fs.renameSync(oldFilePath, newFilePath);
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
        const filepath = path.join(category, filename);
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

app.listen(PORT, () => console.log(`Server v3.4 running on ${PORT}`));