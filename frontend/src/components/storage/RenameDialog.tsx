"use client";

import { useState, useEffect } from "react";
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
import type { StorageItem } from "@/lib/api";

interface RenameDialogProps {
  open: boolean;
  item: StorageItem | null;
  onOpenChange: (open: boolean) => void;
  onRename: (newName: string) => Promise<void>;
}

export function RenameDialog({
  open,
  item,
  onOpenChange,
  onRename,
}: RenameDialogProps) {
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (item) {
      setName(item.name);
      setError(null);
    }
  }, [item]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!name.trim()) {
      setError("Navn kan ikke være tomt");
      return;
    }

    if (name === item?.name) {
      onOpenChange(false);
      return;
    }

    // Validate name (no special characters)
    if (/[\/\\:*?"<>|]/.test(name)) {
      setError('Navnet kan ikke inneholde / \\ : * ? " < > |');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await onRename(name.trim());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Kunne ikke endre navn");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[400px]">
        <DialogHeader>
          <DialogTitle>Endre navn</DialogTitle>
          <DialogDescription>
            Skriv inn et nytt navn for{" "}
            {item?.is_directory ? "mappen" : "filen"}.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit}>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="name">Navn</Label>
              <Input
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                disabled={loading}
                autoFocus
              />
              {error && <p className="text-sm text-destructive">{error}</p>}
            </div>
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={loading}
            >
              Avbryt
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? "Endrer..." : "Endre navn"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
