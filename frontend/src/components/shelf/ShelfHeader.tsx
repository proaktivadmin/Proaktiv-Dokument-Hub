"use client";

/**
 * ShelfHeader - Title, count, and collapse toggle for a shelf row
 */

import { ChevronDown, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface ShelfHeaderProps {
  title: string;
  count: number;
  isCollapsed: boolean;
  onToggle: () => void;
}

export function ShelfHeader({ title, count, isCollapsed, onToggle }: ShelfHeaderProps) {
  return (
    <div className="flex items-center gap-3 mb-3">
      <Button
        variant="ghost"
        size="sm"
        className="h-8 w-8 p-0"
        onClick={onToggle}
      >
        {isCollapsed ? (
          <ChevronRight className="h-5 w-5 text-gray-400" />
        ) : (
          <ChevronDown className="h-5 w-5 text-gray-400" />
        )}
      </Button>
      
      <h3 className="text-lg font-semibold text-[#272630]">{title}</h3>
      
      <Badge
        variant="secondary"
        className={cn(
          "bg-[#BCAB8A]/20 text-[#272630] hover:bg-[#BCAB8A]/30",
          count === 0 && "bg-gray-100 text-gray-500"
        )}
      >
        {count}
      </Badge>
    </div>
  );
}
