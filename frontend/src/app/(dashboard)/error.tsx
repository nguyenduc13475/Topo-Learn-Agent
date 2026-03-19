"use client";

import { useEffect } from "react";
import { AlertCircle, RefreshCcw } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function DashboardError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("[Dashboard Boundary Caught Error]:", error);
  }, [error]);

  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center space-y-4 animate-in fade-in zoom-in-95">
      <div className="w-16 h-16 bg-destructive/10 rounded-full flex items-center justify-center mb-2">
        <AlertCircle className="w-8 h-8 text-destructive" />
      </div>
      <h2 className="text-2xl font-bold tracking-tight text-foreground">
        Something went wrong!
      </h2>
      <p className="text-muted-foreground max-w-md">
        An unexpected error occurred while loading this section. You can try
        reloading the page or returning to the dashboard.
      </p>
      <div className="flex gap-4 mt-6">
        <Button onClick={() => reset()} className="gap-2">
          <RefreshCcw className="w-4 h-4" /> Try again
        </Button>
      </div>
    </div>
  );
}
