import { useState, useEffect } from 'react'

export default function Preview({ filename }) {
    const [content, setContent] = useState('')
    const [refreshKey, setRefreshKey] = useState(0)

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
    }, [filename, refreshKey])

    return (
        <div className="flex flex-col h-full bg-white rounded-xl overflow-hidden shadow-xl">
            <div className="bg-slate-100 p-2 border-b border-slate-200 flex justify-between items-center">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-wider px-2">Preview</span>
                <button
                    onClick={() => setRefreshKey(k => k + 1)}
                    className="text-slate-400 hover:text-slate-600 p-1 rounded hover:bg-slate-200 transition-colors"
                    title="Refresh Preview"
                >
                    🔄
                </button>
            </div>
            <iframe
                srcDoc={content}
                title="Preview"
                className="flex-1 w-full h-full border-none bg-white"
                sandbox="allow-scripts"
            />
        </div>
    )
}
