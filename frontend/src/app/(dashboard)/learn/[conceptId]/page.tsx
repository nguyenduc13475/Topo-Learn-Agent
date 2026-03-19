"use client";

import { use, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowRight, ChevronLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useTranslation } from "@/hooks/use-translation";
import { ConceptViewer } from "@/features/learning/components/ConceptViewer";
import { TutorChatBox } from "@/features/learning/components/TutorChatBox";
import { Concept } from "@/types/graph";
import { useLearnStore } from "@/store/useLearnStore";
import { apiClient } from "@/lib/api-client";

export default function LearnConceptPage({
  params,
}: {
  params: Promise<{ conceptId: string }>;
}) {
  const router = useRouter();
  const { t } = useTranslation();
  const clearChat = useLearnStore((state) => state.clearChat);
  const resolvedParams = use(params);

  const [concept, setConcept] = useState<Concept | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchConcept = async () => {
      try {
        const data = await apiClient<Concept>(
          `/graph/concepts/${resolvedParams.conceptId}`,
        );
        setConcept(data);
      } catch (error) {
        console.error("Failed to load concept", error);
      } finally {
        setLoading(false);
      }
    };
    fetchConcept();
    return () => clearChat();
  }, [resolvedParams.conceptId, clearChat]);

  if (loading || !concept) {
    return (
      <div className="flex h-[60vh] items-center justify-center">
        <div className="animate-pulse flex flex-col items-center gap-4">
          <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
          <p className="text-muted-foreground font-medium">
            {t.common.loading}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-6xl mx-auto pb-10">
      <div className="flex items-center justify-between">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.back()}
          className="text-muted-foreground"
        >
          <ChevronLeft className="w-4 h-4 mr-1" /> Back
        </Button>
        <Button
          onClick={() => router.push(`/quiz/${concept.id}`)}
          className="gap-2 shadow-md"
        >
          {t.learning.takeQuiz} <ArrowRight className="w-4 h-4" />
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        <div className="lg:col-span-7 space-y-6">
          <ConceptViewer concept={concept} />
        </div>
        <div className="lg:col-span-5 relative">
          <div className="sticky top-24">
            <TutorChatBox conceptId={concept.id} />
          </div>
        </div>
      </div>
    </div>
  );
}
