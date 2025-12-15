"use client";

import { FileText, Download, Clock, AlertCircle } from "lucide-react";
import { Header } from "@/components/layout/Header";
import { Skeleton } from "@/components/ui/skeleton";
import { useDashboardStats } from "@/hooks/useDashboard";
import { useRecentTemplates } from "@/hooks/useTemplates";
import { useCategories } from "@/hooks/useCategories";
import { formatDistanceToNow } from "date-fns";
import { nb } from "date-fns/locale";
import Link from "next/link";

function StatCardSkeleton() {
  return (
    <div className="bg-white rounded-md p-6 border border-[#E5E5E5]">
      <Skeleton className="h-4 w-24 mb-2" />
      <Skeleton className="h-10 w-16" />
    </div>
  );
}

function TemplateListSkeleton() {
  return (
    <div className="space-y-3">
      {[1, 2, 3, 4, 5].map((i) => (
        <div key={i} className="flex items-center gap-3 p-3 border border-[#E5E5E5] rounded-md">
          <Skeleton className="h-10 w-10 rounded-md" />
          <div className="flex-1">
            <Skeleton className="h-4 w-48 mb-1" />
            <Skeleton className="h-3 w-24" />
          </div>
        </div>
      ))}
    </div>
  );
}

function CategorySkeleton() {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {[1, 2, 3, 4].map((i) => (
        <div key={i} className="p-4 rounded-md bg-[#F5F5F0]">
          <Skeleton className="h-5 w-24 mb-2" />
          <Skeleton className="h-8 w-12 mb-1" />
          <Skeleton className="h-3 w-16" />
        </div>
      ))}
    </div>
  );
}

export default function Dashboard() {
  const { stats, isLoading: statsLoading, error: statsError, refetch: refetchStats } = useDashboardStats();
  const { templates: recentTemplates, isLoading: templatesLoading, refetch: refetchTemplates } = useRecentTemplates();
  const { categories, isLoading: categoriesLoading } = useCategories();

  const handleUploadSuccess = () => {
    refetchStats();
    refetchTemplates();
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return "Ukjent";
    try {
      return formatDistanceToNow(new Date(dateString), { addSuffix: true, locale: nb });
    } catch {
      return "Ukjent";
    }
  };

  const getFileTypeIcon = (fileType: string) => {
    const colors: Record<string, string> = {
      pdf: "text-red-500",
      docx: "text-blue-500",
      doc: "text-blue-500",
      xlsx: "text-green-500",
      xls: "text-green-500",
    };
    return colors[fileType] || "text-muted-foreground";
  };

  return (
    <div className="min-h-screen bg-background">
      <Header onUploadSuccess={handleUploadSuccess} />

      <main className="container mx-auto px-6 py-8">
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-foreground">Dashboard</h2>
          <p className="text-muted-foreground">Oversikt over alle maler og aktivitet</p>
        </div>

        {/* Error State */}
        {statsError && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3">
            <AlertCircle className="h-5 w-5 text-red-600" />
            <p className="text-red-800">{statsError}</p>
          </div>
        )}

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {statsLoading ? (
            <>
              <div className="bg-[#272630] text-white rounded-md p-6 border border-[#E5E5E5]">
                <Skeleton className="h-4 w-24 mb-2 bg-white/20" />
                <Skeleton className="h-10 w-16 bg-white/20" />
              </div>
              <StatCardSkeleton />
              <StatCardSkeleton />
              <StatCardSkeleton />
            </>
          ) : (
            <>
              <div className="bg-[#272630] text-white rounded-md p-6">
                <p className="text-white/70 text-sm font-sans">Totalt maler</p>
                <p className="text-4xl font-serif font-bold mt-2">{stats?.total_templates ?? 0}</p>
              </div>

              <div className="bg-white rounded-md p-6 border border-[#E5E5E5]">
                <p className="text-[#272630]/60 text-sm font-sans">Publiserte</p>
                <p className="text-4xl font-serif font-bold text-[#272630] mt-2">
                  {stats?.published_templates ?? 0}
                </p>
              </div>

              <div className="bg-white rounded-md p-6 border border-[#E5E5E5]">
                <p className="text-[#272630]/60 text-sm font-sans">Utkast</p>
                <p className="text-4xl font-serif font-bold text-[#272630] mt-2">
                  {stats?.draft_templates ?? 0}
                </p>
              </div>

              <div className="bg-white rounded-md p-6 border border-[#E5E5E5]">
                <div className="flex items-center gap-2 text-[#272630]/60 text-sm font-sans">
                  <Download className="h-4 w-4 text-[#BCAB8A]" />
                  Nedlastinger (30d)
                </div>
                <p className="text-4xl font-serif font-bold text-[#272630] mt-2">
                  {stats?.total_downloads_30d ?? 0}
                </p>
              </div>
            </>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Recent Templates */}
          <div className="lg:col-span-2 bg-white rounded-md p-6 border border-[#E5E5E5]">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-[#272630]">Nylig opplastet</h3>
              <Link
                href="/templates"
                className="text-sm text-[#BCAB8A] hover:text-[#BCAB8A]/80 font-medium"
              >
                Se alle →
              </Link>
            </div>

            {templatesLoading ? (
              <TemplateListSkeleton />
            ) : recentTemplates.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <FileText className="h-12 w-12 mx-auto mb-3 opacity-50" />
                <p>Ingen maler lastet opp ennå.</p>
                <p className="text-sm">Klikk "Last opp" for å legge til din første mal.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {recentTemplates.map((template) => (
                  <div
                    key={template.id}
                    className="flex items-center gap-3 p-3 border rounded-lg hover:bg-muted transition-colors"
                  >
                    <div
                      className={`p-2 rounded bg-muted ${getFileTypeIcon(
                        template.file_type
                      )}`}
                    >
                      <FileText className="h-5 w-5" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium truncate">{template.title}</p>
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <span className="uppercase">{template.file_type}</span>
                        <span>•</span>
                        <span
                          className={`px-2 py-0.5 rounded-full text-xs ${
                            template.status === "published"
                              ? "bg-green-100 text-green-700"
                              : template.status === "draft"
                              ? "bg-amber-100 text-amber-700"
                              : "bg-muted text-muted-foreground"
                          }`}
                        >
                          {template.status === "published"
                            ? "Publisert"
                            : template.status === "draft"
                            ? "Utkast"
                            : template.status}
                        </span>
                      </div>
                    </div>
                    <div className="text-sm text-muted-foreground flex items-center gap-1">
                      <Clock className="h-4 w-4" />
                      {formatDate(template.created_at)}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Categories */}
          <div className="bg-white rounded-md p-6 border border-[#E5E5E5]">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-[#272630]">Kategorier</h3>
              <Link
                href="/categories"
                className="text-sm text-[#BCAB8A] hover:text-[#BCAB8A]/80 font-medium"
              >
                Administrer →
              </Link>
            </div>

            {categoriesLoading ? (
              <div className="space-y-3">
                {[1, 2, 3, 4].map((i) => (
                  <div key={i} className="p-3 rounded-md bg-[#F5F5F0]">
                    <Skeleton className="h-4 w-24" />
                  </div>
                ))}
              </div>
            ) : categories.length === 0 ? (
              <div className="text-center py-6 text-[#272630]/50">
                <p>Ingen kategorier opprettet.</p>
              </div>
            ) : (
              <div className="space-y-2">
                {categories.map((category) => (
                  <Link
                    key={category.id}
                    href={`/templates?category=${category.id}`}
                    className="flex items-center gap-3 p-3 rounded-md bg-[#F5F5F0] hover:bg-[#E9E7DC] transition-colors"
                  >
                    {category.icon && <span className="text-lg">{category.icon}</span>}
                    <span className="font-medium text-[#272630]">{category.name}</span>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Recent Activity from Dashboard Stats */}
        {!statsLoading && stats?.recent_uploads && stats.recent_uploads.length > 0 && (
          <div className="mt-8 bg-white rounded-md p-6 border border-[#E5E5E5]">
            <h3 className="text-lg font-semibold text-[#272630] mb-4">Nylig aktivitet</h3>
            <div className="space-y-2">
              {stats.recent_uploads.map((upload) => (
                <div
                  key={upload.template_id}
                  className="flex items-center gap-3 text-sm text-[#272630]/60"
                >
                  <div className="w-2 h-2 rounded-full bg-[#BCAB8A]" />
                  <span className="font-medium text-[#272630]">{upload.title}</span>
                  <span className="text-[#272630]/50">ble lastet opp</span>
                  <span className="ml-auto text-[#272630]/50">
                    {formatDate(upload.created_at)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
