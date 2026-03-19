"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";
import { create } from "zustand";
import { persist } from "zustand/middleware";
import { apiClient } from "@/lib/api-client";

interface UserProfile {
  id: number;
  email: string;
  full_name: string;
}

interface AuthState {
  token: string | null;
  isAuthenticated: boolean;
  user: UserProfile | null;
  setToken: (token: string) => void;
  fetchUser: () => Promise<void>;
  logout: () => void;
}

export const useAuth = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,
      isAuthenticated: false,
      user: null,

      setToken: (token: string) => {
        set({ token, isAuthenticated: true });
        get().fetchUser();
      },

      fetchUser: async () => {
        try {
          const userData = await apiClient<UserProfile>("/auth/me");
          set({ user: userData });
        } catch (error) {
          console.error("[AuthStore] Failed to fetch user profile", error);
          get().logout();
        }
      },

      logout: () => {
        set({ token: null, isAuthenticated: false, user: null });
      },
    }),
    {
      name: "topo-auth-storage",
    },
  ),
);

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const { token, user, fetchUser } = useAuth();
  const router = useRouter();
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    if (!token) {
      router.push("/login");
    } else if (!user) {
      fetchUser().finally(() => {
        setTimeout(() => setIsChecking(false), 0);
      });
    } else {
      const timer = setTimeout(() => {
        setIsChecking(false);
      }, 0);

      return () => clearTimeout(timer);
    }
  }, [token, user, router, fetchUser]);

  if (isChecking || !token) {
    return (
      <div className="h-screen w-screen flex items-center justify-center bg-secondary/30">
        <Loader2 className="w-10 h-10 animate-spin text-primary" />
      </div>
    );
  }

  return <>{children}</>;
}
