"use client";

import { useEffect, useRef, useState } from "react";
import { Maximize2, Minimize2, Code, Eye, Loader2, FlaskConical, FlaskConicalOff, FileText, Scissors } from "lucide-react";
import { Button } from "@/components/ui/button";

/**
 * TemplatePreview Component
 * 
 * Renders HTML templates in an isolated iframe with the full Vitec/Proaktiv
 * styling loaded from an external CSS file.
 * 
 * The CSS file (/vitec-theme.css) is loaded via a link tag inside the iframe,
 * ensuring complete style isolation from the main application.
 * 
 * Features:
 * - A4 page break visualization for print layout planning
 * - Test data toggle for previewing with sample values
 * - Source code view toggle
 * - Fullscreen mode
 */

interface TemplatePreviewProps {
  content: string;
  title?: string;
  isLoading?: boolean;
  error?: string;
  /** Stylesheet to load inside the iframe (defaults to /vitec-theme.css) */
  stylesheetHref?: string;
  /** Highlight merge fields in preview (developer aid). Default: false */
  highlightMergeFields?: boolean;
  /** Optional header HTML to render above the template content (PDF-like previews) */
  headerHtml?: string | null;
  /** Optional footer HTML to render below the template content (PDF-like previews) */
  footerHtml?: string | null;
  /** Optional signature HTML to render below the template content (email-like previews) */
  signatureHtml?: string | null;
  /** Whether test data mode is enabled */
  testDataEnabled?: boolean;
  /** Callback to toggle test data mode */
  onToggleTestData?: () => void;
  /** Whether processed test data is available */
  hasProcessedData?: boolean;
}

export function TemplatePreview({
  content,
  title,
  isLoading = false,
  error,
  stylesheetHref = "/vitec-theme.css",
  highlightMergeFields = false,
  headerHtml = null,
  footerHtml = null,
  signatureHtml = null,
  testDataEnabled = false,
  onToggleTestData,
  hasProcessedData = false,
}: TemplatePreviewProps) {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showSource, setShowSource] = useState(false);
  const [showPageBreaks, setShowPageBreaks] = useState(false);

  /**
   * Highlight merge fields in the content
   * Converts [[field.name]] to highlighted spans
   */
  const applyMergeFieldHighlights = (html: string): string => {
    return html.replace(
      /\[\[([^\]]+)\]\]/g,
      '<span class="merge-field-highlight">[[$1]]</span>'
    );
  };

  const extractVitecInnerHtml = (html: string): { inner: string; wrapperAttributes: string } => {
    try {
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, "text/html");
      const wrapper = doc.getElementById("vitecTemplate");
      if (!wrapper) return { inner: html, wrapperAttributes: "" };

      // Preserve wrapper attributes (except id) in a simple string form
      const attrs = Array.from(wrapper.attributes)
        .filter((a) => a.name !== "id")
        .map((a) => `${a.name}="${a.value}"`)
        .join(" ");

      return { inner: wrapper.innerHTML, wrapperAttributes: attrs };
    } catch {
      return { inner: html, wrapperAttributes: "" };
    }
  };

  /**
   * Build the complete HTML document for the iframe
   * Uses an external stylesheet for full Vitec/Proaktiv styling
   * Automatically wraps content in #vitecTemplate for consistent centering
   */
  const buildPreviewDocument = (): string => {
    const processedContent = highlightMergeFields ? applyMergeFieldHighlights(content) : content;
    const pageBreakClass = showPageBreaks ? "show-page-breaks" : "";

    // Always render inside #vitecTemplate; if content already has wrapper, extract innerHTML.
    const { inner, wrapperAttributes } = extractVitecInnerHtml(processedContent);
    const headerBlock = headerHtml ? `<div data-vitec-preview="header">${headerHtml}</div>` : "";
    const footerBlock = footerHtml ? `<div data-vitec-preview="footer">${footerHtml}</div>` : "";
    const signatureBlock = signatureHtml ? `<div data-vitec-preview="signature">${signatureHtml}</div>` : "";

    const wrappedContent = `<div id="vitecTemplate" ${wrapperAttributes}>
      ${headerBlock}
      ${inner}
      ${signatureBlock}
      ${footerBlock}
    </div>`;

    return `<!DOCTYPE html>
<html lang="no">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${title || "Template Preview"}</title>
  <link rel="stylesheet" href="${stylesheetHref}" />
</head>
<body class="vitec-preview-mode ${pageBreakClass}">
  ${wrappedContent}
</body>
</html>`;
  };

  // Update iframe content when content changes or page break mode toggles
  useEffect(() => {
    if (iframeRef.current && content && !showSource) {
      const doc = iframeRef.current.contentDocument;
      if (doc) {
        doc.open();
        doc.write(buildPreviewDocument());
        doc.close();
      }
    }
  }, [content, showSource, showPageBreaks]);

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96 bg-muted rounded-lg border">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin text-secondary mx-auto mb-3" />
          <p className="text-muted-foreground">Laster forhåndsvisning...</p>
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
      <div className="flex items-center justify-center h-96 bg-muted rounded-lg border">
        <p className="text-muted-foreground">Ingen innhold å vise</p>
      </div>
    );
  }

  const containerClass = isFullscreen
    ? "fixed inset-0 z-50 bg-background flex flex-col"
    : "flex flex-col h-full";

  return (
    <div className={containerClass}>
      {/* Toolbar */}
      <div className="flex items-center justify-between px-4 py-2 bg-muted border-b shrink-0">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-muted-foreground">
            {title || "Forhåndsvisning"}
          </span>
          <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded">
            HTML
          </span>
          {testDataEnabled && (
            <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded flex items-center gap-1">
              <FlaskConical className="h-3 w-3" />
              Testdata
            </span>
          )}
          {showPageBreaks && (
            <span className="text-xs bg-amber-100 text-amber-700 px-2 py-0.5 rounded flex items-center gap-1">
              <Scissors className="h-3 w-3" />
              A4 Sideskift
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {/* Test Data Toggle */}
          {onToggleTestData && hasProcessedData && (
            <Button
              variant={testDataEnabled ? "default" : "outline"}
              size="sm"
              onClick={onToggleTestData}
              title={testDataEnabled ? "Vis originalt innhold" : "Vis med testdata"}
              className={testDataEnabled ? "bg-blue-600 hover:bg-blue-700" : ""}
            >
              {testDataEnabled ? (
                <>
                  <FlaskConicalOff className="h-4 w-4 mr-1" />
                  Original
                </>
              ) : (
                <>
                  <FlaskConical className="h-4 w-4 mr-1" />
                  Testdata
                </>
              )}
            </Button>
          )}
          {/* Page Break Toggle */}
          <Button
            variant={showPageBreaks ? "default" : "outline"}
            size="sm"
            onClick={() => setShowPageBreaks(!showPageBreaks)}
            title={showPageBreaks ? "Skjul sideskift" : "Vis A4-sideskift"}
            className={showPageBreaks ? "bg-amber-600 hover:bg-amber-700" : ""}
          >
            {showPageBreaks ? (
              <>
                <FileText className="h-4 w-4 mr-1" />
                Skjul A4
              </>
            ) : (
              <>
                <Scissors className="h-4 w-4 mr-1" />
                Vis A4
              </>
            )}
          </Button>
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
      <div className="flex-1 overflow-auto bg-muted">
        {showSource ? (
          <pre className="p-4 bg-primary text-primary-foreground text-sm font-mono overflow-auto h-full">
            <code>{content}</code>
          </pre>
        ) : (
          <iframe
            ref={iframeRef}
            title="Template Preview"
            className="w-full h-full border-0 bg-muted"
            sandbox="allow-same-origin"
            style={{ minHeight: isFullscreen ? "100%" : "600px" }}
          />
        )}
      </div>
    </div>
  );
}
