"use client";

import { useState } from "react";
import { useRouter, useParams } from "next/navigation";
import { 
  Users, ChevronRight, Home, Phone, Mail,
  Globe, Calendar, Edit, PenLine, AlertTriangle, ExternalLink,
  Building2, Clock, CheckSquare,
  Facebook, Instagram, Linkedin, Twitter
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
import { AssetGallery } from "@/components/assets";
import { EmployeeForm, SignaturePreview } from "@/components/employees";
import { useEmployee } from "@/hooks/v3/useEmployees";
import { useAssets } from "@/hooks/v3/useAssets";
import { useChecklistInstances } from "@/hooks/v3/useChecklists";
import { useOffices } from "@/hooks/v3/useOffices";
import { cn } from "@/lib/utils";
import type { EmployeeStatus } from "@/types/v3";

const statusConfig: Record<EmployeeStatus, { label: string; className: string }> = {
  active: { label: "Aktiv", className: "bg-green-500/10 text-green-600" },
  onboarding: { label: "Onboarding", className: "bg-blue-500/10 text-blue-600" },
  offboarding: { label: "Offboarding", className: "bg-amber-500/10 text-amber-600" },
  inactive: { label: "Inaktiv", className: "bg-gray-500/10 text-gray-600" },
};

export default function EmployeeDetailPage() {
  const router = useRouter();
  const params = useParams();
  const employeeId = params.id as string;

  const { employee, isLoading: employeeLoading, refetch: refetchEmployee } = useEmployee(employeeId);
  const { assets, categoryCounts, isLoading: assetsLoading, refetch: refetchAssets } = useAssets({ employee_id: employeeId });
  const { instances: checklists, isLoading: checklistsLoading } = useChecklistInstances({ employee_id: employeeId });
  const { offices } = useOffices();

  const [editFormOpen, setEditFormOpen] = useState(false);

  if (employeeLoading) {
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

  if (!employee) {
    return (
      <div className="min-h-screen bg-background">
        <Header />
        <main className="container mx-auto px-6 py-8">
          <div className="text-center py-12">
            <h1 className="text-2xl font-bold mb-2">Ansatt ikke funnet</h1>
            <p className="text-muted-foreground mb-4">Den ansatte du leter etter eksisterer ikke.</p>
            <Button onClick={() => router.push("/employees")}>
              Tilbake til ansatte
            </Button>
          </div>
        </main>
      </div>
    );
  }

  const status = statusConfig[employee.status];
  const hasSocialLinks = Boolean(
    employee.facebook_url ||
    employee.instagram_url ||
    employee.twitter_url ||
    employee.linkedin_url
  );
  const mismatchCount =
    (employee.entra_mismatch_fields?.length ?? 0) + (employee.entra_upn_mismatch ? 1 : 0);
  const entraHasData = Boolean(employee.entra_user_id || employee.entra_mail || employee.entra_upn);
  const entraStatus = !entraHasData ? "missing" : mismatchCount > 0 ? "mismatch" : "match";
  const vitecStatus = entraHasData ? entraStatus : "primary";
  const bubbleBase = "h-2.5 w-2.5 rounded-full shadow-soft";
  const bubbleClass = (source: "entra" | "vitec", state: "missing" | "match" | "mismatch" | "primary") => {
    const baseColor = source === "entra" ? "bg-sky-500" : "bg-emerald-500";
    if (state === "missing") {
      return cn(bubbleBase, `${baseColor}/30 ring-1 ring-slate-200`);
    }
    if (state === "mismatch") {
      return cn(bubbleBase, baseColor, "ring-2 ring-amber-500/60");
    }
    if (state === "primary") {
      return cn(bubbleBase, baseColor, "ring-1 ring-emerald-500/30");
    }
    return cn(bubbleBase, baseColor, "ring-1 ring-emerald-500/30");
  };
  const mismatchLabels = [
    ...(employee.entra_mismatch_fields ?? []),
    ...(employee.entra_upn_mismatch ? ["entra_upn"] : []),
  ]
    .map((field) => {
      const labelMap: Record<string, string> = {
        display_name: "Visningsnavn",
        first_name: "Fornavn",
        last_name: "Etternavn",
        title: "Tittel",
        email: "E-post",
        phone: "Mobil",
        office_name: "Avdeling",
        office_location: "Kontorsted",
        office_street: "Adresse",
        office_postal: "Postnummer",
        country: "Land",
        entra_upn: "UPN",
      };
      return labelMap[field] ?? field;
    })
    .join(", ");

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
            <BreadcrumbLink href="/employees" className="flex items-center gap-1">
              <Users className="h-4 w-4" />
              Ansatte
            </BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator>
            <ChevronRight className="h-4 w-4" />
          </BreadcrumbSeparator>
          <BreadcrumbItem>
            <BreadcrumbPage>{employee.full_name}</BreadcrumbPage>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>

      {/* Employee Header Card */}
      <Card className="mb-6">
        <CardContent className="p-6">
          <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
            <div className="flex items-start gap-4">
              {/* Avatar */}
              <div 
                className="w-20 h-20 rounded-full flex items-center justify-center text-white font-bold text-2xl shrink-0"
                style={{ backgroundColor: employee.office.color }}
              >
                {employee.initials}
              </div>

              <div>
                <div className="flex items-center gap-2 mb-1">
                  <h1 className="text-2xl font-bold">{employee.full_name}</h1>
                  <Badge className={status.className}>{status.label}</Badge>
                  <div className="flex items-center gap-1">
                    <span
                      className={bubbleClass("vitec", vitecStatus)}
                      title={vitecStatus === "primary" ? "Vitec: primærkilde" : "Vitec: status"}
                    />
                    <span
                      className={bubbleClass("entra", entraStatus)}
                      title={
                        entraStatus === "missing"
                          ? "Entra: ikke synkronisert"
                          : entraStatus === "mismatch"
                            ? `Entra: ${mismatchCount} avvik`
                            : "Entra: i sync"
                      }
                    />
                  </div>
                </div>

                {employee.title && (
                  <p className="text-lg text-muted-foreground mb-2">{employee.title}</p>
                )}

                <div className="flex items-center gap-1.5 text-sm text-muted-foreground mb-2">
                  <Building2 className="h-4 w-4" />
                  <a 
                    href={`/offices/${employee.office.id}`}
                    className="text-primary hover:underline"
                  >
                    {employee.office.name}
                  </a>
                </div>

                <div className="flex items-center gap-4 text-sm">
                  {employee.email && (
                    <a href={`mailto:${employee.email}`} className="flex items-center gap-1.5 text-primary hover:underline">
                      <Mail className="h-4 w-4" />
                      {employee.email}
                    </a>
                  )}
                  {employee.phone && (
                    <a href={`tel:${employee.phone}`} className="flex items-center gap-1.5 text-primary hover:underline">
                      <Phone className="h-4 w-4" />
                      {employee.phone}
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
            </div>
          </div>

          {/* Online links */}
          {(employee.homepage_profile_url || hasSocialLinks) && (
            <div className="flex flex-wrap items-center gap-3 mt-4 pt-4 border-t">
              {employee.homepage_profile_url && (
                <a href={employee.homepage_profile_url} target="_blank" rel="noopener noreferrer">
                  <Button variant="outline" size="sm">
                    <Globe className="h-4 w-4 mr-1" />
                    Profilside
                    <ExternalLink className="h-3 w-3 ml-1" />
                  </Button>
                </a>
              )}
              {hasSocialLinks && (
                <div className="flex items-center gap-3">
                  {employee.facebook_url && (
                    <a
                      href={employee.facebook_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      aria-label="Facebook"
                    >
                      <Facebook className="h-5 w-5 text-muted-foreground hover:text-primary" />
                    </a>
                  )}
                  {employee.instagram_url && (
                    <a
                      href={employee.instagram_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      aria-label="Instagram"
                    >
                      <Instagram className="h-5 w-5 text-muted-foreground hover:text-primary" />
                    </a>
                  )}
                  {employee.twitter_url && (
                    <a
                      href={employee.twitter_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      aria-label="Twitter"
                    >
                      <Twitter className="h-5 w-5 text-muted-foreground hover:text-primary" />
                    </a>
                  )}
                  {employee.linkedin_url && (
                    <a
                      href={employee.linkedin_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      aria-label="LinkedIn"
                    >
                      <Linkedin className="h-5 w-5 text-muted-foreground hover:text-primary" />
                    </a>
                  )}
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Offboarding panel */}
      {employee.status === "offboarding" && (
        <Card className="mb-6 border-amber-500/50 bg-amber-500/5">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-amber-600">
              <AlertTriangle className="h-5 w-5" />
              Offboarding i gang
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {employee.end_date && (
                <div>
                  <div className="text-sm text-muted-foreground">Sluttdato</div>
                  <div className="font-medium">
                    {new Date(employee.end_date).toLocaleDateString("nb-NO")}
                    {employee.days_until_end !== null && (
                      <span className="text-amber-600 ml-2">
                        ({employee.days_until_end <= 0 ? "Passert" : `${employee.days_until_end} dager`})
                      </span>
                    )}
                  </div>
                </div>
              )}
              {employee.hide_from_homepage_date && (
                <div>
                  <div className="text-sm text-muted-foreground">Skjules fra hjemmeside</div>
                  <div className="font-medium">
                    {new Date(employee.hide_from_homepage_date).toLocaleDateString("nb-NO")}
                  </div>
                </div>
              )}
              {employee.delete_data_date && (
                <div>
                  <div className="text-sm text-muted-foreground">Slett data</div>
                  <div className="font-medium">
                    {new Date(employee.delete_data_date).toLocaleDateString("nb-NO")}
                  </div>
                </div>
              )}
            </div>

            {checklists.length > 0 && (
              <div className="mt-4 pt-4 border-t border-amber-500/20">
                <div className="text-sm text-muted-foreground mb-2">Sjekkliste fremgang</div>
                {checklists.map((checklist) => (
                  <div key={checklist.id} className="flex items-center gap-3">
                    <div className="flex-1 bg-amber-500/20 rounded-full h-2">
                      <div 
                        className="bg-amber-500 h-2 rounded-full transition-all"
                        style={{ width: `${checklist.progress_percentage}%` }}
                      />
                    </div>
                    <span className="text-sm font-medium">
                      {checklist.completed_count}/{checklist.total_count}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Tabs */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview" className="gap-2">
            <Users className="h-4 w-4" />
            Oversikt
          </TabsTrigger>
          <TabsTrigger value="assets" className="gap-2">
            <Globe className="h-4 w-4" />
            Filer ({assets.length})
          </TabsTrigger>
          <TabsTrigger value="checklists" className="gap-2">
            <CheckSquare className="h-4 w-4" />
            Sjekklister ({checklists.length})
          </TabsTrigger>
          <TabsTrigger value="signature" className="gap-2">
            <PenLine className="h-4 w-4" />
            Signatur
          </TabsTrigger>
        </TabsList>

        <TabsContent value="overview">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Kontaktinformasjon</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {employee.email && (
                  <div className="flex items-center gap-3">
                    <Mail className="h-4 w-4 text-muted-foreground" />
                    <span>{employee.email}</span>
                  </div>
                )}
                {employee.phone && (
                  <div className="flex items-center gap-3">
                    <Phone className="h-4 w-4 text-muted-foreground" />
                    <span>{employee.phone}</span>
                  </div>
                )}
                {!employee.email && !employee.phone && (
                  <p className="text-muted-foreground text-sm">Ingen kontaktinformasjon registrert</p>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Ansettelsesforhold</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center gap-3">
                  <Building2 className="h-4 w-4 text-muted-foreground" />
                  <span>{employee.office.name}</span>
                </div>
                {employee.start_date && (
                  <div className="flex items-center gap-3">
                    <Calendar className="h-4 w-4 text-muted-foreground" />
                    <span>Startdato: {new Date(employee.start_date).toLocaleDateString("nb-NO")}</span>
                  </div>
                )}
                <div className="flex items-center gap-3">
                  <Clock className="h-4 w-4 text-muted-foreground" />
                  <span>Status: {status.label}</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Entra ID (sekundær)</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {!entraHasData && (
                  <p className="text-muted-foreground text-sm">Ingen Entra-data synkronisert ennå.</p>
                )}
                {entraHasData && (
                  <>
                    {employee.entra_upn && (
                      <div className="flex items-center gap-3">
                        <Mail className="h-4 w-4 text-muted-foreground" />
                        <span>UPN: {employee.entra_upn}</span>
                      </div>
                    )}
                    {employee.entra_mail && (
                      <div className="flex items-center gap-3">
                        <Mail className="h-4 w-4 text-muted-foreground" />
                        <span>E-post: {employee.entra_mail}</span>
                      </div>
                    )}
                    {employee.entra_job_title && (
                      <div className="flex items-center gap-3">
                        <Building2 className="h-4 w-4 text-muted-foreground" />
                        <span>Tittel: {employee.entra_job_title}</span>
                      </div>
                    )}
                    {employee.entra_mobile_phone && (
                      <div className="flex items-center gap-3">
                        <Phone className="h-4 w-4 text-muted-foreground" />
                        <span>Mobil: {employee.entra_mobile_phone}</span>
                      </div>
                    )}
                    {employee.entra_department && (
                      <div className="flex items-center gap-3">
                        <Building2 className="h-4 w-4 text-muted-foreground" />
                        <span>Avdeling: {employee.entra_department}</span>
                      </div>
                    )}
                    {employee.entra_office_location && (
                      <div className="flex items-center gap-3">
                        <Home className="h-4 w-4 text-muted-foreground" />
                        <span>Kontorsted: {employee.entra_office_location}</span>
                      </div>
                    )}
                    {employee.entra_last_synced_at && (
                      <div className="flex items-center gap-3">
                        <Clock className="h-4 w-4 text-muted-foreground" />
                        <span>
                          Sist synkronisert:{" "}
                          {new Date(employee.entra_last_synced_at).toLocaleString("nb-NO")}
                        </span>
                      </div>
                    )}
                    {employee.entra_account_enabled !== null && (
                      <div className="flex items-center gap-3">
                        <CheckSquare className="h-4 w-4 text-muted-foreground" />
                        <span>Konto: {employee.entra_account_enabled ? "Aktiv" : "Deaktivert"}</span>
                      </div>
                    )}
                  </>
                )}
                {mismatchCount > 0 && (
                  <div className="flex items-center gap-2 text-xs text-amber-700 bg-amber-50 rounded px-2 py-1">
                    <AlertTriangle className="h-3 w-3 shrink-0" />
                    <span>Avvik mellom Vitec og Entra: {mismatchLabels}</span>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="assets">
          <AssetGallery
            assets={assets}
            categoryCounts={categoryCounts}
            isLoading={assetsLoading}
            scope="employee"
            scopeId={employeeId}
            onRefresh={refetchAssets}
          />
        </TabsContent>

        <TabsContent value="checklists">
          <Card>
            <CardHeader>
              <CardTitle>Sjekklister</CardTitle>
            </CardHeader>
            <CardContent>
              {checklistsLoading ? (
                <Skeleton className="h-24 w-full" />
              ) : checklists.length === 0 ? (
                <p className="text-muted-foreground">Ingen sjekklister tildelt denne ansatte.</p>
              ) : (
                <div className="space-y-4">
                  {checklists.map((checklist) => (
                    <div key={checklist.id} className="p-4 border rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <div>
                          <h4 className="font-medium">{checklist.template.name}</h4>
                          <p className="text-sm text-muted-foreground">{checklist.template.description}</p>
                        </div>
                        <Badge variant={checklist.is_completed ? "default" : "secondary"}>
                          {checklist.is_completed ? "Fullført" : "Pågår"}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="flex-1 bg-muted rounded-full h-2">
                          <div 
                            className="bg-primary h-2 rounded-full transition-all"
                            style={{ width: `${checklist.progress_percentage}%` }}
                          />
                        </div>
                        <span className="text-sm font-medium">
                          {checklist.completed_count}/{checklist.total_count}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="signature">
          <SignaturePreview
            employeeId={employeeId}
            employeeEmail={employee.email || ""}
            employeeName={employee.full_name}
          />
        </TabsContent>
      </Tabs>

      {/* Edit form */}
      <EmployeeForm
        open={editFormOpen}
        onOpenChange={setEditFormOpen}
        employee={employee}
        offices={offices}
        onSuccess={() => {
          refetchEmployee();
          setEditFormOpen(false);
        }}
      />
      </main>
    </div>
  );
}
