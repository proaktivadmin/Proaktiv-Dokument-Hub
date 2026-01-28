"use client";

import { useEffect, useMemo, useState } from "react";
import {
  Building2,
  Layers,
  Map as MapIcon,
  ShieldAlert,
  RefreshCw,
} from "lucide-react";
import { Header } from "@/components/layout/Header";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import dynamic from "next/dynamic";
import type { Geometry } from "geojson";
import { territoriesApi } from "@/lib/api/territories";
import type { TerritoryMapData, TerritorySource } from "@/types/v3";

// Dynamically import Leaflet with no SSR
const TerritoryMap = dynamic(
  () => import("@/components/territories/TerritoryMap"),
  { 
    ssr: false,
    loading: () => <div className="h-[500px] w-full bg-[#FAFAF7] flex items-center justify-center border border-dashed border-[#E5E5E5] rounded-lg">Laster kartbase...</div>
  }
);

type TerritoryStats = {
  total_territories: number;
  by_source: Record<TerritorySource, number>;
  offices_with_territories: number;
  blacklisted_count: number;
};

const SOURCE_LABELS: Record<TerritorySource, string> = {
  vitec_next: "Vitec Next",
  finn: "Finn.no",
  anbudstjenester: "Anbudstjenester",
  homepage: "Hjemmeside",
  tjenestetorget: "Tjenestetorget.no",
  eiendomsmegler: "Eiendomsmegler.no",
  meglersmart: "MeglerSmart.no",
  other: "Annen kilde",
};

export default function TerritoriesPage() {
  const [stats, setStats] = useState<TerritoryStats | null>(null);
  const [layers, setLayers] = useState<TerritorySource[]>([]);
  const [selectedLayers, setSelectedLayers] = useState<TerritorySource[]>([]);
  const [mapData, setMapData] = useState<TerritoryMapData | null>(null);
  const [geometryData, setGeometryData] = useState<Record<string, Geometry> | null>(null);
  const [statsLoading, setStatsLoading] = useState(true);
  const [layersLoading, setLayersLoading] = useState(true);
  const [geometryLoading, setGeometryLoading] = useState(true);
  const [mapLoading, setMapLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadStats = async () => {
      setStatsLoading(true);
      setError(null);
      try {
        const data = await territoriesApi.getStats();
        setStats(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Kunne ikke hente statistikk");
      } finally {
        setStatsLoading(false);
      }
    };

    loadStats();
  }, []);

  useEffect(() => {
    const loadLayers = async () => {
      setLayersLoading(true);
      setError(null);
      try {
        const response = await territoriesApi.getLayers();
        const layerList = Array.isArray(response)
          ? response
          : (response as { layers?: TerritorySource[] }).layers ?? [];
        setLayers(layerList);
        setSelectedLayers(layerList);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Kunne ikke hente lag");
      } finally {
        setLayersLoading(false);
      }
    };

    loadLayers();
  }, []);

  useEffect(() => {
    const loadGeometry = async () => {
      setGeometryLoading(true);
      try {
        const response = await fetch("/territory-geometry.json");
        if (response.ok) {
          const data = await response.json();
          setGeometryData(data);
        }
      } catch (err) {
        console.error("Failed to load territory geometry:", err);
      } finally {
        setGeometryLoading(false);
      }
    };

    loadGeometry();
  }, []);

  useEffect(() => {
    const loadMapData = async () => {
      if (selectedLayers.length === 0) {
        setMapData(null);
        return;
      }

      setMapLoading(true);
      setError(null);
      try {
        const data = await territoriesApi.getMapData(selectedLayers);
        setMapData(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Kunne ikke hente kartdata");
      } finally {
        setMapLoading(false);
      }
    };

    loadMapData();
  }, [selectedLayers]);

  const sourceCounts = useMemo(() => {
    if (!stats?.by_source) return [];
    return Object.entries(stats.by_source).map(([key, value]) => ({
      source: key as TerritorySource,
      count: value,
    }));
  }, [stats]);

  const toggleLayer = (layer: TerritorySource) => {
    setSelectedLayers((prev) =>
      prev.includes(layer) ? prev.filter((item) => item !== layer) : [...prev, layer]
    );
  };

  return (
    <div className="min-h-screen bg-background">
      <Header />

      <main className="container mx-auto px-6 py-8 space-y-8">
        <div>
          <h2 className="text-2xl font-bold text-foreground">Markedsområder</h2>
          <p className="text-muted-foreground">
            Oversikt over postnummer-tildelinger, leverandørkilder og svartelister.
          </p>
        </div>

        {error && (
          <div className="rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-base flex items-center gap-2 text-[#272630]/80">
                <MapIcon className="h-4 w-4 text-[#272630]/60" />
                Tildelinger
              </CardTitle>
            </CardHeader>
            <CardContent>
              {statsLoading ? (
                <Skeleton className="h-8 w-24" />
              ) : (
                <div className="text-3xl font-semibold text-[#272630]">
                  {stats?.total_territories ?? 0}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-base flex items-center gap-2 text-[#272630]/80">
                <Building2 className="h-4 w-4 text-[#272630]/60" />
                Kontorer med områder
              </CardTitle>
            </CardHeader>
            <CardContent>
              {statsLoading ? (
                <Skeleton className="h-8 w-24" />
              ) : (
                <div className="text-3xl font-semibold text-[#272630]">
                  {stats?.offices_with_territories ?? 0}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-base flex items-center gap-2 text-[#272630]/80">
                <ShieldAlert className="h-4 w-4 text-[#272630]/60" />
                Svartelistet
              </CardTitle>
            </CardHeader>
            <CardContent>
              {statsLoading ? (
                <Skeleton className="h-8 w-24" />
              ) : (
                <div className="text-3xl font-semibold text-[#272630]">
                  {stats?.blacklisted_count ?? 0}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2 text-[#272630]/80">
              <Layers className="h-4 w-4 text-[#272630]/60" />
              Kilde-lag
            </CardTitle>
            <CardDescription>
              Velg hvilke leverandørkilder som skal vises i kartet.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {layersLoading ? (
              <div className="flex gap-2">
                {[1, 2, 3].map((idx) => (
                  <Skeleton key={idx} className="h-9 w-24" />
                ))}
              </div>
            ) : layers.length === 0 ? (
              <p className="text-sm text-muted-foreground">Ingen lag tilgjengelig.</p>
            ) : (
              <div className="flex flex-wrap gap-2">
                {layers.map((layer) => {
                  const isActive = selectedLayers.includes(layer);
                  return (
                    <Button
                      key={layer}
                      type="button"
                      variant={isActive ? "default" : "outline"}
                      size="sm"
                      onClick={() => toggleLayer(layer)}
                    >
                      {SOURCE_LABELS[layer] ?? layer}
                    </Button>
                  );
                })}
              </div>
            )}

            {sourceCounts.length > 0 && (
              <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                {sourceCounts.map((item) => (
                  <div
                    key={item.source}
                    className="rounded-md border border-[#E5E5E5] bg-[#F5F5F0] px-3 py-2 text-sm"
                  >
                    <div className="text-[#272630]/70">{SOURCE_LABELS[item.source]}</div>
                    <div className="text-[#272630] font-semibold">{item.count}</div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2 text-[#272630]/80">
              <MapIcon className="h-4 w-4 text-[#272630]/60" />
              Kartvisning
            </CardTitle>
            <CardDescription>
              Kartet vises når postnummer-geometri er tilgjengelig.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {mapLoading || geometryLoading ? (
               <div className="rounded-lg border border-dashed border-[#E5E5E5] bg-[#FAFAF7] p-10 text-center text-sm text-muted-foreground min-h-[500px] flex items-center justify-center">
                <div className="flex items-center justify-center gap-2 text-[#272630]/60">
                  <RefreshCw className="h-4 w-4 animate-spin" />
                  Laster kartdata...
                </div>
              </div>
            ) : mapData && geometryData ? (
              <div className="space-y-4">
                <TerritoryMap mapData={mapData} geometryData={geometryData} />
                <div className="text-center text-xs text-[#272630]/60">
                   {mapData.features.length} tildelinger funnet i valgte lag.
                </div>
              </div>
            ) : (
              <div className="rounded-lg border border-dashed border-[#E5E5E5] bg-[#FAFAF7] p-10 text-center text-sm text-muted-foreground">
                <div className="space-y-2">
                  <p>Velg kilde-lag over for å vise tildelinger i kartet.</p>
                  <p className="text-xs text-[#272630]/60">
                    Sørg for at kilder har aktive tildelinger lastet.
                  </p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
 
