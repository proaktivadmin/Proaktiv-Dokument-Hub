"use client";

import { useState } from "react";
import {
  FolderTree,
  Plus,
  Pencil,
  Trash2,
  GripVertical,
  Folder,
  FileText,
  FileSpreadsheet,
  File,
  Files,
  FileCheck,
  FileCheck2,
  FilePlus,
  FileQuestion,
  Home,
  Users,
  Building,
  Building2,
  Mail,
  Send,
  MessageSquare,
  MessageCircle,
  Shield,
  ShieldCheck,
  Scale,
  Info,
  InfoIcon,
  Megaphone,
  Type,
  Briefcase,
  Receipt,
  CreditCard,
  Landmark,
  Gavel,
  BookOpen,
  ClipboardList,
  AlertCircle,
  CheckCircle,
  type LucideIcon,
} from "lucide-react";
import { Header } from "@/components/layout/Header";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useCategories } from "@/hooks/useCategories";

// Icon mapping for dynamic icon rendering - comprehensive list
const iconMap: Record<string, LucideIcon> = {
  // Folders
  Folder,
  FolderTree,
  // Files
  File,
  Files,
  FileText,
  FileSpreadsheet,
  FileCheck,
  FileCheck2,
  FilePlus,
  FileQuestion,
  // Buildings & Places
  Home,
  Building,
  Building2,
  Landmark,
  // People
  Users,
  // Communication
  Mail,
  Send,
  MessageSquare,
  MessageCircle,
  Megaphone,
  // Legal & Business
  Shield,
  ShieldCheck,
  Scale,
  Gavel,
  Briefcase,
  // Finance
  Receipt,
  CreditCard,
  // Info & Status
  Info,
  InfoIcon,
  AlertCircle,
  CheckCircle,
  // Text
  Type,
  BookOpen,
  ClipboardList,
};

// Helper function to get icon component from string name
function getCategoryIcon(iconName: string | null | undefined): LucideIcon {
  if (!iconName) return Folder;
  
  // Check if it's a lucide icon name
  const Icon = iconMap[iconName];
  if (Icon) return Icon;
  
  // Default fallback
  return Folder;
}

// Helper to check if icon is an emoji (starts with non-ASCII)
function isEmoji(str: string | null | undefined): boolean {
  if (!str) return false;
  return /^[\u{1F300}-\u{1F9FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]/u.test(str);
}

// Extend categoryApi with create and delete methods inline for this page
const extendedCategoryApi = {
  async create(data: { name: string; icon?: string; description?: string }) {
    const response = await fetch("http://localhost:8000/api/categories", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Failed to create category");
    }
    return response.json();
  },

  async delete(categoryId: string) {
    const response = await fetch(`http://localhost:8000/api/categories/${categoryId}`, {
      method: "DELETE",
    });
    if (!response.ok && response.status !== 204) {
      const error = await response.json();
      throw new Error(error.detail || "Failed to delete category");
    }
  },
};

function CategorySkeleton() {
  return (
    <div className="space-y-3">
      {[1, 2, 3, 4].map((i) => (
        <div key={i} className="flex items-center gap-4 p-4 border rounded-lg">
          <Skeleton className="h-5 w-5" />
          <Skeleton className="h-10 w-10 rounded-md" />
          <div className="flex-1 space-y-2">
            <Skeleton className="h-4 w-32" />
            <Skeleton className="h-3 w-48" />
          </div>
        </div>
      ))}
    </div>
  );
}

export default function CategoriesPage() {
  const { categories, isLoading, error, refetch } = useCategories();
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newCategoryName, setNewCategoryName] = useState("");
  const [newCategoryIcon, setNewCategoryIcon] = useState("");
  const [newCategoryDescription, setNewCategoryDescription] = useState("");
  const [isCreating, setIsCreating] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);

  const handleCreateCategory = async () => {
    if (!newCategoryName.trim()) {
      setCreateError("Navn er påkrevd");
      return;
    }

    setIsCreating(true);
    setCreateError(null);

    try {
      await extendedCategoryApi.create({
        name: newCategoryName.trim(),
        icon: newCategoryIcon.trim() || undefined,
        description: newCategoryDescription.trim() || undefined,
      });

      setCreateDialogOpen(false);
      setNewCategoryName("");
      setNewCategoryIcon("");
      setNewCategoryDescription("");
      refetch();
    } catch (err) {
      setCreateError(err instanceof Error ? err.message : "Kunne ikke opprette kategori");
    } finally {
      setIsCreating(false);
    }
  };

  const handleDeleteCategory = async (categoryId: string, categoryName: string) => {
    if (!confirm(`Er du sikker på at du vil slette kategorien "${categoryName}"?`)) {
      return;
    }

    try {
      await extendedCategoryApi.delete(categoryId);
      refetch();
    } catch (err) {
      console.error("Failed to delete category:", err);
      alert("Kunne ikke slette kategorien. Prøv igjen.");
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Header />

      <main className="container mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h2 className="text-2xl font-bold text-foreground">Kategorier</h2>
            <p className="text-muted-foreground">Organiser malene dine i kategorier</p>
          </div>
          <Button onClick={() => setCreateDialogOpen(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Ny kategori
          </Button>
        </div>

        {/* Categories List */}
        <div className="bg-white rounded-lg shadow-sm border">
          {isLoading ? (
            <div className="p-4">
              <CategorySkeleton />
            </div>
          ) : error ? (
            <div className="p-8 text-center text-red-600">
              <p>Feil ved lasting av kategorier: {error}</p>
              <Button variant="outline" onClick={refetch} className="mt-4">
                Prøv igjen
              </Button>
            </div>
          ) : categories.length === 0 ? (
            <div className="p-12 text-center text-slate-500">
              <FolderTree className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p className="text-lg font-medium">Ingen kategorier opprettet</p>
              <p className="text-sm mb-4">Opprett kategorier for å organisere malene dine.</p>
              <Button onClick={() => setCreateDialogOpen(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Opprett første kategori
              </Button>
            </div>
          ) : (
            <div className="divide-y">
              {categories.map((category, index) => {
                const IconComponent = getCategoryIcon(category.icon);
                const showEmoji = isEmoji(category.icon);

                return (
                  <div
                    key={category.id}
                    className="flex items-center gap-4 p-4 hover:bg-slate-50 transition-colors group"
                  >
                    {/* Drag Handle */}
                    <div className="cursor-grab active:cursor-grabbing">
                      <GripVertical className="h-5 w-5 text-slate-300 group-hover:text-slate-400 transition-colors" />
                    </div>

                    {/* Icon Container */}
                    <div className="flex-shrink-0 p-2.5 bg-primary/10 rounded-md">
                      {showEmoji ? (
                        <span className="text-xl leading-none">{category.icon}</span>
                      ) : (
                        <IconComponent className="h-5 w-5 text-primary" />
                      )}
                    </div>

                    {/* Category Info */}
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-slate-900">{category.name}</p>
                      {category.description && (
                        <p className="text-sm text-muted-foreground truncate">
                          {category.description}
                        </p>
                      )}
                    </div>

                    {/* Sort Order Badge */}
                    <div className="hidden sm:block">
                      <span className="text-xs text-slate-400 bg-slate-100 px-2 py-1 rounded">
                        #{category.sort_order ?? index + 1}
                      </span>
                    </div>

                    {/* Actions */}
                    <div className="flex gap-1">
                      <Button
                        variant="ghost"
                        size="icon"
                        title="Rediger"
                        className="h-8 w-8 text-slate-500 hover:text-slate-700"
                      >
                        <Pencil className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        title="Slett"
                        className="h-8 w-8 text-slate-500 hover:text-red-600"
                        onClick={() => handleDeleteCategory(category.id, category.name)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Info Card */}
        <div className="mt-6 p-4 bg-sky-50 border border-sky-200 rounded-lg">
          <p className="text-sky-800 text-sm">
            <strong>Tips:</strong> Dra kategoriene for å endre rekkefølgen. Kategorier brukes til å
            organisere og filtrere maler.
          </p>
        </div>
      </main>

      {/* Create Category Dialog */}
      <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Ny kategori</DialogTitle>
            <DialogDescription>
              Opprett en ny kategori for å organisere malene dine.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="category-name">Navn</Label>
              <Input
                id="category-name"
                placeholder="F.eks. Kontrakter"
                value={newCategoryName}
                onChange={(e) => setNewCategoryName(e.target.value)}
                disabled={isCreating}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="category-icon">
                Ikon{" "}
                <span className="text-muted-foreground font-normal">
                  (emoji eller: FileText, Folder, Home, Users, Building, Mail)
                </span>
              </Label>
              <Input
                id="category-icon"
                placeholder="F.eks. 📄 eller FileText"
                value={newCategoryIcon}
                onChange={(e) => setNewCategoryIcon(e.target.value)}
                disabled={isCreating}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="category-description">
                Beskrivelse{" "}
                <span className="text-muted-foreground font-normal">(valgfritt)</span>
              </Label>
              <Input
                id="category-description"
                placeholder="En kort beskrivelse..."
                value={newCategoryDescription}
                onChange={(e) => setNewCategoryDescription(e.target.value)}
                disabled={isCreating}
              />
            </div>

            {createError && (
              <p className="text-sm text-destructive">{createError}</p>
            )}
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setCreateDialogOpen(false)}
              disabled={isCreating}
            >
              Avbryt
            </Button>
            <Button onClick={handleCreateCategory} disabled={isCreating}>
              {isCreating ? "Oppretter..." : "Opprett"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
