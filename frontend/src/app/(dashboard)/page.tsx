"use client";

import { useEffect, useState } from "react";
import { FileText, Layers, Target, Flame } from "lucide-react";
import { useTranslation } from "@/hooks/use-translation";
import { StatCard } from "@/features/dashboard/components/StatCard";
import { NextReviewCard } from "@/features/dashboard/components/NextReviewCard";
import { apiClient } from "@/lib/api-client";
import { Loader2 } from "lucide-react";

interface DashboardStats {
  analyzed_docs: number;
  review_concepts: number;
  average_score: string;
  learning_streak: string;
  next_concept: { id: number | null; name: string; document_name: string };
}

export default function DashboardPage() {
  const { t } = useTranslation();
  const [stats, setStats] = useState<DashboardStats | null>(null);

  useEffect(() => {
    apiClient<DashboardStats>("/dashboard/summary")
      .then(setStats)
      .catch((e) => console.error("Failed to load dashboard stats", e));
  }, []);

  if (!stats) {
    return (
      <div className="flex h-[50vh] items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500 pb-10">
      {/* Header Section */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-foreground">
          {t.dashboard.welcome}
        </h1>
        <p className="text-muted-foreground mt-2 text-lg">
          {t.dashboard.subtitle}
        </p>
      </div>

      {/* Main Call to Action: Next Concept to Review based on SM-2 */}
      {stats.next_concept.id !== null && (
        <section>
          <NextReviewCard
            conceptId={stats.next_concept.id as number}
            conceptName={stats.next_concept.name}
            documentName={stats.next_concept.document_name}
          />
        </section>
      )}

      {/* Statistics Grid */}
      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title={t.dashboard.stats.analyzedDocs}
          value={stats.analyzed_docs}
          icon={<FileText className="w-6 h-6" />}
        />
        <StatCard
          title={t.dashboard.stats.reviewConcepts}
          value={stats.review_concepts}
          icon={<Layers className="w-6 h-6" />}
        />
        <StatCard
          title={t.dashboard.stats.averageScore}
          value={`${stats.average_score}/5.0`}
          icon={<Target className="w-6 h-6" />}
        />
        <StatCard
          title={t.dashboard.stats.learningStreak}
          value={`${stats.learning_streak} Days`}
          icon={<Flame className="w-6 h-6 text-orange-500" />}
          className="border-orange-500/20"
        />
      </section>

      {/* Placeholder for Recent Activity/Logs (Optional extension later) */}
      <section className="pt-4">
        <h2 className="text-xl font-semibold tracking-tight text-foreground mb-4">
          {t.dashboard.recentActivity}
        </h2>
        <div className="border border-dashed border-border rounded-xl p-8 text-center bg-secondary/20">
          <p className="text-muted-foreground">
            No recent activity to show yet.
          </p>
        </div>
      </section>
    </div>
  );
}
