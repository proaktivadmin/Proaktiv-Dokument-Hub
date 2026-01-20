"use client";

import { useState } from "react";
import { AxiosError } from "axios";
import { Header } from "@/components/layout/Header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { officesApi } from "@/lib/api/offices";
import { employeesApi } from "@/lib/api/employees";
import { vitecApi } from "@/lib/api/vitec";
import { useToast } from "@/hooks/use-toast";
import { Image, Building2, Users, RefreshCcw } from "lucide-react";

export default function SyncPage() {
  const { toast } = useToast();
  const [isSyncingOffices, setIsSyncingOffices] = useState(false);
  const [isSyncingEmployees, setIsSyncingEmployees] = useState(false);
  const [isSyncingOfficePictures, setIsSyncingOfficePictures] = useState(false);
  const [isSyncingEmployeePictures, setIsSyncingEmployeePictures] = useState(false);

  const handleSyncOffices = async () => {
    setIsSyncingOffices(true);
    try {
      const result = await officesApi.sync();
      toast({
        title: "Kontorer synkronisert",
        description: `${result.synced} av ${result.total} kontorer oppdatert. ${result.created} nye, ${result.updated} oppdatert, ${result.skipped} hoppet over.`,
      });
    } catch (error) {
      const message = extractErrorMessage(error, "Kunne ikke synkronisere kontorer.");
      toast({
        title: "Synkronisering feilet",
        description: message,
        variant: "destructive",
      });
    } finally {
      setIsSyncingOffices(false);
    }
  };

  const handleSyncEmployees = async () => {
    setIsSyncingEmployees(true);
    try {
      const result = await employeesApi.sync();
      toast({
        title: "Medarbeidere synkronisert",
        description: `${result.synced} av ${result.total} medarbeidere oppdatert. ${result.created} nye, ${result.updated} oppdatert, ${result.skipped} hoppet over.${result.missing_office > 0 ? ` ${result.missing_office} mangler kontor.` : ""}`,
      });
    } catch (error) {
      const message = extractErrorMessage(error, "Kunne ikke synkronisere medarbeidere.");
      toast({
        title: "Synkronisering feilet",
        description: message,
        variant: "destructive",
      });
    } finally {
      setIsSyncingEmployees(false);
    }
  };

  const handleSyncOfficePictures = async () => {
    setIsSyncingOfficePictures(true);
    try {
      const result = await vitecApi.syncOfficePictures();
      toast({
        title: "Kontorbilder synkronisert",
        description: `${result.synced} av ${result.total} bilder lastet ned. ${result.failed > 0 ? `${result.failed} feilet.` : ""}`,
      });
    } catch (error) {
      const message = extractErrorMessage(error, "Kunne ikke synkronisere kontorbilder.");
      toast({
        title: "Synkronisering feilet",
        description: message,
        variant: "destructive",
      });
    } finally {
      setIsSyncingOfficePictures(false);
    }
  };

  const handleSyncEmployeePictures = async () => {
    setIsSyncingEmployeePictures(true);
    try {
      const result = await vitecApi.syncEmployeePictures();
      toast({
        title: "Medarbeiderbilder synkronisert",
        description: `${result.synced} av ${result.total} bilder lastet ned. ${result.failed > 0 ? `${result.failed} feilet.` : ""}`,
      });
    } catch (error) {
      const message = extractErrorMessage(error, "Kunne ikke synkronisere medarbeiderbilder.");
      toast({
        title: "Synkronisering feilet",
        description: message,
        variant: "destructive",
      });
    } finally {
      setIsSyncingEmployeePictures(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container mx-auto px-6 py-8">
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-foreground">Vitec synkronisering</h2>
          <p className="text-muted-foreground">
            Synkroniser data og bilder direkte fra Vitec Hub.
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          {/* Office Data Sync */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-100 dark:bg-emerald-900/20">
                  <Building2 className="h-5 w-5 text-emerald-600 dark:text-emerald-400" />
                </div>
                <div>
                  <CardTitle>Kontorer</CardTitle>
                  <CardDescription>Synkroniser kontordata</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-muted-foreground">
                Henter kontorer fra Vitec og oppdaterer navn, adresse, kontaktinformasjon og andre detaljer.
              </p>
              <Button
                onClick={handleSyncOffices}
                disabled={isSyncingOffices}
                className="w-full"
              >
                <RefreshCcw className={`mr-2 h-4 w-4 ${isSyncingOffices ? "animate-spin" : ""}`} />
                {isSyncingOffices ? "Synkroniserer..." : "Synkroniser kontorer"}
              </Button>
            </CardContent>
          </Card>

          {/* Employee Data Sync */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-sky-100 dark:bg-sky-900/20">
                  <Users className="h-5 w-5 text-sky-600 dark:text-sky-400" />
                </div>
                <div>
                  <CardTitle>Medarbeidere</CardTitle>
                  <CardDescription>Synkroniser medarbeiderdata</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-muted-foreground">
                Henter medarbeidere fra Vitec og oppdaterer navn, tittel, kontaktinformasjon og roller.
              </p>
              <Button
                onClick={handleSyncEmployees}
                disabled={isSyncingEmployees}
                className="w-full"
              >
                <RefreshCcw className={`mr-2 h-4 w-4 ${isSyncingEmployees ? "animate-spin" : ""}`} />
                {isSyncingEmployees ? "Synkroniserer..." : "Synkroniser medarbeidere"}
              </Button>
            </CardContent>
          </Card>

          {/* Office Pictures Sync */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-purple-100 dark:bg-purple-900/20">
                  <Building2 className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                </div>
                <div>
                  <CardTitle>Kontorbilder</CardTitle>
                  <CardDescription>Synkroniser bannerbilder</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-muted-foreground">
                Laster ned bannerbilder for alle kontorer fra Vitec Hub.
              </p>
              <Button
                onClick={handleSyncOfficePictures}
                disabled={isSyncingOfficePictures}
                variant="outline"
                className="w-full"
              >
                <Image className={`mr-2 h-4 w-4 ${isSyncingOfficePictures ? "animate-pulse" : ""}`} />
                {isSyncingOfficePictures ? "Synkroniserer..." : "Synkroniser kontorbilder"}
              </Button>
            </CardContent>
          </Card>

          {/* Employee Pictures Sync */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-amber-100 dark:bg-amber-900/20">
                  <Image className="h-5 w-5 text-amber-600 dark:text-amber-400" />
                </div>
                <div>
                  <CardTitle>Medarbeiderbilder</CardTitle>
                  <CardDescription>Synkroniser profilbilder</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-muted-foreground">
                Laster ned profilbilder for alle medarbeidere fra Vitec Hub.
              </p>
              <Button
                onClick={handleSyncEmployeePictures}
                disabled={isSyncingEmployeePictures}
                variant="outline"
                className="w-full"
              >
                <Image className={`mr-2 h-4 w-4 ${isSyncingEmployeePictures ? "animate-pulse" : ""}`} />
                {isSyncingEmployeePictures ? "Synkroniserer..." : "Synkroniser medarbeiderbilder"}
              </Button>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}

const extractErrorMessage = (error: unknown, fallback: string): string => {
  if (error instanceof AxiosError && error.response?.data?.detail) {
    return error.response.data.detail;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return fallback;
};
