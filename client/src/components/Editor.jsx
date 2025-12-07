import { useState, useEffect } from 'react'

export default function Editor({ filename, onSave }) {
    const [content, setContent] = useState('')
    const [isSaving, setIsSaving] = useState(false)

    useEffect(() => {
        const fetchContent = async () => {
            try {
                const res = await fetch(`http://localhost:3000/api/files/${filename}`)
                const text = await res.text()
                setContent(text)
            } catch (err) {
                console.error(err)
            }
        }
        if (filename) fetchContent()
    }, [filename])

    const handleSave = async () => {
        setIsSaving(true)
        try {
            await fetch(`http://localhost:3000/api/files/${filename}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content })
            })
            onSave()
        } catch (err) {
            console.error(err)
        } finally {
            setIsSaving(false)
        }
    }

    return (
        <div className="flex flex-col h-full bg-slate-800 rounded-xl border border-slate-700 overflow-hidden shadow-xl">
            <div className="bg-slate-900 p-3 border-b border-slate-700 flex justify-between items-center">
                <span className="text-sm font-mono text-slate-400">{filename}</span>
                <button
                    onClick={handleSave}
                    disabled={isSaving}
                    className="px-3 py-1 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 rounded text-xs font-medium transition-colors"
                >
                    {isSaving ? 'Saving...' : 'Save Changes'}
                </button>
            </div>
            <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                className="flex-1 bg-slate-800 text-slate-300 p-4 font-mono text-sm resize-none focus:outline-none"
                spellCheck="false"
            />
        </div>
    )
}
