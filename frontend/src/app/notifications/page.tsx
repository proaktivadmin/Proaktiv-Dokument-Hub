"use client";

import { useState, useCallback, useEffect } from "react";
import { useRouter } from "next/navigation";
import { formatDistanceToNow, format } from "date-fns";
import { nb } from "date-fns/locale";
import {
  AlertTriangle,
  Bell,
  Building,
  Building2,
  Check,
  ChevronDown,
  ChevronRight,
  Filter,
  Info,
  RefreshCw,
  Trash2,
  UserCog,
  UserMinus,
  UserPlus,
  XCircle,
  type LucideIcon,
} from "lucide-react";
import { Header } from "@/components/layout/Header";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { cn } from "@/lib/utils";
import { notificationsApi } from "@/lib/api/notifications";
import type { Notification, NotificationType, NotificationSeverity } from "@/types/notification";

const typeIcons: Record<NotificationType, LucideIcon> = {
  employee_added: UserPlus,
  employee_removed: UserMinus,
  employee_updated: UserCog,
  office_added: Building2,
  office_removed: Building,
  office_updated: Building2,
  upn_mismatch: AlertTriangle,
  sync_error: XCircle,
};

const typeLabels: Record<NotificationType, string> = {
  employee_added: "Ansatt lagt til",
  employee_removed: "Ansatt fjernet",
  employee_updated: "Ansatt oppdatert",
  office_added: "Kontor lagt til",
  office_removed: "Kontor fjernet",
  office_updated: "Kontor oppdatert",
  upn_mismatch: "UPN-avvik",
  sync_error: "Synkfeil",
};

const severityStyles: Record<NotificationSeverity, { bg: string; text: string; badge: string }> = {
  info: { bg: "bg-emerald-50", text: "text-emerald-700", badge: "bg-emerald-100 text-emerald-700 border-emerald-200" },
  warning: { bg: "bg-amber-50", text: "text-amber-700", badge: "bg-amber-100 text-amber-700 border-amber-200" },
  error: { bg: "bg-red-50", text: "text-red-700", badge: "bg-red-100 text-red-700 border-red-200" },
};

const PAGE_SIZE = 50;

export default function NotificationsPage() {
  const router = useRouter();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [total, setTotal] = useState(0);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [page, setPage] = useState(0);

  const [filterType, setFilterType] = useState<string>("all");
  const [filterSeverity, setFilterSeverity] = useState<string>("all");
  const [filterRead, setFilterRead] = useState<string>("all");

  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set());

  const fetchNotifications = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await notificationsApi.list({
        skip: page * PAGE_SIZE,
        limit: PAGE_SIZE,
        unread_only: filterRead === "unread",
      });
      setNotifications(data.items);
      setTotal(data.total);
      setUnreadCount(data.unread_count);
    } catch {
      // Silently handle — notifications are non-critical
    } finally {
      setIsLoading(false);
    }
  }, [page, filterRead]);

  useEffect(() => {
    fetchNotifications();
  }, [fetchNotifications]);

  const handleMarkAsRead = async (id: string) => {
    await notificationsApi.markAsRead(id);
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
    );
    setUnreadCount((prev) => Math.max(0, prev - 1));
  };

  const handleMarkAllAsRead = async () => {
    await notificationsApi.markAllAsRead();
    setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
    setUnreadCount(0);
  };

  const handleDelete = async (id: string) => {
    const existing = notifications.find((n) => n.id === id);
    await notificationsApi.delete(id);
    setNotifications((prev) => prev.filter((n) => n.id !== id));
    setTotal((prev) => prev - 1);
    if (existing && !existing.is_read) {
      setUnreadCount((prev) => Math.max(0, prev - 1));
    }
  };

  const handleClearAll = async () => {
    if (!confirm("Er du sikker på at du vil slette alle varsler?")) return;
    await notificationsApi.clearAll();
    setNotifications([]);
    setTotal(0);
    setUnreadCount(0);
  };

  const toggleExpanded = (id: string) => {
    setExpandedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const navigateToEntity = (notification: Notification) => {
    if (!notification.is_read) {
      void handleMarkAsRead(notification.id);
    }
    if (notification.entity_id) {
      if (notification.entity_type === "employee") {
        router.push(`/employees/${notification.entity_id}`);
      } else if (notification.entity_type === "office") {
        router.push(`/offices/${notification.entity_id}`);
      }
    }
  };

  const filtered = notifications.filter((n) => {
    if (filterType !== "all" && n.type !== filterType) return false;
    if (filterSeverity !== "all" && n.severity !== filterSeverity) return false;
    if (filterRead === "read" && !n.is_read) return false;
    return true;
  });

  const grouped = groupByDate(filtered);
  const totalPages = Math.ceil(total / PAGE_SIZE);

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="mx-auto max-w-4xl px-6 py-8">
        {/* Page header */}
        <div className="mb-6">
          <h1 className="font-serif text-2xl font-semibold text-[#272630]">
            Varsler
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Synkroniseringshistorikk og endringslogg
          </p>
        </div>

        {/* Stats bar */}
        <div className="mb-6 flex items-center gap-4">
          <div className="flex items-center gap-2 rounded-lg border bg-white px-4 py-2 shadow-card">
            <Bell className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm font-medium">{total}</span>
            <span className="text-sm text-muted-foreground">totalt</span>
          </div>
          {unreadCount > 0 && (
            <div className="flex items-center gap-2 rounded-lg border border-amber-200 bg-amber-50 px-4 py-2">
              <span className="h-2 w-2 rounded-full bg-amber-500" />
              <span className="text-sm font-medium text-amber-800">{unreadCount}</span>
              <span className="text-sm text-amber-700">ulest</span>
            </div>
          )}
        </div>

        {/* Toolbar */}
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3 rounded-lg border bg-white p-3 shadow-card">
          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4 text-muted-foreground" />
            <Select value={filterType} onValueChange={setFilterType}>
              <SelectTrigger className="h-8 w-[160px] text-xs">
                <SelectValue placeholder="Alle typer" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Alle typer</SelectItem>
                <SelectItem value="office_updated">Kontor oppdatert</SelectItem>
                <SelectItem value="office_added">Kontor lagt til</SelectItem>
                <SelectItem value="office_removed">Kontor fjernet</SelectItem>
                <SelectItem value="employee_updated">Ansatt oppdatert</SelectItem>
                <SelectItem value="employee_added">Ansatt lagt til</SelectItem>
                <SelectItem value="employee_removed">Ansatt fjernet</SelectItem>
                <SelectItem value="upn_mismatch">UPN-avvik</SelectItem>
                <SelectItem value="sync_error">Synkfeil</SelectItem>
              </SelectContent>
            </Select>
            <Select value={filterSeverity} onValueChange={setFilterSeverity}>
              <SelectTrigger className="h-8 w-[130px] text-xs">
                <SelectValue placeholder="Alle nivåer" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Alle nivåer</SelectItem>
                <SelectItem value="info">Info</SelectItem>
                <SelectItem value="warning">Advarsel</SelectItem>
                <SelectItem value="error">Feil</SelectItem>
              </SelectContent>
            </Select>
            <Select value={filterRead} onValueChange={(v) => { setFilterRead(v); setPage(0); }}>
              <SelectTrigger className="h-8 w-[130px] text-xs">
                <SelectValue placeholder="Alle" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Alle</SelectItem>
                <SelectItem value="unread">Uleste</SelectItem>
                <SelectItem value="read">Leste</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => void fetchNotifications()}
              disabled={isLoading}
            >
              <RefreshCw className={cn("h-4 w-4 mr-1", isLoading && "animate-spin")} />
              Oppdater
            </Button>
            {unreadCount > 0 && (
              <Button variant="outline" size="sm" onClick={() => void handleMarkAllAsRead()}>
                <Check className="h-4 w-4 mr-1" />
                Merk alle som lest
              </Button>
            )}
            {notifications.length > 0 && (
              <Button
                variant="outline"
                size="sm"
                className="text-destructive hover:text-destructive"
                onClick={() => void handleClearAll()}
              >
                <Trash2 className="h-4 w-4 mr-1" />
                Slett alle
              </Button>
            )}
          </div>
        </div>

        {/* Notification list */}
        {isLoading && notifications.length === 0 ? (
          <div className="flex items-center justify-center py-16 text-muted-foreground">
            <RefreshCw className="h-6 w-6 animate-spin" />
          </div>
        ) : filtered.length === 0 ? (
          <div className="flex flex-col items-center justify-center rounded-lg border bg-white py-16 shadow-card">
            <Bell className="mb-3 h-12 w-12 text-muted-foreground/40" />
            <p className="font-serif text-lg font-medium text-muted-foreground">
              Ingen varsler
            </p>
            <p className="mt-1 text-sm text-muted-foreground/70">
              {filterType !== "all" || filterSeverity !== "all" || filterRead !== "all"
                ? "Prøv å endre filtrene."
                : "Varsler vises her etter synkronisering."}
            </p>
          </div>
        ) : (
          <div className="space-y-6">
            {grouped.map(({ label, items }) => (
              <div key={label}>
                <h2 className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                  {label}
                </h2>
                <div className="overflow-hidden rounded-lg border bg-white shadow-card">
                  {items.map((notification, idx) => {
                    const Icon = typeIcons[notification.type] ?? Info;
                    const styles = severityStyles[notification.severity];
                    const isExpanded = expandedIds.has(notification.id);
                    const metadata = notification.metadata as Record<string, unknown> | null;
                    const changedFields = (metadata?.changed_fields as string[]) ?? [];

                    return (
                      <div
                        key={notification.id}
                        className={cn(
                          "transition-colors duration-fast ease-standard",
                          idx > 0 && "border-t",
                          !notification.is_read && "bg-[#faf9f6]"
                        )}
                      >
                        {/* Main row */}
                        <div className="flex items-start gap-3 px-4 py-3">
                          {/* Expand toggle */}
                          <button
                            type="button"
                            onClick={() => toggleExpanded(notification.id)}
                            className="mt-1 shrink-0 rounded p-0.5 text-muted-foreground hover:bg-muted"
                          >
                            {isExpanded ? (
                              <ChevronDown className="h-4 w-4" />
                            ) : (
                              <ChevronRight className="h-4 w-4" />
                            )}
                          </button>

                          {/* Icon */}
                          <div
                            className={cn(
                              "mt-0.5 shrink-0 rounded-full p-1.5 ring-1 ring-black/3",
                              styles.bg, styles.text
                            )}
                          >
                            <Icon className="h-4 w-4" />
                          </div>

                          {/* Content */}
                          <div className="min-w-0 flex-1">
                            <div className="flex items-start justify-between gap-2">
                              <div className="flex items-center gap-2">
                                <p className={cn(
                                  "text-sm text-primary",
                                  !notification.is_read && "font-semibold"
                                )}>
                                  {notification.title}
                                </p>
                                {!notification.is_read && (
                                  <span className="h-2 w-2 shrink-0 rounded-full bg-[#BCAB8A]" />
                                )}
                              </div>
                              <span className="shrink-0 text-xs text-muted-foreground">
                                {format(new Date(notification.created_at), "HH:mm", { locale: nb })}
                              </span>
                            </div>
                            <p className="mt-0.5 text-sm text-muted-foreground">
                              {notification.message}
                            </p>
                            <div className="mt-1.5 flex flex-wrap items-center gap-1.5">
                              <Badge variant="outline" className={cn("text-xs", styles.badge)}>
                                {typeLabels[notification.type]}
                              </Badge>
                              {changedFields.length > 0 && (
                                <span className="text-xs text-muted-foreground">
                                  {changedFields.length} felt endret
                                </span>
                              )}
                            </div>
                          </div>

                          {/* Actions */}
                          <div className="flex shrink-0 items-center gap-1">
                            {!notification.is_read && (
                              <Button
                                variant="ghost"
                                size="icon"
                                className="h-7 w-7"
                                onClick={() => void handleMarkAsRead(notification.id)}
                                title="Merk som lest"
                              >
                                <Check className="h-3.5 w-3.5" />
                              </Button>
                            )}
                            {notification.entity_id && (
                              <Button
                                variant="ghost"
                                size="icon"
                                className="h-7 w-7"
                                onClick={() => navigateToEntity(notification)}
                                title="Gå til"
                              >
                                <ChevronRight className="h-3.5 w-3.5" />
                              </Button>
                            )}
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-7 w-7 text-muted-foreground hover:text-destructive"
                              onClick={() => void handleDelete(notification.id)}
                              title="Slett"
                            >
                              <Trash2 className="h-3.5 w-3.5" />
                            </Button>
                          </div>
                        </div>

                        {/* Expanded detail */}
                        {isExpanded && metadata && (
                          <div className="border-t bg-muted/30 px-4 py-3 pl-[72px]">
                            <div className="space-y-2 text-sm">
                              {changedFields.length > 0 && (
                                <div>
                                  <p className="mb-1 text-xs font-medium uppercase tracking-wide text-muted-foreground">
                                    Endrede felt
                                  </p>
                                  <div className="flex flex-wrap gap-1">
                                    {changedFields.map((field) => (
                                      <Badge key={field} variant="secondary" className="text-xs">
                                        {fieldLabel(field)}
                                      </Badge>
                                    ))}
                                  </div>
                                </div>
                              )}
                              <MetadataGrid metadata={metadata} />
                              <p className="text-xs text-muted-foreground">
                                {format(new Date(notification.created_at), "d. MMMM yyyy 'kl.' HH:mm:ss", { locale: nb })}
                              </p>
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="mt-6 flex items-center justify-center gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={page === 0}
              onClick={() => setPage((p) => p - 1)}
            >
              Forrige
            </Button>
            <span className="text-sm text-muted-foreground">
              Side {page + 1} av {totalPages}
            </span>
            <Button
              variant="outline"
              size="sm"
              disabled={page >= totalPages - 1}
              onClick={() => setPage((p) => p + 1)}
            >
              Neste
            </Button>
          </div>
        )}
      </main>
    </div>
  );
}

function MetadataGrid({ metadata }: { metadata: Record<string, unknown> }) {
  const fields: { key: string; label: string; className?: string }[] = [
    { key: "office_name", label: "Kontor" },
    { key: "employee_name", label: "Ansatt" },
    { key: "email", label: "E-post" },
    { key: "vitec_department_id", label: "Avdeling ID" },
    { key: "short_code", label: "Kortkode" },
    { key: "expected_upn", label: "Forventet UPN" },
    { key: "actual_upn", label: "Faktisk UPN" },
    { key: "operation", label: "Operasjon" },
    { key: "error", label: "Feil", className: "col-span-2 text-red-600" },
  ];

  return (
    <div className="grid grid-cols-2 gap-x-6 gap-y-1 text-xs">
      {fields.map(({ key, label, className }) => {
        const value = metadata[key];
        if (!value) return null;
        return (
          <div key={key} className={className}>
            <span className="text-muted-foreground">{label}: </span>
            <span className={key === "office_name" || key === "employee_name" ? "font-medium" : undefined}>
              {String(value)}
            </span>
          </div>
        );
      })}
    </div>
  );
}

function fieldLabel(field: string): string {
  const labels: Record<string, string> = {
    name: "Navn",
    legal_name: "Juridisk navn",
    email: "E-post",
    phone: "Telefon",
    street_address: "Adresse",
    postal_code: "Postnummer",
    city: "By",
    description: "Beskrivelse",
    is_active: "Aktiv",
    vitec_department_id: "Avdeling-ID",
    title: "Tittel",
    first_name: "Fornavn",
    last_name: "Etternavn",
    profile_image_url: "Profilbilde",
    banner_image_url: "Bannerbilde",
    department_number: "Avdelingsnr",
  };
  return labels[field] ?? field;
}

interface DateGroup {
  label: string;
  items: Notification[];
}

function groupByDate(notifications: Notification[]): DateGroup[] {
  const groups = new Map<string, Notification[]>();

  for (const n of notifications) {
    const date = new Date(n.created_at);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    let label: string;
    if (diffDays === 0) {
      label = "I dag";
    } else if (diffDays === 1) {
      label = "I går";
    } else if (diffDays < 7) {
      label = formatDistanceToNow(date, { addSuffix: true, locale: nb });
    } else {
      label = format(date, "d. MMMM yyyy", { locale: nb });
    }

    const existing = groups.get(label);
    if (existing) {
      existing.push(n);
    } else {
      groups.set(label, [n]);
    }
  }

  return Array.from(groups.entries()).map(([label, items]) => ({ label, items }));
}
