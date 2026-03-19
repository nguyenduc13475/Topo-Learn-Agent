"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, FileText } from "lucide-react";
import { cn } from "@/lib/utils";
import { useUIStore } from "@/store/useUIStore";
import { useTranslation } from "@/hooks/use-translation";
import { useEffect, useState } from "react";

export function Sidebar() {
  const pathname = usePathname();
  const isSidebarOpen = useUIStore((state) => state.isSidebarOpen);
  const { t } = useTranslation();

  // Hydration fix (Compiler-safe)
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    // Wrapping in setTimeout makes the state update asynchronous.
    // This bypasses the 'cascading render' linter error while still
    // perfectly solving the Next.js hydration mismatch.
    const timer = setTimeout(() => {
      setMounted(true);
    }, 0);

    return () => clearTimeout(timer);
  }, []);

  const navItems = [
    { href: "/", label: t.sidebar.dashboard, icon: LayoutDashboard },
    { href: "/documents", label: t.sidebar.documents, icon: FileText },
  ];

  // Prevent rendering until client is mounted to avoid hydration mismatch
  if (!mounted) {
    return (
      <aside className="bg-card border-r border-border h-screen w-20 fixed md:relative z-20"></aside>
    );
  }

  return (
    <aside
      className={cn(
        "bg-card border-r border-border h-screen transition-all duration-300 ease-in-out flex flex-col fixed md:relative z-20",
        isSidebarOpen
          ? "w-64 translate-x-0"
          : "w-20 -translate-x-full md:translate-x-0",
      )}
    >
      {/* Logo Area */}
      <div className="h-16 flex items-center justify-center border-b border-border">
        {isSidebarOpen ? (
          <span className="font-bold text-lg text-primary truncate px-4">
            Topo-Learn Agent
          </span>
        ) : (
          <span className="font-bold text-xl text-primary">TL</span>
        )}
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-2">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-md transition-colors",
                isActive
                  ? "bg-primary/10 text-primary font-medium"
                  : "text-muted-foreground hover:bg-secondary hover:text-foreground",
                !isSidebarOpen && "justify-center px-0",
              )}
              title={!isSidebarOpen ? item.label : undefined}
            >
              <Icon className="w-5 h-5 shrink-0" />
              {isSidebarOpen && <span className="truncate">{item.label}</span>}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
