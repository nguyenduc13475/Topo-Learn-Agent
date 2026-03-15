import { useUIStore } from "@/store/useUIStore";
import { dictionaries } from "@/lib/i18n/dictionaries";

export function useTranslation() {
  const language = useUIStore((state) => state.language);

  // Fallback to English if something goes wrong, though 'vi' is default in store
  const t = dictionaries[language] || dictionaries.en;

  return { t, language };
}
