"use client";

import { useState, useEffect } from "react";
import { useTranslation } from "@/hooks/use-translation";
import { UploadZone } from "@/features/document-upload/components/UploadZone";
import { DocumentCard } from "@/features/document-upload/components/DocumentCard";
import { DocumentItem } from "@/types/document";
import { apiClient } from "@/lib/api-client";
import { useAppWebSocket } from "@/hooks/use-websocket";
import { toast } from "sonner";

export default function DocumentsPage() {
  const { t } = useTranslation();
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  const fetchDocuments = async () => {
    try {
      const docs = await apiClient<DocumentItem[]>("/documents/");
      setDocuments(docs);
    } catch (error) {
      console.error("Failed to fetch documents", error);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  // CATCH EVENTS FROM WEBSOCKETS DIRECTLY VIA CALLBACK TO AVOID CASCADING RENDERS
  useAppWebSocket((message) => {
    if (message.event === "DOCUMENT_STATUS_UPDATED") {
      const { document_id, status } = message.payload;
      setDocuments((prevDocs) =>
        prevDocs.map((doc) =>
          doc.id === document_id ? { ...doc, status: status } : doc,
        ),
      );
    }
  });

  const handleFileUpload = async (file: File) => {
    setIsUploading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await apiClient<DocumentItem>("/documents/upload", {
        method: "POST",
        body: formData,
      });
      setDocuments([response, ...documents]);
    } catch (error) {
      console.error("[DocumentsPage] Upload failed", error);
      toast.error("Failed to upload document. Please try again.");
    } finally {
      setIsUploading(false);
    }
  };

  const handleDeleteDocument = async (id: number) => {
    try {
      await apiClient(`/documents/${id}`, { method: "DELETE" });
      setDocuments(documents.filter((doc) => doc.id !== id));
    } catch (error) {
      console.error("Failed to delete", error);
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-foreground">
          {t.documents.title}
        </h1>
        <p className="text-muted-foreground mt-2">{t.documents.subtitle}</p>
      </div>

      <section>
        <UploadZone
          onUploadSuccess={handleFileUpload}
          isUploading={isUploading}
        />
      </section>

      <section className="space-y-4">
        <h2 className="text-xl font-semibold tracking-tight text-foreground">
          {t.documents.recentUploads}
        </h2>
        {documents.length === 0 ? (
          <div className="text-center py-12 border border-dashed border-border rounded-xl bg-secondary/30">
            <p className="text-muted-foreground">{t.documents.emptyState}</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {documents.map((doc) => (
              <DocumentCard
                key={doc.id}
                document={doc}
                onDelete={handleDeleteDocument}
              />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
