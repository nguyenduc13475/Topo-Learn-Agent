"use client";

import { BookOpen, FileText, PlayCircle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useTranslation } from "@/hooks/use-translation";
import { Concept } from "@/types/graph";

interface ConceptViewerProps {
  concept: Concept;
}

export function ConceptViewer({ concept }: ConceptViewerProps) {
  const { t } = useTranslation();

  // Ensure relative media URLs hit the backend properly in all environments
  const getMediaUrl = (url: string) => {
    if (url.startsWith("http")) return url;

    // Ensure the URL starts with a slash to avoid broken relative paths
    const formattedUrl = url.startsWith("/") ? url : `/${url}`;

    // Simply return the absolute path. Next.js/Nginx will route it to the backend.
    return formattedUrl;
  };

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
                  <object
                    data={`${getMediaUrl(concept.file_url)}#toolbar=0${
                      concept.context_index?.match(/page\s*(\d+)/i)
                        ? `&page=${concept.context_index.match(/page\s*(\d+)/i)![1]}`
                        : ""
                    }`}
                    type="application/pdf"
                    className="w-full h-150 border-none bg-white rounded-md"
                    title="PDF Viewer"
                  >
                    {/* Fallback UI if the browser entirely blocks inline PDFs */}
                    <div className="flex flex-col items-center justify-center h-full bg-secondary/20 space-y-4 p-8 text-center border border-dashed border-border rounded-md">
                      <p className="text-muted-foreground">
                        Your browser or workspace environment restricts inline
                        PDF rendering.
                      </p>
                      <a
                        href={getMediaUrl(concept.file_url!)}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="px-4 py-2 bg-primary text-primary-foreground text-sm font-medium rounded-md hover:bg-primary/90 transition-colors"
                      >
                        Open PDF in New Tab
                      </a>
                    </div>
                  </object>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
