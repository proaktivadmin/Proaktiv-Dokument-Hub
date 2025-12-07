import { useState } from 'react'

export default function GitControls() {
    const [status, setStatus] = useState('')
    const [loading, setLoading] = useState(false)

    const handleSync = async () => {
        setLoading(true)
        setStatus('Syncing...')
        try {
            const res = await fetch('http://localhost:3000/api/git/sync', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: 'Update from HTML Hub' })
            })
            const data = await res.json()
            if (data.error) throw new Error(data.error)
            setStatus('Synced!')
            setTimeout(() => setStatus(''), 3000)
        } catch (err) {
            setStatus('Error: ' + err.message)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="flex items-center gap-4">
            {status && <span className="text-sm text-slate-400">{status}</span>}
            <button
                onClick={handleSync}
                disabled={loading}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 rounded-md text-sm font-medium transition-all shadow-lg shadow-blue-900/20"
            >
                {loading ? 'Syncing...' : 'Push Updates'}
            </button>
        </div>
    )
}
