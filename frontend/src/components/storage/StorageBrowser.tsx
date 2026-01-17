"use client";

import { useState, useEffect, useCallback } from "react";
import {
  Folder,
  File,
  FileText,
  FileImage,
  FileSpreadsheet,
  Download,
  Trash2,
  Edit3,
  Import,
  RefreshCw,
  Upload,
  FolderPlus,
  ChevronRight,
  Home,
  AlertCircle,
  Loader2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { storageApi, type StorageItem, type BrowseResponse } from "@/lib/api";
import { RenameDialog } from "./RenameDialog";
import { NewFolderDialog } from "./NewFolderDialog";
import { ImportToLibraryDialog } from "./ImportToLibraryDialog";
import { UploadDialog } from "./UploadDialog";
import { cn } from "@/lib/utils";

interface StorageBrowserProps {
  onStatusChange?: (connected: boolean) => void;
}

export function StorageBrowser({ onStatusChange }: StorageBrowserProps) {
  const [currentPath, setCurrentPath] = useState("/");
  const [items, setItems] = useState<StorageItem[]>([]);
  const [parentPath, setParentPath] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedItems, setSelectedItems] = useState<Set<string>>(new Set());

  // Dialog states
  const [renameItem, setRenameItem] = useState<StorageItem | null>(null);
  const [deleteItem, setDeleteItem] = useState<StorageItem | null>(null);
  const [importItem, setImportItem] = useState<StorageItem | null>(null);
  const [showNewFolder, setShowNewFolder] = useState(false);
  const [showUpload, setShowUpload] = useState(false);

  const loadDirectory = useCallback(async (path: string) => {
    setLoading(true);
    setError(null);

    try {
      const data = await storageApi.browse(path);
      setItems(data.items);
      setCurrentPath(data.path);
      setParentPath(data.parent_path);
      setSelectedItems(new Set());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Kunne ikke laste mappe");
      setItems([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDirectory(currentPath);
  }, []);

  // Check connection status only once on mount
  useEffect(() => {
    storageApi.getStatus().then((status) => {
      onStatusChange?.(status.connected);
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleNavigate = (path: string) => {
    loadDirectory(path);
  };

  const handleRefresh = () => {
    loadDirectory(currentPath);
  };

  const handleDownload = async (item: StorageItem) => {
    try {
      const blob = await storageApi.download(item.path);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = item.name;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Kunne ikke laste ned fil");
    }
  };

  const handleDelete = async () => {
    if (!deleteItem) return;

    try {
      await storageApi.delete(deleteItem.path);
      setDeleteItem(null);
      handleRefresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Kunne ikke slette");
    }
  };

  const handleRename = async (newName: string) => {
    if (!renameItem) return;

    try {
      const parentDir = renameItem.path.substring(
        0,
        renameItem.path.lastIndexOf("/")
      );
      const newPath = `${parentDir}/${newName}`;
      await storageApi.move(renameItem.path, newPath);
      setRenameItem(null);
      handleRefresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Kunne ikke endre navn");
    }
  };

  const handleCreateFolder = async (name: string) => {
    try {
      const path = `${currentPath.replace(/\/$/, "")}/${name}`;
      await storageApi.createDirectory(path);
      setShowNewFolder(false);
      handleRefresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Kunne ikke opprette mappe");
    }
  };

  const handleUploadComplete = () => {
    setShowUpload(false);
    handleRefresh();
  };

  const handleImportComplete = () => {
    setImportItem(null);
    // Optionally show success message
  };

  const toggleSelection = (path: string) => {
    const newSelection = new Set(selectedItems);
    if (newSelection.has(path)) {
      newSelection.delete(path);
    } else {
      newSelection.add(path);
    }
    setSelectedItems(newSelection);
  };

  const getFileIcon = (item: StorageItem) => {
    if (item.is_directory) {
      return <Folder className="h-5 w-5 text-yellow-500" />;
    }

    const ext = item.name.split(".").pop()?.toLowerCase();
    switch (ext) {
      case "html":
      case "htm":
      case "doc":
      case "docx":
      case "pdf":
        return <FileText className="h-5 w-5 text-blue-500" />;
      case "jpg":
      case "jpeg":
      case "png":
      case "gif":
      case "svg":
        return <FileImage className="h-5 w-5 text-green-500" />;
      case "xls":
      case "xlsx":
        return <FileSpreadsheet className="h-5 w-5 text-emerald-600" />;
      default:
        return <File className="h-5 w-5 text-gray-500" />;
    }
  };

  const formatSize = (bytes: number): string => {
    if (bytes === 0) return "-";
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const formatDate = (dateStr: string | null): string => {
    if (!dateStr) return "-";
    try {
      return new Date(dateStr).toLocaleDateString("nb-NO", {
        day: "2-digit",
        month: "short",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return "-";
    }
  };

  const canImport = (item: StorageItem): boolean => {
    if (item.is_directory) return false;
    const ext = item.name.split(".").pop()?.toLowerCase();
    return ["html", "htm", "doc", "docx", "pdf", "xls", "xlsx"].includes(
      ext || ""
    );
  };

  // Build breadcrumb parts
  const pathParts = currentPath
    .split("/")
    .filter((p) => p)
    .map((part, idx, arr) => ({
      name: part,
      path: "/" + arr.slice(0, idx + 1).join("/"),
    }));

  return (
    <div className="flex flex-col h-full">
      {/* Toolbar */}
      <div className="flex items-center justify-between gap-4 mb-4">
        {/* Breadcrumb */}
        <nav className="flex items-center gap-1 text-sm overflow-x-auto">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => handleNavigate("/")}
            className="px-2"
          >
            <Home className="h-4 w-4" />
          </Button>
          {pathParts.map((part, idx) => (
            <div key={part.path} className="flex items-center">
              <ChevronRight className="h-4 w-4 text-muted-foreground" />
              <Button
                variant="ghost"
                size="sm"
                onClick={() => handleNavigate(part.path)}
                className={cn(
                  "px-2",
                  idx === pathParts.length - 1 && "font-medium"
                )}
              >
                {part.name}
              </Button>
            </div>
          ))}
        </nav>

        {/* Actions */}
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            disabled={loading}
          >
            <RefreshCw
              className={cn("h-4 w-4 mr-2", loading && "animate-spin")}
            />
            Oppdater
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowNewFolder(true)}
          >
            <FolderPlus className="h-4 w-4 mr-2" />
            Ny mappe
          </Button>
          <Button size="sm" onClick={() => setShowUpload(true)}>
            <Upload className="h-4 w-4 mr-2" />
            Last opp
          </Button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="flex items-center gap-2 p-3 mb-4 text-sm text-destructive bg-destructive/10 rounded-lg">
          <AlertCircle className="h-4 w-4" />
          {error}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setError(null)}
            className="ml-auto"
          >
            Lukk
          </Button>
        </div>
      )}

      {/* File List */}
      <Card className="flex-1 overflow-hidden">
        <div className="overflow-auto h-full">
          {loading ? (
            <div className="flex items-center justify-center h-full">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : items.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
              <Folder className="h-12 w-12 mb-2" />
              <p>Mappen er tom</p>
            </div>
          ) : (
            <table className="w-full">
              <thead className="bg-muted/50 sticky top-0">
                <tr className="text-left text-sm text-muted-foreground">
                  <th className="w-10 p-3"></th>
                  <th className="p-3">Navn</th>
                  <th className="w-28 p-3">Størrelse</th>
                  <th className="w-40 p-3">Endret</th>
                  <th className="w-20 p-3"></th>
                </tr>
              </thead>
              <tbody>
                {/* Parent directory link */}
                {parentPath && (
                  <tr
                    className="border-b hover:bg-muted/30 cursor-pointer"
                    onClick={() => handleNavigate(parentPath)}
                  >
                    <td className="p-3"></td>
                    <td className="p-3">
                      <div className="flex items-center gap-3">
                        <Folder className="h-5 w-5 text-yellow-500" />
                        <span className="text-muted-foreground">..</span>
                      </div>
                    </td>
                    <td className="p-3 text-sm text-muted-foreground">-</td>
                    <td className="p-3 text-sm text-muted-foreground">-</td>
                    <td className="p-3"></td>
                  </tr>
                )}

                {items.map((item) => (
                  <tr
                    key={item.path}
                    className={cn(
                      "border-b hover:bg-muted/30",
                      item.is_directory && "cursor-pointer",
                      selectedItems.has(item.path) && "bg-primary/5"
                    )}
                    onClick={() =>
                      item.is_directory && handleNavigate(item.path)
                    }
                  >
                    <td className="p-3" onClick={(e) => e.stopPropagation()}>
                      <Checkbox
                        checked={selectedItems.has(item.path)}
                        onCheckedChange={() => toggleSelection(item.path)}
                      />
                    </td>
                    <td className="p-3">
                      <div className="flex items-center gap-3">
                        {getFileIcon(item)}
                        <span className="truncate max-w-md">{item.name}</span>
                      </div>
                    </td>
                    <td className="p-3 text-sm text-muted-foreground">
                      {formatSize(item.size)}
                    </td>
                    <td className="p-3 text-sm text-muted-foreground">
                      {formatDate(item.modified)}
                    </td>
                    <td className="p-3" onClick={(e) => e.stopPropagation()}>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm">
                            ...
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          {!item.is_directory && (
                            <DropdownMenuItem
                              onClick={() => handleDownload(item)}
                            >
                              <Download className="h-4 w-4 mr-2" />
                              Last ned
                            </DropdownMenuItem>
                          )}
                          {canImport(item) && (
                            <DropdownMenuItem
                              onClick={() => setImportItem(item)}
                            >
                              <Import className="h-4 w-4 mr-2" />
                              Importer til bibliotek
                            </DropdownMenuItem>
                          )}
                          <DropdownMenuSeparator />
                          <DropdownMenuItem
                            onClick={() => setRenameItem(item)}
                          >
                            <Edit3 className="h-4 w-4 mr-2" />
                            Endre navn
                          </DropdownMenuItem>
                          <DropdownMenuItem
                            onClick={() => setDeleteItem(item)}
                            className="text-destructive"
                          >
                            <Trash2 className="h-4 w-4 mr-2" />
                            Slett
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </Card>

      {/* Dialogs */}
      <RenameDialog
        open={!!renameItem}
        item={renameItem}
        onOpenChange={(open) => !open && setRenameItem(null)}
        onRename={handleRename}
      />

      <NewFolderDialog
        open={showNewFolder}
        onOpenChange={setShowNewFolder}
        onCreate={handleCreateFolder}
      />

      <UploadDialog
        open={showUpload}
        currentPath={currentPath}
        onOpenChange={setShowUpload}
        onComplete={handleUploadComplete}
      />

      <ImportToLibraryDialog
        open={!!importItem}
        item={importItem}
        onOpenChange={(open) => !open && setImportItem(null)}
        onComplete={handleImportComplete}
      />

      <AlertDialog open={!!deleteItem} onOpenChange={() => setDeleteItem(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Slett {deleteItem?.name}?</AlertDialogTitle>
            <AlertDialogDescription>
              {deleteItem?.is_directory
                ? "Denne mappen og alt innhold vil bli slettet permanent."
                : "Denne filen vil bli slettet permanent."}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Avbryt</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Slett
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
