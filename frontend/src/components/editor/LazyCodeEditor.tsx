"use client";

/**
 * LazyCodeEditor - Dynamically imported Monaco editor
 * 
 * This wrapper uses next/dynamic to lazy load the Monaco editor,
 * significantly reducing the initial JavaScript bundle size.
 * 
 * Monaco Editor is ~2MB+ of JavaScript - by lazy loading it,
 * we only download it when users actually need the code editor.
 */

import dynamic from "next/dynamic";
import { Loader2 } from "lucide-react";

// Lazy load the CodeEditor component with a loading placeholder
const CodeEditor = dynamic(
  () => import("./CodeEditor").then((mod) => mod.CodeEditor),
  {
    loading: () => (
      <div className="flex items-center justify-center h-full min-h-[200px] bg-gray-900 text-gray-400 rounded-md">
        <Loader2 className="h-6 w-6 animate-spin mr-2" />
        Laster kodeeditor...
      </div>
    ),
    ssr: false, // Monaco doesn't work with SSR
  }
);

// Re-export the lazy-loaded editor with the same interface
export { CodeEditor as LazyCodeEditor };

// Also export as default for dynamic imports
export default CodeEditor;
