"use client";

import { Menu, Globe, Search, Loader2 } from "lucide-react";
import { useUIStore, Language } from "@/store/useUIStore";
import { useTranslation } from "@/hooks/use-translation";
import { useEffect, useState, useRef } from "react";
import { useAuth } from "@/hooks/use-auth";
import { useDebounce } from "@/hooks/use-debounce";
import { apiClient } from "@/lib/api-client";
import { useRouter } from "next/navigation";
import Link from "next/link";

interface SearchResult {
  id: number;
  name: string;
  document_name: string;
  definition_snippet: string;
}

export function Topbar() {
  const toggleSidebar = useUIStore((state) => state.toggleSidebar);
  const setLanguage = useUIStore((state) => state.setLanguage);
  const { language, t } = useTranslation();
  const { user, logout } = useAuth();
  const router = useRouter();

  const [mounted, setMounted] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);

  const searchRef = useRef<HTMLDivElement>(null);
  const debouncedSearch = useDebounce(searchQuery, 400);

  useEffect(() => {
    const timer = setTimeout(() => {
      setMounted(true);
    }, 0);
    return () => clearTimeout(timer);
  }, []);

  // Handle clicking outside of search dropdown
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        searchRef.current &&
        !searchRef.current.contains(event.target as Node)
      ) {
        setShowDropdown(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Execute Search
  useEffect(() => {
    if (debouncedSearch.length >= 2) {
      const timer = setTimeout(() => {
        setIsSearching(true);
      }, 0);

      apiClient<SearchResult[]>(
        `/dashboard/search?q=${encodeURIComponent(debouncedSearch)}`,
      )
        .then((results) => {
          setSearchResults(results);
          setShowDropdown(true);
        })
        .catch((e) => console.error("Search failed", e))
        .finally(() => {
          setIsSearching(false);
        });

      return () => clearTimeout(timer);
    } else {
      const timer = setTimeout(() => {
        setSearchResults([]);
        setShowDropdown(false);
      }, 0);

      return () => clearTimeout(timer);
    }
  }, [debouncedSearch]);

  const handleLanguageToggle = () => {
    const newLang: Language = language === "vi" ? "en" : "vi";
    setLanguage(newLang);
  };

  const getInitials = (name: string) => {
    if (!name) return "U";
    const parts = name.trim().split(" ");
    if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
  };

  return (
    <header className="h-16 bg-background border-b border-border flex items-center justify-between px-4 lg:px-6 sticky top-0 z-50 shadow-sm">
      <div className="flex items-center gap-4 flex-1">
        <button
          onClick={toggleSidebar}
          className="p-2 rounded-md hover:bg-secondary text-muted-foreground hover:text-foreground transition-colors focus:outline-none focus:ring-2 focus:ring-primary/50"
          aria-label="Toggle Sidebar"
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Global Search Bar */}
        <div
          ref={searchRef}
          className="relative hidden md:flex w-full max-w-md"
        >
          <div className="flex items-center bg-secondary rounded-md px-3 py-1.5 w-full border border-transparent focus-within:border-primary/50 focus-within:ring-1 focus-within:ring-primary/50 transition-all">
            <Search className="w-4 h-4 text-muted-foreground mr-2 shrink-0" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onFocus={() => {
                if (searchResults.length > 0) setShowDropdown(true);
              }}
              placeholder={mounted ? t.topbar.searchPlaceholder : "Search..."}
              className="bg-transparent border-none outline-none text-sm w-full text-foreground placeholder:text-muted-foreground"
            />
            {isSearching && (
              <Loader2 className="w-4 h-4 text-primary animate-spin shrink-0" />
            )}
          </div>

          {/* Search Dropdown */}
          {showDropdown && searchResults.length > 0 && (
            <div className="absolute top-full left-0 right-0 mt-2 bg-card border border-border rounded-lg shadow-lg overflow-hidden flex flex-col max-h-100">
              {searchResults.map((result) => (
                <Link
                  key={result.id}
                  href={`/learn/${result.id}`}
                  onClick={() => setShowDropdown(false)}
                  className="px-4 py-3 hover:bg-secondary/50 border-b border-border last:border-0 transition-colors"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-semibold text-sm text-primary">
                      {result.name}
                    </span>
                    <span className="text-[10px] uppercase text-muted-foreground font-medium bg-secondary px-2 py-0.5 rounded-sm">
                      {result.document_name}
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground line-clamp-2">
                    {result.definition_snippet}
                  </p>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="flex items-center gap-3 shrink-0">
        {mounted && (
          <button
            onClick={handleLanguageToggle}
            className="flex items-center gap-2 p-2 rounded-md hover:bg-secondary text-sm font-medium transition-colors"
            title={t.topbar.language}
          >
            <Globe className="w-4 h-4 text-muted-foreground" />
            <span className="uppercase">{language}</span>
          </button>
        )}

        {/* Real Profile Avatar */}
        <div
          className="w-9 h-9 rounded-full bg-primary/20 flex items-center justify-center text-primary font-bold text-sm cursor-pointer hover:bg-primary/30 transition-colors relative group"
          title={user?.full_name || t.topbar.profile}
        >
          {mounted && user ? getInitials(user.full_name) : "U"}

          {/* Simple Hover Logout Menu */}
          <div className="absolute top-full right-0 mt-2 w-32 bg-card border border-border rounded-md shadow-md opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all">
            <button
              onClick={() => {
                logout();
                router.push("/login");
              }}
              className="w-full text-left px-4 py-2 text-sm text-destructive hover:bg-destructive/10 transition-colors"
            >
              {mounted ? t.topbar.logout : "Logout"}
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
