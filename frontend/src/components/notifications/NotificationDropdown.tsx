"use client";

import { Bell, Check, RefreshCw, Trash2 } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useNotifications } from "@/hooks/use-notifications";
import { cn } from "@/lib/utils";
import { NotificationItem } from "./NotificationItem";

interface NotificationDropdownProps {
  className?: string;
}

export function NotificationDropdown({ className }: NotificationDropdownProps) {
  const {
    notifications,
    unreadCount,
    isLoading,
    refresh,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    clearAll,
  } = useNotifications({ limit: 20, pollInterval: 30000 });

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button
          type="button"
          className={cn(
            "relative rounded-md p-2 text-foreground/70 transition-colors duration-fast ease-standard",
            "hover:bg-card/60 hover:text-foreground",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-strong",
            className
          )}
          title="Varsler"
          aria-label="Varsler"
        >
          <Bell className="h-5 w-5" />
          {unreadCount > 0 && (
            <span
              className={cn(
                "absolute -right-0.5 -top-0.5 flex h-[18px] min-w-[18px] items-center justify-center",
                "rounded-full bg-destructive px-1 text-[10px] font-medium text-destructive-foreground",
                "animate-in fade-in zoom-in duration-fast"
              )}
            >
              {unreadCount > 99 ? "99+" : unreadCount}
            </span>
          )}
        </button>
      </DropdownMenuTrigger>

      <DropdownMenuContent
        align="end"
        className="w-80 max-h-[480px] overflow-hidden bg-card p-0"
      >
        <div className="flex items-center justify-between border-b border-border px-4 py-3">
          <h3 className="font-serif text-sm font-semibold text-primary">
            Varsler
          </h3>
          <div className="flex items-center gap-1">
            <button
              type="button"
              onClick={() => void refresh()}
              className="rounded-md p-1.5 text-muted-foreground transition-colors duration-fast ease-standard hover:bg-secondary/70 hover:text-foreground"
              title="Oppdater"
              aria-label="Oppdater"
            >
              <RefreshCw
                className={cn("h-4 w-4", isLoading && "animate-spin")}
              />
            </button>
            {unreadCount > 0 && (
              <button
                type="button"
                onClick={() => void markAllAsRead()}
                className="rounded-md p-1.5 text-muted-foreground transition-colors duration-fast ease-standard hover:bg-secondary/70 hover:text-foreground"
                title="Merk alle som lest"
                aria-label="Merk alle som lest"
              >
                <Check className="h-4 w-4" />
              </button>
            )}
            {notifications.length > 0 && (
              <button
                type="button"
                onClick={() => void clearAll()}
                className="rounded-md p-1.5 text-muted-foreground transition-colors duration-fast ease-standard hover:bg-destructive/10 hover:text-destructive"
                title="Fjern alle"
                aria-label="Fjern alle"
              >
                <Trash2 className="h-4 w-4" />
              </button>
            )}
          </div>
        </div>

        <div className="max-h-[400px] overflow-y-auto">
          {isLoading && notifications.length === 0 ? (
            <div className="flex items-center justify-center py-8 text-muted-foreground">
              <RefreshCw className="h-5 w-5 animate-spin" />
            </div>
          ) : notifications.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-8 text-muted-foreground">
              <Bell className="mb-2 h-8 w-8" />
              <p className="text-sm">Ingen varsler</p>
            </div>
          ) : (
            <div className="divide-y divide-border/60">
              {notifications.map((notification) => (
                <NotificationItem
                  key={notification.id}
                  notification={notification}
                  onMarkAsRead={markAsRead}
                  onDelete={deleteNotification}
                />
              ))}
            </div>
          )}
        </div>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
