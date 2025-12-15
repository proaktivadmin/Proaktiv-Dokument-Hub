"use client";

import { useEffect, useRef, useState } from "react";
import { Maximize2, Minimize2, Code, Eye, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";

/**
 * TemplatePreview Component
 * 
 * Renders HTML templates in an isolated iframe with the full Vitec/Proaktiv
 * styling loaded from an external CSS file.
 * 
 * The CSS file (/vitec-theme.css) is loaded via a link tag inside the iframe,
 * ensuring complete style isolation from the main application.
 */

interface TemplatePreviewProps {
  content: string;
  title?: string;
  isLoading?: boolean;
  error?: string;
}

export function TemplatePreview({
  content,
  title,
  isLoading = false,
  error,
}: TemplatePreviewProps) {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showSource, setShowSource] = useState(false);

  /**
   * Highlight merge fields in the content
   * Converts [[field.name]] to highlighted spans
   */
  const highlightMergeFields = (html: string): string => {
    return html.replace(
      /\[\[([^\]]+)\]\]/g,
      '<span class="merge-field-highlight">[[$1]]</span>'
    );
  };

  /**
   * Build the complete HTML document for the iframe
   * Uses an external stylesheet for full Vitec/Proaktiv styling
   */
  const buildPreviewDocument = (): string => {
    const processedContent = highlightMergeFields(content);
    
    return `<!DOCTYPE html>
<html lang="no">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${title || "Template Preview"}</title>
  <link rel="stylesheet" href="/vitec-theme.css" />
</head>
<body class="vitec-preview-mode">
  ${processedContent}
</body>
</html>`;
  };

  // Update iframe content when content changes
  useEffect(() => {
    if (iframeRef.current && content && !showSource) {
      const doc = iframeRef.current.contentDocument;
      if (doc) {
        doc.open();
        doc.write(buildPreviewDocument());
        doc.close();
      }
    }
  }, [content, showSource]);

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96 bg-slate-50 rounded-lg border">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin text-sky-600 mx-auto mb-3" />
          <p className="text-slate-500">Laster forhåndsvisning...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-96 bg-red-50 rounded-lg border border-red-200">
        <div className="text-center">
          <p className="text-red-600 font-medium">Kunne ikke laste forhåndsvisning</p>
          <p className="text-red-500 text-sm mt-1">{error}</p>
        </div>
      </div>
    );
  }

  if (!content) {
    return (
      <div className="flex items-center justify-center h-96 bg-slate-50 rounded-lg border">
        <p className="text-slate-500">Ingen innhold å vise</p>
      </div>
    );
  }

  const containerClass = isFullscreen
    ? "fixed inset-0 z-50 bg-white flex flex-col"
    : "flex flex-col h-full";

  return (
    <div className={containerClass}>
      {/* Toolbar */}
      <div className="flex items-center justify-between px-4 py-2 bg-slate-100 border-b shrink-0">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-slate-600">
            {title || "Forhåndsvisning"}
          </span>
          <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded">
            HTML
          </span>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowSource(!showSource)}
            title={showSource ? "Vis forhåndsvisning" : "Vis kildekode"}
          >
            {showSource ? (
              <>
                <Eye className="h-4 w-4 mr-1" />
                Forhåndsvisning
              </>
            ) : (
              <>
                <Code className="h-4 w-4 mr-1" />
                Kildekode
              </>
            )}
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={toggleFullscreen}
            title={isFullscreen ? "Avslutt fullskjerm" : "Fullskjerm"}
          >
            {isFullscreen ? (
              <Minimize2 className="h-4 w-4" />
            ) : (
              <Maximize2 className="h-4 w-4" />
            )}
          </Button>
        </div>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-auto bg-slate-200">
        {showSource ? (
          <pre className="p-4 bg-slate-900 text-slate-100 text-sm font-mono overflow-auto h-full">
            <code>{content}</code>
          </pre>
        ) : (
          <iframe
            ref={iframeRef}
            title="Template Preview"
            className="w-full h-full border-0 bg-slate-200"
            sandbox="allow-same-origin"
            style={{ minHeight: isFullscreen ? "100%" : "600px" }}
          />
        )}
      </div>
    </div>
  );
}
