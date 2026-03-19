"use client";

import { ReactNode } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface StatCardProps {
  title: string;
  value: string | number;
  icon: ReactNode;
  trend?: string;
  trendUp?: boolean;
  className?: string;
}

export function StatCard({
  title,
  value,
  icon,
  trend,
  trendUp,
  className,
}: StatCardProps) {
  return (
    <Card
      className={cn(
        "overflow-hidden group hover:shadow-md transition-all duration-300 border-border",
        className,
      )}
    >
      <CardContent className="p-6 relative">
        {/* Subtle background gradient on hover */}
        <div className="absolute inset-0 bg-linear-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

        <div className="relative z-10 flex items-center justify-between">
          <div className="space-y-2">
            <p className="text-sm font-medium text-muted-foreground">{title}</p>
            <div className="flex items-baseline gap-2">
              <h3 className="text-3xl font-bold tracking-tight text-foreground">
                {value}
              </h3>
              {trend && (
                <span
                  className={cn(
                    "text-xs font-medium px-2 py-0.5 rounded-full",
                    trendUp
                      ? "bg-green-500/10 text-green-600 dark:text-green-400"
                      : "bg-destructive/10 text-destructive",
                  )}
                >
                  {trend}
                </span>
              )}
            </div>
          </div>
          <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center text-primary group-hover:scale-110 transition-transform duration-300">
            {icon}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
