"use client";

import { FileText, Video, Calendar, ArrowRight, Trash2 } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { DocumentItem } from "@/types/document";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { useTranslation } from "@/hooks/use-translation";

interface DocumentCardProps {
  document: DocumentItem;
  onDelete?: (id: number) => void;
}

export function DocumentCard({ document, onDelete }: DocumentCardProps) {
  const { t } = useTranslation();
  const isVideo = document.file_type === "video";
  const Icon = isVideo ? Video : FileText;

  // Format date safely
  const formattedDate = new Date(document.uploaded_at).toLocaleDateString(
    undefined,
    {
      year: "numeric",
      month: "short",
      day: "numeric",
    },
  );

  return (
    <Card className="group hover:border-primary/50 transition-all duration-300 relative overflow-hidden">
      <div className="absolute top-0 left-0 w-1 h-full bg-primary/80 scale-y-0 group-hover:scale-y-100 transition-transform origin-top duration-300" />

      <CardContent className="p-5">
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-start gap-4 flex-1 overflow-hidden">
            <div
              className={`p-3 rounded-lg shrink-0 ${isVideo ? "bg-blue-500/10 text-blue-500" : "bg-orange-500/10 text-orange-500"}`}
            >
              <Icon className="w-6 h-6" />
            </div>

            <div className="flex-1 min-w-0">
              <h4
                className="font-semibold text-foreground truncate"
                title={document.title}
              >
                {document.title}
              </h4>
              <div className="flex items-center gap-3 mt-1.5 text-xs text-muted-foreground">
                <span className="flex items-center gap-1">
                  <Calendar className="w-3 h-3" />
                  {formattedDate}
                </span>
                <span className="px-2 py-0.5 rounded-full bg-secondary text-secondary-foreground font-medium text-[10px] uppercase">
                  {document.file_type}
                </span>

                {/* Add real-time visual feedback for background ML tasks */}
                {document.status === "completed" && (
                  <span className="text-green-600 font-medium flex items-center gap-1">
                    ✓ {t.documents.processingStatus}
                  </span>
                )}
                {document.status === "processing" && (
                  <span className="text-primary font-medium flex items-center gap-1">
                    <span className="w-3 h-3 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                    Processing...
                  </span>
                )}
                {document.status === "failed" && (
                  <span className="text-destructive font-medium flex items-center gap-1">
                    ✗ Failed
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-2 shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">
            <Button
              variant="ghost"
              size="icon-sm"
              className="text-destructive hover:text-destructive hover:bg-destructive/10"
              onClick={() => onDelete?.(document.id)}
            >
              <Trash2 className="w-4 h-4" />
            </Button>
            <Link href={`/graph/${document.id}`}>
              <Button size="sm" className="gap-1.5">
                Graph
                <ArrowRight className="w-3.5 h-3.5" />
              </Button>
            </Link>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
