"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { AxiosError } from "axios";
import { Header } from "@/components/layout/Header";
import { OfficeGrid, OfficeForm } from "@/components/offices";
import { useOffices } from "@/hooks/v3/useOffices";
import { officesApi } from "@/lib/api/offices";
import { entraSyncApi } from "@/lib/api/entra-sync";
import { vitecApi } from "@/lib/api/vitec";
import { useToast } from "@/hooks/use-toast";
import type { OfficeWithStats } from "@/types/v3";

export default function OfficesPage() {
  const router = useRouter();
  // Exclude sub-offices from main list - they appear under their parent
  const { offices, cities, isLoading, refetch } = useOffices({ include_sub: false });
  const { toast } = useToast();
  const [formOpen, setFormOpen] = useState(false);
  const [editingOffice, setEditingOffice] = useState<OfficeWithStats | null>(null);
  const [isSyncing, setIsSyncing] = useState(false);
  const [isEntraImporting, setIsEntraImporting] = useState(false);

  const handleOfficeClick = (office: OfficeWithStats) => {
    router.push(`/offices/${office.id}`);
  };

  const handleEdit = (office: OfficeWithStats) => {
    setEditingOffice(office);
    setFormOpen(true);
  };

  const handleDeactivate = async (office: OfficeWithStats) => {
    if (!confirm(`Er du sikker på at du vil deaktivere "${office.name}"?`)) return;
    
    try {
      await officesApi.deactivate(office.id);
      refetch();
    } catch (err) {
      console.error("Failed to deactivate:", err);
    }
  };

  const handleFormClose = () => {
    setFormOpen(false);
    setEditingOffice(null);
  };

  const handleFormSuccess = () => {
    refetch();
    handleFormClose();
  };

  const handleSync = async () => {
    setIsSyncing(true);
    try {
      const result = await officesApi.sync();

      // Also sync pictures from Vitec Hub
      try {
        const picResult = await vitecApi.syncOfficePictures();
        await refetch();
        toast({
          title: "Kontorer synkronisert",
          description: `Oppdatert ${result.synced} av ${result.total} kontorer. ${picResult.synced} bilder hentet.`,
        });
      } catch {
        await refetch();
        toast({
          title: "Kontorer synkronisert",
          description: `Oppdatert ${result.synced} av ${result.total} kontorer. Bildesynk feilet.`,
        });
      }
    } catch (error) {
      console.error("Failed to sync offices:", error);
      
      let errorMessage = "Kunne ikke hente kontorer fra Vitec Hub.";
      if (error instanceof AxiosError && error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error instanceof Error) {
        errorMessage = error.message;
      }
      
      toast({
        title: "Synkronisering feilet",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsSyncing(false);
    }
  };

  const handleEntraImport = async () => {
    setIsEntraImporting(true);
    try {
      const result = await entraSyncApi.importOffices({ dry_run: false });
      if (result.success) {
        await refetch();
        toast({
          title: "Entra-import fullført",
          description: `${result.matched_updated ?? 0} kontorer oppdatert${result.offices_not_matched ? `, ${result.offices_not_matched} uten match` : ''}.`,
        });
      } else {
        toast({
          title: "Entra-import feilet",
          description: result.error ?? "Ukjent feil",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error("Failed to import from Entra:", error);
      
      let errorMessage = "Kunne ikke importere fra Entra ID.";
      if (error instanceof AxiosError && error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error instanceof Error) {
        errorMessage = error.message;
      }
      
      toast({
        title: "Entra-import feilet",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsEntraImporting(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container mx-auto px-6 py-8">
      {/* Header */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-foreground">Kontorer</h2>
        <p className="text-muted-foreground">
          Administrer kontorer, ansatte og markedsområder
        </p>
      </div>

      {/* Grid */}
      <OfficeGrid
        offices={offices}
        cities={cities}
        isLoading={isLoading}
        onOfficeClick={handleOfficeClick}
        onCreateNew={() => setFormOpen(true)}
        onSync={handleSync}
        isSyncing={isSyncing}
        onEntraImport={handleEntraImport}
        isEntraImporting={isEntraImporting}
        onEdit={handleEdit}
        onDeactivate={handleDeactivate}
        onEmployeeClick={(emp) => router.push(`/employees/${emp.id}`)}
      />

      {/* Form dialog */}
      <OfficeForm
        open={formOpen}
        onOpenChange={handleFormClose}
        office={editingOffice}
        onSuccess={handleFormSuccess}
      />
      </main>
    </div>
  );
}
