"use client";

import { useEffect, useRef, useCallback } from "react";

/**
 * Vitec base styles that complement the skin CSS
 * These are derived from analyzing Vitec's site.min.css
 * 
 * Defined outside component to prevent recreation on each render.
 */
const VITEC_BASE_STYLES = `
  /* ===== VITEC BASE STYLES ===== */
  /* Derived from Vitec's site.min.css to ensure accurate preview */
  
  body {
    font-family: 'Open Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    font-size: 14px;
    line-height: 1.5;
    color: #212529;
    background-color: #f8f9fa;
    margin: 0;
    padding: 0;
  }
  
  /* Fixed header styling */
  header.navbar.fixed-top {
    padding: 0.75rem 1rem;
    z-index: 1030;
  }
  
  header .object-header {
    font-weight: 600;
    font-size: 1rem;
  }
  
  header .nav-pills .nav-link {
    padding: 0.25rem 0.75rem;
    font-size: 0.875rem;
    margin-left: 0.5rem;
  }
  
  /* Main content area */
  main {
    padding-bottom: 2rem;
  }
  
  /* Bootstrap container centering */
  .container {
    width: 100%;
    padding-right: 15px;
    padding-left: 15px;
    margin-right: auto;
    margin-left: auto;
  }
  
  @media (min-width: 576px) {
    .container { max-width: 540px; }
  }
  @media (min-width: 768px) {
    .container { max-width: 720px; }
  }
  @media (min-width: 992px) {
    .container { max-width: 960px; }
  }
  @media (min-width: 1200px) {
    .container { max-width: 1140px; }
  }
  
  /* Article sections - Vitec specific */
  article.info {
    padding: 1.5rem 0;
    margin-bottom: 0;
  }
  
  article.info .header {
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 1rem;
  }
  
  article.info dl {
    margin-bottom: 0;
  }
  
  article.info dt {
    font-weight: 600;
    margin-top: 0.75rem;
  }
  
  article.info dt:first-child {
    margin-top: 0;
  }
  
  article.info dd {
    margin-bottom: 0;
    margin-left: 0;
  }
  
  article.container.primary {
    padding: 1.5rem;
    margin-bottom: 1rem;
    background: white;
    border-radius: 0;
  }
  
  article.container.primary.status {
    border-radius: 0;
  }
  
  article.container.primary h2 {
    font-size: 1.25rem;
    font-weight: 600;
    margin-bottom: 1rem;
  }
  
  /* Fieldset and legend styling */
  fieldset {
    border: none;
    padding: 0;
    margin: 0 0 1.5rem 0;
  }
  
  legend {
    font-size: 1.1rem;
    font-weight: 600;
    padding: 0;
    margin-bottom: 1rem;
    border-bottom: 2px solid #e9ecef;
    padding-bottom: 0.5rem;
    width: 100%;
  }
  
  .scroll-target {
    position: absolute;
    top: -80px;
  }
  
  /* Alert boxes - Vitec style */
  .alert-outline-bordered {
    background: #fff;
    border: 1px solid #dee2e6;
    border-radius: 0.25rem;
    padding: 1rem;
    margin-bottom: 1rem;
  }
  
  .alert.alert-info {
    border-radius: 0.25rem;
  }
  
  .alert.alert-warning {
    border-radius: 0.25rem;
  }
  
  /* List group - Vitec style */
  .list-group-item {
    border: 1px solid rgba(0,0,0,0.125);
    padding: 0.75rem 1.25rem;
  }
  
  .list-group-item .link-text {
    margin-left: 0.5rem;
  }
  
  .list-group-item small {
    display: block;
    margin-top: 0.25rem;
    color: #6c757d;
  }
  
  /* Form styling */
  .form-row {
    display: flex;
    flex-wrap: wrap;
    margin-right: -5px;
    margin-left: -5px;
  }
  
  .form-row > .col,
  .form-row > [class*="col-"] {
    padding-right: 5px;
    padding-left: 5px;
  }
  
  .form-group {
    margin-bottom: 1rem;
  }
  
  .form-group label {
    margin-bottom: 0.25rem;
    font-weight: 500;
  }
  
  .form-control {
    display: block;
    width: 100%;
    padding: 0.375rem 0.75rem;
    font-size: 1rem;
    line-height: 1.5;
    color: #495057;
    background-color: #fff;
    border: 1px solid #ced4da;
    border-radius: 0.25rem;
    transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
  }
  
  .form-control:focus {
    border-color: #80bdff;
    outline: 0;
    box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
  }
  
  textarea.form-control {
    min-height: 80px;
  }
  
  select.form-control {
    height: calc(1.5em + 0.75rem + 2px);
  }
  
  .helper-text {
    font-size: 0.8rem;
    color: #6c757d;
    display: block;
    margin-top: 0.25rem;
  }
  
  .required-mark {
    color: #dc3545;
    margin-left: 2px;
  }
  
  /* Consent options - Vitec specific */
  label.with-input {
    display: flex;
    flex-wrap: wrap;
    align-items: flex-start;
    cursor: pointer;
    margin-bottom: 0;
    font-weight: 400;
  }
  
  label.with-input > span {
    display: flex;
    align-items: flex-start;
  }
  
  label.with-input input[type="checkbox"] {
    margin-right: 0.5rem;
    margin-top: 0.25rem;
    width: 18px;
    height: 18px;
  }
  
  label.with-input .consent-link {
    margin-left: auto;
    font-size: 0.875rem;
    color: inherit;
    text-decoration: none;
  }
  
  label.with-input .consent-link:hover {
    text-decoration: underline;
  }
  
  label.with-input .consent-link .link-text {
    margin-right: 0.25rem;
  }
  
  /* Input group */
  .input-group {
    position: relative;
    display: flex;
    flex-wrap: wrap;
    align-items: stretch;
    width: 100%;
  }
  
  .input-group > .form-control {
    position: relative;
    flex: 1 1 auto;
    width: 1%;
    min-width: 0;
  }
  
  .input-group-append {
    margin-left: -1px;
    display: flex;
  }
  
  .input-group-text {
    display: flex;
    align-items: center;
    padding: 0.375rem 0.75rem;
    font-size: 1rem;
    font-weight: 400;
    line-height: 1.5;
    color: #495057;
    text-align: center;
    white-space: nowrap;
    background-color: #e9ecef;
    border: 1px solid #ced4da;
    border-radius: 0.25rem;
  }
  
  .input-group > .form-control:not(:last-child) {
    border-top-right-radius: 0;
    border-bottom-right-radius: 0;
  }
  
  .input-group-append .input-group-text {
    border-top-left-radius: 0;
    border-bottom-left-radius: 0;
  }
  
  /* Buttons */
  .btn {
    display: inline-block;
    font-weight: 400;
    text-align: center;
    white-space: nowrap;
    vertical-align: middle;
    user-select: none;
    border: 1px solid transparent;
    padding: 0.375rem 0.75rem;
    font-size: 1rem;
    line-height: 1.5;
    border-radius: 0.25rem;
    transition: color 0.15s ease-in-out, background-color 0.15s ease-in-out;
    cursor: pointer;
  }
  
  .btn-lg {
    padding: 0.5rem 1rem;
    font-size: 1.25rem;
    border-radius: 0.3rem;
  }
  
  .btn-block {
    display: block;
    width: 100%;
  }
  
  .btn i {
    margin-left: 0.5rem;
  }
  
  /* Modal styling */
  .modal-content {
    border-radius: 0.3rem;
  }
  
  .modal-header {
    padding: 1rem;
    border-bottom: 1px solid #dee2e6;
  }
  
  .modal-header .modal-title {
    font-size: 1.25rem;
    margin: 0;
  }
  
  .modal-header .close {
    padding: 1rem;
    margin: -1rem -1rem -1rem auto;
    background: transparent;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
  }
  
  .modal-body {
    padding: 1rem;
  }
  
  .modal-footer {
    padding: 1rem;
    border-top: 1px solid #dee2e6;
  }
  
  /* Responsive adjustments */
  @media (max-width: 767.98px) {
    article.container.primary {
      padding: 1rem;
    }
    
    .form-row > [class*="col-"] {
      flex: 0 0 100%;
      max-width: 100%;
    }
    
    header .d-none.d-sm-inline {
      display: none !important;
    }
  }
  
  /* Break word for long emails */
  .break-word {
    word-break: break-all;
  }
  
  /* Footer */
  footer {
    background: #f8f9fa;
    border-top: 1px solid #dee2e6;
  }
  
  /* ===== VISNINGSPORTAL SPECIFIC STYLES ===== */
  
  /* Background image - full page cover */
  .background-image {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: -1;
  }
  
  .background-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  
  /* Main container for visning - white card overlay */
  /* Live portal uses: 1140px max-width, 32px padding, no border-radius/shadow */
  .container.main {
    background: rgba(255, 255, 255, 0.97);
    padding: 32px 32px 16px;
    margin-top: 0;
    margin-bottom: 0;
    margin-left: auto;
    margin-right: auto;
    border-radius: 0;
    box-shadow: none;
    max-width: 1140px;
  }
  
  @media (max-width: 1199.98px) {
    .container.main { max-width: 960px; }
  }
  @media (max-width: 991.98px) {
    .container.main { max-width: 720px; }
  }
  @media (max-width: 767.98px) {
    .container.main { max-width: 540px; padding: 16px; }
  }
  
  /* Visning title - matches live portal (32px, 500 weight) */
  .container.main h1 {
    font-size: 32px;
    font-weight: 500;
    margin-bottom: 8px;
    line-height: 1.2;
  }
  
  .container.main h1 strong {
    font-weight: 500;
    margin-right: 0.25rem;
  }
  
  /* Section headings (fieldset legends) - 24px, 400 weight */
  .container.main h2,
  .container.main legend {
    font-size: 24px;
    font-weight: 400;
    margin-bottom: 8px;
  }
  
  /* Participant selection buttons */
  .participants + div {
    display: flex;
    flex-wrap: wrap;
    gap: 0.25rem;
  }
  
  /* Check option styling for consents */
  .check-option {
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;
    margin-bottom: 0.75rem;
  }
  
  .check-option input[type="checkbox"] {
    margin-top: 0.25rem;
    width: 18px;
    height: 18px;
    flex-shrink: 0;
  }
  
  .check-option label {
    margin-bottom: 0;
    font-weight: 400;
    cursor: pointer;
  }
  
  .check-option .consent-link {
    margin-left: 0.5rem;
  }
  
  /* Footer for visning - matches live portal styling */
  footer.footer,
  footer.container.footer {
    background: rgba(255, 255, 255, 0.97);
    border-top: none;
    text-align: center;
    padding: 8px;
    color: #212529;
    text-shadow: none;
    max-width: 1140px;
    margin-left: auto;
    margin-right: auto;
  }
  
  footer.footer a,
  footer.container.footer a {
    color: #205493;
    text-decoration: none;
  }
  
  footer.footer a:hover,
  footer.container.footer a:hover {
    text-decoration: underline;
  }
  
  /* Required field styling */
  .required-field small {
    color: #6c757d;
  }
  
  /* Screen reader only */
  .sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
  }
`;

/**
 * PortalFrame Component
 * 
 * Renders HTML content in an isolated iframe with the specified skin CSS.
 * Used for previewing Vitec portal skins (bud/visning).
 * 
 * Includes Vitec's base styles to ensure accurate preview.
 */

interface PortalFrameProps {
  /** HTML content to render inside the iframe */
  content: string;
  /** Path to the skin CSS file (e.g., "/skins/proaktiv-bud.css"). If undefined, uses vanilla Bootstrap. */
  skinCssHref?: string;
  /** Title for the iframe */
  title?: string;
  /** Additional class names */
  className?: string;
  /** Minimum height for the iframe */
  minHeight?: string;
  /** Portal type for specific base styles */
  portalType?: "bud" | "visning";
}

export function PortalFrame({
  content,
  skinCssHref,
  title = "Portal Preview",
  className = "",
  minHeight = "600px",
  portalType = "bud",
}: PortalFrameProps) {
  const iframeRef = useRef<HTMLIFrameElement>(null);

  /**
   * Build the complete HTML document for the iframe
   * Loads Bootstrap 4 (used by Vitec portals) and the custom skin CSS
   */
  const buildDocument = useCallback((): string => {
    // Only include custom skin CSS if provided (not vanilla mode)
    const skinCssLink = skinCssHref 
      ? `<!-- Custom Skin CSS (Proaktiv branding) -->\n  <link rel="stylesheet" href="${skinCssHref}">`
      : `<!-- Vanilla mode - no custom skin CSS -->`;

    return `<!DOCTYPE html>
<html lang="no">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${title}</title>
  <!-- Bootstrap 4 (Vitec portals use Bootstrap 4) -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/css/bootstrap.min.css">
  <!-- Font Awesome 5 (for icons) -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
  <!-- Google Fonts - Open Sans (Proaktiv font) -->
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700&display=swap">
  ${skinCssLink}
  <!-- Vitec base styles -->
  <style>${VITEC_BASE_STYLES}</style>
</head>
<body data-portal-type="${portalType}">
  ${content}
  <!-- Bootstrap JS for modals -->
  <script src="https://cdn.jsdelivr.net/npm/jquery@3.5.1/dist/jquery.slim.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>`;
  }, [title, skinCssHref, content, portalType]);

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
      sandbox="allow-same-origin allow-scripts"
    />
  );
}
