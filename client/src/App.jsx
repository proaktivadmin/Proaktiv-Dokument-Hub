import React, { useState, useEffect, useMemo, useRef } from 'react';
import Editor from '@monaco-editor/react';
import { Folder, FileCode, GitBranch, ChevronRight, ChevronDown, LayoutTemplate, Smartphone, Monitor, FileText, Download, AlertTriangle, GripVertical, Settings, Play, Save, Search, Command, Activity, Box, Type, Hash, Mail, Phone, User, MapPin, MoreHorizontal, Code, Tag, Plus, Check, Pencil, Trash2, FolderPlus, X, Upload, FileUp, FileDown, Copy, Clock } from 'lucide-react';

const API_URL = 'http://localhost:5000/api';
const DEFAULT_META = { category: 'General', receiver: 'Systemstandard', output: 'PDF og e-post', assignmentType: '', phase: '', subject: 'Oppgjørsoppstilling [[eiendom.adresse]]', cssVersion: 'style.css', headerTemplate: '', footerTemplate: '', marginTop: 2, marginBottom: 2, marginLeft: 2, marginRight: 2 };

// --- PREMIUM COMPONENTS ---

const GlassInput = ({ label, icon: Icon, value, onChange, placeholder, warning }) => {
  const [focused, setFocused] = useState(false);
  const hasValue = value && value.length > 0;

  return (
    <div className="relative pt-4 mb-2 group">
      <div className={`absolute bottom-0 left-0 right-0 h-[1px] bg-white/10 transition-all duration-300 ${focused ? 'bg-gradient-to-r from-cyan-400 to-blue-500 h-[2px]' : ''}`}></div>
      <div className="flex items-center">
        {Icon && <Icon size={14} className={`mr-3 transition-colors duration-300 ${focused ? 'text-cyan-400' : 'text-slate-600'}`} />}
        <input
          type="text"
          value={value}
          onChange={onChange}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          className="bg-transparent border-none outline-none text-sm text-slate-200 w-full py-2 font-medium"
        />
      </div>
      <label className={`absolute left-0 transition-all duration-300 pointer-events-none ${focused || hasValue ? 'top-0 text-[10px] text-cyan-400 font-bold uppercase tracking-wider' : 'top-6 text-sm text-slate-500 ml-7'}`}>
        {label}
      </label>
      {warning && <div className="absolute right-0 top-6 text-orange-400 animate-pulse"><AlertTriangle size={14} /></div>}
    </div>
  );
};

const GlassSelect = ({ label, icon: Icon, value, onChange, options, placeholder }) => {
  const [focused, setFocused] = useState(false);
  const hasValue = value && value.length > 0;

  return (
    <div className="relative pt-4 mb-2 group">
      <div className={`absolute bottom-0 left-0 right-0 h-[1px] bg-white/10 transition-all duration-300 ${focused ? 'bg-gradient-to-r from-purple-400 to-pink-500 h-[2px]' : ''}`}></div>
      <div className="flex items-center relative">
        {Icon && <Icon size={14} className={`mr-3 transition-colors duration-300 ${focused ? 'text-purple-400' : 'text-slate-600'}`} />}
        <select
          value={value}
          onChange={onChange}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          className="bg-transparent border-none outline-none text-sm text-slate-200 w-full py-2 font-medium appearance-none cursor-pointer relative z-10"
        >
          {placeholder && <option value="" className="bg-slate-900">{placeholder}</option>}
          {options.map(opt => <option key={opt} value={opt} className="bg-slate-900 text-slate-200">{opt}</option>)}
        </select>
        <ChevronDown size={14} className="absolute right-0 text-slate-600 pointer-events-none" />
      </div>
      <label className={`absolute left-0 transition-all duration-300 pointer-events-none ${focused || hasValue ? 'top-0 text-[10px] text-purple-400 font-bold uppercase tracking-wider' : 'top-6 text-sm text-slate-500 ml-7'}`}>
        {label}
      </label>
    </div>
  );
};

const Resizer = ({ onMouseDown }) => (
  <div
    className="w-4 flex items-center justify-center cursor-col-resize group hover:scale-110 transition-transform"
    onMouseDown={onMouseDown}
  >
    <div className="w-1 h-8 rounded-full bg-white/10 group-hover:bg-cyan-400/50 transition-colors"></div>
  </div>
);

const DeviceSkin = ({ mode, children, subject, to }) => {
  if (mode === 'mobile') return (
    <div className="relative mx-auto border-gray-900 bg-gray-900 border-[12px] rounded-[3rem] h-[680px] w-[340px] shadow-2xl ring-1 ring-white/10 transition-all duration-500 ease-out hover:scale-[1.02]">
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-32 h-6 bg-black rounded-b-2xl z-20"></div>
      <div className="rounded-[2.4rem] overflow-hidden w-full h-full bg-white flex flex-col relative z-10">
        <div className="bg-[#f2f2f7]/90 backdrop-blur-md px-5 py-4 border-b border-gray-300/50 pt-10">
          <div className="text-black font-bold text-sm truncate tracking-tight">From: Adrian</div>
          <div className="text-gray-500 text-xs truncate">Subject: {subject}</div>
        </div>
        <div className="flex-1 overflow-auto bg-white">{children}</div>
      </div>
    </div>
  );
  if (mode === 'desktop') return (
    <div className="w-[960px] h-[680px] bg-white rounded-xl shadow-2xl flex flex-col overflow-hidden border border-slate-200/50 mx-auto ring-1 ring-black/5 transition-all duration-500 ease-out hover:scale-[1.01]">
      <div className="bg-[#0078d4] h-10 flex items-center px-4 text-white text-xs font-bold shadow-sm justify-between shrink-0">
        <span>Outlook</span>
        <div className="flex gap-1.5"><div className="w-2.5 h-2.5 rounded-full bg-white/20"></div><div className="w-2.5 h-2.5 rounded-full bg-white/20"></div></div>
      </div>
      <div className="bg-[#f8f9fa] border-b border-gray-200 p-4 space-y-2 shrink-0">
        <div className="flex gap-3 text-sm text-gray-700 items-center"><span className="w-12 text-right text-gray-500 text-xs uppercase tracking-wider font-semibold">Subject</span> <span className="font-medium bg-white px-3 py-1 rounded border border-gray-200 flex-1 shadow-sm">{subject}</span></div>
      </div>
      <div className="flex-1 relative bg-white">
        <div className="absolute inset-0 overflow-auto custom-scrollbar">
          {children}
        </div>
      </div>
    </div>
  );
  // A4 mode - use auto height to show full document, min-height ensures at least one page visible
  return (
    <div className="bg-white w-[210mm] shadow-2xl mx-auto relative ring-1 ring-black/5 transition-all duration-500 ease-out">
      <div className="min-h-[297mm]">{children}</div>
      <div className="absolute top-[1123px] left-0 w-full border-b-2 border-red-300 border-dashed opacity-50 pointer-events-none"></div>
    </div>
  );
};

function App() {
  const [initData, setInitData] = useState({ files: [], cssFiles: [], htmlFiles: [], testData: {}, snippets: [] });
  const [selectedPath, setSelectedPath] = useState(null);
  const [content, setContent] = useState('');
  const [meta, setMeta] = useState(DEFAULT_META);
  const [activeResources, setActiveResources] = useState({ header: '', footer: '' });
  const [variableOverrides, setVariableOverrides] = useState({});
  const [expandedFolders, setExpandedFolders] = useState({});
  const [status, setStatus] = useState('');
  const [leftTab, setLeftTab] = useState('files');
  const [rightTab, setRightTab] = useState('preview');
  const [viewMode, setViewMode] = useState('a4');
  const [searchQuery, setSearchQuery] = useState('');

  // RESIZE STATE
  const [leftWidth, setLeftWidth] = useState(320);
  const [rightWidth, setRightWidth] = useState(500);
  const [resizing, setResizing] = useState(null); // 'left' | 'right' | null

  // TEMPLATE MANAGEMENT
  const [templateModal, setTemplateModal] = useState(null); // { type: 'rename' | 'delete' | 'duplicate', path: string, name: string }
  const [templateInput, setTemplateInput] = useState('');

  // PREVIEW SCALING
  const previewContainerRef = useRef(null);
  const [scale, setScale] = useState(1);

  // RECENT FILES (persist to localStorage)
  const [recentFiles, setRecentFiles] = useState(() => {
    try { return JSON.parse(localStorage.getItem('htmlhub_recent') || '[]'); } catch { return []; }
  });
  const searchInputRef = useRef(null);

  // CATEGORY MANAGEMENT
  const [categoryModal, setCategoryModal] = useState(null); // { type: 'create' | 'rename' | 'delete', category?: string }
  const [categoryInput, setCategoryInput] = useState('');

  const handleCategoryCreate = async () => {
    if (!categoryInput.trim()) return;
    await fetch(`${API_URL}/categories/create`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: categoryInput.trim() })
    });
    setCategoryModal(null); setCategoryInput(''); fetchInit();
    setStatus('Category created'); setTimeout(() => setStatus(''), 2000);
  };

  const handleCategoryRename = async () => {
    if (!categoryInput.trim() || !categoryModal?.category) return;
    await fetch(`${API_URL}/categories/rename`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ oldName: categoryModal.category, newName: categoryInput.trim() })
    });
    setCategoryModal(null); setCategoryInput(''); fetchInit();
    setStatus('Category renamed'); setTimeout(() => setStatus(''), 2000);
  };

  const handleCategoryDelete = async () => {
    if (!categoryModal?.category) return;
    await fetch(`${API_URL}/categories/delete`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: categoryModal.category })
    });
    setCategoryModal(null); fetchInit();
    setStatus('Category deleted'); setTimeout(() => setStatus(''), 2000);
  };

  // IMPORT/EXPORT
  const [importModal, setImportModal] = useState(false);
  const [importFiles, setImportFiles] = useState([]); // Array of { name, content, category, tags }
  const fileInputRef = useRef(null);

  const handleFileSelect = async (e) => {
    const files = Array.from(e.target.files);
    const newFiles = await Promise.all(files.map(async (file) => {
      const content = await file.text();
      return { name: file.name, content, category: 'Uncategorized', tags: '' };
    }));
    setImportFiles([...importFiles, ...newFiles]);
  };

  const handleImport = async () => {
    if (importFiles.length === 0) return;
    const payload = importFiles.map(f => ({
      filename: f.name,
      content: f.content,
      category: f.category,
      tags: f.tags.split(',').map(t => t.trim()).filter(Boolean)
    }));
    await fetch(`${API_URL}/files/import`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ files: payload })
    });
    setImportModal(false); setImportFiles([]); fetchInit();
    setStatus(`Imported ${payload.length} file(s)`); setTimeout(() => setStatus(''), 2000);
  };

  const handleExport = async () => {
    if (!selectedPath) return;
    const res = await fetch(`${API_URL}/files/export`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ filepaths: [selectedPath] })
    });
    const data = await res.json();
    if (data.exports && data.exports.length > 0) {
      const exp = data.exports[0];
      const blob = new Blob([exp.content], { type: 'text/html' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url; a.download = exp.filename; a.click();
      URL.revokeObjectURL(url);
      setStatus('Exported'); setTimeout(() => setStatus(''), 2000);
    }
  };

  useEffect(() => {
    if (!previewContainerRef.current) return;

    const observer = new ResizeObserver((entries) => {
      for (const entry of entries) {
        const width = entry.contentRect.width;
        const padding = 40;
        let contentWidth = 840; // A4 default
        if (viewMode === 'mobile') contentWidth = 380;
        if (viewMode === 'desktop') contentWidth = 1000;

        const s = Math.min(1, (width - padding) / contentWidth);
        setScale(s);
      }
    });

    observer.observe(previewContainerRef.current);
    return () => observer.disconnect();
  }, [viewMode]);

  const editorRef = useRef(null);

  useEffect(() => { fetchInit(); }, []);
  useEffect(() => {
    const loadRes = async () => {
      const hRes = await fetch(`${API_URL}/resources/read`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ filename: meta.headerTemplate }) });
      const fRes = await fetch(`${API_URL}/resources/read`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ filename: meta.footerTemplate }) });
      setActiveResources({ header: (await hRes.json()).content, footer: (await fRes.json()).content });
    };
    if (selectedPath) loadRes();
  }, [meta.headerTemplate, meta.footerTemplate, selectedPath]);

  useEffect(() => {
    const handleMM = (e) => {
      if (resizing === 'left') {
        setLeftWidth(Math.max(250, Math.min(500, e.clientX)));
      }
      if (resizing === 'right') {
        // rightWidth = distance from mouse to right edge of window
        // Smaller value = larger editor, larger value = larger preview
        const newWidth = window.innerWidth - e.clientX - 16; // 16px for padding
        setRightWidth(Math.max(280, Math.min(900, newWidth)));
      }
    };
    const handleMU = () => setResizing(null);
    if (resizing) {
      window.addEventListener('mousemove', handleMM);
      window.addEventListener('mouseup', handleMU);
    }
    return () => {
      window.removeEventListener('mousemove', handleMM);
      window.removeEventListener('mouseup', handleMU);
    };
  }, [resizing]);

  // KEYBOARD SHORTCUTS
  useEffect(() => {
    const handleKeyDown = (e) => {
      // Ignore if typing in input/textarea
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
        if (e.key === 'Escape') { e.target.blur(); setSearchQuery(''); }
        return;
      }

      if (e.ctrlKey && e.key === 's') {
        e.preventDefault();
        if (e.shiftKey) handleSave(true); // Ctrl+Shift+S = new version
        else handleSave(false); // Ctrl+S = save
      }
      if (e.ctrlKey && e.key === 'f') {
        e.preventDefault();
        searchInputRef.current?.focus();
      }
      if (e.ctrlKey && e.key === 'd' && selectedPath) {
        e.preventDefault();
        const parts = selectedPath.split(/[/\\]/);
        const filename = parts[parts.length - 1].replace('.html', '');
        setTemplateModal({ type: 'duplicate', path: selectedPath, name: filename });
        setTemplateInput(filename + '-copy');
      }
      if (e.key === 'Escape') {
        setCategoryModal(null);
        setTemplateModal(null);
        setImportModal(false);
        setSearchQuery('');
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [selectedPath]);

  // Persist recent files to localStorage
  useEffect(() => {
    localStorage.setItem('htmlhub_recent', JSON.stringify(recentFiles));
  }, [recentFiles]);

  const fetchInit = async () => setInitData(await (await fetch(`${API_URL}/init`)).json());

  // Template rename/delete handlers
  const handleTemplateRename = async () => {
    if (!templateInput.trim() || !templateModal?.path) return;
    const oldPath = templateModal.path;
    const parts = oldPath.split(/[/\\]/);
    parts.pop();
    const newPath = parts.length > 0 ? `${parts.join('/')}/${templateInput.trim()}.html` : `${templateInput.trim()}.html`;
    // Read content, save to new path, delete old
    const res = await fetch(`${API_URL}/files/read`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ filepath: oldPath }) });
    const data = await res.json();
    await fetch(`${API_URL}/files/save`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ filepath: newPath, content: data.content, meta: data.meta }) });
    await fetch(`${API_URL}/files/delete`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ filepath: oldPath }) });
    setTemplateModal(null); setTemplateInput(''); fetchInit();
    if (selectedPath === oldPath) setSelectedPath(newPath);
    setStatus('Template renamed'); setTimeout(() => setStatus(''), 2000);
  };

  const handleTemplateDelete = async () => {
    if (!templateModal?.path) return;
    await fetch(`${API_URL}/files/delete`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ filepath: templateModal.path }) });
    if (selectedPath === templateModal.path) { setSelectedPath(null); setContent(''); }
    setTemplateModal(null); fetchInit();
    setStatus('Template deleted'); setTimeout(() => setStatus(''), 2000);
  };

  const handleTemplateDuplicate = async () => {
    if (!templateInput.trim() || !templateModal?.path) return;
    const srcPath = templateModal.path;
    const parts = srcPath.split(/[/\\]/);
    parts.pop();
    const newPath = parts.length > 0 ? `${parts.join('/')}/${templateInput.trim()}.html` : `${templateInput.trim()}.html`;
    // Read source content, save to new path
    const res = await fetch(`${API_URL}/files/read`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ filepath: srcPath }) });
    const data = await res.json();
    await fetch(`${API_URL}/files/save`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ filepath: newPath, content: data.content, meta: data.meta }) });
    setTemplateModal(null); setTemplateInput(''); fetchInit();
    setStatus('Template duplicated'); setTimeout(() => setStatus(''), 2000);
    loadFile(newPath); // Load the new duplicate
  };

  // Auto-add variable with demo value
  const autoAddVariable = async (key) => {
    // Generate demo value based on key name
    let demoValue = 'Demo Value';
    if (key.includes('navn')) demoValue = 'Ola Nordmann';
    else if (key.includes('adresse') || key.includes('gatenavnognr')) demoValue = 'Storgata 1';
    else if (key.includes('postnr')) demoValue = '0000';
    else if (key.includes('poststed') || key.includes('sted')) demoValue = 'Oslo';
    else if (key.includes('tlf') || key.includes('telefon')) demoValue = '900 00 000';
    else if (key.includes('epost') || key.includes('email')) demoValue = 'demo@example.no';
    else if (key.includes('pris') || key.includes('sum') || key.includes('belop')) demoValue = '100 000,-';
    else if (key.includes('prosent')) demoValue = '2,5%';
    else if (key.includes('dato')) demoValue = new Date().toLocaleDateString('nb-NO');
    else if (key.includes('nr') || key.includes('nummer')) demoValue = '12345';
    else if (key.includes('orgnr')) demoValue = '999 999 999';
    else if (key.includes('tittel')) demoValue = 'Eiendomsmegler';
    else if (key.includes('kommune')) demoValue = 'Oslo';
    else if (key.includes('boligtype')) demoValue = 'Leilighet';

    await fetch(`${API_URL}/variables/add`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ key, value: demoValue })
    });
    fetchInit();
    setStatus(`Added: ${key} = "${demoValue}"`); setTimeout(() => setStatus(''), 3000);
  };

  const loadFile = async (filepath) => {
    const data = await (await fetch(`${API_URL}/files/read`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ filepath }) })).json();
    setSelectedPath(filepath); setContent(data.content); setMeta({ ...DEFAULT_META, ...data.meta }); setVariableOverrides({}); setRightTab('preview');
    // Track in recent files (max 5, no duplicates)
    setRecentFiles(prev => {
      const filtered = prev.filter(p => p !== filepath);
      return [filepath, ...filtered].slice(0, 5);
    });
  };

  const handleSave = async (asNewVersion) => {
    if (!selectedPath) return;
    let savePath = selectedPath;
    if (asNewVersion) {
      const parts = selectedPath.split(/[/\\]/);
      const filename = parts.pop();
      const match = filename.match(/(.*)\.v(\d+)\.html$/);
      let newName = match ? `${match[1]}.v${parseInt(match[2]) + 1}.html` : `${filename.replace('.html', '')}.v2.html`;
      savePath = parts.join('/') ? `${parts.join('/')}/${newName}` : newName;
    }
    await fetch(`${API_URL}/files/save`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ filepath: savePath, content, meta }) });
    setStatus('Saved'); fetchInit(); if (asNewVersion) setSelectedPath(savePath); setTimeout(() => setStatus(''), 2000);
  };

  const insertSnippet = (code) => { editorRef.current.executeEdits("snippet", [{ range: editorRef.current.getSelection(), text: code }]); editorRef.current.focus(); };
  const gitAction = async (act) => { setStatus('Git...'); await fetch(`${API_URL}/git/${act}`, { method: 'POST' }); setStatus('Done'); setTimeout(() => setStatus(''), 2000); };

  const fileTree = useMemo(() => {
    const tree = {};
    const query = searchQuery.toLowerCase().trim();
    initData.files.forEach(path => {
      // Filter by search query
      if (query && !path.toLowerCase().includes(query)) return;

      const parts = path.split(/[/\\]/);
      let cat = parts.length > 1 ? parts[0] : 'Uncategorized';
      let fn = parts[parts.length - 1];
      if (!tree[cat]) tree[cat] = {};
      const match = fn.match(/(.*)\.v(\d+)\.html$/);
      let base = match ? match[1] : fn.replace('.html', '');
      let ver = match ? parseInt(match[2]) : 1;
      if (!tree[cat][base]) tree[cat][base] = [];
      tree[cat][base].push({ path, ver });
    });
    return tree;
  }, [initData.files, searchQuery]);

  const detectedTags = useMemo(() => (content.match(/\[\[(.*?)\]\]/g) || []).map(t => t.replace(/\[|\]/g, '')), [content]);

  const previewSource = useMemo(() => {
    let inj = content; let subj = meta.subject;
    [...detectedTags, ...((meta.subject.match(/\[\[(.*?)\]\]/g) || []).map(t => t.replace(/\[|\]/g, '')))].forEach(k => {
      const val = variableOverrides[k] || initData.testData[k] || `[[${k}]]`;
      inj = inj.replaceAll(`[[${k}]]`, val); subj = subj.replaceAll(`[[${k}]]`, val);
    });
    const isEmail = viewMode !== 'a4';
    const marginStyles = isEmail ? 'padding:0;' : `padding:${meta.marginTop}cm ${meta.marginRight}cm ${meta.marginBottom}cm ${meta.marginLeft}cm;`;
    return `<!DOCTYPE html><html style="height:100%;min-height:100%;"><head><link rel="stylesheet" href="http://localhost:5000/resources/${meta.cssVersion}"><style>html,body{min-height:100%;height:auto;}body{font-family:sans-serif;background:white;margin:0;${marginStyles}}</style></head><body>${activeResources.header}${inj}${activeResources.footer}</body></html>`;
  }, [content, meta, activeResources, variableOverrides, viewMode, initData.testData, detectedTags]);

  const getIconForTag = (tag) => {
    if (tag.includes('navn')) return User;
    if (tag.includes('adresse') || tag.includes('sted')) return MapPin;
    if (tag.includes('tlf')) return Phone;
    if (tag.includes('email') || tag.includes('epost')) return Mail;
    if (tag.includes('nr')) return Hash;
    return Type;
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden relative font-sans text-slate-200 select-none">
      <div className="aurora-bg"></div>

      {/* FLOATING LAYOUT CONTAINER */}
      <div className="relative z-10 flex w-full h-full p-4 gap-2">

        {/* LEFT ISLAND: NAVIGATION & FILES */}
        <div className="flex flex-col gap-4 shrink-0 animate-fade-in-up" style={{ width: leftWidth, animationDelay: '0.1s' }}>
          {/* BRAND HEADER */}
          <div className="glass-panel rounded-2xl p-4 flex items-center justify-between group cursor-default transition-all hover:border-white/20">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-lg shadow-lg shadow-cyan-500/20 group-hover:shadow-cyan-500/40 transition-all duration-500">
                <LayoutTemplate className="text-white" size={18} />
              </div>
              <div>
                <h1 className="font-bold text-base tracking-tight text-white">HTML Hub</h1>
                <div className="text-[9px] font-medium text-cyan-400 tracking-widest uppercase opacity-80">Premium</div>
              </div>
            </div>
            <MoreHorizontal size={16} className="text-slate-500 hover:text-white cursor-pointer" />
          </div>

          {/* FILE EXPLORER */}
          <div className="flex-1 glass-panel rounded-2xl flex flex-col overflow-hidden relative">
            {/* TABS */}
            <div className="flex p-1.5 gap-1 border-b border-white/5">
              <button onClick={() => setLeftTab('files')} className={`flex-1 py-2 text-[10px] font-bold rounded-lg transition-all duration-300 ${leftTab === 'files' ? 'bg-white/10 text-white shadow-inner' : 'text-slate-500 hover:text-slate-300 hover:bg-white/5'}`}>FILES</button>
              <button onClick={() => setLeftTab('snippets')} className={`flex-1 py-2 text-[10px] font-bold rounded-lg transition-all duration-300 ${leftTab === 'snippets' ? 'bg-white/10 text-white shadow-inner' : 'text-slate-500 hover:text-slate-300 hover:bg-white/5'}`}>SNIPPETS</button>
            </div>

            <div className="flex-1 overflow-y-auto p-3 space-y-4 custom-scrollbar">
              {leftTab === 'files' ? <>
                {/* RECENT FILES */}
                {recentFiles.length > 0 && (
                  <div className="mb-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-1">
                        <Clock size={10} className="text-amber-400" />
                        <span className="text-[10px] font-bold text-amber-400 uppercase tracking-widest">Recent</span>
                      </div>
                      <button onClick={() => setRecentFiles([])} className="text-[9px] text-slate-600 hover:text-slate-400">Clear</button>
                    </div>
                    <div className="space-y-1">
                      {recentFiles.filter(p => initData.files.includes(p)).map(p => {
                        const name = p.split(/[/\\]/).pop();
                        return (
                          <button key={p} onClick={() => loadFile(p)} className={`w-full text-left px-3 py-2 text-xs rounded-lg transition-all flex items-center gap-2 ${selectedPath === p ? 'bg-amber-500/10 text-amber-300 border border-amber-500/20' : 'text-slate-400 hover:bg-white/5 hover:text-slate-200'}`}>
                            <FileText size={10} className="text-amber-400/70" />
                            <span className="truncate">{name}</span>
                          </button>
                        );
                      })}
                    </div>
                  </div>
                )}
                {/* NEW CATEGORY BUTTON */}
                <button
                  onClick={() => { setCategoryModal({ type: 'create' }); setCategoryInput(''); }}
                  className="w-full flex items-center justify-center gap-2 py-2 text-[10px] font-bold text-slate-500 hover:text-cyan-400 border border-dashed border-slate-700 hover:border-cyan-500/50 rounded-lg transition-all mb-2"
                >
                  <FolderPlus size={12} /> New Category
                </button>
                {/* IMPORT BUTTON */}
                <button
                  onClick={() => setImportModal(true)}
                  className="w-full flex items-center justify-center gap-2 py-2 text-[10px] font-bold text-slate-500 hover:text-emerald-400 border border-dashed border-slate-700 hover:border-emerald-500/50 rounded-lg transition-all mb-2"
                >
                  <FileUp size={12} /> Import Templates
                </button>
                {Object.keys(fileTree).map(cat => (
                  <div key={cat}>
                    <div className="flex items-center justify-between cursor-pointer group mb-2">
                      <div onClick={() => setExpandedFolders(p => ({ ...p, [cat]: !p[cat] }))} className="flex-1 flex items-center gap-1">
                        <ChevronDown size={12} className={`text-slate-600 transition-transform duration-300 ${expandedFolders[cat] ? 'rotate-180' : ''}`} />
                        <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest group-hover:text-cyan-400 transition-colors">{cat}</span>
                      </div>
                      {cat !== 'Uncategorized' && (
                        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                          <button
                            onClick={(e) => { e.stopPropagation(); setCategoryModal({ type: 'rename', category: cat }); setCategoryInput(cat); }}
                            className="p-1 rounded hover:bg-white/10 text-slate-500 hover:text-cyan-400" title="Rename"
                          ><Pencil size={10} /></button>
                          <button
                            onClick={(e) => { e.stopPropagation(); setCategoryModal({ type: 'delete', category: cat }); }}
                            className="p-1 rounded hover:bg-white/10 text-slate-500 hover:text-red-400" title="Delete"
                          ><Trash2 size={10} /></button>
                        </div>
                      )}
                    </div>

                    {expandedFolders[cat] && <div className="space-y-1">
                      {Object.keys(fileTree[cat]).map(base => (
                        <div key={base} className="group/item">
                          {fileTree[cat][base].sort((a, b) => b.ver - a.ver).map((f, i) => (
                            <div key={f.path} className="flex items-center gap-1 mb-1 group/file">
                              <button onClick={() => loadFile(f.path)} className={`flex-1 text-left px-4 py-3 text-xs rounded-xl transition-all relative overflow-hidden group/btn flex items-center justify-between border backdrop-blur-sm ${selectedPath === f.path ? 'bg-cyan-500/10 border-cyan-500/20 text-cyan-200' : 'bg-transparent border-transparent text-slate-400 hover:bg-white/5 hover:border-white/10 hover:text-slate-200 hover:shadow-lg hover:-translate-y-0.5'}`}>
                                {selectedPath === f.path && <div className="absolute left-0 top-0 bottom-0 w-0.5 bg-cyan-400 shadow-[0_0_10px_rgba(34,211,238,0.5)]"></div>}
                                <div className="flex items-center gap-2">
                                  <FileText size={12} className={selectedPath === f.path ? 'text-cyan-400' : 'text-slate-600'} />
                                  <span>{base} <span className="opacity-50 text-[10px]">v{f.ver}</span></span>
                                </div>
                                {i === 0 && <div className="w-1.5 h-1.5 rounded-full bg-cyan-500 shadow-[0_0_5px_rgba(6,182,212,0.5)]"></div>}
                              </button>
                              {/* Template Actions */}
                              <div className="flex items-center gap-0.5 opacity-0 group-hover/file:opacity-100 transition-opacity">
                                <button
                                  onClick={() => { setTemplateModal({ type: 'duplicate', path: f.path, name: base }); setTemplateInput(base + '-copy'); }}
                                  className="p-1.5 rounded hover:bg-white/10 text-slate-500 hover:text-emerald-400" title="Duplicate (Ctrl+D)"
                                ><Copy size={10} /></button>
                                <button
                                  onClick={() => { setTemplateModal({ type: 'rename', path: f.path, name: base }); setTemplateInput(base); }}
                                  className="p-1.5 rounded hover:bg-white/10 text-slate-500 hover:text-cyan-400" title="Rename"
                                ><Pencil size={10} /></button>
                                <button
                                  onClick={() => setTemplateModal({ type: 'delete', path: f.path, name: base })}
                                  className="p-1.5 rounded hover:bg-white/10 text-slate-500 hover:text-red-400" title="Delete"
                                ><Trash2 size={10} /></button>
                              </div>
                            </div>
                          ))}
                        </div>
                      ))}
                    </div>}
                  </div>
                ))}
              </> : <div className="space-y-6">
                {/* VARIABLES SECTION */}
                <div className="mb-6">
                  <div className="flex items-center gap-2 mb-4 px-1">
                    <Tag size={12} className="text-cyan-400" />
                    <span className="text-[10px] font-bold text-cyan-400 uppercase tracking-widest">Variables</span>
                  </div>
                  {initData.snippets.filter(grp => grp.category.startsWith('Tags:')).map((grp, i) => (
                    <div key={i} className="mb-4">
                      <h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-3 px-1">{grp.category.replace('Tags: ', '')}</h3>
                      <div className="grid grid-cols-1 gap-2">
                        {grp.items.map(snip => (
                          <button key={snip.label} onClick={() => insertSnippet(snip.code)} className="group glass-panel-hover border-transparent bg-white/5 p-3 rounded-xl text-left transition-all duration-300 hover:border-cyan-500/20">
                            <div className="text-xs font-bold text-slate-300 group-hover:text-white mb-1 flex items-center gap-2"><Type size={12} className="text-cyan-400" /> {snip.label}</div>
                            <div className="text-[10px] text-slate-500 group-hover:text-slate-400 truncate pl-5">{snip.desc}</div>
                          </button>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
                {/* VITEC LOGIC SECTION */}
                <div className="pt-4 border-t border-white/10">
                  <div className="flex items-center gap-2 mb-4 px-1">
                    <Code size={12} className="text-purple-400" />
                    <span className="text-[10px] font-bold text-purple-400 uppercase tracking-widest">Vitec Logic & Layout</span>
                  </div>
                  {initData.snippets.filter(grp => !grp.category.startsWith('Tags:')).map((grp, i) => (
                    <div key={i} className="mb-4">
                      <h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-3 px-1">{grp.category}</h3>
                      <div className="grid grid-cols-1 gap-2">
                        {grp.items.map(snip => (
                          <button key={snip.label} onClick={() => insertSnippet(snip.code)} className="group glass-panel-hover border-transparent bg-white/5 p-3 rounded-xl text-left transition-all duration-300 hover:border-purple-500/20">
                            <div className="text-xs font-bold text-slate-300 group-hover:text-white mb-1 flex items-center gap-2"><Code size={12} className="text-purple-400" /> {snip.label}</div>
                            <div className="text-[10px] text-slate-500 group-hover:text-slate-400 truncate pl-5">{snip.desc}</div>
                          </button>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>}
            </div>

            {/* ACTION BAR */}
            <div className="p-3 border-t border-white/5 flex gap-2 bg-black/20 backdrop-blur-sm">
              <button onClick={() => gitAction('pull')} className="flex-1 bg-slate-800/50 hover:bg-slate-700/80 text-slate-300 text-[10px] font-bold py-2.5 rounded-lg flex gap-2 justify-center items-center transition-all border border-white/5 hover:border-white/20 group"><Download size={12} className="group-hover:-translate-y-0.5 transition-transform" /> Pull</button>
              <button onClick={() => gitAction('push')} className="flex-1 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white text-[10px] font-bold py-2.5 rounded-lg flex gap-2 justify-center items-center transition-all shadow-lg shadow-cyan-900/20 hover:shadow-cyan-500/30 group"><GitBranch size={12} className="group-hover:rotate-12 transition-transform" /> Push</button>
            </div>
          </div>
        </div>

        {/* LEFT RESIZER */}
        <Resizer onMouseDown={() => setResizing('left')} />

        {/* CENTER ISLAND: EDITOR */}
        <div className="flex-1 flex flex-col gap-4 animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
          {/* COMMAND BAR */}
          <div className="glass-panel rounded-full px-4 py-2.5 flex items-center gap-3">
            <Search size={14} className="text-slate-500" />
            <input
              ref={searchInputRef}
              type="text"
              placeholder="Search templates... (Ctrl+F)"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-transparent border-none outline-none text-xs text-slate-300 placeholder:text-slate-600 flex-1 w-full"
            />
            {searchQuery && (
              <button onClick={() => setSearchQuery('')} className="text-slate-500 hover:text-white">
                <X size={12} />
              </button>
            )}
          </div>

          {/* EDITOR PANEL */}
          <div className="flex-1 glass-panel rounded-2xl overflow-hidden relative flex flex-col shadow-2xl">
            {selectedPath ?
              <>
                <div className="h-10 border-b border-white/5 flex items-center justify-between px-4 bg-white/[0.02]">
                  <div className="flex items-center gap-2 text-xs text-slate-400">
                    <FileCode size={14} className="text-cyan-400" />
                    <span className="opacity-50">{selectedPath.split('/').slice(0, -1).join(' / ')} /</span>
                    <span className="text-slate-200 font-medium">{selectedPath.split('/').pop()}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <button onClick={handleExport} className="text-[10px] text-slate-500 hover:text-emerald-400 flex items-center gap-1.5 transition-colors"><FileDown size={12} /> Export</button>
                    <div className="text-[10px] text-slate-600 flex items-center gap-1.5"><div className="w-1.5 h-1.5 rounded-full bg-emerald-500"></div> Saved</div>
                  </div>
                </div>
                <Editor
                  onMount={(editor, monaco) => {
                    editorRef.current = editor;
                    monaco.editor.defineTheme('glass-theme', {
                      base: 'vs-dark',
                      inherit: true,
                      rules: [{ background: '00000000' }],
                      colors: {
                        'editor.background': '#00000000',
                        'minimap.background': '#00000000',
                        'editorGutter.background': '#00000000'
                      }
                    });
                    monaco.editor.setTheme('glass-theme');
                  }}
                  height="100%"
                  defaultLanguage="html"
                  theme="glass-theme"
                  value={content}
                  onChange={setContent}
                  options={{ minimap: { enabled: false }, fontSize: 14, fontFamily: "JetBrains Mono", padding: { top: 24, bottom: 24 }, wordWrap: 'on', scrollBeyondLastLine: false, lineNumbers: 'on', renderLineHighlight: 'all', smoothScrolling: true, cursorBlinking: 'smooth', cursorSmoothCaretAnimation: 'on' }}
                />
              </>
              : <div className="flex-1 flex flex-col items-center justify-center text-slate-600 relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-tr from-cyan-500/5 to-purple-500/5"></div>
                <div className="w-32 h-32 bg-gradient-to-br from-cyan-500/10 to-purple-600/10 rounded-full flex items-center justify-center mb-8 animate-float blur-xl absolute"></div>
                <div className="w-24 h-24 bg-white/5 rounded-3xl flex items-center justify-center mb-6 backdrop-blur-md border border-white/10 shadow-2xl relative z-10">
                  <LayoutTemplate size={40} className="text-slate-400" />
                </div>
                <p className="text-xl font-medium text-slate-400 relative z-10">Select a template</p>
                <p className="text-sm text-slate-600 mt-2 relative z-10">Choose a file from the sidebar to start editing</p>
              </div>}

            {status && <div className="absolute bottom-6 right-6 bg-emerald-500 text-white px-5 py-2.5 rounded-full text-xs font-bold shadow-lg shadow-emerald-500/20 backdrop-blur-md animate-fade-in-up flex items-center gap-2"><Activity size={14} className="animate-spin" /> {status}</div>}
          </div>
        </div>

        {/* RIGHT RESIZER */}
        <Resizer onMouseDown={() => setResizing('right')} />

        {/* RIGHT ISLAND: PREVIEW & TOOLS */}
        <div className="flex flex-col gap-4 shrink-0 animate-fade-in-up" style={{ width: rightWidth, animationDelay: '0.3s' }}>
          {/* TOOLBAR */}
          <div className="glass-panel rounded-2xl p-2 flex items-center justify-between">
            <div className="flex items-center gap-1 bg-black/20 p-1 rounded-xl border border-white/5">
              <button onClick={() => setViewMode('a4')} className={`p-2 rounded-lg transition-all duration-300 ${viewMode === 'a4' ? 'bg-slate-700 text-white shadow-lg' : 'text-slate-500 hover:text-slate-300 hover:bg-white/5'}`}><FileText size={14} /></button>
              <button onClick={() => setViewMode('desktop')} className={`p-2 rounded-lg transition-all duration-300 ${viewMode === 'desktop' ? 'bg-slate-700 text-white shadow-lg' : 'text-slate-500 hover:text-slate-300 hover:bg-white/5'}`}><Monitor size={14} /></button>
              <button onClick={() => setViewMode('mobile')} className={`p-2 rounded-lg transition-all duration-300 ${viewMode === 'mobile' ? 'bg-slate-700 text-white shadow-lg' : 'text-slate-500 hover:text-slate-300 hover:bg-white/5'}`}><Smartphone size={14} /></button>
            </div>
            <div className="flex gap-2">
              <button onClick={() => handleSave(false)} className="text-[10px] font-bold bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 border border-cyan-500/20 px-3 py-1.5 rounded-lg transition-all flex items-center gap-2 hover:shadow-lg hover:shadow-cyan-500/10"><Save size={12} /> Save</button>
              <button onClick={() => handleSave(true)} className="text-[10px] font-bold bg-purple-500/10 hover:bg-purple-500/20 text-purple-400 border border-purple-500/20 px-3 py-1.5 rounded-lg transition-all flex items-center gap-2 hover:shadow-lg hover:shadow-purple-500/10"><GitBranch size={12} /> +Ver</button>
            </div>
          </div>

          {/* PREVIEW AREA */}
          <div className="flex-1 glass-panel rounded-2xl overflow-hidden flex flex-col relative shadow-2xl">
            <div ref={previewContainerRef} className="flex-1 bg-black/20 overflow-auto flex justify-center p-8 relative custom-scrollbar">
              <div style={{ transform: `scale(${scale})`, transformOrigin: 'top center' }} className="transition-transform duration-300 ease-out">
                <DeviceSkin mode={viewMode} subject={meta.subject} to={initData.testData['kjøper.navn'] || 'Receiver'}>
                  <iframe
                    title="preview"
                    srcDoc={previewSource}
                    className="border-none bg-white"
                    style={{
                      width: viewMode === 'a4' ? '210mm' : '100%',
                      height: viewMode === 'a4' ? '297mm' : '100%',
                      minHeight: viewMode === 'a4' ? '297mm' : 'auto'
                    }}
                    sandbox="allow-scripts"
                  />
                </DeviceSkin>
              </div>
            </div>

            {/* SETTINGS PANEL */}
            <div className="bg-slate-900/80 backdrop-blur-xl border-t border-white/5 max-h-[40%] flex flex-col">
              <div className="flex border-b border-white/5">
                <button onClick={() => setRightTab('preview')} className={`flex-1 py-3 text-[10px] font-bold tracking-wide transition-all ${rightTab === 'preview' ? 'text-cyan-400 border-b-2 border-cyan-400 bg-white/5' : 'text-slate-500 hover:text-slate-300'}`}>SIMULATOR</button>
                <button onClick={() => setRightTab('settings')} className={`flex-1 py-3 text-[10px] font-bold tracking-wide transition-all ${rightTab === 'settings' ? 'text-purple-400 border-b-2 border-purple-400 bg-white/5' : 'text-slate-500 hover:text-slate-300'}`}>SETTINGS</button>
              </div>
              <div className="flex-1 overflow-y-auto p-6 custom-scrollbar">
                {rightTab === 'preview' ? <div className="space-y-4">
                  {detectedTags.length === 0 && <div className="text-center text-slate-500 py-8 text-sm flex flex-col items-center gap-2"><AlertTriangle className="opacity-20" size={24} /> No tags detected</div>}
                  {detectedTags.map(key => {
                    const isKnown = !!initData.testData[key];
                    const currentValue = variableOverrides[key] || '';
                    return (
                      <div key={key} className="relative">
                        <GlassInput
                          label={key}
                          value={currentValue}
                          onChange={(e) => setVariableOverrides({ ...variableOverrides, [key]: e.target.value })}
                          placeholder={initData.testData[key] || 'No Data'}
                          warning={!isKnown}
                          icon={getIconForTag(key)}
                        />
                        {!isKnown && (
                          <button
                            onClick={() => autoAddVariable(key)}
                            className="absolute right-0 top-4 px-2 py-1 text-[9px] font-bold rounded-md bg-orange-500/10 hover:bg-orange-500/20 text-orange-400 border border-orange-500/20 flex items-center gap-1 transition-all"
                            title="Auto-add with demo value"
                          >
                            <Plus size={10} /> Auto-Add
                          </button>
                        )}
                        {isKnown && (
                          <div className="absolute right-0 top-6 text-emerald-400">
                            <Check size={14} />
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
                  : <div className="space-y-5">
                    <GlassInput
                      label="Subject Line"
                      value={meta.subject}
                      onChange={e => setMeta({ ...meta, subject: e.target.value })}
                      icon={Type}
                    />
                    <div className="grid grid-cols-2 gap-4">
                      <GlassSelect
                        label="Receiver"
                        value={meta.receiver}
                        onChange={e => setMeta({ ...meta, receiver: e.target.value })}
                        options={['Systemstandard', 'Selger', 'Kjøper']}
                        icon={User}
                      />
                      <GlassSelect
                        label="Output"
                        value={meta.output}
                        onChange={e => setMeta({ ...meta, output: e.target.value })}
                        options={['PDF og e-post', 'Kun PDF', 'Kun e-post']}
                        icon={Mail}
                      />
                    </div>
                    <div className="grid grid-cols-3 gap-3 pt-2 border-t border-white/5">
                      {['cssVersion', 'headerTemplate', 'footerTemplate'].map(k => (
                        <GlassSelect
                          key={k}
                          label={k.replace('Template', '')}
                          value={meta[k]}
                          onChange={e => setMeta({ ...meta, [k]: e.target.value })}
                          options={k === 'cssVersion' ? initData.cssFiles : initData.htmlFiles}
                          placeholder="(None)"
                          icon={FileCode}
                        />
                      ))}
                    </div>
                    {/* MARGIN CONTROLS */}
                    <div className="pt-4 border-t border-white/5">
                      <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-3">Page Margins (cm)</div>
                      <div className="grid grid-cols-4 gap-3">
                        <GlassInput
                          label="Top"
                          value={meta.marginTop}
                          onChange={e => setMeta({ ...meta, marginTop: parseFloat(e.target.value) || 0 })}
                          icon={Box}
                        />
                        <GlassInput
                          label="Right"
                          value={meta.marginRight}
                          onChange={e => setMeta({ ...meta, marginRight: parseFloat(e.target.value) || 0 })}
                          icon={Box}
                        />
                        <GlassInput
                          label="Bottom"
                          value={meta.marginBottom}
                          onChange={e => setMeta({ ...meta, marginBottom: parseFloat(e.target.value) || 0 })}
                          icon={Box}
                        />
                        <GlassInput
                          label="Left"
                          value={meta.marginLeft}
                          onChange={e => setMeta({ ...meta, marginLeft: parseFloat(e.target.value) || 0 })}
                          icon={Box}
                        />
                      </div>
                    </div>
                  </div>}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* CATEGORY MODAL */}
      {
        categoryModal && (
          <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center animate-fade-in-up">
            <div className="glass-panel rounded-2xl p-6 w-96 shadow-2xl border border-white/20">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-white">
                  {categoryModal.type === 'create' && 'New Category'}
                  {categoryModal.type === 'rename' && 'Rename Category'}
                  {categoryModal.type === 'delete' && 'Delete Category'}
                </h3>
                <button onClick={() => setCategoryModal(null)} className="text-slate-400 hover:text-white p-1">
                  <X size={18} />
                </button>
              </div>

              {categoryModal.type === 'delete' ? (
                <div>
                  <p className="text-sm text-slate-400 mb-4">
                    Are you sure you want to delete <span className="text-white font-medium">"{categoryModal.category}"</span>?
                    All files will be moved to Uncategorized.
                  </p>
                  <div className="flex gap-3 justify-end">
                    <button onClick={() => setCategoryModal(null)} className="px-4 py-2 text-sm text-slate-400 hover:text-white">Cancel</button>
                    <button onClick={handleCategoryDelete} className="px-4 py-2 text-sm bg-red-500/20 text-red-400 hover:bg-red-500/30 rounded-lg border border-red-500/30">Delete</button>
                  </div>
                </div>
              ) : (
                <div>
                  <input
                    type="text"
                    value={categoryInput}
                    onChange={(e) => setCategoryInput(e.target.value)}
                    placeholder="Category name"
                    className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white text-sm focus:outline-none focus:border-cyan-500/50 mb-4"
                    autoFocus
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        categoryModal.type === 'create' ? handleCategoryCreate() : handleCategoryRename();
                      }
                    }}
                  />
                  <div className="flex gap-3 justify-end">
                    <button onClick={() => setCategoryModal(null)} className="px-4 py-2 text-sm text-slate-400 hover:text-white">Cancel</button>
                    <button
                      onClick={categoryModal.type === 'create' ? handleCategoryCreate : handleCategoryRename}
                      className="px-4 py-2 text-sm bg-cyan-500/20 text-cyan-400 hover:bg-cyan-500/30 rounded-lg border border-cyan-500/30"
                    >
                      {categoryModal.type === 'create' ? 'Create' : 'Rename'}
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        )
      }

      {/* TEMPLATE MODAL */}
      {
        templateModal && (
          <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center animate-fade-in-up">
            <div className="glass-panel rounded-2xl p-6 w-96 shadow-2xl border border-white/20">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-white">
                  {templateModal.type === 'rename' && 'Rename Template'}
                  {templateModal.type === 'delete' && 'Delete Template'}
                  {templateModal.type === 'duplicate' && 'Duplicate Template'}
                </h3>
                <button onClick={() => setTemplateModal(null)} className="text-slate-400 hover:text-white p-1">
                  <X size={18} />
                </button>
              </div>

              {templateModal.type === 'delete' ? (
                <div>
                  <p className="text-sm text-slate-400 mb-4">
                    Are you sure you want to delete <span className="text-white font-medium">"{templateModal.name}"</span>?
                    This action cannot be undone.
                  </p>
                  <div className="flex gap-3 justify-end">
                    <button onClick={() => setTemplateModal(null)} className="px-4 py-2 text-sm text-slate-400 hover:text-white">Cancel</button>
                    <button onClick={handleTemplateDelete} className="px-4 py-2 text-sm bg-red-500/20 text-red-400 hover:bg-red-500/30 rounded-lg border border-red-500/30">Delete</button>
                  </div>
                </div>
              ) : (
                <div>
                  <input
                    type="text"
                    value={templateInput}
                    onChange={(e) => setTemplateInput(e.target.value)}
                    placeholder={templateModal.type === 'duplicate' ? 'New template name' : 'Template name'}
                    className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white text-sm focus:outline-none focus:border-cyan-500/50 mb-4"
                    autoFocus
                    onKeyDown={(e) => { if (e.key === 'Enter') templateModal.type === 'duplicate' ? handleTemplateDuplicate() : handleTemplateRename(); }}
                  />
                  <div className="flex gap-3 justify-end">
                    <button onClick={() => setTemplateModal(null)} className="px-4 py-2 text-sm text-slate-400 hover:text-white">Cancel</button>
                    <button
                      onClick={templateModal.type === 'duplicate' ? handleTemplateDuplicate : handleTemplateRename}
                      className={`px-4 py-2 text-sm rounded-lg border flex items-center gap-2 ${templateModal.type === 'duplicate' ? 'bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30 border-emerald-500/30' : 'bg-cyan-500/20 text-cyan-400 hover:bg-cyan-500/30 border-cyan-500/30'}`}
                    >
                      {templateModal.type === 'duplicate' && <><Copy size={12} /> Duplicate</>}
                      {templateModal.type === 'rename' && 'Rename'}
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        )
      }

      {/* IMPORT MODAL */}
      {
        importModal && (
          <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center animate-fade-in-up">
            <div className="glass-panel rounded-2xl p-6 w-[500px] shadow-2xl border border-white/20 max-h-[80vh] flex flex-col">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-white flex items-center gap-2"><FileUp size={18} className="text-emerald-400" /> Import Templates</h3>
                <button onClick={() => { setImportModal(false); setImportFiles([]); }} className="text-slate-400 hover:text-white p-1">
                  <X size={18} />
                </button>
              </div>

              {/* FILE DROP ZONE */}
              <div
                onClick={() => fileInputRef.current?.click()}
                className="border-2 border-dashed border-slate-700 hover:border-emerald-500/50 rounded-xl p-8 text-center cursor-pointer transition-all mb-4 hover:bg-white/5"
              >
                <Upload size={32} className="mx-auto text-slate-500 mb-3" />
                <p className="text-sm text-slate-400 mb-1">Click to select or drop HTML files</p>
                <p className="text-[10px] text-slate-600">Supports multiple files</p>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".html,.htm"
                  multiple
                  onChange={handleFileSelect}
                  className="hidden"
                />
              </div>

              {/* FILE LIST */}
              <div className="flex-1 overflow-y-auto space-y-3 mb-4 custom-scrollbar">
                {importFiles.map((file, idx) => (
                  <div key={idx} className="bg-white/5 rounded-xl p-4 border border-white/10">
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-sm font-medium text-white truncate flex-1">{file.name}</span>
                      <button onClick={() => setImportFiles(importFiles.filter((_, i) => i !== idx))} className="text-slate-500 hover:text-red-400 p-1">
                        <X size={14} />
                      </button>
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="text-[10px] text-slate-500 uppercase font-bold mb-1 block">Category</label>
                        <select
                          value={file.category}
                          onChange={(e) => {
                            const updated = [...importFiles];
                            updated[idx].category = e.target.value;
                            setImportFiles(updated);
                          }}
                          className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white text-xs focus:outline-none focus:border-cyan-500/50"
                        >
                          <option value="Uncategorized" className="bg-slate-900">Uncategorized</option>
                          {Object.keys(fileTree).filter(k => k !== 'Uncategorized').map(cat => (
                            <option key={cat} value={cat} className="bg-slate-900">{cat}</option>
                          ))}
                        </select>
                      </div>
                      <div>
                        <label className="text-[10px] text-slate-500 uppercase font-bold mb-1 block">Tags (comma separated)</label>
                        <input
                          type="text"
                          value={file.tags}
                          onChange={(e) => {
                            const updated = [...importFiles];
                            updated[idx].tags = e.target.value;
                            setImportFiles(updated);
                          }}
                          placeholder="tag1, tag2"
                          className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white text-xs focus:outline-none focus:border-cyan-500/50"
                        />
                      </div>
                    </div>
                  </div>
                ))}
                {importFiles.length === 0 && (
                  <div className="text-center py-8 text-slate-500 text-sm">No files selected</div>
                )}
              </div>

              {/* ACTIONS */}
              <div className="flex gap-3 justify-end">
                <button onClick={() => { setImportModal(false); setImportFiles([]); }} className="px-4 py-2 text-sm text-slate-400 hover:text-white">Cancel</button>
                <button
                  onClick={handleImport}
                  disabled={importFiles.length === 0}
                  className="px-4 py-2 text-sm bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30 rounded-lg border border-emerald-500/30 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  <FileUp size={14} /> Import {importFiles.length > 0 && `(${importFiles.length})`}
                </button>
              </div>
            </div>
          </div>
        )
      }
    </div >
  );
}
export default App;
