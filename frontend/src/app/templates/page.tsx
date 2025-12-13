"use client";

import { useState } from "react";
import { FileText, Search, Clock, Download, MoreHorizontal, Trash2 } from "lucide-react";
import { Header } from "@/components/layout/Header";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useTemplates } from "@/hooks/useTemplates";
import { templateApi } from "@/lib/api";
import { formatDistanceToNow } from "date-fns";
import { nb } from "date-fns/locale";

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

export default function TemplatesPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<string | undefined>(undefined);

  const { templates, pagination, isLoading, error, refetch } = useTemplates({
    search: searchQuery || undefined,
    status: statusFilter,
    per_page: 20,
  });

  const handleUploadSuccess = () => {
    refetch();
  };

  const handleDelete = async (templateId: string) => {
    if (!confirm("Er du sikker på at du vil slette denne malen?")) {
      return;
    }

    try {
      await templateApi.delete(templateId);
      refetch();
    } catch (error) {
      console.error("Failed to delete template:", error);
      alert("Kunne ikke slette malen. Prøv igjen.");
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
      pdf: "bg-red-100 text-red-700",
      docx: "bg-blue-100 text-blue-700",
      doc: "bg-blue-100 text-blue-700",
      xlsx: "bg-green-100 text-green-700",
      xls: "bg-green-100 text-green-700",
    };
    return colors[fileType] || "bg-slate-100 text-slate-700";
  };

  const statusFilters = [
    { value: undefined, label: "Alle" },
    { value: "published", label: "Publisert" },
    { value: "draft", label: "Utkast" },
    { value: "archived", label: "Arkivert" },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <Header onUploadSuccess={handleUploadSuccess} />

      <main className="container mx-auto px-6 py-8">
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-slate-900">Maler</h2>
          <p className="text-slate-500">Administrer alle dokumentmaler</p>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg p-4 shadow-sm border mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
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
        <div className="bg-white rounded-lg shadow-sm border">
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
            <div className="p-12 text-center text-slate-500">
              <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p className="text-lg font-medium">Ingen maler funnet</p>
              <p className="text-sm">
                {searchQuery
                  ? "Prøv et annet søkeord"
                  : 'Klikk "Last opp" for å legge til din første mal.'}
              </p>
            </div>
          ) : (
            <>
              {/* Table Header */}
              <div className="grid grid-cols-12 gap-4 p-4 border-b bg-slate-50 text-sm font-medium text-slate-600">
                <div className="col-span-5">Mal</div>
                <div className="col-span-2">Type</div>
                <div className="col-span-2">Status</div>
                <div className="col-span-2">Oppdatert</div>
                <div className="col-span-1"></div>
              </div>

              {/* Table Body */}
              <div className="divide-y">
                {templates.map((template) => (
                  <div
                    key={template.id}
                    className="grid grid-cols-12 gap-4 p-4 items-center hover:bg-slate-50 transition-colors"
                  >
                    <div className="col-span-5 flex items-center gap-3">
                      <div className={`p-2 rounded ${getFileTypeColor(template.file_type)}`}>
                        <FileText className="h-5 w-5" />
                      </div>
                      <div className="min-w-0">
                        <p className="font-medium truncate">{template.title}</p>
                        <p className="text-sm text-slate-500 truncate">
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
                        className={`px-2 py-1 rounded-full text-xs font-medium ${
                          template.status === "published"
                            ? "bg-green-100 text-green-700"
                            : template.status === "draft"
                            ? "bg-amber-100 text-amber-700"
                            : "bg-slate-100 text-slate-700"
                        }`}
                      >
                        {template.status === "published"
                          ? "Publisert"
                          : template.status === "draft"
                          ? "Utkast"
                          : template.status}
                      </span>
                    </div>

                    <div className="col-span-2 flex items-center gap-1 text-sm text-slate-500">
                      <Clock className="h-4 w-4" />
                      {formatDate(template.updated_at)}
                    </div>

                    <div className="col-span-1 flex justify-end gap-1">
                      <Button variant="ghost" size="icon" title="Last ned">
                        <Download className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        title="Slett"
                        onClick={() => handleDelete(template.id)}
                      >
                        <Trash2 className="h-4 w-4 text-red-500" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>

              {/* Pagination */}
              {pagination && pagination.total_pages > 1 && (
                <div className="p-4 border-t flex items-center justify-between">
                  <p className="text-sm text-slate-500">
                    Viser {templates.length} av {pagination.total} maler
                  </p>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" disabled={pagination.page === 1}>
                      Forrige
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={pagination.page === pagination.total_pages}
                    >
                      Neste
                    </Button>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </main>
    </div>
  );
}
