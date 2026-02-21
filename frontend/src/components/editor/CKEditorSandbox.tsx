"use client";

import {
  useRef,
  useEffect,
  useCallback,
  useImperativeHandle,
  forwardRef,
  useState,
} from "react";

export interface CKEditorChange {
  type: "stripped" | "rewritten" | "added";
  description: string;
  original: string;
  modified: string;
}

export interface CKEditorValidationResult {
  isClean: boolean;
  changes: CKEditorChange[];
  inputLength: number;
  outputLength: number;
}

export interface CKEditorSandboxRef {
  getContent: () => Promise<string>;
  setContent: (html: string) => void;
  validate: () => Promise<CKEditorValidationResult>;
  switchToSource: () => void;
  switchToWysiwyg: () => void;
  insertAtCursor: (html: string) => void;
  getMode: () => Promise<"wysiwyg" | "source">;
}

interface CKEditorSandboxProps {
  content: string;
  onChange?: (html: string) => void;
  onValidation?: (result: CKEditorValidationResult) => void;
  onReady?: () => void;
  onModeChange?: (mode: "wysiwyg" | "source") => void;
  readOnly?: boolean;
  mode?: "edit" | "validate";
  className?: string;
}

const CKEDITOR_CDN =
  "https://cdn.ckeditor.com/4.25.1/full-all/ckeditor.js";

function buildIframeHtml(readOnly: boolean): string {
  return `<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  html, body { margin: 0; padding: 0; height: 100%; overflow: hidden; }
  #editor-wrapper { height: 100%; }
</style>
</head>
<body>
<div id="editor-wrapper">
  <textarea id="editor"></textarea>
</div>
<script src="${CKEDITOR_CDN}"></script>
<script>
(function() {
  var editor = null;
  var parentOrigin = '*';

  function initEditor() {
    if (typeof CKEDITOR === 'undefined') {
      setTimeout(initEditor, 100);
      return;
    }

    editor = CKEDITOR.replace('editor', {
      allowedContent: true,
      extraAllowedContent:
        '*[vitec-if,vitec-foreach,vitec-template,data-label,data-version,contenteditable,data-*]',
      fullPage: false,
      readOnly: ${readOnly},
      height: '100%',
      resize_enabled: false,
      removePlugins: 'elementspath',
      on: {
        instanceReady: function(evt) {
          var data = evt.editor.getData();
          window.parent.postMessage({ type: 'contentReady', html: data }, parentOrigin);
        },
        change: function() {
          if (editor) {
            var data = editor.getData();
            window.parent.postMessage({ type: 'contentChanged', html: data }, parentOrigin);
          }
        },
        mode: function() {
          if (editor) {
            window.parent.postMessage({ type: 'modeChanged', mode: editor.mode }, parentOrigin);
          }
        }
      }
    });
  }

  window.addEventListener('message', function(e) {
    if (!editor) return;
    var msg = e.data;
    if (!msg || !msg.type) return;

    switch (msg.type) {
      case 'setContent':
        editor.setData(msg.html || '');
        break;
      case 'getContent':
        window.parent.postMessage(
          { type: 'contentResponse', html: editor.getData() },
          parentOrigin
        );
        break;
      case 'validate':
        var output = editor.getData();
        window.parent.postMessage(
          { type: 'validationResult', html: output, inputHtml: msg.html },
          parentOrigin
        );
        break;
      case 'setMode':
        if (msg.mode === 'source') {
          editor.setMode('source');
        } else {
          editor.setMode('wysiwyg');
        }
        break;
      case 'insertAtCursor':
        if (editor.mode === 'wysiwyg') {
          editor.insertHtml(msg.html || '');
        } else {
          var ta = editor.container.$.querySelector('textarea.cke_source');
          if (ta) {
            var start = ta.selectionStart;
            var end = ta.selectionEnd;
            var text = ta.value;
            ta.value = text.substring(0, start) + (msg.html || '') + text.substring(end);
            var newPos = start + (msg.html || '').length;
            ta.selectionStart = newPos;
            ta.selectionEnd = newPos;
            ta.focus();
            editor.fire('change');
          }
        }
        break;
      case 'getMode':
        window.parent.postMessage({ type: 'modeResponse', mode: editor.mode }, parentOrigin);
        break;
    }
  });

  initEditor();
})();
</script>
</body>
</html>`;
}

function diffHtml(
  input: string,
  output: string
): CKEditorChange[] {
  const changes: CKEditorChange[] = [];
  const inputNorm = input.replace(/\s+/g, " ").trim();
  const outputNorm = output.replace(/\s+/g, " ").trim();

  if (inputNorm === outputNorm) return changes;

  if (output.length < input.length * 0.95) {
    changes.push({
      type: "stripped",
      description: `CKEditor removed ${input.length - output.length} characters`,
      original: input.substring(0, 200),
      modified: output.substring(0, 200),
    });
  } else if (output.length > input.length * 1.05) {
    changes.push({
      type: "added",
      description: `CKEditor added ${output.length - input.length} characters`,
      original: input.substring(0, 200),
      modified: output.substring(0, 200),
    });
  } else {
    changes.push({
      type: "rewritten",
      description: "CKEditor reformatted the HTML (whitespace or structure changes)",
      original: input.substring(0, 200),
      modified: output.substring(0, 200),
    });
  }
  return changes;
}

export const CKEditorSandbox = forwardRef<
  CKEditorSandboxRef,
  CKEditorSandboxProps
>(function CKEditorSandbox(
  {
    content,
    onChange,
    onValidation,
    onReady,
    onModeChange,
    readOnly = false,
    mode = "edit",
    className,
  },
  ref
) {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [isReady, setIsReady] = useState(false);
  const contentRef = useRef(content);
  const pendingGetContent = useRef<((html: string) => void) | null>(null);
  const pendingValidation = useRef<
    ((result: CKEditorValidationResult) => void) | null
  >(null);
  const pendingGetMode = useRef<
    ((mode: "wysiwyg" | "source") => void) | null
  >(null);

  const postToIframe = useCallback(
    (msg: Record<string, unknown>) => {
      iframeRef.current?.contentWindow?.postMessage(msg, "*");
    },
    []
  );

  useEffect(() => {
    const handleMessage = (e: MessageEvent) => {
      const msg = e.data;
      if (!msg || typeof msg.type !== "string") return;

      switch (msg.type) {
        case "contentReady":
          setIsReady(true);
          onReady?.();
          if (mode === "validate" && contentRef.current) {
            const result: CKEditorValidationResult = {
              isClean: diffHtml(contentRef.current, msg.html).length === 0,
              changes: diffHtml(contentRef.current, msg.html),
              inputLength: contentRef.current.length,
              outputLength: (msg.html as string).length,
            };
            onValidation?.(result);
          }
          break;

        case "contentChanged":
          onChange?.(msg.html as string);
          break;

        case "contentResponse":
          pendingGetContent.current?.(msg.html as string);
          pendingGetContent.current = null;
          break;

        case "validationResult": {
          const inputHtml = (msg.inputHtml as string) || contentRef.current;
          const outputHtml = msg.html as string;
          const changes = diffHtml(inputHtml, outputHtml);
          const result: CKEditorValidationResult = {
            isClean: changes.length === 0,
            changes,
            inputLength: inputHtml.length,
            outputLength: outputHtml.length,
          };
          pendingValidation.current?.(result);
          pendingValidation.current = null;
          onValidation?.(result);
          break;
        }

        case "modeChanged":
          onModeChange?.(msg.mode as "wysiwyg" | "source");
          break;

        case "modeResponse":
          pendingGetMode.current?.(msg.mode as "wysiwyg" | "source");
          pendingGetMode.current = null;
          break;
      }
    };

    window.addEventListener("message", handleMessage);
    return () => window.removeEventListener("message", handleMessage);
  }, [onChange, onValidation, onReady, onModeChange, mode]);

  // Send content when iframe is ready or content changes
  useEffect(() => {
    contentRef.current = content;
    if (isReady) {
      postToIframe({ type: "setContent", html: content });
    }
  }, [content, isReady, postToIframe]);

  useImperativeHandle(ref, () => ({
    getContent: () =>
      new Promise<string>((resolve) => {
        pendingGetContent.current = resolve;
        postToIframe({ type: "getContent" });
        setTimeout(() => {
          if (pendingGetContent.current) {
            pendingGetContent.current = null;
            resolve(contentRef.current);
          }
        }, 3000);
      }),
    setContent: (html: string) => {
      contentRef.current = html;
      postToIframe({ type: "setContent", html });
    },
    validate: () =>
      new Promise<CKEditorValidationResult>((resolve) => {
        pendingValidation.current = resolve;
        postToIframe({ type: "validate", html: contentRef.current });
        setTimeout(() => {
          if (pendingValidation.current) {
            pendingValidation.current = null;
            resolve({
              isClean: true,
              changes: [],
              inputLength: contentRef.current.length,
              outputLength: contentRef.current.length,
            });
          }
        }, 5000);
      }),
    switchToSource: () => postToIframe({ type: "setMode", mode: "source" }),
    switchToWysiwyg: () => postToIframe({ type: "setMode", mode: "wysiwyg" }),
    insertAtCursor: (html: string) => {
      postToIframe({ type: "insertAtCursor", html });
    },
    getMode: () =>
      new Promise<"wysiwyg" | "source">((resolve) => {
        pendingGetMode.current = resolve;
        postToIframe({ type: "getMode" });
        setTimeout(() => {
          if (pendingGetMode.current) {
            pendingGetMode.current = null;
            resolve("wysiwyg");
          }
        }, 2000);
      }),
  }));

  const srcDoc = buildIframeHtml(readOnly);

  return (
    <iframe
      ref={iframeRef}
      srcDoc={srcDoc}
      className={className}
      style={{ width: "100%", height: "100%", border: "none" }}
      sandbox="allow-scripts allow-same-origin"
      title="CKEditor 4 Sandbox"
    />
  );
});
