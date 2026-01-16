"use client";

/**
 * CodeEditor - Monaco-based HTML code editor
 * Provides syntax highlighting, formatting, and editing for HTML templates
 */

import { useRef, useCallback } from "react";
import Editor, { OnMount, OnChange } from "@monaco-editor/react";
import type { editor } from "monaco-editor";
import { Loader2 } from "lucide-react";

interface CodeEditorProps {
  value: string;
  onChange?: (value: string) => void;
  language?: "html" | "css" | "javascript" | "json";
  readOnly?: boolean;
  height?: string | number;
  theme?: "vs-dark" | "light";
  wordWrap?: "on" | "off" | "wordWrapColumn" | "bounded";
  minimap?: boolean;
  lineNumbers?: "on" | "off" | "relative" | "interval";
  fontSize?: number;
  onSave?: (value: string) => void;
}

export function CodeEditor({
  value,
  onChange,
  language = "html",
  readOnly = false,
  height = "100%",
  theme = "vs-dark",
  wordWrap = "on",
  minimap = false,
  lineNumbers = "on",
  fontSize = 14,
  onSave,
}: CodeEditorProps) {
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);

  const handleEditorDidMount: OnMount = useCallback((editor, monaco) => {
    editorRef.current = editor;

    // Configure HTML formatting
    monaco.languages.html.htmlDefaults.setOptions({
      format: {
        tabSize: 2,
        insertSpaces: true,
        wrapLineLength: 120,
        wrapAttributes: "auto",
        indentInnerHtml: true,
        preserveNewLines: true,
        maxPreserveNewLines: 2,
        endWithNewline: true,
      },
    });

    // Add Ctrl+S save shortcut
    if (onSave) {
      editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
        const currentValue = editor.getValue();
        onSave(currentValue);
      });
    }

    // Add Shift+Alt+F format shortcut
    editor.addCommand(
      monaco.KeyMod.Shift | monaco.KeyMod.Alt | monaco.KeyCode.KeyF,
      () => {
        editor.getAction("editor.action.formatDocument")?.run();
      }
    );
  }, [onSave]);

  const handleEditorChange: OnChange = useCallback(
    (value) => {
      if (onChange && value !== undefined) {
        onChange(value);
      }
    },
    [onChange]
  );

  const handleFormat = useCallback(() => {
    editorRef.current?.getAction("editor.action.formatDocument")?.run();
  }, []);

  return (
    <div className="h-full w-full flex flex-col">
      <Editor
        height={height}
        language={language}
        value={value}
        onChange={handleEditorChange}
        onMount={handleEditorDidMount}
        theme={theme}
        loading={
          <div className="flex items-center justify-center h-full bg-gray-900 text-gray-400">
            <Loader2 className="h-6 w-6 animate-spin mr-2" />
            Laster editor...
          </div>
        }
        options={{
          readOnly,
          wordWrap,
          minimap: { enabled: minimap },
          lineNumbers,
          fontSize,
          scrollBeyondLastLine: false,
          automaticLayout: true,
          tabSize: 2,
          insertSpaces: true,
          formatOnPaste: true,
          formatOnType: false,
          renderWhitespace: "selection",
          bracketPairColorization: { enabled: true },
          folding: true,
          foldingStrategy: "indentation",
          showFoldingControls: "mouseover",
          smoothScrolling: true,
          cursorBlinking: "smooth",
          cursorSmoothCaretAnimation: "on",
          padding: { top: 16, bottom: 16 },
        }}
      />
    </div>
  );
}

export { CodeEditor as default };
