"use client";

import { useState } from "react";
import { FolderTree, Plus, Pencil, Trash2, GripVertical } from "lucide-react";
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
import { categoryApi } from "@/lib/api";

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
          <Skeleton className="h-6 w-6" />
          <Skeleton className="h-5 w-32" />
          <Skeleton className="h-4 w-48 ml-auto" />
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
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <Header />

      <main className="container mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h2 className="text-2xl font-bold text-slate-900">Kategorier</h2>
            <p className="text-slate-500">Organiser malene dine i kategorier</p>
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
              {categories.map((category, index) => (
                <div
                  key={category.id}
                  className="flex items-center gap-4 p-4 hover:bg-slate-50 transition-colors"
                >
                  <GripVertical className="h-5 w-5 text-slate-300 cursor-grab" />

                  <div className="w-10 h-10 rounded-lg bg-slate-100 flex items-center justify-center text-xl">
                    {category.icon || "📁"}
                  </div>

                  <div className="flex-1">
                    <p className="font-medium">{category.name}</p>
                    {category.description && (
                      <p className="text-sm text-slate-500">{category.description}</p>
                    )}
                  </div>

                  <div className="text-sm text-slate-500">
                    Rekkefølge: {category.sort_order ?? index + 1}
                  </div>

                  <div className="flex gap-1">
                    <Button variant="ghost" size="icon" title="Rediger">
                      <Pencil className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      title="Slett"
                      onClick={() => handleDeleteCategory(category.id, category.name)}
                    >
                      <Trash2 className="h-4 w-4 text-red-500" />
                    </Button>
                  </div>
                </div>
              ))}
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
                <span className="text-muted-foreground font-normal">(emoji, valgfritt)</span>
              </Label>
              <Input
                id="category-icon"
                placeholder="F.eks. 📄"
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
