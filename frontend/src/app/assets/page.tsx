"use client";

import { useState } from "react";
import { Image as ImageIcon, ChevronRight, Home, Building2, User } from "lucide-react";
import { Header } from "@/components/layout/Header";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AssetGallery } from "@/components/assets";
import { useAssets } from "@/hooks/v3/useAssets";
import { useOffices } from "@/hooks/v3/useOffices";

export default function AssetsPage() {
  const [scope, setScope] = useState<"global" | "office" | "employee">("global");

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
      {/* Breadcrumb */}
      <Breadcrumb className="mb-6">
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbLink href="/" className="flex items-center gap-1">
              <Home className="h-4 w-4" />
              Dashboard
            </BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator>
            <ChevronRight className="h-4 w-4" />
          </BreadcrumbSeparator>
          <BreadcrumbItem>
            <BreadcrumbPage className="flex items-center gap-1">
              <ImageIcon className="h-4 w-4" />
              Mediefiler
            </BreadcrumbPage>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>

      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Mediefiler</h1>
        <p className="text-muted-foreground">
          Administrer logoer, bilder og dokumenter for hele selskapet
        </p>
      </div>

      {/* Scope tabs */}
      <Tabs value={scope} onValueChange={(v) => setScope(v as "global" | "office" | "employee")} className="space-y-6">
        <TabsList>
          <TabsTrigger value="global" className="gap-2">
            <ImageIcon className="h-4 w-4" />
            Globalt ({globalAssets.length})
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
                    <a 
                      key={office.id}
                      href={`/offices/${office.id}`}
                      className="p-4 border rounded-lg hover:border-primary transition-colors flex items-center gap-3"
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
                    </a>
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
              <a 
                href="/employees" 
                className="inline-block mt-4 text-primary hover:underline"
              >
                Se alle ansatte →
              </a>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
      </main>
    </div>
  );
}
