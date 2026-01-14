"use client";

/**
 * CodeSnippetCard - Individual code snippet card with copy functionality
 * Used for Vitec Logic patterns, Layout snippets, etc.
 */

import { useState } from "react";
import { Copy, Check, Code, Layout, GitBranch } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export interface CodeSnippet {
  label: string;
  desc: string;
  code: string;
  category?: string;
}

interface CodeSnippetCardProps {
  snippet: CodeSnippet;
  onCopy?: (code: string) => void;
  variant?: "logic" | "layout" | "default";
}

const VARIANT_ICONS = {
  logic: <GitBranch className="h-4 w-4" />,
  layout: <Layout className="h-4 w-4" />,
  default: <Code className="h-4 w-4" />,
};

const VARIANT_COLORS = {
  logic: "border-l-purple-500",
  layout: "border-l-blue-500",
  default: "border-l-gray-500",
};

export function CodeSnippetCard({
  snippet,
  onCopy,
  variant = "default",
}: CodeSnippetCardProps) {
  const [copied, setCopied] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);

  const handleCopy = async (e?: React.MouseEvent) => {
    e?.stopPropagation();
    
    try {
      await navigator.clipboard.writeText(snippet.code);
      setCopied(true);
      onCopy?.(snippet.code);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy:", err);
    }
  };

  // Truncate long code for preview
  const previewCode = snippet.code.length > 100 
    ? snippet.code.slice(0, 100) + "..." 
    : snippet.code;

  return (
    <div
      className={cn(
        "flex flex-col rounded-lg border border-l-4 bg-white p-3 transition-all duration-200",
        "hover:shadow-md",
        VARIANT_COLORS[variant]
      )}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="text-gray-400">{VARIANT_ICONS[variant]}</span>
          <h4 className="font-medium text-gray-900">{snippet.label}</h4>
        </div>
        <Button
          variant="ghost"
          size="icon"
          className={cn(
            "h-8 w-8 shrink-0",
            copied ? "text-green-500" : "text-gray-400 hover:text-gray-900"
          )}
          onClick={handleCopy}
          title="Kopier til utklippstavle"
        >
          {copied ? (
            <Check className="h-4 w-4" />
          ) : (
            <Copy className="h-4 w-4" />
          )}
        </Button>
      </div>

      {/* Description */}
      {snippet.desc && (
        <p className="mt-1 text-xs text-gray-500">{snippet.desc}</p>
      )}

      {/* Code preview */}
      <div className="mt-2">
        <button
          className="w-full text-left rounded bg-gray-900 hover:bg-gray-800 px-3 py-2 text-xs font-mono text-gray-100 transition-colors overflow-hidden"
          onClick={() => setIsExpanded(!isExpanded)}
          title={isExpanded ? "Klikk for å skjule" : "Klikk for å vise mer"}
        >
          <pre className="whitespace-pre-wrap">
            {isExpanded ? snippet.code : previewCode}
          </pre>
        </button>
      </div>

      {/* Quick copy button */}
      <div className="mt-2 flex justify-end">
        <Button
          variant="outline"
          size="sm"
          className="text-xs"
          onClick={handleCopy}
        >
          {copied ? "Kopiert!" : "Kopier kode"}
        </Button>
      </div>
    </div>
  );
}
