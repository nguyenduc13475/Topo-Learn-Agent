import { create } from "zustand";
import { persist } from "zustand/middleware";

export type Language = "en" | "vi";

interface UIState {
  isSidebarOpen: boolean;
  language: Language;
  toggleSidebar: () => void;
  setLanguage: (lang: Language) => void;
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      isSidebarOpen: true, // Default open on desktop
      language: "vi", // Default language is Vietnamese
      toggleSidebar: () =>
        set((state) => {
          console.log(
            `[UI Store] Toggling sidebar. New state: ${!state.isSidebarOpen}`,
          );
          return { isSidebarOpen: !state.isSidebarOpen };
        }),
      setLanguage: (language) =>
        set(() => {
          console.log(`[UI Store] Language changed to: ${language}`);
          return { language };
        }),
    }),
    {
      name: "topo-ui-storage", // Key for localStorage
      partialize: (state) => ({ language: state.language }), // Only persist language
    },
  ),
);
