"use client";

import { useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { authApi } from "@/lib/api/auth";
import { Mail, Lock, AlertCircle, Loader2 } from "lucide-react";

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const returnTo = searchParams.get("returnTo") || "/";

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      await authApi.login(email, password);
      router.push(returnTo);
      router.refresh();
    } catch (err: unknown) {
      if (err && typeof err === "object" && "response" in err) {
        const axiosError = err as { response?: { data?: { detail?: string } } };
        setError(axiosError.response?.data?.detail || "Feil e-post eller passord");
      } else {
        setError("Kunne ikke koble til serveren");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-linear-to-br from-slate-50 to-slate-100">
      <div className="w-full max-w-md p-8">
        <div className="bg-white rounded-xl shadow-lg border border-slate-200 p-8">
          <div className="flex flex-col items-center gap-2 mb-2">
            <img
              src="https://proaktiv.no/assets/logos/logo.svg"
              alt="Proaktiv"
              className="h-8 w-auto"
            />
            <span className="font-serif text-2xl text-slate-500">Admin</span>
          </div>
          <p className="text-sm text-center text-slate-500 mb-6">
            Logg inn med din arbeids-e-post
          </p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">E-post</Label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                <Input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="navn@proaktiv.no"
                  autoFocus
                  autoComplete="email"
                  disabled={isLoading}
                  className="h-11 pl-9"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">Passord</Label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                <Input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Skriv inn passord"
                  autoComplete="current-password"
                  disabled={isLoading}
                  className="h-11 pl-9"
                />
              </div>
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
              disabled={isLoading || !email || !password}
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
          Proaktiv Admin · Kun for intern bruk
        </p>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center bg-linear-to-br from-slate-50 to-slate-100">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      }
    >
      <LoginForm />
    </Suspense>
  );
}
