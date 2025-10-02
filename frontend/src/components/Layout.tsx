// src/components/Layout.tsx
import { Navigation } from "./Navigation";
import { Footer } from "./Footer";
import { SearchBar } from "./SearchBar";
import type { ReactNode } from "react";

export function Layout({ children }: { children: ReactNode }) {
    return (
        <div className="flex flex-col min-h-screen">
            {/* Header cố định với Navigation + SearchBar */}
            <header className="bg-white shadow fixed top-0 left-0 w-full z-50">
                <div className="container mx-auto px-6 py-4">
                    {/* Logo + Navigation */}
                    <div className="flex justify-between items-center mb-4">
                        <h1 className="text-xl font-bold text-gray-800">NEROMIND</h1>
                        <Navigation />
                    </div>

                    {/* SearchBar luôn hiện trong header */}
                    <SearchBar />
                </div>
            </header>

            {/* Main content (có padding-top để không bị header che) */}
            <main className="flex-1 pt-40">{children}</main>

            {/* Footer luôn ở cuối */}
            <Footer />
        </div>
    );
}