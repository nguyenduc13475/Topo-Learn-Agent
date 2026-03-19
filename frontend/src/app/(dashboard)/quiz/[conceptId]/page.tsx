"use client";

import { use, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ChevronLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useTranslation } from "@/hooks/use-translation";
import { QuizRunner } from "@/features/quiz-review/components/QuizRunner";
import { QuizQuestion } from "@/types/quiz";
import { apiClient } from "@/lib/api-client";

export default function QuizPage({
  params,
}: {
  params: Promise<{ conceptId: string }>;
}) {
  const router = useRouter();
  const { t } = useTranslation();
  const resolvedParams = use(params);
  const [questions, setQuestions] = useState<QuizQuestion[] | null>(null);

  useEffect(() => {
    const fetchQuiz = async () => {
      try {
        const data = await apiClient<QuizQuestion[]>(
          `/quiz/${resolvedParams.conceptId}/generate`,
        );
        setQuestions(data);
      } catch (error) {
        console.error("Failed to generate quiz", error);
        alert("Failed to generate quiz. Check server logs.");
      }
    };
    fetchQuiz();
  }, [resolvedParams.conceptId]);

  const handleBackToLearning = () => {
    router.push(`/learn/${resolvedParams.conceptId}`);
  };

  if (!questions) {
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

  if (questions.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-[60vh] space-y-4 text-center animate-in fade-in zoom-in-95">
        <h2 className="text-2xl font-bold text-foreground">
          No Questions Generated
        </h2>
        <p className="text-muted-foreground max-w-md">
          The AI couldn&apos;t generate a quiz for this specific concept based
          on the current context. Please try reviewing the material directly.
        </p>
        <Button onClick={handleBackToLearning} className="mt-4">
          <ChevronLeft className="w-4 h-4 mr-2" /> {t.quiz.backToLearning}
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto pb-10">
      <div className="flex items-center justify-between mb-8">
        <div>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleBackToLearning}
            className="text-muted-foreground hover:text-foreground mb-2 -ml-2"
          >
            <ChevronLeft className="w-4 h-4 mr-1" />
            {t.quiz.backToLearning}
          </Button>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">
            {t.quiz.title}
          </h1>
          <p className="text-muted-foreground mt-1">{t.quiz.subtitle}</p>
        </div>
      </div>

      <QuizRunner
        conceptId={Number(resolvedParams.conceptId)}
        questions={questions}
        onBackToLearning={handleBackToLearning}
        onComplete={(result) => {
          console.log("[QuizPage] Quiz completed, SM-2 result:", result);
        }}
      />
    </div>
  );
}
