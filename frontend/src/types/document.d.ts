// [Document Domain Types] Matches backend schema DocumentResponse
export interface DocumentItem {
  id: number;
  title: string;
  file_type: "pdf" | "video" | string;
  uploaded_at: string;
  status?: "processing" | "completed" | "failed"; // For UI state handling
  file_url?: string;
}
