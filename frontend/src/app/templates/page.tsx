"use client";

import { useState, useEffect, useMemo, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import {
  FileText,
  Search,
  Clock,
  Download,
  MoreHorizontal,
  Trash2,
  Pencil,
  Eye,
  X,
  LayoutGrid,
  List,
} from "lucide-react";
import { Header } from "@/components/layout/Header";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
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
import { EditTemplateDialog } from "@/components/templates/EditTemplateDialog";
import { PreviewDialog } from "@/components/templates/PreviewDialog";
import { TemplateDetailSheet } from "@/components/templates/TemplateDetailSheet";
import { useTemplates } from "@/hooks/useTemplates";
import { useCategories } from "@/hooks/useCategories";
import { templateApi } from "@/lib/api";
import { getCategoryIcon } from "@/lib/category-icons";
import { formatDistanceToNow } from "date-fns";
import { nb } from "date-fns/locale";
import type { Template, TemplateStatus } from "@/types";
import { ShelfLibrary } from "@/components/shelf";

function TemplateTableSkeleton() {
  return (
    <div className="space-y-4">
      {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
        <div key={i} className="flex items-center gap-4 p-4 border rounded-lg">
          <Skeleton className="h-10 w-10 rounded" />
          <div className="flex-1">
            <Skeleton className="h-4 w-48 mb-2" />
            <Skeleton className="h-3 w-32" />
          </div>
          <Skeleton className="h-6 w-16" />
          <Skeleton className="h-4 w-24" />
        </div>
      ))}
    </div>
  );
}

type ViewMode = "table" | "shelf";

type OriginKey = "vitec" | "kundemal" | "unknown";

const getOriginKey = (template: Template): OriginKey => {
  const tagNames = (template.tags ?? [])
    .map((tag) => tag.name.trim().toLowerCase())
    .filter(Boolean);
  if (tagNames.some((name) => name.includes("kundemal"))) return "kundemal";
  if (tagNames.some((name) => name.includes("vitec"))) return "vitec";
  return "unknown";
};

const originGroupOrder: { key: OriginKey; label: string }[] = [
  { key: "vitec", label: "Vitec Next" },
  { key: "kundemal", label: "Kundemal" },
  { key: "unknown", label: "Ukjent" },
];

function TemplatesPageContent() {
  const searchParams = useSearchParams();
  const categoryFromUrl = searchParams.get("category");
  const receiverFromUrl = searchParams.get("receiver");
  
  const [viewMode, setViewMode] = useState<ViewMode>("shelf");
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<TemplateStatus | undefined>(undefined);
  const [categoryFilter, setCategoryFilter] = useState<string | undefined>(undefined);
  const [receiverFilter, setReceiverFilter] = useState<string | undefined>(undefined);
  const [tablePage, setTablePage] = useState(1);

  // Sync category filter with URL params
  useEffect(() => {
    setCategoryFilter(categoryFromUrl || undefined);
  }, [categoryFromUrl]);

  useEffect(() => {
    setReceiverFilter(receiverFromUrl || undefined);
  }, [receiverFromUrl]);

  useEffect(() => {
    setTablePage(1);
  }, [searchQuery, statusFilter, categoryFilter, receiverFilter]);

  // Fetch categories for display
  const { categories } = useCategories();
  const selectedCategory = categories.find((c) => c.id === categoryFilter);
  const selectedReceiver = receiverFilter ?? null;

  // Edit dialog state
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [templateToEdit, setTemplateToEdit] = useState<Template | null>(null);

  // Delete confirmation state
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [templateToDelete, setTemplateToDelete] = useState<Template | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  // Preview dialog state
  const [previewDialogOpen, setPreviewDialogOpen] = useState(false);
  const [templateToPreview, setTemplateToPreview] = useState<Template | null>(null);

  // Detail sheet state (for row click)
  const [detailSheetOpen, setDetailSheetOpen] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null);

  const { templates, pagination, isLoading, error, refetch } = useTemplates({
    search: searchQuery || undefined,
    status: statusFilter,
    category_id: categoryFilter,
    receiver: receiverFilter,
    page: tablePage,
    per_page: 100,
  });

  const clearCategoryFilter = () => {
    setCategoryFilter(undefined);
    const params = new URLSearchParams(searchParams.toString());
    params.delete("category");
    const url = params.toString() ? `/templates?${params.toString()}` : "/templates";
    window.history.replaceState({}, "", url);
  };

  const clearReceiverFilter = () => {
    setReceiverFilter(undefined);
    const params = new URLSearchParams(searchParams.toString());
    params.delete("receiver");
    const url = params.toString() ? `/templates?${params.toString()}` : "/templates";
    window.history.replaceState({}, "", url);
  };

  const handleUploadSuccess = () => {
    refetch();
  };

  const handleEditClick = (template: Template) => {
    setTemplateToEdit(template);
    setEditDialogOpen(true);
  };

  const handleEditSuccess = () => {
    refetch();
    setTemplateToEdit(null);
  };

  const handleDeleteClick = (template: Template) => {
    setTemplateToDelete(template);
    setDeleteDialogOpen(true);
  };

  const handlePreviewClick = (template: Template) => {
    setTemplateToPreview(template);
    setPreviewDialogOpen(true);
  };

  const handleRowClick = (template: Template) => {
    setSelectedTemplate(template);
    setDetailSheetOpen(true);
  };

  const handleSheetEdit = (template: Template) => {
    setDetailSheetOpen(false);
    handleEditClick(template);
  };

  const handleSheetDownload = (template: Template) => {
    handleDownload(template);
  };

  const handleDeleteConfirm = async () => {
    if (!templateToDelete) return;

    setIsDeleting(true);
    try {
      await templateApi.delete(templateToDelete.id);
      refetch();
      setDeleteDialogOpen(false);
      setTemplateToDelete(null);
    } catch (error) {
      console.error("Failed to delete template:", error);
      // Keep dialog open so user can see error or retry
    } finally {
      setIsDeleting(false);
    }
  };

  const handleDownload = async (template: Template) => {
    try {
      const { download_url, file_name } = await templateApi.getDownloadUrl(template.id);
      // For mock URLs, just show an alert. For real URLs, open in new tab.
      if (download_url.startsWith("mock://")) {
        alert(`Nedlasting er ikke tilgjengelig ennå. Fil: ${file_name}`);
      } else {
        window.open(download_url, "_blank");
      }
    } catch (error) {
      console.error("Failed to get download URL:", error);
      alert("Kunne ikke laste ned filen. Prøv igjen.");
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return "Ukjent";
    try {
      return formatDistanceToNow(new Date(dateString), { addSuffix: true, locale: nb });
    } catch {
      return "Ukjent";
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const getFileTypeColor = (fileType: string) => {
    const colors: Record<string, string> = {
      pdf: "bg-[#F5EDE1] text-[#8A5A2B]",
      docx: "bg-[#E6EEF9] text-[#1E40AF]",
      doc: "bg-[#E6EEF9] text-[#1E40AF]",
      xlsx: "bg-[#E8F5EC] text-[#166534]",
      xls: "bg-[#E8F5EC] text-[#166534]",
      html: "bg-[#F3E8FF] text-[#6D28D9]",
      htm: "bg-[#F3E8FF] text-[#6D28D9]",
    };
    return colors[fileType] || "bg-muted text-muted-foreground";
  };

  const canPreview = (fileType: string) => {
    return fileType === "html" || fileType === "htm";
  };

  const statusFilters: Array<{ value: TemplateStatus | undefined; label: string }> = [
    { value: undefined, label: "Alle" },
    { value: "published", label: "Publisert" },
    { value: "draft", label: "Utkast" },
    { value: "archived", label: "Arkivert" },
  ];



  const groupedTemplates = useMemo(() => {
    const grouped: Record<OriginKey, Template[]> = {
      vitec: [],
      kundemal: [],
      unknown: [],
    };

    templates.forEach((template) => {
      grouped[getOriginKey(template)].push(template);
    });

    return grouped;
  }, [templates]);

  const renderTemplateRow = (template: Template) => (
    <div
      key={template.id}
      onClick={() => handleRowClick(template)}
      className="grid grid-cols-12 gap-4 p-4 items-center cursor-pointer hover:bg-[#F5F5F0] transition-colors"
    >
      <div className="col-span-5 flex items-center gap-3">
        <div className={`p-2 rounded-md ${getFileTypeColor(template.file_type)}`}>
          <FileText className="h-5 w-5" />
        </div>
        <div className="min-w-0">
          <p className="font-medium text-[#272630] truncate">{template.title}</p>
          <p className="text-sm text-[#272630]/50 font-sans truncate">
            {template.file_name} • {formatFileSize(template.file_size_bytes)}
          </p>
        </div>
      </div>

      <div className="col-span-2">
        <span
          className={`px-2 py-1 rounded text-xs uppercase font-medium ${getFileTypeColor(
            template.file_type
          )}`}
        >
          {template.file_type}
        </span>
      </div>

      <div className="col-span-2">
        <span
          className={`px-2 py-1 rounded-md text-xs font-medium font-sans ${
            template.status === "published"
              ? "bg-green-50 text-green-700 border border-green-200"
              : template.status === "draft"
              ? "bg-amber-50 text-amber-700 border border-amber-200"
              : "bg-[#F5F5F0] text-[#272630]/60"
          }`}
        >
          {template.status === "published"
            ? "Publisert"
            : template.status === "draft"
            ? "Utkast"
            : template.status}
        </span>
      </div>

      <div className="col-span-2 flex items-center gap-1 text-sm text-[#272630]/50 font-sans">
        <Clock className="h-4 w-4 text-[#BCAB8A]" />
        {formatDate(template.updated_at)}
      </div>

      <div className="col-span-1 flex justify-end" onClick={(e) => e.stopPropagation()}>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon">
              <MoreHorizontal className="h-4 w-4" />
              <span className="sr-only">Åpne meny</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            {canPreview(template.file_type) && (
              <DropdownMenuItem onClick={() => handlePreviewClick(template)}>
                <Eye className="mr-2 h-4 w-4" />
                Forhåndsvis
              </DropdownMenuItem>
            )}
            <DropdownMenuItem onClick={() => handleDownload(template)}>
              <Download className="mr-2 h-4 w-4" />
              Last ned
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => handleEditClick(template)}>
              <Pencil className="mr-2 h-4 w-4" />
              Rediger
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              onClick={() => handleDeleteClick(template)}
              className="text-red-600 focus:text-red-600 focus:bg-red-50"
            >
              <Trash2 className="mr-2 h-4 w-4" />
              Slett
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-background">
      <Header onUploadSuccess={handleUploadSuccess} />

      <main className="container mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h2 className="text-2xl font-bold text-foreground">Maler</h2>
            <p className="text-muted-foreground">Administrer alle dokumentmaler</p>
          </div>
          
          {/* View mode toggle */}
          <div className="flex items-center gap-1 p-1 bg-gray-100 rounded-lg">
            <Button
              variant={viewMode === "table" ? "default" : "ghost"}
              size="sm"
              onClick={() => setViewMode("table")}
              className="gap-2"
            >
              <List className="h-4 w-4" />
              Liste
            </Button>
            <Button
              variant={viewMode === "shelf" ? "default" : "ghost"}
              size="sm"
              onClick={() => setViewMode("shelf")}
              className="gap-2"
            >
              <LayoutGrid className="h-4 w-4" />
              Hylle
            </Button>
          </div>
        </div>

        {/* Active Filters */}
        {(selectedCategory || selectedReceiver) && (
          <div className="flex flex-wrap items-center gap-3 mb-4">
            {selectedCategory && (
              <div className="flex items-center gap-2">
                <span className="text-sm text-[#272630]/60 font-sans">Filtrert etter kategori:</span>
                <div className="inline-flex items-center gap-1 px-3 py-1 rounded-md bg-[#BCAB8A] text-white text-sm font-medium">
                  {(() => {
                    const IconComponent = getCategoryIcon(selectedCategory.icon);
                    return <IconComponent className="h-3.5 w-3.5" />;
                  })()}
                  {selectedCategory.name}
                  <button
                    onClick={clearCategoryFilter}
                    className="ml-1 hover:bg-white/20 rounded-full p-0.5"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </div>
              </div>
            )}
            {selectedReceiver && (
              <div className="flex items-center gap-2">
                <span className="text-sm text-[#272630]/60 font-sans">Filtrert etter mottaker:</span>
                <div className="inline-flex items-center gap-1 px-3 py-1 rounded-md bg-[#272630] text-white text-sm font-medium">
                  {selectedReceiver}
                  <button
                    onClick={clearReceiverFilter}
                    className="ml-1 hover:bg-white/20 rounded-full p-0.5"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Shelf View */}
        {viewMode === "shelf" && (
          <div className="bg-white rounded-md p-6 border" style={{ minHeight: "60vh" }}>
            <ShelfLibrary
              key={`${categoryFilter ?? "all"}-${receiverFilter ?? "all"}-${statusFilter ?? "all"}`}
              initialFilters={{
                category_id: categoryFilter ?? null,
                receiver: receiverFilter ?? null,
                status: statusFilter ?? null,
              }}
              onTemplateSelect={(template) => handleRowClick(template as unknown as Template)}
              onTemplatePreview={(template) => handlePreviewClick(template as unknown as Template)}
              onTemplateEdit={(template) => handleEditClick(template as unknown as Template)}
              onTemplateDelete={(template) => handleDeleteClick(template as unknown as Template)}
            />
          </div>
        )}

        {/* Table View */}
        {viewMode === "table" && (
          <>
        {/* Filters */}
        <div className="bg-white rounded-md p-4 border border-[#E5E5E5] mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Søk i maler..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>

            <div className="flex gap-2">
              {statusFilters.map((filter) => (
                <Button
                  key={filter.value ?? "all"}
                  variant={statusFilter === filter.value ? "default" : "outline"}
                  size="sm"
                  onClick={() => setStatusFilter(filter.value)}
                >
                  {filter.label}
                </Button>
              ))}
            </div>
          </div>
        </div>

        {/* Templates List */}
        <div className="bg-white rounded-md border border-[#E5E5E5]">
          {isLoading ? (
            <div className="p-4">
              <TemplateTableSkeleton />
            </div>
          ) : error ? (
            <div className="p-8 text-center text-red-600">
              <p>Feil ved lasting av maler: {error}</p>
              <Button variant="outline" onClick={refetch} className="mt-4">
                Prøv igjen
              </Button>
            </div>
          ) : templates.length === 0 ? (
            <div className="p-12 text-center text-[#272630]/50">
              <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p className="text-lg font-medium font-serif">Ingen maler funnet</p>
              <p className="text-sm font-sans">
                {searchQuery
                  ? "Prøv et annet søkeord"
                  : 'Klikk "Last opp" for å legge til din første mal.'}
              </p>
            </div>
          ) : (
            <>
              {/* Table Header */}
              <div className="grid grid-cols-12 gap-4 p-4 border-b border-[#E5E5E5] bg-[#F5F5F0] text-sm font-medium text-[#272630]/70 font-sans">
                <div className="col-span-5">Mal</div>
                <div className="col-span-2">Type</div>
                <div className="col-span-2">Status</div>
                <div className="col-span-2">Oppdatert</div>
                <div className="col-span-1"></div>
              </div>

              {/* Table Body */}
              <div className="divide-y divide-[#E5E5E5]">
                {originGroupOrder.map((group) => {
                  const groupTemplates = groupedTemplates[group.key];
                  if (groupTemplates.length === 0) return null;

                  return (
                    <div key={group.key} className="bg-white">
                      <div className="px-4 py-2 text-xs font-semibold uppercase tracking-wide bg-[#F5F5F0] text-[#272630]/70">
                        {group.label} • {groupTemplates.length}
                      </div>
                      <div className="divide-y divide-[#E5E5E5]">
                        {groupTemplates.map((template) => renderTemplateRow(template))}
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Pagination */}
              {pagination && pagination.total_pages > 1 && (
                <div className="p-4 border-t border-[#E5E5E5] flex items-center justify-between">
                  <p className="text-sm text-[#272630]/50 font-sans">
                    Viser {templates.length} av {pagination.total} maler • Side {pagination.page} av{" "}
                    {pagination.total_pages}
                  </p>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={pagination.page === 1}
                      onClick={() => setTablePage((prev) => Math.max(1, prev - 1))}
                    >
                      Forrige
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={pagination.page === pagination.total_pages}
                      onClick={() =>
                        setTablePage((prev) =>
                          Math.min(pagination.total_pages, prev + 1)
                        )
                      }
                    >
                      Neste
                    </Button>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
          </>
        )}
      </main>

      {/* Edit Dialog */}
      <EditTemplateDialog
        template={templateToEdit}
        open={editDialogOpen}
        onOpenChange={setEditDialogOpen}
        onSuccess={handleEditSuccess}
      />

      {/* Preview Dialog */}
      <PreviewDialog
        template={templateToPreview}
        open={previewDialogOpen}
        onOpenChange={setPreviewDialogOpen}
      />

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Er du sikker?</AlertDialogTitle>
            <AlertDialogDescription>
              Du er i ferd med å slette malen{" "}
              <span className="font-semibold">&quot;{templateToDelete?.title}&quot;</span>.
              Denne handlingen kan ikke angres.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isDeleting}>Avbryt</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteConfirm}
              disabled={isDeleting}
              className="bg-red-600 hover:bg-red-700 focus:ring-red-600"
            >
              {isDeleting ? "Sletter..." : "Ja, slett malen"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Template Detail Sheet */}
      <TemplateDetailSheet
        template={selectedTemplate}
        open={detailSheetOpen}
        onOpenChange={setDetailSheetOpen}
        onEdit={handleSheetEdit}
        onDownload={handleSheetDownload}
      />
    </div>
  );
}

// Wrapper with Suspense boundary for useSearchParams
export default function TemplatesPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="animate-pulse text-muted-foreground">Laster maler...</div>
      </div>
    }>
      <TemplatesPageContent />
    </Suspense>
  );
}
