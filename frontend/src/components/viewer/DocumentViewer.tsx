"use client";

/**
 * DocumentViewer - Main viewer container with multiple preview modes
 */

import { useState, useEffect } from "react";
import { Settings, Download, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { PreviewModeSelector, type PreviewMode } from "./PreviewModeSelector";
import { A4Frame } from "./A4Frame";
import { ElementInspector } from "./ElementInspector";
import { useElementInspector } from "@/hooks/v2";
import { templateApi } from "@/lib/api";

interface DocumentViewerProps {
  templateId: string;
  defaultMode?: PreviewMode;
  enableInspector?: boolean;
  onBack?: () => void;
  onSettings?: () => void;
}

export function DocumentViewer({
  templateId,
  defaultMode = "a4",
  enableInspector = true,
  onBack,
  onSettings,
}: DocumentViewerProps) {
  const [mode, setMode] = useState<PreviewMode>(defaultMode);
  const [content, setContent] = useState<string>("");
  const [title, setTitle] = useState<string>("");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const {
    selectedElement,
    elementPath,
    isOpen: inspectorOpen,
    selectElement,
    clearSelection,
    copyElementCode,
  } = useElementInspector();

  // Fetch template content
  useEffect(() => {
    const fetchContent = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const data = await templateApi.getContent(templateId);
        setContent(data.content);
        setTitle(data.title);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load template");
      } finally {
        setIsLoading(false);
      }
    };

    fetchContent();
  }, [templateId]);

  // Determine which modes to hide based on template type
  // For now, show all modes
  const hiddenModes: PreviewMode[] = [];

  const handleDownload = async () => {
    try {
      const { download_url, file_name } = await templateApi.getDownloadUrl(templateId);
      
      // Create a link and trigger download
      const link = document.createElement("a");
      link.href = download_url;
      link.download = file_name;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err) {
      console.error("Download failed:", err);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <header className="flex items-center justify-between gap-4 px-4 py-3 border-b bg-white/80 backdrop-blur-sm">
        <div className="flex items-center gap-3">
          {onBack && (
            <Button variant="ghost" size="icon" onClick={onBack}>
              <ArrowLeft className="h-5 w-5" />
            </Button>
          )}
          <h1 className="text-lg font-semibold text-[#272630] truncate">
            {title || "Laster..."}
          </h1>
        </div>

        <div className="flex items-center gap-2">
          {onSettings && (
            <Button variant="outline" size="sm" onClick={onSettings}>
              <Settings className="h-4 w-4 mr-1" />
              Innstillinger
            </Button>
          )}
          <Button variant="outline" size="sm" onClick={handleDownload}>
            <Download className="h-4 w-4 mr-1" />
            Last ned
          </Button>
        </div>
      </header>

      {/* Mode selector */}
      <div className="flex justify-center py-3 border-b bg-gray-50">
        <PreviewModeSelector
          value={mode}
          onChange={setMode}
          hiddenModes={hiddenModes}
        />
      </div>

      {/* Content area */}
      <main className="flex-1 overflow-hidden bg-gray-100">
        {isLoading && (
          <div className="flex items-center justify-center h-full text-gray-500">
            Laster forhåndsvisning...
          </div>
        )}

        {error && (
          <div className="flex items-center justify-center h-full text-red-500">
            {error}
          </div>
        )}

        {!isLoading && !error && content && (
          <>
            {mode === "a4" && (
              <A4Frame
                content={content}
                margins={{
                  top: 1.5,
                  bottom: 1.0,
                  left: 1.0,
                  right: 1.2,
                }}
                onElementClick={enableInspector ? selectElement : undefined}
              />
            )}

            {mode === "desktop_email" && (
              <div className="flex justify-center p-4">
                <div
                  className="bg-white shadow-lg rounded-lg overflow-hidden"
                  style={{ width: 960 }}
                >
                  <div className="bg-gray-200 px-4 py-2 flex items-center gap-2">
                    <div className="flex gap-1.5">
                      <div className="w-3 h-3 rounded-full bg-red-400" />
                      <div className="w-3 h-3 rounded-full bg-yellow-400" />
                      <div className="w-3 h-3 rounded-full bg-green-400" />
                    </div>
                    <span className="text-sm text-gray-500 ml-2">E-post forhåndsvisning</span>
                  </div>
                  <div
                    className="p-4"
                    dangerouslySetInnerHTML={{ __html: content }}
                  />
                </div>
              </div>
            )}

            {mode === "mobile_email" && (
              <div className="flex justify-center p-4">
                <div
                  className="bg-white shadow-lg rounded-3xl overflow-hidden border-4 border-gray-800"
                  style={{ width: 375 }}
                >
                  {/* Phone notch */}
                  <div className="bg-gray-800 h-6 flex justify-center items-end">
                    <div className="w-20 h-4 bg-gray-900 rounded-t-lg" />
                  </div>
                  {/* Content */}
                  <div
                    className="p-4 max-h-[600px] overflow-y-auto"
                    dangerouslySetInnerHTML={{ __html: content }}
                  />
                </div>
              </div>
            )}

            {mode === "sms" && (
              <div className="flex justify-center p-4">
                <div
                  className="bg-white shadow-lg rounded-3xl overflow-hidden border-4 border-gray-800"
                  style={{ width: 340 }}
                >
                  {/* Phone header */}
                  <div className="bg-gray-100 px-4 py-2 text-center border-b">
                    <span className="text-xs text-gray-500">SMS</span>
                  </div>
                  {/* Message bubble */}
                  <div className="p-4">
                    <div className="bg-green-500 text-white rounded-2xl rounded-tr-sm px-4 py-2 max-w-[80%] ml-auto">
                      {/* Strip HTML for SMS */}
                      <span className="text-sm">
                        {content.replace(/<[^>]*>/g, "").trim()}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </main>

      {/* Element Inspector */}
      {enableInspector && (
        <ElementInspector
          element={selectedElement}
          elementPath={elementPath}
          isOpen={inspectorOpen}
          onClose={clearSelection}
          onCopy={copyElementCode}
        />
      )}
    </div>
  );
}
