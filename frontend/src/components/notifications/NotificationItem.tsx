"use client";

import type { KeyboardEvent, MouseEvent } from "react";
import { useRouter } from "next/navigation";
import { formatDistanceToNow } from "date-fns";
import { nb } from "date-fns/locale";
import {
  AlertTriangle,
  Building,
  Building2,
  Info,
  UserCog,
  UserMinus,
  UserPlus,
  X,
  XCircle,
  type LucideIcon,
} from "lucide-react";
import { cn } from "@/lib/utils";
import type { Notification } from "@/types/notification";

interface NotificationItemProps {
  notification: Notification;
  onMarkAsRead: (id: string) => Promise<void>;
  onDelete: (id: string) => Promise<void>;
}

const typeIcons: Record<Notification["type"], LucideIcon> = {
  employee_added: UserPlus,
  employee_removed: UserMinus,
  employee_updated: UserCog,
  office_added: Building2,
  office_removed: Building,
  office_updated: Building2,
  upn_mismatch: AlertTriangle,
  sync_error: XCircle,
};

const severityStyles: Record<Notification["severity"], string> = {
  info: "text-emerald-600 bg-emerald-50",
  warning: "text-amber-600 bg-amber-50",
  error: "text-red-600 bg-red-50",
};

export function NotificationItem({
  notification,
  onMarkAsRead,
  onDelete,
}: NotificationItemProps) {
  const router = useRouter();
  const Icon = typeIcons[notification.type] ?? Info;

  const handleClick = () => {
    if (!notification.is_read) {
      void onMarkAsRead(notification.id);
    }

    if (notification.entity_id) {
      if (notification.entity_type === "employee") {
        router.push(`/employees/${notification.entity_id}`);
      } else if (notification.entity_type === "office") {
        router.push(`/offices/${notification.entity_id}`);
      }
    }
  };

  const handleDelete = (event: MouseEvent<HTMLButtonElement>) => {
    event.stopPropagation();
    void onDelete(notification.id);
  };

  const handleKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      handleClick();
    }
  };

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      className={cn(
        "flex items-start gap-3 px-4 py-3 cursor-pointer transition-colors duration-fast ease-standard",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-strong",
        "hover:bg-[#f5f5f0]",
        !notification.is_read && "bg-[#f8f8f5]"
      )}
    >
      <div
        className={cn(
          "shrink-0 rounded-full p-1.5 ring-1 ring-black/3",
          severityStyles[notification.severity]
        )}
      >
        <Icon className="h-4 w-4" />
      </div>

      <div className="min-w-0 flex-1">
        <div className="flex items-start justify-between gap-2">
          <p
            className={cn(
              "text-sm text-primary",
              !notification.is_read && "font-medium"
            )}
          >
            {notification.title}
          </p>

          {!notification.is_read && (
            <div className="mt-1 h-2 w-2 shrink-0 rounded-full bg-accent" />
          )}
        </div>

        <p className="mt-0.5 line-clamp-2 text-xs text-muted-foreground">
          {notification.message}
        </p>

        <p className="mt-1 text-xs text-muted-foreground/80">
          {formatDistanceToNow(new Date(notification.created_at), {
            addSuffix: true,
            locale: nb,
          })}
        </p>
      </div>

      <button
        type="button"
        onClick={handleDelete}
        className="shrink-0 rounded-md p-1 text-muted-foreground transition-colors duration-fast ease-standard hover:bg-[#f0f0eb] hover:text-primary"
        title="Fjern varsling"
        aria-label="Fjern varsling"
      >
        <X className="h-3.5 w-3.5" />
      </button>
    </div>
  );
}
