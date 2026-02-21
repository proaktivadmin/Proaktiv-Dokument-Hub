"use client";

import { useCallback, useRef, useState } from "react";

interface MergeFieldHighlighterProps {
  editorIframeRef: React.RefObject<HTMLIFrameElement | null>;
  isSourceMode: boolean;
}

const HIGHLIGHT_STYLE_ID = "merge-field-highlight-style";
const HIGHLIGHT_CSS = `
.mf-highlight {
  background-color: rgba(188, 171, 138, 0.2);
  border: 1px dashed rgba(188, 171, 138, 0.5);
  border-radius: 2px;
  padding: 0 2px;
  cursor: pointer;
}
.mf-highlight:hover {
  background-color: rgba(188, 171, 138, 0.35);
}
`;

/**
 * Provides a toggle to highlight [[...]] merge field patterns in CKEditor WYSIWYG mode.
 * Injects CSS into the CKEditor iframe and walks the DOM to wrap patterns.
 * Highlights are stripped before saving via removeHighlights().
 */
export function useMergeFieldHighlighter({
  editorIframeRef,
  isSourceMode,
}: MergeFieldHighlighterProps) {
  const [isActive, setIsActive] = useState(false);
  const highlightedRef = useRef(false);

  const injectStyle = useCallback(() => {
    const iframe = editorIframeRef.current;
    if (!iframe?.contentDocument) return;

    const iframeDoc = iframe.contentDocument;
    const editorIframe = iframeDoc.querySelector(
      "iframe.cke_wysiwyg_frame"
    ) as HTMLIFrameElement | null;

    const targetDoc = editorIframe?.contentDocument || iframeDoc;
    if (targetDoc.getElementById(HIGHLIGHT_STYLE_ID)) return;

    const style = targetDoc.createElement("style");
    style.id = HIGHLIGHT_STYLE_ID;
    style.textContent = HIGHLIGHT_CSS;
    targetDoc.head.appendChild(style);
  }, [editorIframeRef]);

  const applyHighlights = useCallback(() => {
    const iframe = editorIframeRef.current;
    if (!iframe?.contentDocument) return;

    const iframeDoc = iframe.contentDocument;
    const editorIframe = iframeDoc.querySelector(
      "iframe.cke_wysiwyg_frame"
    ) as HTMLIFrameElement | null;

    const targetDoc = editorIframe?.contentDocument || iframeDoc;
    const body = targetDoc.body;
    if (!body) return;

    injectStyle();

    function walkAndHighlight(node: Node) {
      if (node.nodeType === Node.TEXT_NODE) {
        const text = node.textContent || "";
        const regex = /\[\[([^\]]+)\]\]/g;
        if (!regex.test(text)) return;

        regex.lastIndex = 0;
        const parent = node.parentNode;
        if (!parent) return;

        if (
          parent instanceof HTMLElement &&
          parent.classList.contains("mf-highlight")
        )
          return;

        const frag = document.createDocumentFragment();
        let lastIndex = 0;
        let match;

        while ((match = regex.exec(text)) !== null) {
          if (match.index > lastIndex) {
            frag.appendChild(
              document.createTextNode(text.substring(lastIndex, match.index))
            );
          }

          const span = document.createElement("span");
          span.className = "mf-highlight";
          span.setAttribute("data-mf-path", match[1]);
          span.textContent = match[0];
          frag.appendChild(span);

          lastIndex = match.index + match[0].length;
        }

        if (lastIndex < text.length) {
          frag.appendChild(document.createTextNode(text.substring(lastIndex)));
        }

        parent.replaceChild(frag, node);
      } else if (
        node.nodeType === Node.ELEMENT_NODE &&
        !(node as HTMLElement).classList?.contains("mf-highlight")
      ) {
        const children = Array.from(node.childNodes);
        for (const child of children) {
          walkAndHighlight(child);
        }
      }
    }

    walkAndHighlight(body);
    highlightedRef.current = true;
  }, [editorIframeRef, injectStyle]);

  const removeHighlights = useCallback(() => {
    const iframe = editorIframeRef.current;
    if (!iframe?.contentDocument) return;

    const iframeDoc = iframe.contentDocument;
    const editorIframe = iframeDoc.querySelector(
      "iframe.cke_wysiwyg_frame"
    ) as HTMLIFrameElement | null;

    const targetDoc = editorIframe?.contentDocument || iframeDoc;
    const body = targetDoc.body;
    if (!body) return;

    const highlights = body.querySelectorAll(".mf-highlight");
    highlights.forEach((el) => {
      const text = el.textContent || "";
      const textNode = targetDoc.createTextNode(text);
      el.parentNode?.replaceChild(textNode, el);
    });

    // Normalize adjacent text nodes
    body.normalize();
    highlightedRef.current = false;
  }, [editorIframeRef]);

  const toggle = useCallback(() => {
    if (isSourceMode) return;

    if (isActive) {
      removeHighlights();
      setIsActive(false);
    } else {
      applyHighlights();
      setIsActive(true);
    }
  }, [isActive, isSourceMode, applyHighlights, removeHighlights]);

  return {
    isActive,
    toggle,
    removeHighlights,
    applyHighlights,
  };
}
