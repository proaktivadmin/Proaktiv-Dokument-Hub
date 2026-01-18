"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { Search, Users } from "lucide-react";
import { Header } from "@/components/layout/Header";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { RECEIVER_TYPES } from "@/lib/vitec/receiver-types";

export default function MottakerePage() {
  const [query, setQuery] = useState("");

  const filtered = useMemo(() => {
    const term = query.trim().toLowerCase();
    if (!term) return RECEIVER_TYPES;

    return RECEIVER_TYPES.filter((role) => {
      const haystack = [
        role.name,
        role.reserved_for,
        role.group,
        role.rules,
        role.source,
        String(role.id),
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();
      return haystack.includes(term);
    });
  }, [query]);

  return (
    <div className="min-h-screen bg-background">
      <Header />

      <main className="container mx-auto px-6 py-8">
        <div className="flex items-start justify-between gap-4 mb-8">
          <div>
            <h2 className="text-2xl font-bold text-foreground">Mottakere</h2>
            <p className="text-muted-foreground">
              Roller og relasjonstyper fra Vitec Next (kunderelasjoner).
            </p>
          </div>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Users className="h-4 w-4" />
            {filtered.length} roller
          </div>
        </div>

        <div className="mb-6 max-w-md">
          <div className="relative">
            <Search className="h-4 w-4 text-muted-foreground absolute left-3 top-1/2 -translate-y-1/2" />
            <Input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Søk etter rolle, gruppe eller regelverk..."
              className="pl-9"
            />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border divide-y">
          {filtered.map((role) => (
            <Link
              key={role.id}
              href={{ pathname: "/templates", query: { receiver: role.name } }}
              className="p-4 flex flex-col gap-2 md:flex-row md:items-start md:gap-4 hover:bg-slate-50 transition-colors"
            >
              <div className="text-xs text-muted-foreground md:w-20">#{role.id}</div>
              <div className="flex-1">
                <div className="flex items-center gap-2 flex-wrap">
                  <p className="font-medium text-foreground">{role.name}</p>
                  {role.source === "Custom" && (
                    <Badge variant="secondary">Tillegg</Badge>
                  )}
                </div>
                <div className="mt-2 flex flex-wrap gap-2">
                  <Badge variant="outline">Gruppe: {role.group || "-"}</Badge>
                  <Badge variant="outline">Reservert for: {role.reserved_for || "-"}</Badge>
                  <Badge variant="outline">Rangering: {role.ranking || "-"}</Badge>
                  <Badge variant="outline">Regelverk: {role.rules || "-"}</Badge>
                </div>
              </div>
            </Link>
          ))}
          {filtered.length === 0 && (
            <div className="p-8 text-center text-muted-foreground">
              Ingen roller matcher søket.
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
