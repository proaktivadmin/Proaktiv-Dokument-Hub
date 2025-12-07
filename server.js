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

app.listen(PORT, () => console.log(`Server v3.1 running on ${PORT}`));