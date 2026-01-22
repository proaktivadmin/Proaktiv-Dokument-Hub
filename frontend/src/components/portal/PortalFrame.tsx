"use client";

import { useEffect, useRef, useCallback } from "react";

/**
 * PortalFrame Component
 * 
 * Renders HTML content in an isolated iframe with the specified skin CSS.
 * Used for previewing Vitec portal skins (bud/visning).
 */

interface PortalFrameProps {
  /** HTML content to render inside the iframe */
  content: string;
  /** Path to the skin CSS file (e.g., "/skins/proaktiv-bud.css") */
  skinCssHref: string;
  /** Title for the iframe */
  title?: string;
  /** Additional class names */
  className?: string;
  /** Minimum height for the iframe */
  minHeight?: string;
}

export function PortalFrame({
  content,
  skinCssHref,
  title = "Portal Preview",
  className = "",
  minHeight = "600px",
}: PortalFrameProps) {
  const iframeRef = useRef<HTMLIFrameElement>(null);

  /**
   * Build the complete HTML document for the iframe
   * Loads Bootstrap 4 (used by Vitec portals) and the custom skin CSS
   */
  const buildDocument = useCallback((): string => {
    return `<!DOCTYPE html>
<html lang="no">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${title}</title>
  <!-- Bootstrap 4 (Vitec portals use Bootstrap) -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/css/bootstrap.min.css">
  <!-- Font Awesome (for icons) -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
  <!-- Google Fonts -->
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700&display=swap">
  <!-- Custom Skin CSS -->
  <link rel="stylesheet" href="${skinCssHref}">
  <style>
    body {
      margin: 0;
      padding: 20px;
      min-height: 100vh;
    }
    .portal-container {
      max-width: 600px;
      margin: 0 auto;
      background: white;
      border-radius: 4px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.1);
      overflow: hidden;
    }
    .portal-header {
      padding: 20px;
      border-bottom: 1px solid #eee;
    }
    .portal-content {
      padding: 20px;
    }
    .portal-footer {
      padding: 15px 20px;
      background: #f8f9fa;
      border-top: 1px solid #eee;
      font-size: 12px;
      color: #666;
    }
  </style>
</head>
<body>
  ${content}
</body>
</html>`;
  }, [title, skinCssHref, content]);

  // Update iframe content when content or CSS changes
  useEffect(() => {
    if (iframeRef.current) {
      const doc = iframeRef.current.contentDocument;
      if (doc) {
        doc.open();
        doc.write(buildDocument());
        doc.close();
      }
    }
  }, [buildDocument]);

  return (
    <iframe
      ref={iframeRef}
      title={title}
      className={`w-full border-0 ${className}`}
      style={{ minHeight }}
      sandbox="allow-same-origin"
    />
  );
}
