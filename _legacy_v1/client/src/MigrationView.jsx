import React, { useState, useEffect } from 'react';

const MigrationView = () => {
    const [status, setStatus] = useState('idle'); // idle, processing, done, error
    const [results, setResults] = useState([]);
    const [log, setLog] = useState('');

    const runBatch = async () => {
        setStatus('processing');
        setLog('Starting batch process...\n');
        try {
            const response = await fetch('http://localhost:5000/api/sanitize/batch', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await response.json();

            if (data.error) throw new Error(data.error);

            setResults(data.results);
            setLog(prev => prev + `Processed ${data.results.length} files.\n`);
            setStatus('done');
        } catch (err) {
            setLog(prev => prev + `Error: ${err.message}\n`);
            setStatus('error');
        }
    };

    return (
        <div style={{ padding: '20px', color: '#fff' }}>
            <h1>Migration Factory</h1>
            <p style={{ marginBottom: '20px', color: '#ccc' }}>
                Batch process legacy templates from <code>library/Legacy_Import</code> to <code>library/Ready_For_Export</code>.
            </p>

            <div style={{ marginBottom: '20px' }}>
                <button
                    onClick={runBatch}
                    disabled={status === 'processing'}
                    style={{
                        padding: '10px 20px',
                        fontSize: '16px',
                        backgroundColor: status === 'processing' ? '#555' : '#272630',
                        color: 'white',
                        border: '1px solid #bcab8a',
                        cursor: status === 'processing' ? 'not-allowed' : 'pointer'
                    }}
                >
                    {status === 'processing' ? 'Processing...' : 'Run Sanitizer Batch'}
                </button>
            </div>

            {status !== 'idle' && (
                <div style={{
                    backgroundColor: 'rgba(0,0,0,0.3)',
                    padding: '15px',
                    borderRadius: '8px',
                    border: '1px solid #444',
                    fontFamily: 'monospace'
                }}>
                    <pre>{log}</pre>

                    {results.length > 0 && (
                        <div style={{ marginTop: '10px' }}>
                            <h3>Results:</h3>
                            <ul style={{ listStyle: 'none', padding: 0 }}>
                                {results.map((res, i) => (
                                    <li key={i} style={{
                                        padding: '5px 0',
                                        color: res.success ? '#a4b5a8' : 'red'
                                    }}>
                                        [{res.success ? 'OK' : 'FAIL'}] {res.file}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default MigrationView;
