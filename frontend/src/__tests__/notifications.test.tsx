import { describe, expect, it, beforeEach, vi } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";

import type { Notification } from "@/types/notification";
import { NotificationDropdown } from "@/components/notifications/NotificationDropdown";
import { NotificationItem } from "@/components/notifications/NotificationItem";
import { useNotifications } from "@/hooks/use-notifications";

vi.mock("@/hooks/use-notifications", () => ({
  useNotifications: vi.fn(),
}));

type UseNotificationsReturn = {
  notifications: Notification[];
  unreadCount: number;
  total: number;
  isLoading: boolean;
  error: Error | null;
  refresh: () => Promise<void>;
  markAsRead: (id: string) => Promise<void>;
  markAllAsRead: () => Promise<void>;
  deleteNotification: (id: string) => Promise<void>;
  clearAll: () => Promise<void>;
};

const mockUseNotifications = vi.mocked(useNotifications);

const baseNotification: Notification = {
  id: "123",
  type: "employee_added",
  entity_type: "employee",
  entity_id: "456",
  title: "Ny ansatt",
  message: "John Doe ble lagt til",
  severity: "info",
  is_read: false,
  metadata: null,
  created_at: new Date().toISOString(),
};

const buildHookReturn = (
  overrides: Partial<UseNotificationsReturn> = {}
): UseNotificationsReturn => ({
  notifications: [],
  unreadCount: 0,
  total: 0,
  isLoading: false,
  error: null,
  refresh: vi.fn().mockResolvedValue(undefined),
  markAsRead: vi.fn().mockResolvedValue(undefined),
  markAllAsRead: vi.fn().mockResolvedValue(undefined),
  deleteNotification: vi.fn().mockResolvedValue(undefined),
  clearAll: vi.fn().mockResolvedValue(undefined),
  ...overrides,
});

beforeEach(() => {
  mockUseNotifications.mockReset();
});

describe("NotificationItem", () => {
  it("renders notification title and message", () => {
    render(
      <NotificationItem
        notification={baseNotification}
        onMarkAsRead={vi.fn().mockResolvedValue(undefined)}
        onDelete={vi.fn().mockResolvedValue(undefined)}
      />
    );

    expect(screen.getByText("Ny ansatt")).toBeInTheDocument();
    expect(screen.getByText("John Doe ble lagt til")).toBeInTheDocument();
  });

  it("shows unread indicator for unread notifications", () => {
    const { container } = render(
      <NotificationItem
        notification={baseNotification}
        onMarkAsRead={vi.fn().mockResolvedValue(undefined)}
        onDelete={vi.fn().mockResolvedValue(undefined)}
      />
    );

    const unreadDot = container.querySelector(".bg-accent");
    expect(unreadDot).toBeInTheDocument();
  });

  it("calls onDelete when delete button clicked", () => {
    const onDelete = vi.fn().mockResolvedValue(undefined);
    render(
      <NotificationItem
        notification={baseNotification}
        onMarkAsRead={vi.fn().mockResolvedValue(undefined)}
        onDelete={onDelete}
      />
    );

    fireEvent.click(screen.getByLabelText("Fjern varsling"));

    expect(onDelete).toHaveBeenCalledWith("123");
  });
});

describe("NotificationDropdown", () => {
  it("renders unread badge when unread count is greater than zero", () => {
    mockUseNotifications.mockReturnValue(
      buildHookReturn({ unreadCount: 12 })
    );

    render(<NotificationDropdown />);

    expect(screen.getByText("12")).toBeInTheDocument();
  });

  it("shows empty state when no notifications", async () => {
    mockUseNotifications.mockReturnValue(
      buildHookReturn({ notifications: [], isLoading: false })
    );

    render(<NotificationDropdown />);

    const trigger = screen.getByLabelText("Varsler");
    fireEvent.pointerDown(trigger);
    fireEvent.click(trigger);

    expect(await screen.findByText("Ingen varsler")).toBeInTheDocument();
  });

  it("triggers actions from dropdown controls", () => {
    const refresh = vi.fn().mockResolvedValue(undefined);
    const markAllAsRead = vi.fn().mockResolvedValue(undefined);
    const clearAll = vi.fn().mockResolvedValue(undefined);

    mockUseNotifications.mockReturnValue(
      buildHookReturn({
        notifications: [baseNotification],
        unreadCount: 1,
        refresh,
        markAllAsRead,
        clearAll,
      })
    );

    render(<NotificationDropdown />);

    const trigger = screen.getByLabelText("Varsler");
    fireEvent.pointerDown(trigger);
    fireEvent.click(trigger);
    fireEvent.click(screen.getByLabelText("Oppdater"));
    fireEvent.click(screen.getByLabelText("Merk alle som lest"));
    fireEvent.click(screen.getByLabelText("Fjern alle"));

    expect(refresh).toHaveBeenCalledTimes(1);
    expect(markAllAsRead).toHaveBeenCalledTimes(1);
    expect(clearAll).toHaveBeenCalledTimes(1);
  });
});
