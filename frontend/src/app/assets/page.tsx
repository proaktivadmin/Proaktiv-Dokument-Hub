"use client";

import { useState } from "react";
import { Image as ImageIcon, Building2, User, Sparkles } from "lucide-react";
import Link from "next/link";
import { Header } from "@/components/layout/Header";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AssetGallery, LogoLibrary } from "@/components/assets";
import { useAssets } from "@/hooks/v3/useAssets";
import { useOffices } from "@/hooks/v3/useOffices";

export default function AssetsPage() {
  const [scope, setScope] = useState<"global" | "office" | "employee" | "logos">("global");

  const { 
    assets: globalAssets, 
    categoryCounts: globalCounts, 
    isLoading: globalLoading, 
    refetch: refetchGlobal 
  } = useAssets({ is_global: true });

  const { offices, isLoading: officesLoading } = useOffices();

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container mx-auto px-6 py-8">
      {/* Header */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-foreground">Mediefiler</h2>
        <p className="text-muted-foreground">
          Administrer logoer, bilder og dokumenter for hele selskapet
        </p>
      </div>

      {/* Scope tabs */}
      <Tabs value={scope} onValueChange={(v) => setScope(v as "global" | "office" | "employee" | "logos")} className="space-y-6">
        <TabsList>
          <TabsTrigger value="global" className="gap-2">
            <ImageIcon className="h-4 w-4" />
            Globalt ({globalAssets.length})
          </TabsTrigger>
          <TabsTrigger value="logos" className="gap-2">
            <Sparkles className="h-4 w-4" />
            Proaktiv Logoer
          </TabsTrigger>
          <TabsTrigger value="office" className="gap-2">
            <Building2 className="h-4 w-4" />
            Per kontor
          </TabsTrigger>
          <TabsTrigger value="employee" className="gap-2">
            <User className="h-4 w-4" />
            Per ansatt
          </TabsTrigger>
        </TabsList>

        <TabsContent value="global">
          <AssetGallery
            assets={globalAssets}
            categoryCounts={globalCounts}
            isLoading={globalLoading}
            scope="global"
            onRefresh={refetchGlobal}
          />
        </TabsContent>

        <TabsContent value="logos">
          <LogoLibrary />
        </TabsContent>

        <TabsContent value="office">
          <Card>
            <CardHeader>
              <CardTitle>Filer per kontor</CardTitle>
            </CardHeader>
            <CardContent>
              {officesLoading ? (
                <p className="text-muted-foreground">Laster kontorer...</p>
              ) : offices.length === 0 ? (
                <p className="text-muted-foreground">Ingen kontorer funnet. Opprett et kontor først.</p>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {offices.map((office) => (
                    <Link
                      key={office.id}
                      href={`/offices/${office.id}`}
                      className="p-4 border rounded-lg bg-white shadow-card ring-1 ring-black/3 hover:border-[#BCAB8A] hover:shadow-card-hover hover:-translate-y-0.5 transition-all duration-slow flex items-center gap-3"
                    >
                      <div 
                        className="w-10 h-10 rounded-lg flex items-center justify-center text-white font-bold text-sm"
                        style={{ backgroundColor: office.color }}
                      >
                        {office.short_code}
                      </div>
                      <div>
                        <h3 className="font-medium">{office.name}</h3>
                        <p className="text-sm text-muted-foreground">
                          Se kontorfiler →
                        </p>
                      </div>
                    </Link>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="employee">
          <Card>
            <CardHeader>
              <CardTitle>Filer per ansatt</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">
                Gå til en ansatts profil for å se og laste opp filer knyttet til den ansatte.
              </p>
              <Link
                href="/employees"
                className="inline-block mt-4 text-primary hover:underline"
              >
                Se alle ansatte →
              </Link>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
      </main>
    </div>
  );
}
