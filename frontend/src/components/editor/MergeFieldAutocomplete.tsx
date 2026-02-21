"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { useMergeFieldAutocomplete } from "@/hooks/v2";
import { cn } from "@/lib/utils";
import type { MergeField } from "@/types/v2";

interface MergeFieldAutocompleteProps {
  editorIframeRef: React.RefObject<HTMLIFrameElement | null>;
  onInsert: (syntax: string) => void;
  isSourceMode: boolean;
}

/**
 * Floating autocomplete popover that appears when user types `[[` in CKEditor source mode.
 * Listens to the source textarea inside the CKEditor iframe for `[[` patterns.
 */
export function MergeFieldAutocomplete({
  editorIframeRef,
  onInsert,
  isSourceMode,
}: MergeFieldAutocompleteProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [position, setPosition] = useState({ top: 0, left: 0 });
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [triggerOffset, setTriggerOffset] = useState<number | null>(null);
  const panelRef = useRef<HTMLDivElement>(null);

  const { suggestions } = useMergeFieldAutocomplete(query, 10);

  const close = useCallback(() => {
    setIsOpen(false);
    setQuery("");
    setSelectedIndex(0);
    setTriggerOffset(null);
  }, []);

  const insertField = useCallback(
    (field: MergeField) => {
      const iframe = editorIframeRef.current;
      if (!iframe?.contentWindow) return;

      const ta = iframe.contentDocument?.querySelector(
        "textarea.cke_source"
      ) as HTMLTextAreaElement | null;
      if (!ta || triggerOffset === null) return;

      const text = ta.value;
      const beforeTrigger = text.substring(0, triggerOffset);
      const afterCursor = text.substring(ta.selectionStart);
      const insertion = `[[${field.path}]]`;
      ta.value = beforeTrigger + insertion + afterCursor;
      const newPos = triggerOffset + insertion.length;
      ta.selectionStart = newPos;
      ta.selectionEnd = newPos;
      ta.focus();

      onInsert(insertion);
      close();
    },
    [editorIframeRef, onInsert, close, triggerOffset]
  );

  // Approximate cursor position in textarea
  const calculatePosition = useCallback(
    (ta: HTMLTextAreaElement, offset: number) => {
      const iframe = editorIframeRef.current;
      if (!iframe) return { top: 0, left: 0 };

      const iframeRect = iframe.getBoundingClientRect();
      const taRect = ta.getBoundingClientRect();

      const textBefore = ta.value.substring(0, offset);
      const lines = textBefore.split("\n");
      const lineHeight = parseInt(
        getComputedStyle(ta).lineHeight || "18",
        10
      );
      const charWidth = 7.8;
      const currentLineIndex = lines.length - 1;
      const currentLineLength = lines[currentLineIndex].length;

      const scrollTop = ta.scrollTop;
      const scrollLeft = ta.scrollLeft;

      const top =
        iframeRect.top +
        taRect.top +
        currentLineIndex * lineHeight -
        scrollTop +
        lineHeight +
        4;
      const left =
        iframeRect.left +
        taRect.left +
        currentLineLength * charWidth -
        scrollLeft;

      return { top: Math.max(top, 0), left: Math.max(left, 0) };
    },
    [editorIframeRef]
  );

  // Listen to textarea input in source mode
  useEffect(() => {
    if (!isSourceMode) {
      close();
      return;
    }

    const iframe = editorIframeRef.current;
    if (!iframe?.contentDocument) return;

    let textarea: HTMLTextAreaElement | null = null;
    let pollId: ReturnType<typeof setInterval> | null = null;

    const handleInput = () => {
      if (!textarea) return;
      const cursorPos = textarea.selectionStart;
      const text = textarea.value;

      // Look back from cursor for `[[`
      const lookback = text.substring(Math.max(0, cursorPos - 50), cursorPos);
      const bracketIdx = lookback.lastIndexOf("[[");

      if (bracketIdx === -1) {
        if (isOpen) close();
        return;
      }

      const afterBrackets = lookback.substring(bracketIdx + 2);

      // If there's a closing `]]`, the field is already complete
      if (afterBrackets.includes("]]")) {
        if (isOpen) close();
        return;
      }

      // Only allow word chars, dots, and asterisks in partial
      if (!/^[\w.*]*$/.test(afterBrackets)) {
        if (isOpen) close();
        return;
      }

      const absoluteTriggerOffset = cursorPos - lookback.length + bracketIdx;
      setTriggerOffset(absoluteTriggerOffset);
      setQuery(afterBrackets);
      setSelectedIndex(0);
      setPosition(calculatePosition(textarea, cursorPos));
      setIsOpen(true);
    };

    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return;

      if (e.key === "Escape") {
        e.preventDefault();
        e.stopPropagation();
        close();
        return;
      }

      if (e.key === "ArrowDown") {
        e.preventDefault();
        setSelectedIndex((prev) =>
          prev < suggestions.length - 1 ? prev + 1 : 0
        );
        return;
      }

      if (e.key === "ArrowUp") {
        e.preventDefault();
        setSelectedIndex((prev) =>
          prev > 0 ? prev - 1 : suggestions.length - 1
        );
        return;
      }

      if (e.key === "Enter" || e.key === "Tab") {
        if (suggestions.length > 0) {
          e.preventDefault();
          e.stopPropagation();
          insertField(suggestions[selectedIndex]);
        }
        return;
      }
    };

    const attachListeners = () => {
      textarea = iframe.contentDocument?.querySelector(
        "textarea.cke_source"
      ) as HTMLTextAreaElement | null;
      if (!textarea) return;

      textarea.addEventListener("input", handleInput);
      textarea.addEventListener("keydown", handleKeyDown);
      textarea.addEventListener("blur", () => {
        setTimeout(close, 200);
      });
      if (pollId) clearInterval(pollId);
    };

    pollId = setInterval(() => {
      const ta = iframe.contentDocument?.querySelector(
        "textarea.cke_source"
      ) as HTMLTextAreaElement | null;
      if (ta) attachListeners();
    }, 200);

    // Also try immediately
    attachListeners();

    return () => {
      if (pollId) clearInterval(pollId);
      if (textarea) {
        textarea.removeEventListener("input", handleInput);
        textarea.removeEventListener("keydown", handleKeyDown);
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isSourceMode, isOpen, suggestions, selectedIndex]);

  if (!isOpen || !isSourceMode || suggestions.length === 0) {
    return null;
  }

  return (
    <div
      ref={panelRef}
      className="fixed z-9999 rounded-lg border bg-white shadow-elevated max-h-64 overflow-y-auto min-w-[280px] max-w-[400px]"
      style={{ top: position.top, left: position.left }}
    >
      <div className="px-3 py-1.5 text-xs text-muted-foreground border-b bg-gray-50 rounded-t-lg">
        Flettekoder ({suggestions.length})
      </div>
      {suggestions.map((field, index) => (
        <button
          key={field.id}
          className={cn(
            "w-full flex flex-col items-start px-3 py-2 text-left transition-colors",
            "border-b last:border-b-0",
            index === selectedIndex
              ? "bg-[#BCAB8A]/15 text-[#272630]"
              : "hover:bg-gray-50"
          )}
          onMouseDown={(e) => {
            e.preventDefault();
            insertField(field);
          }}
          onMouseEnter={() => setSelectedIndex(index)}
        >
          <div className="flex items-center gap-2">
            <span className="font-medium text-sm">{field.label}</span>
            <code className="text-xs text-gray-500 bg-gray-100 px-1 rounded">
              {field.path}
            </code>
          </div>
          {field.description && (
            <span className="text-xs text-gray-500 mt-0.5">
              {field.description}
            </span>
          )}
        </button>
      ))}
    </div>
  );
}
