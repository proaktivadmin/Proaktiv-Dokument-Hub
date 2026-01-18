"use client";

import { useState, useEffect } from "react";
import { Import, Loader2 } from "lucide-react";
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
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { storageApi, categoryApi, type StorageItem } from "@/lib/api";
import { getCategoryIcon } from "@/lib/category-icons";
import type { Category } from "@/types";

interface ImportToLibraryDialogProps {
  open: boolean;
  item: StorageItem | null;
  onOpenChange: (open: boolean) => void;
  onComplete: () => void;
}

export function ImportToLibraryDialog({
  open,
  item,
  onOpenChange,
  onComplete,
}: ImportToLibraryDialogProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [status, setStatus] = useState<"draft" | "published">("draft");
  const [categoryId, setCategoryId] = useState<string>("");
  const [categories, setCategories] = useState<Category[]>([]);
  const [categoriesLoading, setCategoriesLoading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    if (item) {
      // Generate title from filename
      const name = item.name.replace(/\.[^/.]+$/, ""); // Remove extension
      setTitle(name);
      setDescription(`Importert fra nettverkslagring: ${item.path}`);
      setError(null);
      setSuccess(false);
    }
  }, [item]);

  useEffect(() => {
    if (open && categories.length === 0) {
      setCategoriesLoading(true);
      categoryApi
        .list()
        .then((data) => {
          setCategories(data);
        })
        .catch((err) => {
          console.error("Failed to load categories:", err);
        })
        .finally(() => {
          setCategoriesLoading(false);
        });
    }
  }, [open, categories.length]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!item) return;

    if (!title.trim()) {
      setError("Tittel er påkrevd");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await storageApi.importToLibrary({
        path: item.path,
        title: title.trim(),
        description: description.trim() || undefined,
        status,
        category_id: categoryId || undefined,
      });

      setSuccess(true);
      setTimeout(() => {
        onComplete();
      }, 1500);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Importering feilet");
    } finally {
      setLoading(false);
    }
  };

  const handleClose = (open: boolean) => {
    if (!open && !loading) {
      setTitle("");
      setDescription("");
      setStatus("draft");
      setCategoryId("");
      setError(null);
      setSuccess(false);
      onOpenChange(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Importer til bibliotek</DialogTitle>
          <DialogDescription>
            Importer <strong>{item?.name}</strong> som en ny mal i
            biblioteket.
          </DialogDescription>
        </DialogHeader>

        {success ? (
          <div className="py-8 text-center">
            <div className="mx-auto w-12 h-12 rounded-full bg-green-100 flex items-center justify-center mb-4">
              <Import className="h-6 w-6 text-green-600" />
            </div>
            <p className="text-lg font-medium text-green-600">
              Importert!
            </p>
            <p className="text-sm text-muted-foreground mt-1">
              Malen er lagt til i biblioteket.
            </p>
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            <div className="space-y-4 py-4">
              {/* Title */}
              <div className="space-y-2">
                <Label htmlFor="title">Tittel</Label>
                <Input
                  id="title"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Malens tittel"
                  disabled={loading}
                />
              </div>

              {/* Description */}
              <div className="space-y-2">
                <Label htmlFor="description">
                  Beskrivelse{" "}
                  <span className="text-muted-foreground font-normal">
                    (valgfritt)
                  </span>
                </Label>
                <Textarea
                  id="description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={2}
                  disabled={loading}
                />
              </div>

              {/* Category */}
              <div className="space-y-2">
                <Label htmlFor="category">
                  Kategori{" "}
                  <span className="text-muted-foreground font-normal">
                    (valgfritt)
                  </span>
                </Label>
                <Select
                  value={categoryId}
                  onValueChange={setCategoryId}
                  disabled={loading || categoriesLoading}
                >
                  <SelectTrigger id="category">
                    <SelectValue
                      placeholder={categoriesLoading ? "Laster..." : "Velg kategori"}
                    />
                  </SelectTrigger>
                  <SelectContent>
                    {categories.map((category) => (
                      <SelectItem key={category.id} value={category.id}>
                        {(() => {
                          const IconComponent = getCategoryIcon(category.icon);
                          return <IconComponent className="mr-2 h-4 w-4 text-muted-foreground" />;
                        })()}
                        {category.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Status */}
              <div className="space-y-2">
                <Label>Status</Label>
                <div className="flex gap-4">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      name="status"
                      value="draft"
                      checked={status === "draft"}
                      onChange={() => setStatus("draft")}
                      disabled={loading}
                      className="h-4 w-4"
                    />
                    <span className="text-sm">Utkast</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      name="status"
                      value="published"
                      checked={status === "published"}
                      onChange={() => setStatus("published")}
                      disabled={loading}
                      className="h-4 w-4"
                    />
                    <span className="text-sm">Publisert</span>
                  </label>
                </div>
              </div>

              {/* Error */}
              {error && (
                <div className="p-3 text-sm text-destructive bg-destructive/10 rounded-lg">
                  {error}
                </div>
              )}
            </div>

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => handleClose(false)}
                disabled={loading}
              >
                Avbryt
              </Button>
              <Button type="submit" disabled={loading}>
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Importerer...
                  </>
                ) : (
                  <>
                    <Import className="mr-2 h-4 w-4" />
                    Importer
                  </>
                )}
              </Button>
            </DialogFooter>
          </form>
        )}
      </DialogContent>
    </Dialog>
  );
}
