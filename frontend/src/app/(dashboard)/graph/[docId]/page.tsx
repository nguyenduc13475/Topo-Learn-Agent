"use client";

import { use, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ChevronLeft, Loader2, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useTranslation } from "@/hooks/use-translation";
import { FlowCanvas } from "@/features/knowledge-graph/components/FlowCanvas";
import { apiClient } from "@/lib/api-client";
import { useAppWebSocket } from "@/hooks/use-websocket";
import { toast } from "sonner";

export default function KnowledgeGraphPage({
  params,
}: {
  params: Promise<{ docId: string }>;
}) {
  const router = useRouter();
  const { t } = useTranslation();
  const resolvedParams = use(params);
  const docId = Number(resolvedParams.docId);

  const [graphStatus, setGraphStatus] = useState<string>("pending");
  const [isTriggering, setIsTriggering] = useState(false);

  useEffect(() => {
    const fetchInitialStatus = async () => {
      try {
        const res = await apiClient<{ status: string }>(
          `/graph/${docId}/status`,
        );
        setGraphStatus(res.status);
      } catch (e) {
        console.error("Failed to check initial graph status", e);
      }
    };
    fetchInitialStatus();
  }, [docId]);

  useAppWebSocket((message) => {
    if (
      message.event === "GRAPH_STATUS_UPDATED" &&
      message.payload.document_id === docId
    ) {
      console.log(
        `[GraphPage] WebSocket báo trạng thái mới: ${message.payload.status}`,
      );

      setGraphStatus(message.payload.status);

      if (message.payload.status === "failed") {
        toast.error(`Graph build failed: ${message.payload.error}`);
        setIsTriggering(false);
      }
    }
  });

  const handleTriggerBuild = async () => {
    setIsTriggering(true);
    try {
      await apiClient(`/graph/${docId}/build`, { method: "POST" });
      setGraphStatus("building");
    } catch {
      toast.error(
        "Failed to start graph build. Ensure document processing is complete.",
      );
      setIsTriggering(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] animate-in fade-in duration-500">
      <div className="flex items-center justify-between mb-6 shrink-0">
        <div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => router.push("/documents")}
            className="text-muted-foreground hover:text-foreground mb-2 -ml-2"
          >
            <ChevronLeft className="w-4 h-4 mr-1" />
            {t.graph.backToDocs}
          </Button>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">
            {t.graph.title}
          </h1>
          <p className="text-muted-foreground mt-1">{t.graph.subtitle}</p>
        </div>
      </div>

      {/* Render based on Status */}
      <div className="flex-1 relative rounded-xl overflow-hidden border border-border bg-background shadow-sm">
        {graphStatus === "completed" ? (
          <FlowCanvas documentId={docId} />
        ) : graphStatus === "building" ? (
          <div className="flex flex-col items-center justify-center h-full bg-secondary/10">
            <Loader2 className="w-10 h-10 animate-spin text-primary mb-4" />
            <h3 className="text-xl font-semibold">
              AI is Mapping Knowledge...
            </h3>
            <p className="text-muted-foreground mt-2 max-w-sm text-center">
              We are analyzing the document and building the dependency tree.
              This may take a minute.
            </p>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-full bg-secondary/10">
            <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-4">
              <Sparkles className="w-8 h-8 text-primary" />
            </div>
            <h3 className="text-xl font-semibold mb-2">
              Knowledge Graph not built yet
            </h3>
            <p className="text-muted-foreground mb-6 max-w-md text-center">
              Generate an interactive learning map to unlock smart study paths
              and prerequisites.
            </p>
            <Button
              onClick={handleTriggerBuild}
              disabled={isTriggering}
              className="gap-2 px-8"
            >
              {isTriggering ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Sparkles className="w-4 h-4" />
              )}
              Build Graph Now
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
