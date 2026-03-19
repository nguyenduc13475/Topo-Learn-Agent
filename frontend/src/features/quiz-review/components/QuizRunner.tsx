"use client";

import { useState } from "react";
import {
  CheckCircle2,
  XCircle,
  ArrowRight,
  ArrowLeft,
  RefreshCw,
  Trophy,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useTranslation } from "@/hooks/use-translation";
import {
  QuizQuestion,
  AnswerSubmission,
  QuizResultResponse,
} from "@/types/quiz";
import { cn } from "@/lib/utils";
import { apiClient } from "@/lib/api-client";
import { toast } from "sonner";

interface QuizRunnerProps {
  conceptId: number;
  questions: QuizQuestion[];
  onComplete?: (result: QuizResultResponse) => void;
  onBackToLearning: () => void;
}

export function QuizRunner({
  conceptId,
  questions,
  onComplete,
  onBackToLearning,
}: QuizRunnerProps) {
  const { t } = useTranslation();
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState<
    Record<number, string>
  >({});
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [finalScore, setFinalScore] = useState(0);
  const [isReviewing, setIsReviewing] = useState(false);

  const currentQuestion = questions[currentIndex];
  const totalQuestions = questions.length;
  const progress = ((currentIndex + 1) / totalQuestions) * 100;

  const handleSelectOption = (option: string) => {
    if (isSubmitted) return;
    setSelectedAnswers((prev) => ({
      ...prev,
      [currentIndex]: option,
    }));
  };

  const handleNext = () => {
    if (currentIndex < totalQuestions - 1) {
      setCurrentIndex((prev) => prev + 1);
    }
  };

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex((prev) => prev - 1);
    }
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);

    const submissions: AnswerSubmission[] = questions.map((q, idx) => ({
      question: q.question,
      user_answer: selectedAnswers[idx] || "",
      correct_answer: q.correct_answer,
    }));

    try {
      const result = await apiClient<QuizResultResponse>("/quiz/submit", {
        method: "POST",
        body: JSON.stringify({
          concept_id: conceptId,
          answers: submissions,
        }),
      });

      setFinalScore(result.score_assigned);
      setIsSubmitted(true);
      setCurrentIndex(0);

      if (onComplete) onComplete(result);
      console.log(
        "[QuizRunner] Submission complete. Real Score:",
        result.score_assigned,
      );
    } catch (error) {
      console.error("[QuizRunner] Submission failed", error);
      toast.error(
        "Failed to submit quiz results. Please check your connection.",
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const allAnswered = Object.keys(selectedAnswers).length === totalQuestions;

  // Render Result Header if submitted
  if (isSubmitted && !isReviewing && currentIndex === 0 && finalScore >= 0) {
    return (
      <div className="space-y-6 animate-in fade-in duration-500">
        <Card className="border-primary/20 bg-primary/5 text-center py-8 shadow-sm">
          <div className="flex justify-center mb-4">
            <div className="w-16 h-16 rounded-full bg-primary/20 flex items-center justify-center">
              <Trophy className="w-8 h-8 text-primary" />
            </div>
          </div>
          <CardTitle className="text-2xl mb-2">{t.quiz.scoreTitle}</CardTitle>
          <p className="text-muted-foreground mb-6 max-w-md mx-auto">
            {t.quiz.scoreDesc}
          </p>

          <div className="flex justify-center gap-8 mb-8">
            <div className="text-center">
              <p className="text-sm text-muted-foreground font-medium uppercase tracking-wider mb-1">
                SM-2 Score
              </p>
              <p className="text-3xl font-bold text-foreground">
                {finalScore}{" "}
                <span className="text-lg text-muted-foreground">/ 5</span>
              </p>
            </div>
            <div className="w-px bg-border"></div>
            <div className="text-center">
              <p className="text-sm text-muted-foreground font-medium uppercase tracking-wider mb-1">
                Accuracy
              </p>
              <p className="text-3xl font-bold text-foreground">
                {
                  Object.values(selectedAnswers).filter(
                    (ans, idx) => ans === questions[idx].correct_answer,
                  ).length
                }
                <span className="text-lg text-muted-foreground">
                  {" "}
                  / {totalQuestions}
                </span>
              </p>
            </div>
          </div>

          <div className="flex justify-center gap-4">
            <Button variant="outline" onClick={onBackToLearning}>
              {t.quiz.backToLearning}
            </Button>
            <Button className="gap-2" onClick={() => setIsReviewing(true)}>
              Review Answers <ArrowRight className="w-4 h-4" />
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  if (isSubmitted && isReviewing) {
    return (
      <div className="space-y-6 animate-in fade-in duration-500">
        <div className="flex items-center justify-between">
          <h3 className="text-xl font-bold text-foreground">Review Answers</h3>
          <Button variant="outline" size="sm" onClick={onBackToLearning}>
            {t.quiz.backToLearning}
          </Button>
        </div>

        {/* Render all questions for review */}
        <div className="space-y-6">
          {questions.map((q, idx) => {
            const userAnswer = selectedAnswers[idx];
            const isCorrect = userAnswer === q.correct_answer;

            return (
              <Card
                key={idx}
                className={cn(
                  "border-l-4",
                  isCorrect ? "border-l-green-500" : "border-l-destructive",
                )}
              >
                <CardHeader className="pb-3">
                  <div className="flex items-start gap-3">
                    {isCorrect ? (
                      <CheckCircle2 className="w-6 h-6 text-green-500 shrink-0" />
                    ) : (
                      <XCircle className="w-6 h-6 text-destructive shrink-0" />
                    )}
                    <div>
                      <h4 className="font-medium text-foreground">
                        {q.question}
                      </h4>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid gap-2 pl-9">
                    {q.options.map((opt, oIdx) => {
                      const isSelected = userAnswer === opt;
                      const isActualCorrect = opt === q.correct_answer;

                      let optClass =
                        "border border-border bg-secondary/20 opacity-50";
                      if (isActualCorrect)
                        optClass =
                          "border-green-500 bg-green-500/10 text-green-700 dark:text-green-400 font-medium";
                      else if (isSelected && !isCorrect)
                        optClass =
                          "border-destructive bg-destructive/10 text-destructive font-medium";

                      return (
                        <div
                          key={oIdx}
                          className={cn(
                            "px-4 py-2.5 rounded-lg text-sm",
                            optClass,
                          )}
                        >
                          {opt}
                        </div>
                      );
                    })}
                  </div>

                  <div className="pl-9 mt-4">
                    <div className="bg-primary/5 border border-primary/20 rounded-lg p-4 text-sm text-muted-foreground">
                      <span className="font-semibold text-foreground mr-2">
                        {t.quiz.explanation}:
                      </span>
                      {q.explanation}
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </div>
    );
  }

  // Render Active Quiz
  return (
    <Card className="max-w-3xl mx-auto border-border shadow-sm overflow-hidden animate-in slide-in-from-bottom-4 duration-500">
      {/* Progress Bar */}
      <div className="w-full bg-secondary h-1.5">
        <div
          className="bg-primary h-full transition-all duration-300 ease-out"
          style={{ width: `${progress}%` }}
        />
      </div>

      <CardHeader className="pt-8 pb-6 text-center">
        <p className="text-sm font-medium text-muted-foreground uppercase tracking-widest mb-2">
          {t.quiz.question} {currentIndex + 1} / {totalQuestions}
        </p>
        <CardTitle className="text-2xl font-semibold leading-relaxed text-foreground">
          {currentQuestion.question}
        </CardTitle>
      </CardHeader>

      <CardContent className="px-8 pb-8">
        <div className="grid gap-3">
          {currentQuestion.options.map((option, idx) => {
            const isSelected = selectedAnswers[currentIndex] === option;
            return (
              <button
                key={idx}
                onClick={() => handleSelectOption(option)}
                className={cn(
                  "w-full text-left px-5 py-4 rounded-xl border-2 transition-all duration-200 text-[15px]",
                  isSelected
                    ? "border-primary bg-primary/5 text-primary font-medium shadow-sm"
                    : "border-border bg-card hover:border-primary/40 hover:bg-secondary/50 text-foreground",
                )}
              >
                <div className="flex items-center gap-3">
                  <div
                    className={cn(
                      "w-5 h-5 rounded-full border-2 flex items-center justify-center shrink-0 transition-colors",
                      isSelected ? "border-primary" : "border-muted-foreground",
                    )}
                  >
                    {isSelected && (
                      <div className="w-2.5 h-2.5 bg-primary rounded-full" />
                    )}
                  </div>
                  {option}
                </div>
              </button>
            );
          })}
        </div>
      </CardContent>

      <CardFooter className="px-8 py-4 bg-secondary/30 border-t border-border flex items-center justify-between">
        <Button
          variant="outline"
          onClick={handlePrevious}
          disabled={currentIndex === 0 || isSubmitting}
          className="gap-2"
        >
          <ArrowLeft className="w-4 h-4" /> {t.quiz.previous}
        </Button>

        {currentIndex === totalQuestions - 1 ? (
          <Button
            onClick={handleSubmit}
            disabled={!allAnswered || isSubmitting}
            className="gap-2"
          >
            {isSubmitting ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />{" "}
                {t.quiz.submitting}
              </>
            ) : (
              <>
                {t.quiz.submit} <CheckCircle2 className="w-4 h-4" />
              </>
            )}
          </Button>
        ) : (
          <Button
            onClick={handleNext}
            disabled={!selectedAnswers[currentIndex]}
            className="gap-2"
          >
            {t.quiz.next} <ArrowRight className="w-4 h-4" />
          </Button>
        )}
      </CardFooter>
    </Card>
  );
}
