/**
 * Calculate human-readable time remaining until next review.
 * @param nextReviewDate - ISO string of the next review date from Backend
 * @returns Formatted string (e.g., "Due Now", "In 2 hours", "In 3 days")
 */
export function formatNextReviewDate(nextReviewDate: string): string {
  const now = new Date();
  const reviewDate = new Date(nextReviewDate);
  const diffInHours = (reviewDate.getTime() - now.getTime()) / (1000 * 60 * 60);

  console.log(
    `[SM2Helper] Calculating diff: ${diffInHours.toFixed(2)} hours remaining.`,
  );

  if (diffInHours <= 0) {
    return "Due Now";
  } else if (diffInHours < 24) {
    const hours = Math.ceil(diffInHours);
    return `In ${hours} hour${hours > 1 ? "s" : ""}`;
  } else {
    const diffInDays = Math.ceil(diffInHours / 24);
    return `In ${diffInDays} day${diffInDays > 1 ? "s" : ""}`;
  }
}
