"use client";

import { useState } from "react";
import { Header } from "@/components/layout/Header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Download, BarChart3, Loader2, AlertCircle } from "lucide-react";
import { downloadSalesReport } from "@/lib/api/reports";

export default function ReportsPage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDownload = async () => {
    setLoading(true);
    setError(null);
    try {
      const blob = await downloadSalesReport({ department_id: 1120 });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `formidlingsrapport_1120_${new Date().getFullYear()}.xlsx`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Kunne ikke laste ned rapporten.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Header />

      <main className="container mx-auto px-6 py-8">
        <h1 className="text-2xl font-serif font-bold text-[#272630] mb-2">Rapporter</h1>
        <p className="text-[#272630]/60 mb-8">
          Last ned rapporter for å matche mot tredjepartsrapporter og Vitec Next leder-verktøyet.
        </p>

        <Card className="max-w-xl border border-[#E5E5E5] shadow-card">
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-lg bg-[#E9E7DC]">
                <BarChart3 className="h-6 w-6 text-[#272630]" />
              </div>
              <div>
                <CardTitle className="font-serif">Formidlingsrapport</CardTitle>
                <CardDescription>
                  Vederlag og andre inntekter for meglere som har solgt eiendom dette året (avd. 1120)
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <Button
              onClick={handleDownload}
              disabled={loading}
              className="bg-[#272630] hover:bg-[#272630]/90 text-white"
            >
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Laster ned...
                </>
              ) : (
                <>
                  <Download className="mr-2 h-4 w-4" />
                  Last ned Excel
                </>
              )}
            </Button>
            {error && (
              <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 text-red-700">
                <AlertCircle className="h-4 w-4 shrink-0" />
                <span className="text-sm">{error}</span>
              </div>
            )}
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
