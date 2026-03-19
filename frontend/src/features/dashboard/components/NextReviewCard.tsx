"use client";

import { useRouter } from "next/navigation";
import { BrainCircuit, ArrowRight, Clock } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useTranslation } from "@/hooks/use-translation";

interface NextReviewCardProps {
  conceptId: number;
  conceptName: string;
  documentName: string;
}

export function NextReviewCard({
  conceptId,
  conceptName,
  documentName,
}: NextReviewCardProps) {
  const router = useRouter();
  const { t } = useTranslation();

  const handleStartLearning = () => {
    console.log(
      `[NextReviewCard] Navigating to learn concept ID: ${conceptId}`,
    );
    router.push(`/learn/${conceptId}`);
  };

  return (
    <Card className="relative overflow-hidden border-primary/20 bg-card shadow-md">
      {/* Decorative Background Elements */}
      <div className="absolute -right-20 -top-20 w-64 h-64 bg-primary/5 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute -left-10 -bottom-10 w-40 h-40 bg-blue-500/5 rounded-full blur-2xl pointer-events-none" />

      <CardContent className="p-8 relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div className="flex items-start gap-4">
          <div className="w-14 h-14 rounded-2xl bg-primary/10 flex items-center justify-center text-primary shrink-0 mt-1">
            <BrainCircuit className="w-7 h-7" />
          </div>
          <div className="space-y-1.5">
            <div className="flex items-center gap-2">
              <h3 className="text-xl font-bold text-foreground">
                {t.dashboard.nextReview.title}
              </h3>
              <span className="flex items-center gap-1 text-[10px] uppercase tracking-wider font-semibold text-orange-500 bg-orange-500/10 px-2 py-0.5 rounded-full">
                <Clock className="w-3 h-3" /> Due Now
              </span>
            </div>
            <p className="text-sm text-muted-foreground max-w-xl leading-relaxed">
              {t.dashboard.nextReview.subtitle}
            </p>

            {/* Concept Info */}
            <div className="mt-4 p-4 rounded-xl bg-secondary/50 border border-border inline-block min-w-full md:min-w-100">
              <p className="text-xs text-muted-foreground uppercase tracking-wider font-medium mb-1">
                {documentName}
              </p>
              <p className="text-lg font-semibold text-foreground">
                {conceptName}
              </p>
            </div>
          </div>
        </div>

        <div className="w-full md:w-auto mt-4 md:mt-0">
          <Button
            size="lg"
            className="w-full md:w-auto shadow-lg shadow-primary/20 gap-2 text-base px-8"
            onClick={handleStartLearning}
          >
            {t.dashboard.nextReview.startLearning}
            <ArrowRight className="w-5 h-5" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
