// src/contexts/HomeStateContext.tsx
import { createContext, useContext, useState } from "react";
import type { ReactNode } from "react";
import type { Category, Document } from "../types";

interface HomeState {
  categories: Category[];
  searchQuery: string;
  searchResults: Document[];
  isSearching: boolean;
  setCategories: (cats: Category[]) => void;
  setSearchQuery: (q: string) => void;
  setSearchResults: (docs: Document[]) => void;
  setIsSearching: (v: boolean) => void;
}

const HomeStateContext = createContext<HomeState | undefined>(undefined);

export function HomeStateProvider({ children }: { children: ReactNode }) {
  const [categories, setCategories] = useState<Category[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<Document[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  return (
    <HomeStateContext.Provider value={{
      categories,
      searchQuery,
      searchResults,
      isSearching,
      setCategories,
      setSearchQuery,
      setSearchResults,
      setIsSearching
    }}>
      {children}
    </HomeStateContext.Provider>
  );
}

export function useHomeState() {
  const context = useContext(HomeStateContext);
  if (!context) throw new Error("useHomeState must be used inside HomeStateProvider");
  return context;
}
