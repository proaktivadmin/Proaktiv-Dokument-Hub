"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Building2 } from "lucide-react";
import { Header } from "@/components/layout/Header";
import { OfficeGrid, OfficeForm } from "@/components/offices";
import { useOffices } from "@/hooks/v3/useOffices";
import { officesApi } from "@/lib/api/offices";
import type { OfficeWithStats } from "@/types/v3";

export default function OfficesPage() {
  const router = useRouter();
  const { offices, cities, isLoading, refetch } = useOffices();
  const [formOpen, setFormOpen] = useState(false);
  const [editingOffice, setEditingOffice] = useState<OfficeWithStats | null>(null);

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
        onEdit={handleEdit}
        onDeactivate={handleDeactivate}
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
