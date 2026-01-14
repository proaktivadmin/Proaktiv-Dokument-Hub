"use client";

/**
 * PreviewModeSelector - Tabs for selecting preview mode
 */

import { FileText, Monitor, Smartphone, MessageSquare } from "lucide-react";
import { cn } from "@/lib/utils";

export type PreviewMode = "a4" | "desktop_email" | "mobile_email" | "sms";

interface PreviewModeSelectorProps {
  value: PreviewMode;
  onChange: (mode: PreviewMode) => void;
  hiddenModes?: PreviewMode[];
}

const MODE_CONFIG: {
  id: PreviewMode;
  label: string;
  icon: React.ReactNode;
}[] = [
  { id: "a4", label: "A4/PDF", icon: <FileText className="h-4 w-4" /> },
  { id: "desktop_email", label: "Desktop E-post", icon: <Monitor className="h-4 w-4" /> },
  { id: "mobile_email", label: "Mobil E-post", icon: <Smartphone className="h-4 w-4" /> },
  { id: "sms", label: "SMS", icon: <MessageSquare className="h-4 w-4" /> },
];

export function PreviewModeSelector({
  value,
  onChange,
  hiddenModes = [],
}: PreviewModeSelectorProps) {
  const visibleModes = MODE_CONFIG.filter((m) => !hiddenModes.includes(m.id));

  return (
    <div className="flex items-center gap-1 p-1 bg-gray-100 rounded-lg">
      {visibleModes.map((mode) => (
        <button
          key={mode.id}
          className={cn(
            "flex items-center gap-2 px-3 py-2 text-sm rounded-md transition-colors",
            value === mode.id
              ? "bg-white text-[#272630] shadow-sm font-medium"
              : "text-gray-600 hover:text-[#272630] hover:bg-white/50"
          )}
          onClick={() => onChange(mode.id)}
        >
          {mode.icon}
          <span>{mode.label}</span>
        </button>
      ))}
    </div>
  );
}
