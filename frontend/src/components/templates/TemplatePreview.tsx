"use client";

import { useEffect, useRef, useState } from "react";
import { Maximize2, Minimize2, Code, Eye, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";

/**
 * Proaktiv/Vitec Preview CSS
 * Combined styles for rendering HTML templates in the preview iframe.
 */
const PREVIEW_STYLES = `
/* Base Reset */
html, body {
  margin: 0;
  padding: 0;
  background: #f5f5f5;
  min-height: 100%;
}

/* Proaktiv Design Tokens */
:root {
  --color-primary: #272630;
  --color-pg-bronse: #bcab8a;
  --color-pg-beige: #e9e7dc;
  --color-text: #1d1d1d;
  --font-family-base: 'Arial', 'Helvetica', sans-serif;
  --font-family-serif: 'Georgia', 'Times New Roman', serif;
  --font-size-base: 10pt;
}

body {
  font-family: var(--font-family-base);
  font-size: var(--font-size-base);
  color: var(--color-text);
  line-height: 1.5;
}

/* A4 Container Styling */
#vitecTemplate {
  max-width: 210mm;
  margin: 20px auto;
  padding: 20mm 15mm;
  background: white;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  min-height: 297mm;
  box-sizing: border-box;
}

/* Typography */
h1, h2, h3, h4, h5, h6 {
  font-family: var(--font-family-serif);
  color: var(--color-primary);
  margin-top: 0;
}

h1 {
  font-size: 22pt;
  text-transform: uppercase;
  border-bottom: 3px solid var(--color-pg-bronse);
  padding-bottom: 10px;
  margin-bottom: 25px;
}

h2 {
  font-size: 14pt;
  border-left: 5px solid var(--color-pg-bronse);
  padding: 5px 0 5px 15px;
  margin-top: 30px;
  margin-bottom: 15px;
  background-color: #f9f9f7;
}

h3 {
  font-size: 12pt;
  margin-top: 20px;
}

p {
  margin-bottom: 1em;
}

a {
  color: var(--color-primary);
  text-decoration: underline;
}

strong, b {
  font-weight: 700;
}

/* Tables */
table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
  margin-bottom: 20px;
}

table.vitec-variables-list {
  table-layout: fixed;
}

table.vitec-variables-list td {
  padding: 5px;
  vertical-align: top;
  border-top: 1px solid #ededed;
}

table.vitec-variables-list tr:first-child td {
  border-top: none;
}

/* Signature Block */
.proaktiv-signature-block {
  border-top: 3px solid var(--color-pg-bronse);
  padding-top: 20px;
  margin-top: 40px;
}

/* Hide Vitec resource references */
[vitec-template] {
  display: none !important;
}

/* Merge field highlighting */
.merge-field-highlight {
  background-color: #fff3cd;
  border: 1px dashed #ffc107;
  padding: 0 4px;
  border-radius: 3px;
  font-family: monospace;
  font-size: 0.9em;
}
`;

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
   */
  const buildPreviewDocument = (): string => {
    const processedContent = highlightMergeFields(content);
    
    return `<!DOCTYPE html>
<html lang="no">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${title || "Template Preview"}</title>
  <style>${PREVIEW_STYLES}</style>
</head>
<body class="proaktiv-theme vitec-preview-mode">
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



