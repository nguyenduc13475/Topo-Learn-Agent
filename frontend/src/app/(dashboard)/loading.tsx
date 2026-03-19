import { Loader2 } from "lucide-react";

export default function DashboardLoading() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] w-full">
      <div className="flex flex-col items-center gap-4 animate-pulse">
        <Loader2 className="w-10 h-10 animate-spin text-primary" />
        <p className="text-muted-foreground font-medium text-lg">
          Loading content...
        </p>
      </div>
    </div>
  );
}
