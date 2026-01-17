"use client";

import { useState } from "react";
import { useRouter, useParams } from "next/navigation";
import { 
  Building2, ChevronRight, Home, MapPin, Phone, Mail, 
  Globe, Users, Map, ExternalLink, Edit, Power
} from "lucide-react";
import { Header } from "@/components/layout/Header";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import { EmployeeGrid, EmployeeForm } from "@/components/employees";
import { AssetGallery } from "@/components/assets";
import { OfficeForm } from "@/components/offices";
import { useOffice } from "@/hooks/v3/useOffices";
import { useEmployees } from "@/hooks/v3/useEmployees";
import { useAssets } from "@/hooks/v3/useAssets";
import { officesApi } from "@/lib/api/offices";
import type { EmployeeWithOffice } from "@/types/v3";

export default function OfficeDetailPage() {
  const router = useRouter();
  const params = useParams();
  const officeId = params.id as string;

  const { office, isLoading: officeLoading, refetch: refetchOffice } = useOffice(officeId);
  const { employees, isLoading: employeesLoading, refetch: refetchEmployees } = useEmployees({ office_id: officeId });
  const { assets, categoryCounts, isLoading: assetsLoading, refetch: refetchAssets } = useAssets({ office_id: officeId });

  const [editFormOpen, setEditFormOpen] = useState(false);
  const [employeeFormOpen, setEmployeeFormOpen] = useState(false);
  const [editingEmployee, setEditingEmployee] = useState<EmployeeWithOffice | null>(null);

  const handleDeactivate = async () => {
    if (!office) return;
    if (!confirm(`Er du sikker på at du vil deaktivere "${office.name}"?`)) return;
    
    try {
      await officesApi.deactivate(office.id);
      router.push("/offices");
    } catch (err) {
      console.error("Failed to deactivate:", err);
    }
  };

  if (officeLoading) {
    return (
      <div className="min-h-screen bg-background">
        <Header />
        <main className="container mx-auto px-6 py-8 space-y-6">
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-48 w-full" />
          <Skeleton className="h-96 w-full" />
        </main>
      </div>
    );
  }

  if (!office) {
    return (
      <div className="min-h-screen bg-background">
        <Header />
        <main className="container mx-auto px-6 py-8">
          <div className="text-center py-12">
            <h1 className="text-2xl font-bold mb-2">Kontor ikke funnet</h1>
            <p className="text-muted-foreground mb-4">Kontoret du leter etter eksisterer ikke.</p>
            <Button onClick={() => router.push("/offices")}>
              Tilbake til kontorer
            </Button>
          </div>
        </main>
      </div>
    );
  }

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
            <BreadcrumbLink href="/offices" className="flex items-center gap-1">
              <Building2 className="h-4 w-4" />
              Kontorer
            </BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator>
            <ChevronRight className="h-4 w-4" />
          </BreadcrumbSeparator>
          <BreadcrumbItem>
            <BreadcrumbPage>{office.name}</BreadcrumbPage>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>

      {/* Office Header Card */}
      <Card className="mb-6 border-l-4" style={{ borderLeftColor: office.color }}>
        <CardContent className="p-6">
          <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
            <div className="flex items-start gap-4">
              {/* Color indicator */}
              <div 
                className="w-16 h-16 rounded-lg flex items-center justify-center text-white font-bold text-xl shrink-0"
                style={{ backgroundColor: office.color }}
              >
                {office.short_code}
              </div>

              <div>
                <div className="flex items-center gap-2 mb-1">
                  <h1 className="text-2xl font-bold">{office.name}</h1>
                  <Badge variant={office.is_active ? "default" : "secondary"}>
                    {office.is_active ? "Aktiv" : "Inaktiv"}
                  </Badge>
                </div>

                {office.city && (
                  <div className="flex items-center gap-1.5 text-muted-foreground mb-2">
                    <MapPin className="h-4 w-4" />
                    <span>
                      {office.street_address && `${office.street_address}, `}
                      {office.postal_code} {office.city}
                    </span>
                  </div>
                )}

                <div className="flex items-center gap-4 text-sm">
                  {office.email && (
                    <a href={`mailto:${office.email}`} className="flex items-center gap-1.5 text-primary hover:underline">
                      <Mail className="h-4 w-4" />
                      {office.email}
                    </a>
                  )}
                  {office.phone && (
                    <a href={`tel:${office.phone}`} className="flex items-center gap-1.5 text-primary hover:underline">
                      <Phone className="h-4 w-4" />
                      {office.phone}
                    </a>
                  )}
                </div>
              </div>
            </div>

            <div className="flex gap-2 shrink-0">
              <Button variant="outline" onClick={() => setEditFormOpen(true)}>
                <Edit className="h-4 w-4 mr-2" />
                Rediger
              </Button>
              {office.is_active && (
                <Button variant="outline" className="text-destructive" onClick={handleDeactivate}>
                  <Power className="h-4 w-4 mr-2" />
                  Deaktiver
                </Button>
              )}
            </div>
          </div>

          {/* Quick stats */}
          <div className="grid grid-cols-3 gap-4 mt-6 pt-6 border-t">
            <div className="text-center">
              <div className="text-2xl font-bold">{office.employee_count}</div>
              <div className="text-sm text-muted-foreground">Ansatte</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">{office.active_employee_count}</div>
              <div className="text-sm text-muted-foreground">Aktive</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">{office.territory_count}</div>
              <div className="text-sm text-muted-foreground">Postnummer</div>
            </div>
          </div>

          {/* Online links */}
          {(office.homepage_url || office.google_my_business_url || office.facebook_url || office.linkedin_url) && (
            <div className="flex flex-wrap gap-2 mt-4 pt-4 border-t">
              {office.homepage_url && (
                <a href={office.homepage_url} target="_blank" rel="noopener noreferrer">
                  <Button variant="outline" size="sm">
                    <Globe className="h-4 w-4 mr-1" />
                    Hjemmeside
                    <ExternalLink className="h-3 w-3 ml-1" />
                  </Button>
                </a>
              )}
              {office.google_my_business_url && (
                <a href={office.google_my_business_url} target="_blank" rel="noopener noreferrer">
                  <Button variant="outline" size="sm">
                    Google
                    <ExternalLink className="h-3 w-3 ml-1" />
                  </Button>
                </a>
              )}
              {office.facebook_url && (
                <a href={office.facebook_url} target="_blank" rel="noopener noreferrer">
                  <Button variant="outline" size="sm">
                    Facebook
                    <ExternalLink className="h-3 w-3 ml-1" />
                  </Button>
                </a>
              )}
              {office.linkedin_url && (
                <a href={office.linkedin_url} target="_blank" rel="noopener noreferrer">
                  <Button variant="outline" size="sm">
                    LinkedIn
                    <ExternalLink className="h-3 w-3 ml-1" />
                  </Button>
                </a>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Tabs */}
      <Tabs defaultValue="employees" className="space-y-4">
        <TabsList>
          <TabsTrigger value="employees" className="gap-2">
            <Users className="h-4 w-4" />
            Ansatte ({employees.length})
          </TabsTrigger>
          <TabsTrigger value="assets" className="gap-2">
            <Globe className="h-4 w-4" />
            Filer ({assets.length})
          </TabsTrigger>
          <TabsTrigger value="territory" className="gap-2">
            <Map className="h-4 w-4" />
            Markedsområde
          </TabsTrigger>
        </TabsList>

        <TabsContent value="employees">
          <EmployeeGrid
            employees={employees}
            isLoading={employeesLoading}
            showOffice={false}
            onEmployeeClick={(emp) => router.push(`/employees/${emp.id}`)}
            onCreateNew={() => setEmployeeFormOpen(true)}
            onEdit={(emp) => {
              setEditingEmployee(emp);
              setEmployeeFormOpen(true);
            }}
          />
        </TabsContent>

        <TabsContent value="assets">
          <AssetGallery
            assets={assets}
            categoryCounts={categoryCounts}
            isLoading={assetsLoading}
            scope="office"
            scopeId={officeId}
            onRefresh={refetchAssets}
          />
        </TabsContent>

        <TabsContent value="territory">
          <Card>
            <CardHeader>
              <CardTitle>Markedsområde</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">
                Kartvisning av postnummer tildelt dette kontoret kommer snart.
              </p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Edit office form */}
      <OfficeForm
        open={editFormOpen}
        onOpenChange={setEditFormOpen}
        office={office}
        onSuccess={() => {
          refetchOffice();
          setEditFormOpen(false);
        }}
      />

      {/* Employee form */}
      {office && (
        <EmployeeForm
          open={employeeFormOpen}
          onOpenChange={(open) => {
            setEmployeeFormOpen(open);
            if (!open) setEditingEmployee(null);
          }}
          employee={editingEmployee}
          offices={[office]}
          defaultOfficeId={office.id}
          onSuccess={() => {
            refetchEmployees();
            setEmployeeFormOpen(false);
            setEditingEmployee(null);
          }}
        />
      )}
      </main>
    </div>
  );
}
