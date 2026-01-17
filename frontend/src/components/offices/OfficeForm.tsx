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
import { Checkbox } from "@/components/ui/checkbox";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { officesApi } from "@/lib/api/offices";
import type { Office, OfficeWithStats, OfficeCreatePayload, OfficeUpdatePayload } from "@/types/v3";

interface OfficeFormProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  office?: OfficeWithStats | null;
  onSuccess: () => void;
}

type FormData = {
  name: string;
  short_code: string;
  email: string;
  phone: string;
  street_address: string;
  postal_code: string;
  city: string;
  homepage_url: string;
  google_my_business_url: string;
  facebook_url: string;
  instagram_url: string;
  linkedin_url: string;
  color: string;
  is_active: boolean;
};

const DEFAULT_COLORS = [
  "#4A90D9", "#E67E22", "#9B59B6", "#27AE60", "#E74C3C",
  "#3498DB", "#F1C40F", "#1ABC9C", "#8E44AD", "#2C3E50",
];

export function OfficeForm({ open, onOpenChange, office, onSuccess }: OfficeFormProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const isEditing = !!office;

  const { register, handleSubmit, watch, setValue, formState: { errors } } = useForm<FormData>({
    defaultValues: {
      name: office?.name || "",
      short_code: office?.short_code || "",
      email: office?.email || "",
      phone: office?.phone || "",
      street_address: office?.street_address || "",
      postal_code: office?.postal_code || "",
      city: office?.city || "",
      homepage_url: office?.homepage_url || "",
      google_my_business_url: office?.google_my_business_url || "",
      facebook_url: office?.facebook_url || "",
      instagram_url: office?.instagram_url || "",
      linkedin_url: office?.linkedin_url || "",
      color: office?.color || DEFAULT_COLORS[0],
      is_active: office?.is_active ?? true,
    },
  });

  const selectedColor = watch("color");

  const onSubmit = async (data: FormData) => {
    setIsSubmitting(true);
    setError(null);

    try {
      const payload = {
        name: data.name,
        short_code: data.short_code.toUpperCase(),
        email: data.email || null,
        phone: data.phone || null,
        street_address: data.street_address || null,
        postal_code: data.postal_code || null,
        city: data.city || null,
        homepage_url: data.homepage_url || null,
        google_my_business_url: data.google_my_business_url || null,
        facebook_url: data.facebook_url || null,
        instagram_url: data.instagram_url || null,
        linkedin_url: data.linkedin_url || null,
        color: data.color,
        is_active: data.is_active,
      };

      if (isEditing && office) {
        await officesApi.update(office.id, payload as OfficeUpdatePayload);
      } else {
        await officesApi.create(payload as OfficeCreatePayload);
      }

      onSuccess();
      onOpenChange(false);
    } catch (err) {
      console.error("Failed to save office:", err);
      setError(err instanceof Error ? err.message : "Kunne ikke lagre kontor");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{isEditing ? "Rediger kontor" : "Nytt kontor"}</DialogTitle>
          <DialogDescription>
            {isEditing
              ? "Oppdater kontordetaljene nedenfor"
              : "Fyll ut informasjonen for det nye kontoret"}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)}>
          <Tabs defaultValue="basic" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="basic">Grunnleggende</TabsTrigger>
              <TabsTrigger value="address">Adresse</TabsTrigger>
              <TabsTrigger value="online">Nettsider</TabsTrigger>
            </TabsList>

            <TabsContent value="basic" className="space-y-4 mt-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Navn *</Label>
                  <Input
                    id="name"
                    {...register("name", { required: "Navn er påkrevd" })}
                    placeholder="Proaktiv Stavanger"
                  />
                  {errors.name && (
                    <p className="text-sm text-destructive">{errors.name.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="short_code">Kortkode *</Label>
                  <Input
                    id="short_code"
                    {...register("short_code", { 
                      required: "Kortkode er påkrevd",
                      maxLength: { value: 10, message: "Maks 10 tegn" }
                    })}
                    placeholder="STAV"
                    className="uppercase"
                  />
                  {errors.short_code && (
                    <p className="text-sm text-destructive">{errors.short_code.message}</p>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="email">E-post</Label>
                  <Input
                    id="email"
                    type="email"
                    {...register("email")}
                    placeholder="stavanger@proaktiv.no"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="phone">Telefon</Label>
                  <Input
                    id="phone"
                    {...register("phone")}
                    placeholder="51 00 00 00"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label>Kartfarge</Label>
                <div className="flex flex-wrap gap-2">
                  {DEFAULT_COLORS.map((color) => (
                    <button
                      key={color}
                      type="button"
                      onClick={() => setValue("color", color)}
                      className={`w-8 h-8 rounded-full border-2 transition-all ${
                        selectedColor === color
                          ? "border-primary scale-110"
                          : "border-transparent hover:scale-105"
                      }`}
                      style={{ backgroundColor: color }}
                    />
                  ))}
                  <Input
                    type="color"
                    {...register("color")}
                    className="w-8 h-8 p-0 border-0 cursor-pointer"
                  />
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox
                  id="is_active"
                  checked={watch("is_active")}
                  onCheckedChange={(checked) => setValue("is_active", !!checked)}
                />
                <Label htmlFor="is_active" className="cursor-pointer">
                  Kontoret er aktivt
                </Label>
              </div>
            </TabsContent>

            <TabsContent value="address" className="space-y-4 mt-4">
              <div className="space-y-2">
                <Label htmlFor="street_address">Gateadresse</Label>
                <Input
                  id="street_address"
                  {...register("street_address")}
                  placeholder="Klubbgata 3"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="postal_code">Postnummer</Label>
                  <Input
                    id="postal_code"
                    {...register("postal_code")}
                    placeholder="4013"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="city">By</Label>
                  <Input
                    id="city"
                    {...register("city")}
                    placeholder="Stavanger"
                  />
                </div>
              </div>
            </TabsContent>

            <TabsContent value="online" className="space-y-4 mt-4">
              <div className="space-y-2">
                <Label htmlFor="homepage_url">Hjemmeside</Label>
                <Input
                  id="homepage_url"
                  type="url"
                  {...register("homepage_url")}
                  placeholder="https://proaktiv.no/stavanger"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="google_my_business_url">Google My Business</Label>
                <Input
                  id="google_my_business_url"
                  type="url"
                  {...register("google_my_business_url")}
                  placeholder="https://g.page/proaktiv-stavanger"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="facebook_url">Facebook</Label>
                  <Input
                    id="facebook_url"
                    type="url"
                    {...register("facebook_url")}
                    placeholder="https://facebook.com/..."
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="instagram_url">Instagram</Label>
                  <Input
                    id="instagram_url"
                    type="url"
                    {...register("instagram_url")}
                    placeholder="https://instagram.com/..."
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="linkedin_url">LinkedIn</Label>
                <Input
                  id="linkedin_url"
                  type="url"
                  {...register("linkedin_url")}
                  placeholder="https://linkedin.com/company/..."
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
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Lagrer..." : isEditing ? "Oppdater" : "Opprett"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
