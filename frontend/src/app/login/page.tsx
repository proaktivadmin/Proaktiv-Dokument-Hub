"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { authApi } from "@/lib/api/auth";
import { Lock, AlertCircle, Loader2 } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      await authApi.login(password);
      router.push("/");
      router.refresh();
    } catch (err: unknown) {
      if (err && typeof err === "object" && "response" in err) {
        const axiosError = err as { response?: { data?: { detail?: string } } };
        setError(axiosError.response?.data?.detail || "Feil passord");
      } else {
        setError("Kunne ikke koble til serveren");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="w-full max-w-md p-8">
        {/* Login Card */}
        <div className="bg-white rounded-xl shadow-lg border border-slate-200 p-8">
          <div className="flex items-center justify-center mb-6">
            <div className="p-3 bg-primary/10 rounded-full">
              <Lock className="h-6 w-6 text-primary" />
            </div>
          </div>

          <div className="flex flex-col items-center gap-2 mb-2">
            <img
              src="https://proaktiv.no/assets/logos/logo.svg"
              alt="Proaktiv"
              className="h-8 w-auto"
            />
            <span className="font-serif text-2xl text-slate-500">Admin</span>
          </div>
          <p className="text-sm text-center text-slate-500 mb-6">
            Logg inn for å fortsette
          </p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="password">Passord</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Skriv inn passord"
                autoFocus
                disabled={isLoading}
                className="h-11"
              />
            </div>

            {error && (
              <div className="flex items-center gap-2 text-sm text-red-600 bg-red-50 p-3 rounded-lg">
                <AlertCircle className="h-4 w-4 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <Button
              type="submit"
              className="w-full h-11"
              disabled={isLoading || !password}
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Logger inn...
                </>
              ) : (
                "Logg inn"
              )}
            </Button>
          </form>
        </div>

        <p className="text-xs text-center text-slate-400 mt-6">
          Proaktiv Admin v2.9
        </p>
      </div>
    </div>
  );
}
