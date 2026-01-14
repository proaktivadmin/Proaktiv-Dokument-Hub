"use client";

/**
 * HorizontalScroll - Scrollable container with arrow navigation
 */

import { useRef, useState, useEffect, useCallback, type ReactNode } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface HorizontalScrollProps {
  children: ReactNode;
  gap?: number;
  showArrows?: boolean;
  className?: string;
}

export function HorizontalScroll({
  children,
  gap = 16,
  showArrows = true,
  className,
}: HorizontalScrollProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(false);

  const checkScrollability = useCallback(() => {
    const container = containerRef.current;
    if (!container) return;

    setCanScrollLeft(container.scrollLeft > 0);
    setCanScrollRight(
      container.scrollLeft < container.scrollWidth - container.clientWidth - 1
    );
  }, []);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    checkScrollability();

    // Check again when window resizes
    window.addEventListener("resize", checkScrollability);
    container.addEventListener("scroll", checkScrollability);

    return () => {
      window.removeEventListener("resize", checkScrollability);
      container.removeEventListener("scroll", checkScrollability);
    };
  }, [checkScrollability, children]);

  const scroll = useCallback((direction: "left" | "right") => {
    const container = containerRef.current;
    if (!container) return;

    const scrollAmount = container.clientWidth * 0.8;
    container.scrollBy({
      left: direction === "left" ? -scrollAmount : scrollAmount,
      behavior: "smooth",
    });
  }, []);

  return (
    <div className={cn("relative group", className)}>
      {/* Left arrow */}
      {showArrows && canScrollLeft && (
        <Button
          variant="secondary"
          size="icon"
          className="absolute left-0 top-1/2 z-10 -translate-y-1/2 -translate-x-2 h-8 w-8 rounded-full shadow-lg opacity-0 group-hover:opacity-100 transition-opacity bg-white/90"
          onClick={() => scroll("left")}
        >
          <ChevronLeft className="h-4 w-4" />
        </Button>
      )}

      {/* Scrollable container */}
      <div
        ref={containerRef}
        className="flex overflow-x-auto scrollbar-hide scroll-smooth"
        style={{ gap }}
      >
        {children}
      </div>

      {/* Right arrow */}
      {showArrows && canScrollRight && (
        <Button
          variant="secondary"
          size="icon"
          className="absolute right-0 top-1/2 z-10 -translate-y-1/2 translate-x-2 h-8 w-8 rounded-full shadow-lg opacity-0 group-hover:opacity-100 transition-opacity bg-white/90"
          onClick={() => scroll("right")}
        >
          <ChevronRight className="h-4 w-4" />
        </Button>
      )}
    </div>
  );
}
