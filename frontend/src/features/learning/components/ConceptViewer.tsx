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
    const baseUrl =
      process.env.NEXT_PUBLIC_API_URL?.replace("/api/v1", "") ||
      "http://localhost:8000";
    return `${baseUrl}${url}`;
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
            <div className="prose prose-neutral dark:prose-invert max-w-none">
              <h4 className="text-lg font-semibold text-foreground border-b border-border pb-2 mb-4">
                {t.learning.definition}
              </h4>
              <p className="text-muted-foreground leading-relaxed text-lg whitespace-pre-wrap">
                {concept.definition}
              </p>
            </div>

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
                    src={getMediaUrl(concept.file_url)}
                    controls
                    controlsList="nodownload"
                    className="w-full max-h-125 object-contain bg-black"
                  />
                ) : (
                  <iframe
                    src={`${getMediaUrl(concept.file_url)}#toolbar=0`}
                    className="w-full h-150 border-none bg-white"
                    title="PDF Viewer"
                  />
                )}
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
