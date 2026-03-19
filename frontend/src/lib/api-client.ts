import { useAuth } from "@/hooks/use-auth";
import { toast } from "sonner";

const BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {},
): Promise<T> {
  // Get token directly from Zustand store
  const { token, logout } = useAuth.getState();

  // Use the native Headers API to gracefully handle all TS HeadersInit types
  const headers = new Headers(options.headers);

  // Don't set Content-Type to application/json if sending FormData
  const isFormData = options.body instanceof FormData;
  if (!headers.has("Content-Type") && !isFormData) {
    headers.set("Content-Type", "application/json");
  }

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const config: RequestInit = {
    ...options,
    headers,
  };

  try {
    console.log(`[ApiClient] Making request to: ${endpoint}`);
    const response = await fetch(`${BASE_URL}${endpoint}`, config);

    // Handle globally unauthorized response (Token expired or invalid)
    if (response.status === 401) {
      console.warn(
        "[ApiClient] Unauthorized! Token expired or invalid. Logging out...",
      );
      logout();
      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }
      return Promise.reject(
        new Error("Unauthorized session. Please log in again."),
      );
    }

    // Attempt to parse JSON response
    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      const errorMessage =
        data.detail || data.message || "An unexpected error occurred.";
      console.error(`[ApiClient] Error Response (${response.status}):`, data);

      // Globally trigger a toast notification for all failed API calls
      toast.error(errorMessage);
      throw new Error(errorMessage);
    }

    return data as T;
  } catch (error) {
    console.error(
      `[ApiClient] Network or parsing error for ${endpoint}:`,
      error,
    );

    // Catch fetch failures (e.g., server down, CORS issues)
    if (error instanceof TypeError && error.message.includes("fetch")) {
      toast.error("Network error. Could not connect to the server.");
    }
    throw error;
  }
}
