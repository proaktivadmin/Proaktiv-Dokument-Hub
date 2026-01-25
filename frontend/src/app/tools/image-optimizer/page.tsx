"use client";

import { useState, useCallback, useRef } from "react";
import {
  Upload, Download, Image as ImageIcon, Trash2, Settings2,
  ChevronRight, Home, FileImage, CheckCircle2, AlertCircle,
  ZoomIn, RotateCcw
} from "lucide-react";
import { Header } from "@/components/layout/Header";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { cn } from "@/lib/utils";

interface ProcessedImage {
  id: string;
  originalFile: File;
  originalSize: number;
  originalDimensions: { width: number; height: number };
  processedBlob: Blob | null;
  processedSize: number;
  processedDimensions: { width: number; height: number };
  status: "pending" | "processing" | "done" | "error";
  error?: string;
  previewUrl?: string;
}

function formatSize(bytes: number): string {
  if (bytes >= 1024 * 1024) {
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  } else if (bytes >= 1024) {
    return `${(bytes / 1024).toFixed(0)} KB`;
  }
  return `${bytes} B`;
}

function formatFilename(email: string): string {
  // Convert email to filename format (replace @ with %40 for URL encoding compatibility)
  return email.toLowerCase().replace("@", "%40") + ".jpg";
}

function getImageDimensions(file: File): Promise<{ width: number; height: number }> {
  return new Promise((resolve) => {
    const img = new window.Image();
    img.onload = () => {
      resolve({ width: img.width, height: img.height });
      URL.revokeObjectURL(img.src);
    };
    img.onerror = () => resolve({ width: 0, height: 0 });
    img.src = URL.createObjectURL(file);
  });
}

export default function ImageOptimizerPage() {
  const [images, setImages] = useState<ProcessedImage[]>([]);
  const [maxSize, setMaxSize] = useState(800);
  const [quality, setQuality] = useState(85);
  const [isProcessing, setIsProcessing] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFilesSelect = useCallback(async (files: FileList | null) => {
    if (!files || files.length === 0) return;

    const newImages: ProcessedImage[] = [];
    
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      if (!file.type.startsWith("image/")) continue;

      // Get original dimensions
      const dimensions = await getImageDimensions(file);
      
      newImages.push({
        id: crypto.randomUUID(),
        originalFile: file,
        originalSize: file.size,
        originalDimensions: dimensions,
        processedBlob: null,
        processedSize: 0,
        processedDimensions: { width: 0, height: 0 },
        status: "pending",
        previewUrl: URL.createObjectURL(file),
      });
    }

    setImages(prev => [...prev, ...newImages]);
  }, []);

  const processImage = async (image: ProcessedImage): Promise<ProcessedImage> => {
    return new Promise((resolve) => {
      const img = new window.Image();
      img.onload = () => {
        // Calculate new dimensions
        let newWidth = img.width;
        let newHeight = img.height;
        
        if (Math.max(newWidth, newHeight) > maxSize) {
          if (newWidth > newHeight) {
            newHeight = Math.round(newHeight * (maxSize / newWidth));
            newWidth = maxSize;
          } else {
            newWidth = Math.round(newWidth * (maxSize / newHeight));
            newHeight = maxSize;
          }
        }

        // Create canvas and draw resized image
        const canvas = document.createElement("canvas");
        canvas.width = newWidth;
        canvas.height = newHeight;
        const ctx = canvas.getContext("2d");
        
        if (!ctx) {
          resolve({ ...image, status: "error", error: "Canvas not supported" });
          return;
        }

        // Fill with white background (for transparent PNGs)
        ctx.fillStyle = "#FFFFFF";
        ctx.fillRect(0, 0, newWidth, newHeight);
        ctx.drawImage(img, 0, 0, newWidth, newHeight);

        // Convert to JPEG blob
        canvas.toBlob(
          (blob) => {
            if (blob) {
              resolve({
                ...image,
                processedBlob: blob,
                processedSize: blob.size,
                processedDimensions: { width: newWidth, height: newHeight },
                status: "done",
              });
            } else {
              resolve({ ...image, status: "error", error: "Failed to create blob" });
            }
          },
          "image/jpeg",
          quality / 100
        );
      };

      img.onerror = () => {
        resolve({ ...image, status: "error", error: "Failed to load image" });
      };

      img.src = URL.createObjectURL(image.originalFile);
    });
  };

  const handleProcessAll = async () => {
    setIsProcessing(true);

    const updatedImages = [...images];
    
    for (let i = 0; i < updatedImages.length; i++) {
      if (updatedImages[i].status === "pending" || updatedImages[i].status === "error") {
        updatedImages[i] = { ...updatedImages[i], status: "processing" };
        setImages([...updatedImages]);
        
        const processed = await processImage(updatedImages[i]);
        updatedImages[i] = processed;
        setImages([...updatedImages]);
      }
    }

    setIsProcessing(false);
  };

  const handleDownload = (image: ProcessedImage) => {
    if (!image.processedBlob) return;
    
    // Extract email from filename or use original name
    const originalName = image.originalFile.name.replace(/\.[^/.]+$/, "");
    const filename = originalName.includes("@") 
      ? formatFilename(originalName)
      : `${originalName.toLowerCase()}.jpg`;
    
    const url = URL.createObjectURL(image.processedBlob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleDownloadAll = async () => {
    const doneImages = images.filter(img => img.status === "done" && img.processedBlob);
    
    for (const image of doneImages) {
      handleDownload(image);
      // Small delay between downloads
      await new Promise(r => setTimeout(r, 100));
    }
  };

  const handleRemove = (id: string) => {
    setImages(prev => {
      const image = prev.find(img => img.id === id);
      if (image?.previewUrl) {
        URL.revokeObjectURL(image.previewUrl);
      }
      return prev.filter(img => img.id !== id);
    });
  };

  const handleClear = () => {
    images.forEach(img => {
      if (img.previewUrl) URL.revokeObjectURL(img.previewUrl);
    });
    setImages([]);
  };

  const handleReprocessAll = () => {
    setImages(prev => prev.map(img => ({ ...img, status: "pending" as const, processedBlob: null })));
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    handleFilesSelect(e.dataTransfer.files);
  }, [handleFilesSelect]);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const totalOriginal = images.reduce((sum, img) => sum + img.originalSize, 0);
  const totalProcessed = images.reduce((sum, img) => sum + img.processedSize, 0);
  const savings = totalOriginal > 0 ? Math.round((1 - totalProcessed / totalOriginal) * 100) : 0;
  const doneCount = images.filter(img => img.status === "done").length;

  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container mx-auto px-6 py-8 space-y-6">
        {/* Breadcrumb */}
        <Breadcrumb>
          <BreadcrumbList>
            <BreadcrumbItem>
              <BreadcrumbLink href="/" className="flex items-center gap-1.5">
                <Home className="h-4 w-4" />
                Dashboard
              </BreadcrumbLink>
            </BreadcrumbItem>
            <BreadcrumbSeparator>
              <ChevronRight className="h-4 w-4" />
            </BreadcrumbSeparator>
            <BreadcrumbItem>
              <BreadcrumbPage className="flex items-center gap-1.5">
                <FileImage className="h-4 w-4" />
                Bildeoptimalisering
              </BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>

        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold font-serif text-foreground">Bildeoptimalisering</h1>
            <p className="text-muted-foreground mt-1">
              Optimaliser ansattbilder for raskere lasting og lavere båndbredde
            </p>
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          {/* Settings Panel */}
          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings2 className="h-5 w-5" />
                Innstillinger
              </CardTitle>
              <CardDescription>
                Juster kvalitet og størrelse for optimale resultater
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-3">
                <Label>Maks dimensjon: {maxSize}px</Label>
                <Slider
                  value={[maxSize]}
                  onValueChange={([value]) => setMaxSize(value)}
                  min={200}
                  max={1200}
                  step={50}
                />
                <p className="text-xs text-muted-foreground">
                  Lengste kant skaleres ned til denne størrelsen
                </p>
              </div>

              <div className="space-y-3">
                <Label>JPEG-kvalitet: {quality}%</Label>
                <Slider
                  value={[quality]}
                  onValueChange={([value]) => setQuality(value)}
                  min={50}
                  max={100}
                  step={5}
                />
                <p className="text-xs text-muted-foreground">
                  Høyere kvalitet = større filer. 85% anbefalt.
                </p>
              </div>

              <Separator />

              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Bilder:</span>
                  <span className="font-medium">{images.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Ferdig:</span>
                  <span className="font-medium">{doneCount} / {images.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Original:</span>
                  <span className="font-medium">{formatSize(totalOriginal)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Optimalisert:</span>
                  <span className="font-medium text-green-600">{formatSize(totalProcessed)}</span>
                </div>
                {savings > 0 && (
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Spart:</span>
                    <span className="font-medium text-green-600">{savings}%</span>
                  </div>
                )}
              </div>

              <Separator />

              <div className="flex flex-col gap-2">
                <Button
                  onClick={handleProcessAll}
                  disabled={images.length === 0 || isProcessing}
                  className="w-full"
                >
                  <ZoomIn className="mr-2 h-4 w-4" />
                  {isProcessing ? "Behandler..." : "Optimaliser alle"}
                </Button>
                <Button
                  variant="outline"
                  onClick={handleDownloadAll}
                  disabled={doneCount === 0}
                  className="w-full"
                >
                  <Download className="mr-2 h-4 w-4" />
                  Last ned alle ({doneCount})
                </Button>
                {images.length > 0 && (
                  <>
                    <Button
                      variant="ghost"
                      onClick={handleReprocessAll}
                      disabled={isProcessing}
                      className="w-full"
                    >
                      <RotateCcw className="mr-2 h-4 w-4" />
                      Behandle på nytt
                    </Button>
                    <Button
                      variant="ghost"
                      onClick={handleClear}
                      className="w-full text-destructive hover:text-destructive"
                    >
                      <Trash2 className="mr-2 h-4 w-4" />
                      Fjern alle
                    </Button>
                  </>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Upload & Preview Area */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <ImageIcon className="h-5 w-5" />
                Bilder
              </CardTitle>
              <CardDescription>
                Dra og slipp bilder eller klikk for å velge filer
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Drop zone */}
              <div
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onClick={() => fileInputRef.current?.click()}
                className={cn(
                  "border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors",
                  "hover:border-primary/50 hover:bg-muted/50",
                  images.length === 0 ? "py-16" : "py-6"
                )}
              >
                <Upload className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
                <p className="text-sm text-muted-foreground">
                  Dra og slipp bilder her, eller klikk for å velge
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  Støtter JPG, PNG, WebP
                </p>
              </div>
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept="image/*"
                onChange={(e) => handleFilesSelect(e.target.files)}
                className="hidden"
              />

              {/* Image list */}
              {images.length > 0 && (
                <div className="space-y-2 max-h-[500px] overflow-y-auto">
                  {images.map((image) => (
                    <div
                      key={image.id}
                      className="flex items-center gap-4 p-3 bg-muted/30 rounded-lg"
                    >
                      {/* Preview thumbnail */}
                      <div className="w-12 h-12 rounded overflow-hidden bg-muted shrink-0">
                        {image.previewUrl && (
                          // eslint-disable-next-line @next/next/no-img-element
                          <img
                            src={image.previewUrl}
                            alt=""
                            className="w-full h-full object-cover"
                          />
                        )}
                      </div>

                      {/* Info */}
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">
                          {image.originalFile.name}
                        </p>
                        <div className="flex items-center gap-2 text-xs text-muted-foreground">
                          <span>
                            {image.originalDimensions.width}x{image.originalDimensions.height}
                          </span>
                          <span>→</span>
                          {image.status === "done" ? (
                            <>
                              <span className="text-green-600">
                                {image.processedDimensions.width}x{image.processedDimensions.height}
                              </span>
                              <span className="text-green-600">
                                ({formatSize(image.processedSize)})
                              </span>
                            </>
                          ) : (
                            <span>{formatSize(image.originalSize)}</span>
                          )}
                        </div>
                      </div>

                      {/* Status */}
                      <div className="shrink-0">
                        {image.status === "pending" && (
                          <Badge variant="secondary">Venter</Badge>
                        )}
                        {image.status === "processing" && (
                          <Badge variant="secondary">Behandler...</Badge>
                        )}
                        {image.status === "done" && (
                          <Badge className="bg-green-500/10 text-green-600 hover:bg-green-500/20">
                            <CheckCircle2 className="h-3 w-3 mr-1" />
                            Ferdig
                          </Badge>
                        )}
                        {image.status === "error" && (
                          <Badge variant="destructive">
                            <AlertCircle className="h-3 w-3 mr-1" />
                            Feil
                          </Badge>
                        )}
                      </div>

                      {/* Actions */}
                      <div className="flex items-center gap-1 shrink-0">
                        {image.status === "done" && (
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => handleDownload(image)}
                          >
                            <Download className="h-4 w-4" />
                          </Button>
                        )}
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleRemove(image.id)}
                        >
                          <Trash2 className="h-4 w-4 text-destructive" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Instructions */}
        <Card>
          <CardHeader>
            <CardTitle>Slik bruker du verktøyet</CardTitle>
          </CardHeader>
          <CardContent className="prose prose-sm max-w-none text-muted-foreground">
            <ol className="list-decimal list-inside space-y-2">
              <li>
                <strong>Last opp bilder:</strong> Dra og slipp ansattbilder eller klikk for å velge filer.
                Navngi filene med e-postadresse (f.eks. <code>ola.nordmann@proaktiv.no.jpg</code>).
              </li>
              <li>
                <strong>Juster innstillinger:</strong> Standardverdiene (800px, 85% kvalitet) er optimale for de fleste bruk.
              </li>
              <li>
                <strong>Optimaliser:</strong> Klikk &quot;Optimaliser alle&quot; for å behandle bildene.
              </li>
              <li>
                <strong>Last ned:</strong> Last ned de optimaliserte bildene og last dem opp til WebDAV-serveren.
              </li>
              <li>
                <strong>Oppdater database:</strong> Kjør <code>update_photo_urls_webdav.py</code> for å oppdatere profil-URLene.
              </li>
            </ol>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
