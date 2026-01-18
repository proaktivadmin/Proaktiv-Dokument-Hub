"use client";

/**
 * A4Frame - PDF/A4 preview frame (210mm x 297mm)
 */

import { useRef, useEffect } from "react";
import { cn } from "@/lib/utils";

interface A4FrameProps {
  content: string;
  showMargins?: boolean;
  margins: {
    top: number;
    bottom: number;
    left: number;
    right: number;
  };
  headerHtml?: string;
  footerHtml?: string;
  onElementClick?: (element: HTMLElement, path: string[]) => void;
}

// A4 dimensions in mm
const A4_WIDTH_MM = 210;
const A4_HEIGHT_MM = 297;

// Convert mm to px (at 96 DPI, 1mm ≈ 3.78px)
const MM_TO_PX = 3.78;

function buildPath(element: HTMLElement): string[] {
  const path: string[] = [];
  let current: HTMLElement | null = element;

  while (current && current.tagName !== "BODY") {
    let selector = current.tagName.toLowerCase();
    if (current.id) {
      selector += `#${current.id}`;
    } else if (current.className) {
      const classes = current.className.split(" ").filter(Boolean).slice(0, 2);
      if (classes.length > 0) {
        selector += `.${classes.join(".")}`;
      }
    }
    path.unshift(selector);
    current = current.parentElement;
  }

  return path;
}

export function A4Frame({
  content,
  showMargins = false,
  margins,
  headerHtml,
  footerHtml,
  onElementClick,
}: A4FrameProps) {
  const iframeRef = useRef<HTMLIFrameElement>(null);

  // A4 page dimensions in pixels
  const pageWidth = A4_WIDTH_MM * MM_TO_PX;
  const pageHeight = A4_HEIGHT_MM * MM_TO_PX;

  // Margin values in pixels
  const marginTopPx = margins.top * 10 * MM_TO_PX;
  const marginBottomPx = margins.bottom * 10 * MM_TO_PX;
  const marginLeftPx = margins.left * 10 * MM_TO_PX;
  const marginRightPx = margins.right * 10 * MM_TO_PX;

  useEffect(() => {
    const iframe = iframeRef.current;
    if (!iframe) return;

    const doc = iframe.contentDocument;
    if (!doc) return;

    // Build full HTML with header/footer
    const fullHtml = `
      <!DOCTYPE html>
      <html>
      <head>
        <style>
          * { box-sizing: border-box; margin: 0; padding: 0; }
          body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 12px;
            line-height: 1.4;
            padding: ${marginTopPx}px ${marginRightPx}px ${marginBottomPx}px ${marginLeftPx}px;
          }
          .header { position: absolute; top: 0; left: 0; right: 0; padding: 10px ${marginRightPx}px; }
          .footer { position: absolute; bottom: 0; left: 0; right: 0; padding: 10px ${marginRightPx}px; }
          .content { min-height: calc(100vh - ${marginTopPx + marginBottomPx}px); }
          
          /* Highlight clicked element */
          .inspector-highlight {
            outline: 2px solid #BCAB8A !important;
            outline-offset: 2px;
          }
        </style>
      </head>
      <body>
        ${headerHtml ? `<div class="header">${headerHtml}</div>` : ""}
        <div class="content">${content}</div>
        ${footerHtml ? `<div class="footer">${footerHtml}</div>` : ""}
      </body>
      </html>
    `;

    doc.open();
    doc.write(fullHtml);
    doc.close();

    // Add click handler for element inspection
    if (onElementClick) {
      doc.body.addEventListener("click", (e) => {
        const target = e.target as HTMLElement;
        if (target && target !== doc.body) {
          e.preventDefault();
          e.stopPropagation();

          // Remove previous highlights
          doc.querySelectorAll(".inspector-highlight").forEach((el) => {
            el.classList.remove("inspector-highlight");
          });

          // Highlight clicked element
          target.classList.add("inspector-highlight");

          // Call handler with element and path
          onElementClick(target, buildPath(target));
        }
      });
    }
  }, [content, headerHtml, footerHtml, margins, onElementClick]);

  return (
    <div className="flex justify-center bg-slate-100 p-6 md:p-8 overflow-auto">
      {/* A4 page container */}
      <div
        className={cn(
          "bg-white shadow-lg ring-1 ring-black/5",
          showMargins && "relative"
        )}
        style={{
          width: pageWidth,
          minHeight: pageHeight,
        }}
      >
        {/* Margin indicators */}
        {showMargins && (
          <>
            <div
              className="absolute top-0 left-0 right-0 bg-blue-100/30 border-b border-dashed border-blue-300"
              style={{ height: marginTopPx }}
            />
            <div
              className="absolute bottom-0 left-0 right-0 bg-blue-100/30 border-t border-dashed border-blue-300"
              style={{ height: marginBottomPx }}
            />
            <div
              className="absolute top-0 bottom-0 left-0 bg-blue-100/30 border-r border-dashed border-blue-300"
              style={{ width: marginLeftPx }}
            />
            <div
              className="absolute top-0 bottom-0 right-0 bg-blue-100/30 border-l border-dashed border-blue-300"
              style={{ width: marginRightPx }}
            />
          </>
        )}

        <iframe
          ref={iframeRef}
          className="w-full h-full border-0"
          style={{ minHeight: pageHeight }}
          title="A4 Preview"
        />
      </div>
    </div>
  );
}
