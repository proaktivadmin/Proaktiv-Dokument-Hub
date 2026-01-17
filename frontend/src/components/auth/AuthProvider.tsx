"use client";

import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { authApi } from "@/lib/api/auth";
import { Loader2 } from "lucide-react";

interface AuthProviderProps {
  children: React.ReactNode;
}

// Routes that don't require authentication
const PUBLIC_ROUTES = ["/login"];

export function AuthProvider({ children }: AuthProviderProps) {
  const router = useRouter();
  const pathname = usePathname();
  const [isChecking, setIsChecking] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const checkAuth = async () => {
      // Skip check for public routes
      if (PUBLIC_ROUTES.includes(pathname)) {
        setIsChecking(false);
        return;
      }

      try {
        const status = await authApi.check();
        
        // If auth is not required (no password set), allow access
        if (!status.auth_required) {
          setIsAuthenticated(true);
          setIsChecking(false);
          return;
        }
        
        if (status.authenticated) {
          setIsAuthenticated(true);
        } else {
          router.replace("/login");
        }
      } catch {
        // On error, redirect to login
        router.replace("/login");
      } finally {
        setIsChecking(false);
      }
    };

    checkAuth();
  }, [pathname, router]);

  // Show loading spinner while checking auth
  if (isChecking && !PUBLIC_ROUTES.includes(pathname)) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <p className="text-sm text-muted-foreground">Laster...</p>
        </div>
      </div>
    );
  }

  // For public routes, always render
  if (PUBLIC_ROUTES.includes(pathname)) {
    return <>{children}</>;
  }

  // For protected routes, only render if authenticated
  if (isAuthenticated) {
    return <>{children}</>;
  }

  // Still checking or redirecting - show nothing
  return null;
}
