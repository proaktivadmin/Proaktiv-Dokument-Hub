import React, { useState, useEffect, useMemo, useRef } from 'react';
import Editor from '@monaco-editor/react';
import { Folder, FileCode, GitBranch, ChevronRight, ChevronDown, LayoutTemplate, Smartphone, Monitor, FileText, Download, AlertTriangle, GripVertical, Settings, Play, Save, Search, Command, Activity, Box, Type, Hash, Mail, Phone, User, MapPin, MoreHorizontal } from 'lucide-react';

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
  return <div className="bg-white w-[210mm] min-h-[297mm] shadow-2xl mx-auto relative ring-1 ring-black/5 transition-all duration-500 ease-out hover:scale-[1.01]">{children}<div className="absolute top-[1123px] left-0 w-full border-b-2 border-red-300 border-dashed opacity-50"></div></div>;
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

  // RESIZE STATE
  const [leftWidth, setLeftWidth] = useState(320);
  const [rightWidth, setRightWidth] = useState(500);
  const [resizing, setResizing] = useState(null); // 'left' | 'right' | null

  // PREVIEW SCALING
  const previewContainerRef = useRef(null);
  const [scale, setScale] = useState(1);

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
      if (resizing === 'left') setLeftWidth(Math.max(250, Math.min(600, e.clientX)));
      if (resizing === 'right') setRightWidth(Math.max(300, Math.min(800, window.innerWidth - e.clientX)));
    };
    const handleMU = () => setResizing(null);
    if (resizing) { window.addEventListener('mousemove', handleMM); window.addEventListener('mouseup', handleMU); }
    return () => { window.removeEventListener('mousemove', handleMM); window.removeEventListener('mouseup', handleMU); };
  }, [resizing]);

  const fetchInit = async () => setInitData(await (await fetch(`${API_URL}/init`)).json());

  const loadFile = async (filepath) => {
    const data = await (await fetch(`${API_URL}/files/read`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ filepath }) })).json();
    setSelectedPath(filepath); setContent(data.content); setMeta({ ...DEFAULT_META, ...data.meta }); setVariableOverrides({}); setRightTab('preview');
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
    initData.files.forEach(path => {
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
  }, [initData.files]);

  const detectedTags = useMemo(() => (content.match(/\[\[(.*?)\]\]/g) || []).map(t => t.replace(/\[|\]/g, '')), [content]);

  const previewSource = useMemo(() => {
    let inj = content; let subj = meta.subject;
    [...detectedTags, ...((meta.subject.match(/\[\[(.*?)\]\]/g) || []).map(t => t.replace(/\[|\]/g, '')))].forEach(k => {
      const val = variableOverrides[k] || initData.testData[k] || `[[${k}]]`;
      inj = inj.replaceAll(`[[${k}]]`, val); subj = subj.replaceAll(`[[${k}]]`, val);
    });
    const isEmail = viewMode !== 'a4';
    return `<html><head><link rel="stylesheet" href="http://localhost:5000/resources/${meta.cssVersion}"><style>body{font-family:sans-serif;background:white;margin:0;}${isEmail ? 'body{padding:0}' : `body{padding:${meta.marginTop}cm ${meta.marginRight}cm ${meta.marginBottom}cm ${meta.marginLeft}cm}`}</style></head><body>${activeResources.header}${inj}${activeResources.footer}</body></html>`;
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
              {leftTab === 'files' ? Object.keys(fileTree).map(cat => (
                <div key={cat}>
                  <div onClick={() => setExpandedFolders(p => ({ ...p, [cat]: !p[cat] }))} className="flex items-center justify-between cursor-pointer group mb-2">
                    <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest group-hover:text-cyan-400 transition-colors">{cat}</span>
                    <ChevronDown size={12} className={`text-slate-600 transition-transform duration-300 ${expandedFolders[cat] ? 'rotate-180' : ''}`} />
                  </div>

                  {expandedFolders[cat] && <div className="space-y-1">
                    {Object.keys(fileTree[cat]).map(base => (
                      <div key={base} className="group/item">
                        {fileTree[cat][base].sort((a, b) => b.ver - a.ver).map((f, i) => (
                          <button key={f.path} onClick={() => loadFile(f.path)} className={`w-full text-left px-4 py-3 text-xs rounded-xl transition-all mb-1 relative overflow-hidden group/btn flex items-center justify-between border backdrop-blur-sm ${selectedPath === f.path ? 'bg-cyan-500/10 border-cyan-500/20 text-cyan-200' : 'bg-transparent border-transparent text-slate-400 hover:bg-white/5 hover:border-white/10 hover:text-slate-200 hover:shadow-lg hover:-translate-y-0.5'}`}>
                            {selectedPath === f.path && <div className="absolute left-0 top-0 bottom-0 w-0.5 bg-cyan-400 shadow-[0_0_10px_rgba(34,211,238,0.5)]"></div>}
                            <div className="flex items-center gap-2">
                              <FileText size={12} className={selectedPath === f.path ? 'text-cyan-400' : 'text-slate-600'} />
                              <span>{base} <span className="opacity-50 text-[10px]">v{f.ver}</span></span>
                            </div>
                            {i === 0 && <div className="w-1.5 h-1.5 rounded-full bg-cyan-500 shadow-[0_0_5px_rgba(6,182,212,0.5)]"></div>}
                          </button>
                        ))}
                      </div>
                    ))}
                  </div>}
                </div>
              )) : <div className="space-y-6">{initData.snippets.map((grp, i) => (
                <div key={i}>
                  <h3 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-3 px-1">{grp.category}</h3>
                  <div className="grid grid-cols-1 gap-2">
                    {grp.items.map(snip => (
                      <button key={snip.label} onClick={() => insertSnippet(snip.code)} className="group glass-panel-hover border-transparent bg-white/5 p-3 rounded-xl text-left transition-all duration-300">
                        <div className="text-xs font-bold text-slate-300 group-hover:text-white mb-1 flex items-center gap-2"><Box size={12} className="text-purple-400" /> {snip.label}</div>
                        <div className="text-[10px] text-slate-500 group-hover:text-slate-400 truncate pl-5">{snip.desc}</div>
                      </button>
                    ))}
                  </div>
                </div>
              ))}</div>}
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
            <input type="text" placeholder="Search templates, commands, or files..." className="bg-transparent border-none outline-none text-xs text-slate-300 placeholder:text-slate-600 flex-1 w-full" />
            <div className="flex gap-2">
              <div className="px-1.5 py-0.5 rounded bg-white/5 border border-white/5 text-[9px] text-slate-500 font-mono">⌘K</div>
            </div>
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
            <div ref={previewContainerRef} className="flex-1 bg-black/20 overflow-hidden flex justify-center p-8 relative">
              <div style={{ transform: `scale(${scale})`, transformOrigin: 'top center' }} className="transition-transform duration-300 ease-out">
                <DeviceSkin mode={viewMode} subject={meta.subject} to={initData.testData['kjøper.navn'] || 'Receiver'}><iframe title="preview" srcDoc={previewSource} className="w-full h-full border-none" sandbox="allow-scripts" /></DeviceSkin>
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
                  {detectedTags.map(key => (
                    <GlassInput
                      key={key}
                      label={key}
                      value={variableOverrides[key] || ''}
                      onChange={(e) => setVariableOverrides({ ...variableOverrides, [key]: e.target.value })}
                      placeholder={initData.testData[key] || 'No Data'}
                      warning={!initData.testData[key]}
                      icon={getIconForTag(key)}
                    />
                  ))}
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
                  </div>}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
export default App;
