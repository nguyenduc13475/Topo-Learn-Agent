"use client";

import { useTranslation } from "@/hooks/use-translation";

export default function DashboardPage() {
  const { t } = useTranslation();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-foreground">
          {t.sidebar.dashboard}
        </h1>
        <p className="text-muted-foreground mt-2">
          Chào mừng trở lại! Dưới đây là tổng quan tiến trình học thuật của bạn.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        {/* Statistic Cards Mockup */}
        <div className="p-6 bg-card rounded-xl border border-border shadow-sm">
          <h3 className="font-medium text-sm text-muted-foreground">
            Tài liệu đã phân tích
          </h3>
          <p className="text-3xl font-bold mt-2">12</p>
        </div>
        <div className="p-6 bg-card rounded-xl border border-border shadow-sm">
          <h3 className="font-medium text-sm text-muted-foreground">
            Khái niệm đang ôn tập (SM-2)
          </h3>
          <p className="text-3xl font-bold mt-2 text-primary">156</p>
        </div>
        <div className="p-6 bg-card rounded-xl border border-border shadow-sm">
          <h3 className="font-medium text-sm text-muted-foreground">
            Điểm số trung bình
          </h3>
          <p className="text-3xl font-bold mt-2 text-green-600">4.2/5.0</p>
        </div>
      </div>
    </div>
  );
}
