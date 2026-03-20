"use client";

import { BookOpen, FileText, PlayCircle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useTranslation } from "@/hooks/use-translation";
import { Concept } from "@/types/graph";
import { useState } from "react";
import { Document, Page, pdfjs } from "react-pdf";
import "react-pdf/dist/esm/Page/AnnotationLayer.css";
import "react-pdf/dist/esm/Page/TextLayer.css";

// Set up the PDF.js worker securely via CDN to avoid Next.js Webpack headaches
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

interface ConceptViewerProps {
  concept: Concept;
}

export function ConceptViewer({ concept }: ConceptViewerProps) {
  const { t } = useTranslation();
  const [numPages, setNumPages] = useState<number>();

  // Ensure relative media URLs hit the backend properly in all environments
  const getMediaUrl = (url: string) => {
    if (url.startsWith("http")) return url;

    // Ensure the URL starts with a slash to avoid broken relative paths
    const formattedUrl = url.startsWith("/") ? url : `/${url}`;

    // Simply return the absolute path. Next.js/Nginx will route it to the backend.
    return formattedUrl;
  };

  // Extract the page number from the AI's context index (e.g., "Page 12")
  const pageMatch = concept.context_index?.match(/page\s*(\d+)/i);
  const targetPage = pageMatch ? parseInt(pageMatch[1], 10) : 1;

  function onDocumentLoadSuccess({ numPages }: { numPages: number }) {
    setNumPages(numPages);
  }

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <Card className="border-primary/20 shadow-sm bg-card/50 backdrop-blur-sm">
        <CardHeader className="pb-4">
          <div className="flex items-center gap-2 text-primary mb-2">
            <BookOpen className="w-5 h-5" />
            <span className="text-sm font-semibold uppercase tracking-wider">
              {t.learning.conceptOverview}
            </span>
          </div>
          <CardTitle className="text-3xl font-bold leading-tight">
            {concept.name}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="prose prose-neutral dark:prose-invert max-w-none">
            <h4 className="text-lg font-semibold text-foreground border-b border-border pb-2 mb-4">
              {t.learning.definition}
            </h4>
            <p className="text-muted-foreground leading-relaxed text-lg whitespace-pre-wrap">
              {concept.definition}
            </p>
          </div>
        </CardContent>
      </Card>

      {concept.context_index && (
        <Card className="border-border shadow-none bg-secondary/20">
          <CardContent className="space-y-6 pb-6">
            {/* MEDIA PLAYER: Automatically render Video or PDF */}
            {concept.file_url && (
              <div className="mt-8 overflow-hidden rounded-xl border border-border bg-secondary/10 shadow-inner">
                <div className="bg-secondary/50 px-4 py-2.5 border-b border-border flex items-center gap-2">
                  {concept.file_type === "video" ? (
                    <PlayCircle className="w-4 h-4 text-primary" />
                  ) : (
                    <FileText className="w-4 h-4 text-primary" />
                  )}
                  <span className="text-sm font-semibold text-foreground tracking-wide">
                    Original Document
                  </span>
                </div>

                {concept.file_type === "video" ? (
                  <video
                    // Regex searches the context_index for a timestamp like "15.5s" and jumps to it
                    src={`${getMediaUrl(concept.file_url)}${
                      concept.context_index?.match(/(\d+(\.\d+)?)\s*s/i)
                        ? `#t=${concept.context_index.match(/(\d+(\.\d+)?)\s*s/i)![1]}`
                        : ""
                    }`}
                    controls
                    controlsList="nodownload"
                    className="w-full max-h-125 object-contain bg-black"
                  />
                ) : (
                  // Canvas Rendering instead of <object>
                  <div className="relative flex justify-center bg-zinc-100 overflow-auto max-h-150 p-4 rounded-md">
                    <Document
                      file={getMediaUrl(concept.file_url)}
                      onLoadSuccess={onDocumentLoadSuccess}
                      loading={
                        <div className="p-8 text-muted-foreground animate-pulse">
                          Loading PDF...
                        </div>
                      }
                      error={
                        <div className="p-8 text-destructive text-center">
                          Failed to load PDF. Check CORS settings on your bucket
                          or backend.
                        </div>
                      }
                    >
                      <Page
                        // Fallback to page 1 if targetPage exceeds numPages to prevent crashing
                        pageNumber={
                          numPages && targetPage > numPages ? 1 : targetPage
                        }
                        renderTextLayer={true}
                        renderAnnotationLayer={false}
                        className="shadow-lg"
                        width={800}
                      />
                    </Document>

                    {/* The floating page indicator using numPages */}
                    {numPages && (
                      <div className="absolute bottom-4 right-6 bg-foreground/80 text-background px-3 py-1.5 rounded-md text-xs font-semibold backdrop-blur-sm shadow-md pointer-events-none">
                        Page {targetPage > numPages ? 1 : targetPage} of{" "}
                        {numPages}
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
