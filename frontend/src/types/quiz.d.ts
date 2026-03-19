// [Quiz & Review Domain Types] Matches backend schemas

export interface QuizQuestion {
  question: string;
  options: string[];
  correct_answer: string;
  explanation: string;
}

export interface AnswerSubmission {
  question: string;
  user_answer: string;
  correct_answer: string;
}

export interface QuizSubmission {
  concept_id: number;
  answers: AnswerSubmission[];
}

export interface QuizResultResponse {
  message: string;
  score_assigned: number;
  sm2_updated: {
    next_review_date: string;
    new_ef: number;
  };
}
