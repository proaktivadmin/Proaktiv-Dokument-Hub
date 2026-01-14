"use client";

/**
 * Hook for managing element inspector state in the document viewer.
 */

import { useState, useCallback } from "react";

// Regex to extract merge fields from HTML
const MERGE_FIELD_REGEX = /\[\[([^\]]+)\]\]/g;

export interface UseElementInspectorResult {
  selectedElement: HTMLElement | null;
  elementPath: string[];
  isOpen: boolean;
  selectElement: (element: HTMLElement) => void;
  clearSelection: () => void;
  getElementCode: () => string;
  copyElementCode: () => Promise<void>;
  getMergeFieldsInElement: () => string[];
}

/**
 * Build a path from an element to document root
 */
function buildElementPath(element: HTMLElement): string[] {
  const path: string[] = [];
  let current: HTMLElement | null = element;

  while (current && current !== document.body.parentElement) {
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

/**
 * Hook for managing element inspector state in the document viewer.
 */
export function useElementInspector(): UseElementInspectorResult {
  const [selectedElement, setSelectedElement] = useState<HTMLElement | null>(null);
  const [elementPath, setElementPath] = useState<string[]>([]);
  const [isOpen, setIsOpen] = useState(false);

  const selectElement = useCallback((element: HTMLElement) => {
    setSelectedElement(element);
    setElementPath(buildElementPath(element));
    setIsOpen(true);
  }, []);

  const clearSelection = useCallback(() => {
    setSelectedElement(null);
    setElementPath([]);
    setIsOpen(false);
  }, []);

  const getElementCode = useCallback((): string => {
    if (!selectedElement) return "";
    return selectedElement.outerHTML;
  }, [selectedElement]);

  const copyElementCode = useCallback(async (): Promise<void> => {
    const code = getElementCode();
    if (code) {
      await navigator.clipboard.writeText(code);
    }
  }, [getElementCode]);

  const getMergeFieldsInElement = useCallback((): string[] => {
    if (!selectedElement) return [];
    
    const html = selectedElement.outerHTML;
    const fields: string[] = [];
    let match;
    
    while ((match = MERGE_FIELD_REGEX.exec(html)) !== null) {
      if (!fields.includes(match[1])) {
        fields.push(match[1]);
      }
    }
    
    return fields;
  }, [selectedElement]);

  return {
    selectedElement,
    elementPath,
    isOpen,
    selectElement,
    clearSelection,
    getElementCode,
    copyElementCode,
    getMergeFieldsInElement,
  };
}
