"use client";

import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { authApi } from "@/lib/api/auth";
import { Loader2 } from "lucide-react";

interface AuthProviderProps {
  children: React.ReactNode;
}

// Routes that don't require authentication
const PUBLIC_ROUTES = ["/login"];
const PUBLIC_ROUTE_PREFIXES = ["/signature"];

function isPublicRoute(pathname: string): boolean {
  if (PUBLIC_ROUTES.includes(pathname)) {
    return true;
  }
  return PUBLIC_ROUTE_PREFIXES.some(
    (route) => pathname === route || pathname.startsWith(`${route}/`)
  );
}

export function AuthProvider({ children }: AuthProviderProps) {
  const pathname = usePathname();
  const [isChecking, setIsChecking] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const checkAuth = async () => {
      // Skip check for public routes
      if (isPublicRoute(pathname)) {
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
          const target = pathname ? `/login?returnTo=${encodeURIComponent(pathname)}` : "/login";
          window.location.replace(target);
        }
      } catch {
        // On error, redirect to login (use window.location for reliable navigation)
        const target = pathname ? `/login?returnTo=${encodeURIComponent(pathname)}` : "/login";
        window.location.replace(target);
      } finally {
        setIsChecking(false);
      }
    };

    checkAuth();
  }, [pathname]);

  // Show loading spinner while checking auth
  if (isChecking && !isPublicRoute(pathname)) {
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
  if (isPublicRoute(pathname)) {
    return <>{children}</>;
  }

  // For protected routes, only render if authenticated
  if (isAuthenticated) {
    return <>{children}</>;
  }

  // Redirecting to login - show feedback instead of blank
  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="flex flex-col items-center gap-4">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
        <p className="text-sm text-muted-foreground">Omdirigerer til innlogging...</p>
      </div>
    </div>
  );
}
