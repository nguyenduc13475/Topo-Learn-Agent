"use client";

import { Menu, Globe } from "lucide-react";
import { useUIStore, Language } from "@/store/useUIStore";
import { useTranslation } from "@/hooks/use-translation";

export function Topbar() {
  const toggleSidebar = useUIStore((state) => state.toggleSidebar);
  const setLanguage = useUIStore((state) => state.setLanguage);
  const { language, t } = useTranslation();

  const handleLanguageToggle = () => {
    const newLang: Language = language === "vi" ? "en" : "vi";
    setLanguage(newLang);
  };

  return (
    <header className="h-16 bg-background border-b border-border flex items-center justify-between px-4 lg:px-6 sticky top-0 z-10 shadow-sm">
      <div className="flex items-center gap-4">
        <button
          onClick={toggleSidebar}
          className="p-2 rounded-md hover:bg-secondary text-muted-foreground hover:text-foreground transition-colors focus:outline-none focus:ring-2 focus:ring-primary/50"
          aria-label="Toggle Sidebar"
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Mock Search Bar for visual completeness */}
        <div className="hidden md:flex items-center bg-secondary rounded-md px-3 py-1.5 w-64 border border-transparent focus-within:border-primary/50 focus-within:ring-1 focus-within:ring-primary/50 transition-all">
          <input
            type="text"
            placeholder={t.topbar.searchPlaceholder}
            className="bg-transparent border-none outline-none text-sm w-full text-foreground placeholder:text-muted-foreground"
          />
        </div>
      </div>

      <div className="flex items-center gap-3">
        {/* Language Switcher */}
        <button
          onClick={handleLanguageToggle}
          className="flex items-center gap-2 p-2 rounded-md hover:bg-secondary text-sm font-medium transition-colors"
          title={t.topbar.language}
        >
          <Globe className="w-4 h-4 text-muted-foreground" />
          <span className="uppercase">{language}</span>
        </button>

        {/* Mock Profile Avatar */}
        <div className="w-9 h-9 rounded-full bg-primary/20 flex items-center justify-center text-primary font-bold text-sm cursor-pointer hover:bg-primary/30 transition-colors">
          VD
        </div>
      </div>
    </header>
  );
}
