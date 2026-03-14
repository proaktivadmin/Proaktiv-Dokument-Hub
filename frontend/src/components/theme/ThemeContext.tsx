"use client";

import { createContext, useContext, useCallback, useEffect, useState } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";

const OSLO_TZ = "Europe/Oslo";
const NIGHT_START_HOUR = 18;
const NIGHT_END_HOUR = 7;

function isNightInOslo(): boolean {
  const formatter = new Intl.DateTimeFormat("en-CA", {
    timeZone: OSLO_TZ,
    hour: "numeric",
    hour12: false,
  });
  const hour = parseInt(formatter.format(new Date()), 10);
  if (NIGHT_START_HOUR <= 23 && NIGHT_END_HOUR >= 0) {
    return hour >= NIGHT_START_HOUR || hour < NIGHT_END_HOUR;
  }
  return hour >= NIGHT_START_HOUR && hour < NIGHT_END_HOUR;
}

function msUntilNextHour(): number {
  const now = new Date();
  const next = new Date(now);
  next.setHours(next.getHours() + 1);
  next.setMinutes(0, 0, 0);
  return next.getTime() - now.getTime();
}

type ThemeContextValue = {
  isDark: boolean;
  setDark: (dark: boolean) => void;
};

const ThemeContext = createContext<ThemeContextValue | null>(null);

export function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) {
    return {
      isDark: false,
      setDark: () => {},
    };
  }
  return ctx;
}

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [mounted, setMounted] = useState(false);
  const [isDark, setIsDark] = useState(false);
  const pathname = usePathname();
  const router = useRouter();
  const searchParams = useSearchParams();

  const applyToDom = useCallback((dark: boolean) => {
    const root = document.documentElement;
    if (dark) root.classList.add("dark");
    else root.classList.remove("dark");
  }, []);

  const setDark = useCallback(
    (dark: boolean) => {
      setIsDark(dark);
      applyToDom(dark);
      const params = new URLSearchParams(searchParams?.toString() ?? "");
      params.set("dark", dark ? "1" : "0");
      const query = params.toString();
      router.replace(query ? `${pathname}?${query}` : pathname);
    },
    [pathname, router, searchParams, applyToDom]
  );

  useEffect(() => {
    queueMicrotask(() => setMounted(true));
  }, []);

  useEffect(() => {
    if (!mounted) return;

    const resolve = () => {
      const darkParam =
        typeof window !== "undefined"
          ? new URLSearchParams(window.location.search).get("dark")
          : searchParams?.get("dark");
      const dark =
        darkParam === "1" ? true : darkParam === "0" ? false : isNightInOslo();
      setIsDark(dark);
      applyToDom(dark);
    };

    resolve();
    const timeout = setTimeout(resolve, msUntilNextHour());
    return () => clearTimeout(timeout);
  }, [mounted, pathname, searchParams, applyToDom]);

  useEffect(() => {
    if (!mounted) return;

    const interval = setInterval(() => {
      const darkParam = new URLSearchParams(window.location.search).get("dark");
      const dark =
        darkParam === "1"
          ? true
          : darkParam === "0"
            ? false
            : isNightInOslo();
      setIsDark(dark);
      applyToDom(dark);
    }, 60_000);

    return () => clearInterval(interval);
  }, [mounted, applyToDom]);

  return (
    <ThemeContext.Provider value={{ isDark, setDark }}>
      {children}
    </ThemeContext.Provider>
  );
}
