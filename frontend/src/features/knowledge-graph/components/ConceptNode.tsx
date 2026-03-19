"use client";

import { Handle, Position } from "@xyflow/react";
import { CheckCircle2, Lock, PlayCircle } from "lucide-react";
import { cn } from "@/lib/utils";

export interface ConceptNodeData {
  label: string;
  status: "completed" | "current" | "locked";
}

export function ConceptNode({ data }: { data: ConceptNodeData }) {
  console.log(
    `[ConceptNode] Rendering node: ${data.label} with status: ${data.status}`,
  );

  const isCompleted = data.status === "completed";
  const isCurrent = data.status === "current";
  const isLocked = data.status === "locked";

  return (
    <div
      className={cn(
        "px-4 py-3 shadow-md rounded-xl border-2 bg-card min-w-45 transition-all group",
        isCompleted && "border-green-500/50 hover:border-green-500",
        isCurrent && "border-primary shadow-primary/20 hover:shadow-primary/40",
        isLocked &&
          "border-border opacity-60 grayscale hover:grayscale-0 hover:opacity-100",
      )}
    >
      {/* Incoming edge connection point */}
      <Handle
        type="target"
        position={Position.Top}
        className="w-3 h-3 border-2 border-background bg-muted-foreground/50"
      />

      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          {isCompleted && <CheckCircle2 className="w-5 h-5 text-green-500" />}
          {isCurrent && (
            <PlayCircle className="w-5 h-5 text-primary animate-pulse" />
          )}
          {isLocked && <Lock className="w-4 h-4 text-muted-foreground" />}
          <span
            className={cn(
              "font-semibold text-sm",
              isCompleted && "text-foreground",
              isCurrent && "text-primary",
              isLocked && "text-muted-foreground",
            )}
          >
            {data.label}
          </span>
        </div>
      </div>

      {/* Outgoing edge connection point */}
      <Handle
        type="source"
        position={Position.Bottom}
        className="w-3 h-3 border-2 border-background bg-muted-foreground/50"
      />
    </div>
  );
}
