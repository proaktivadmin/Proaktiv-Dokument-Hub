"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { employeesApi } from "@/lib/api/employees";
import type { 
  EmployeeWithOffice, 
  EmployeeCreatePayload, 
  EmployeeUpdatePayload,
  OfficeWithStats,
  EmployeeStatus
} from "@/types/v3";

interface EmployeeFormProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  employee?: EmployeeWithOffice | null;
  offices: OfficeWithStats[];
  defaultOfficeId?: string;
  onSuccess: () => void;
}

type FormData = {
  first_name: string;
  last_name: string;
  title: string;
  email: string;
  phone: string;
  office_id: string;
  status: EmployeeStatus;
  start_date: string;
  homepage_profile_url: string;
  linkedin_url: string;
};

export function EmployeeForm({ 
  open, 
  onOpenChange, 
  employee, 
  offices,
  defaultOfficeId,
  onSuccess 
}: EmployeeFormProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const isEditing = !!employee;

  const { register, handleSubmit, watch, setValue, formState: { errors } } = useForm<FormData>({
    defaultValues: {
      first_name: employee?.first_name || "",
      last_name: employee?.last_name || "",
      title: employee?.title || "",
      email: employee?.email || "",
      phone: employee?.phone || "",
      office_id: employee?.office_id || defaultOfficeId || "",
      status: employee?.status || "active",
      start_date: employee?.start_date?.split("T")[0] || new Date().toISOString().split("T")[0],
      homepage_profile_url: employee?.homepage_profile_url || "",
      linkedin_url: employee?.linkedin_url || "",
    },
  });

  const onSubmit = async (data: FormData) => {
    setIsSubmitting(true);
    setError(null);

    try {
      const payload = {
        first_name: data.first_name,
        last_name: data.last_name,
        title: data.title || null,
        email: data.email || null,
        phone: data.phone || null,
        office_id: data.office_id,
        status: data.status,
        start_date: data.start_date || null,
        homepage_profile_url: data.homepage_profile_url || null,
        linkedin_url: data.linkedin_url || null,
        end_date: null,
        hide_from_homepage_date: null,
        delete_data_date: null,
      };

      if (isEditing && employee) {
        await employeesApi.update(employee.id, payload as EmployeeUpdatePayload);
      } else {
        await employeesApi.create(payload as EmployeeCreatePayload);
      }

      onSuccess();
      onOpenChange(false);
    } catch (err) {
      console.error("Failed to save employee:", err);
      setError(err instanceof Error ? err.message : "Kunne ikke lagre ansatt");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{isEditing ? "Rediger ansatt" : "Ny ansatt"}</DialogTitle>
          <DialogDescription>
            {isEditing
              ? "Oppdater ansattdetaljene nedenfor"
              : "Fyll ut informasjonen for den nye ansatte"}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)}>
          <Tabs defaultValue="basic" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="basic">Grunnleggende</TabsTrigger>
              <TabsTrigger value="online">Nettsider</TabsTrigger>
            </TabsList>

            <TabsContent value="basic" className="space-y-4 mt-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="first_name">Fornavn *</Label>
                  <Input
                    id="first_name"
                    {...register("first_name", { required: "Fornavn er påkrevd" })}
                    placeholder="Per"
                  />
                  {errors.first_name && (
                    <p className="text-sm text-destructive">{errors.first_name.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="last_name">Etternavn *</Label>
                  <Input
                    id="last_name"
                    {...register("last_name", { required: "Etternavn er påkrevd" })}
                    placeholder="Hansen"
                  />
                  {errors.last_name && (
                    <p className="text-sm text-destructive">{errors.last_name.message}</p>
                  )}
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="title">Tittel</Label>
                <Input
                  id="title"
                  {...register("title")}
                  placeholder="Eiendomsmegler MNEF"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="email">E-post</Label>
                  <Input
                    id="email"
                    type="email"
                    {...register("email")}
                    placeholder="per.hansen@proaktiv.no"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="phone">Telefon</Label>
                  <Input
                    id="phone"
                    {...register("phone")}
                    placeholder="912 34 567"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="office_id">Kontor *</Label>
                  <Select 
                    value={watch("office_id")} 
                    onValueChange={(value) => setValue("office_id", value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Velg kontor" />
                    </SelectTrigger>
                    <SelectContent>
                      {offices.map((office) => (
                        <SelectItem key={office.id} value={office.id}>
                          <div className="flex items-center gap-2">
                            <div 
                              className="w-2 h-2 rounded-full"
                              style={{ backgroundColor: office.color }}
                            />
                            {office.name}
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {!watch("office_id") && (
                    <p className="text-sm text-destructive">Kontor er påkrevd</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="status">Status</Label>
                  <Select 
                    value={watch("status")} 
                    onValueChange={(value) => setValue("status", value as EmployeeStatus)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="active">Aktiv</SelectItem>
                      <SelectItem value="onboarding">Onboarding</SelectItem>
                      <SelectItem value="offboarding">Offboarding</SelectItem>
                      <SelectItem value="inactive">Inaktiv</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="start_date">Startdato</Label>
                <Input
                  id="start_date"
                  type="date"
                  {...register("start_date")}
                />
              </div>
            </TabsContent>

            <TabsContent value="online" className="space-y-4 mt-4">
              <div className="space-y-2">
                <Label htmlFor="homepage_profile_url">Profilside på hjemmesiden</Label>
                <Input
                  id="homepage_profile_url"
                  type="url"
                  {...register("homepage_profile_url")}
                  placeholder="https://proaktiv.no/ansatte/per-hansen"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="linkedin_url">LinkedIn</Label>
                <Input
                  id="linkedin_url"
                  type="url"
                  {...register("linkedin_url")}
                  placeholder="https://linkedin.com/in/per-hansen"
                />
              </div>
            </TabsContent>
          </Tabs>

          {error && (
            <div className="mt-4 p-3 bg-destructive/10 text-destructive text-sm rounded-md">
              {error}
            </div>
          )}

          <DialogFooter className="mt-6">
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Avbryt
            </Button>
            <Button type="submit" disabled={isSubmitting || !watch("office_id")}>
              {isSubmitting ? "Lagrer..." : isEditing ? "Oppdater" : "Opprett"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
