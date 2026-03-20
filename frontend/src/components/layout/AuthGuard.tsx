"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";
import { useAuth } from "@/hooks/use-auth";

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
