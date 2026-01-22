'use client';

import { useEffect } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

/**
 * Global error boundary that catches errors in the root layout.
 * This component must define its own html and body tags since it
 * replaces the root layout when triggered.
 */
export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error('Global error:', error);
  }, [error]);

  return (
    <html lang="nb">
      <body className="min-h-screen bg-slate-50 font-sans antialiased">
        <div className="flex min-h-screen flex-col items-center justify-center px-4">
          <div className="mx-auto max-w-md text-center">
            <div className="mb-6 flex justify-center">
              <div className="rounded-full bg-red-100 p-4">
                <AlertTriangle className="h-12 w-12 text-red-600" />
              </div>
            </div>
            
            <h1 className="mb-2 text-2xl font-bold text-slate-900">
              Kritisk feil
            </h1>
            
            <p className="mb-6 text-slate-600">
              En alvorlig feil oppstod i applikasjonen. Vennligst prøv å laste siden på nytt.
            </p>

            {error.digest && (
              <p className="mb-6 text-xs text-slate-500">
                Feilkode: {error.digest}
              </p>
            )}

            <button
              onClick={reset}
              className="inline-flex items-center gap-2 rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-slate-500 focus:ring-offset-2"
            >
              <RefreshCw className="h-4 w-4" />
              Prøv igjen
            </button>
          </div>
        </div>
      </body>
    </html>
  );
}
