import { useState } from 'react'

export default function Dashboard({ files, onOpenFile, onRefresh }) {
    const [newFileName, setNewFileName] = useState('')
    const [isCreating, setIsCreating] = useState(false)

    const handleCreate = async (e) => {
        e.preventDefault()
        if (!newFileName) return

        try {
            await fetch('http://localhost:3000/api/files', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ filename: newFileName })
            })
            setNewFileName('')
            setIsCreating(false)
            onRefresh()
        } catch (err) {
            console.error(err)
        }
    }

    const handleDelete = async (e, filename) => {
        e.stopPropagation()
        if (!confirm(`Delete ${filename}?`)) return

        try {
            await fetch(`http://localhost:3000/api/files/${filename}`, {
                method: 'DELETE'
            })
            onRefresh()
        } catch (err) {
            console.error(err)
        }
    }

    return (
        <div>
            <div className="flex justify-between items-center mb-8">
                <h2 className="text-2xl font-light text-slate-300">Your Library</h2>
                <button
                    onClick={() => setIsCreating(true)}
                    className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 rounded-md text-sm font-medium transition-colors"
                >
                    + New Template
                </button>
            </div>

            {isCreating && (
                <form onSubmit={handleCreate} className="mb-8 bg-slate-800 p-4 rounded-lg border border-slate-700 flex gap-4 items-center">
                    <input
                        type="text"
                        value={newFileName}
                        onChange={(e) => setNewFileName(e.target.value)}
                        placeholder="template-name"
                        className="bg-slate-900 border border-slate-700 rounded px-3 py-2 text-white focus:outline-none focus:border-blue-500 flex-1"
                        autoFocus
                    />
                    <button type="submit" className="text-emerald-400 hover:text-emerald-300">Create</button>
                    <button type="button" onClick={() => setIsCreating(false)} className="text-slate-400 hover:text-slate-300">Cancel</button>
                </form>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {files.map(file => (
                    <div
                        key={file}
                        onClick={() => onOpenFile(file)}
                        className="group bg-slate-800 hover:bg-slate-750 border border-slate-700 hover:border-blue-500/50 rounded-xl p-6 cursor-pointer transition-all hover:shadow-xl hover:shadow-blue-900/10 relative"
                    >
                        <div className="flex justify-between items-start">
                            <div className="w-12 h-12 bg-slate-900 rounded-lg flex items-center justify-center mb-4 text-2xl">
                                📄
                            </div>
                            <button
                                onClick={(e) => handleDelete(e, file)}
                                className="opacity-0 group-hover:opacity-100 text-slate-500 hover:text-red-400 transition-opacity p-2"
                            >
                                🗑️
                            </button>
                        </div>
                        <h3 className="text-lg font-medium text-slate-200 group-hover:text-blue-400 transition-colors truncate">
                            {file}
                        </h3>
                        <p className="text-sm text-slate-500 mt-2">HTML Template</p>
                    </div>
                ))}

                {files.length === 0 && !isCreating && (
                    <div className="col-span-full text-center py-20 text-slate-500">
                        No templates found. Create one to get started!
                    </div>
                )}
            </div>
        </div>
    )
}
