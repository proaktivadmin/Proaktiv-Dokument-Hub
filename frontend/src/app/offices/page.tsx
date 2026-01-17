"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Building2, ChevronRight, Home } from "lucide-react";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
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
    <div className="container mx-auto px-4 py-6 max-w-7xl">
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
              <Building2 className="h-4 w-4" />
              Kontorer
            </BreadcrumbPage>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>

      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Kontorer</h1>
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
    </div>
  );
}
