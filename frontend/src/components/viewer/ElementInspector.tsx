"use client";

/**
 * ElementInspector - Panel showing HTML code of selected element
 */

import { useState } from "react";
import { X, Copy, Check } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ElementInspectorProps {
  element: HTMLElement | null;
  elementPath: string[];
  isOpen: boolean;
  onClose: () => void;
  onCopy?: () => void;
}

export function ElementInspector({
  element,
  elementPath,
  isOpen,
  onClose,
  onCopy,
}: ElementInspectorProps) {
  const [copied, setCopied] = useState(false);

  if (!isOpen || !element) {
    return null;
  }

  const code = element.outerHTML;

  // Format HTML with basic indentation
  const formattedCode = code
    .replace(/></g, ">\n<")
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean)
    .join("\n");

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
    onCopy?.();
  };

  return (
    <div className="border-t bg-white/95 backdrop-blur-sm">
      {/* Header with path */}
      <div className="flex items-center justify-between gap-4 px-4 py-2 border-b bg-gray-50">
        <div className="flex items-center gap-2 text-sm text-gray-600 overflow-x-auto">
          <span className="text-gray-400">📍</span>
          {elementPath.map((segment, i) => (
            <span key={i} className="flex items-center gap-1">
              {i > 0 && <span className="text-gray-300">›</span>}
              <code className="text-xs">{segment}</code>
            </span>
          ))}
        </div>
        <Button variant="ghost" size="icon" className="h-6 w-6" onClick={onClose}>
          <X className="h-4 w-4" />
        </Button>
      </div>

      {/* Code display */}
      <div className="relative max-h-48 overflow-auto p-4">
        <pre className="text-sm text-gray-800 font-mono whitespace-pre-wrap">
          <code>{formattedCode}</code>
        </pre>

        {/* Copy button */}
        <Button
          variant="secondary"
          size="sm"
          className="absolute top-2 right-2"
          onClick={handleCopy}
        >
          {copied ? (
            <>
              <Check className="h-4 w-4 mr-1 text-green-500" />
              Kopiert
            </>
          ) : (
            <>
              <Copy className="h-4 w-4 mr-1" />
              Kopier
            </>
          )}
        </Button>
      </div>
    </div>
  );
}
