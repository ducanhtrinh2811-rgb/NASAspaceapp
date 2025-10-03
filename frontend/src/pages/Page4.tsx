// src/pages/Page4.tsx
import { useNavigate, useLocation } from "react-router-dom";
import { useEffect, useState } from "react";
import { SearchBar } from "../components/SearchBar";
import { Navigation } from "../components/Navigation";
import { Footer } from "../components/Footer";
import { BackToTopButton } from "../components/BackToTopButton";
import { ArrowLeft, FileText, Users, AlertCircle } from "lucide-react";
import type { ArticleSummary } from "../types";
import { getArticleSummary } from "../services/ArticleService";

// ✅ Parse content với regex an toàn hơn
function parseContentSections(content: string): { heading: string; items: string[] }[] {
    if (!content || typeof content !== 'string') return [];

    const sections: { heading: string; items: string[] }[] = [];

    // Split by double newline or single newline
    const blocks = content.split(/\n{2,}|\n(?=\*\*)/);

    let currentHeading = '';
    let currentItems: string[] = [];

    for (const block of blocks) {
        const trimmed = block.trim();
        if (!trimmed) continue;

        // Check if line starts with **Heading**
        const headingMatch = trimmed.match(/^\*\*(.+?)\*\*:?\s*/);

        if (headingMatch) {
            // Save previous section
            if (currentHeading || currentItems.length > 0) {
                sections.push({
                    heading: currentHeading,
                    items: currentItems.filter(item => item.trim())
                });
            }

            // Start new section
            currentHeading = headingMatch[1].trim();

            // Get remaining text after heading
            const remainingText = trimmed.substring(headingMatch[0].length).trim();

            // Split by bullet points or newlines
            const items = remainingText
                .split(/\n/)
                .map(line => line.replace(/^-\s*/, '').trim())
                .filter(line => line);

            currentItems = items;
        } else {
            // Text without heading - split into bullet points
            const items = trimmed
                .split(/\n/)
                .map(line => line.replace(/^-\s*/, '').trim())
                .filter(line => line);

            currentItems.push(...items);
        }
    }

    // Save last section
    if (currentHeading || currentItems.length > 0) {
        sections.push({
            heading: currentHeading,
            items: currentItems.filter(item => item.trim())
        });
    }

    // Clean up sections
    return sections
        .filter(s => s.items.length > 0)
        .map(s => ({
            ...s,
            heading: s.heading || 'Overview'
        }));
}

// ✅ Component hiển thị section
function SectionCard({
    title,
    content,
    icon
}: {
    title: string;
    content: string;
    icon?: React.ReactNode;
}) {
    const subsections = parseContentSections(content);

    if (!content || subsections.length === 0) return null;

    return (
        <section className="mb-8">
            {/* Section Header */}
            <div className="flex items-center gap-2 mb-4 pb-2 border-b-2 border-blue-600">
                {icon}
                <h2 className="text-lg font-bold text-gray-900 uppercase tracking-wide">
                    {title}
                </h2>
            </div>

            {/* Subsections */}
            <div className="space-y-4">
                {subsections.map((sub, idx) => (
                    <div key={idx} className="bg-white border border-gray-200 rounded-lg p-5 shadow-sm hover:shadow-md transition-shadow">
                        {/* Subheading */}
                        {sub.heading && (
                            <h3 className="text-base font-semibold text-blue-700 mb-3">
                                {sub.heading}
                            </h3>
                        )}

                        {/* Content Items */}
                        <ul className="space-y-2">
                            {sub.items.map((item, i) => (
                                <li key={i} className="flex gap-2 text-sm text-gray-700 leading-relaxed">
                                    <span className="text-blue-600 mt-1.5 flex-shrink-0">•</span>
                                    <span>{item}</span>
                                </li>
                            ))}
                        </ul>
                    </div>
                ))}
            </div>
        </section>
    );
}

export default function Page4() {
    const navigate = useNavigate();
    const location = useLocation();
    const [article, setArticle] = useState<ArticleSummary | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const searchParams = new URLSearchParams(location.search);
        const url = searchParams.get("url");

        if (!url) {
            setError("No URL provided");
            setLoading(false);
            return;
        }

        setLoading(true);
        setError(null);

        console.log("🔍 Fetching article:", url);

        getArticleSummary(url)
            .then((data) => {
                console.log("✅ Article loaded:", data);
                setArticle(data);
                setLoading(false);
            })
            .catch((err) => {
                console.error("❌ Error fetching article:", err);
                setError(err.message || "Failed to load article");
                setLoading(false);
            });
    }, [location.search]);

    // Loading State
    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto mb-4"></div>
                    <p className="text-gray-600 text-lg font-medium">Analyzing article...</p>
                    <p className="text-gray-500 text-sm mt-2">This may take 30-60 seconds</p>
                </div>
            </div>
        );
    }

    // Error State
    if (error || !article) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center max-w-md">
                    <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
                    <p className="text-red-600 text-lg font-medium mb-2">
                        {error || "Unable to load article"}
                    </p>
                    <p className="text-gray-600 text-sm mb-6">
                        Please check the URL and try again
                    </p>
                    <button
                        onClick={() => navigate(-1)}
                        className="px-6 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium"
                    >
                        Go Back
                    </button>
                </div>
            </div>
        );
    }

    // Define sections with icons
    const sections = [
        {
            id: "Background",
            label: "Background & Context",
            icon: <FileText className="w-5 h-5 text-blue-600" />
        },
        {
            id: "Methodology",
            label: "Methods & Study Design",
            icon: <FileText className="w-5 h-5 text-blue-600" />
        },
        {
            id: "KeyFindings",
            label: "Key Results & Findings",
            icon: <FileText className="w-5 h-5 text-blue-600" />
        },
        {
            id: "Implications",
            label: "Discussion & Implications",
            icon: <FileText className="w-5 h-5 text-blue-600" />
        },
        {
            id: "Conclusion",
            label: "Conclusions",
            icon: <FileText className="w-5 h-5 text-blue-600" />
        },
        {
            id: "EthicalConsiderations",
            label: "Ethical Considerations",
            icon: <FileText className="w-5 h-5 text-blue-600" />
        },
        {
            id: "AdditionalNotes",
            label: "Additional Notes",
            icon: <FileText className="w-5 h-5 text-blue-600" />
        },
    ];

    // Check if we have any content
    const hasContent = sections.some(sec =>
        article.summary[sec.id as keyof typeof article.summary]
    );

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <header className="sticky top-0 z-50 bg-white border-b border-gray-200 shadow-sm">
                <div className="container mx-auto px-6 py-3 flex items-center justify-between">
                    <button
                        onClick={() => navigate(-1)}
                        className="flex items-center gap-2 text-gray-600 hover:text-blue-600 transition font-medium"
                    >
                        <ArrowLeft className="w-5 h-5" />
                        <span>Back</span>
                    </button>
                    <SearchBar placeholder="Search in article..." />
                    <Navigation />
                </div>
            </header>

            {/* Main Content */}
            <main className="container mx-auto px-6 py-8 max-w-5xl">
                {/* Article Header */}
                <div className="bg-white rounded-lg shadow-md p-8 mb-8">
                    <div className="inline-block bg-blue-600 text-white text-xs font-bold px-3 py-1 rounded mb-4">
                        RESEARCH ARTICLE
                    </div>

                    <h1 className="text-3xl font-bold text-gray-900 mb-4 leading-tight">
                        {article.title}
                    </h1>

                    {/* Authors */}
                    {article.authors && article.authors.length > 0 && (
                        <div className="flex items-start gap-2 text-gray-700">
                            <Users className="w-5 h-5 mt-0.5 flex-shrink-0 text-gray-500" />
                            <p className="text-sm leading-relaxed">
                                <span className="font-semibold">Authors: </span>
                                {article.authors.join(", ")}
                            </p>
                        </div>
                    )}
                </div>

                {/* Article Sections */}
                {hasContent ? (
                    <div className="space-y-6">
                        {sections.map((sec) => {
                            const content = article.summary[sec.id as keyof typeof article.summary];
                            if (!content || content.trim() === "") return null;

                            return (
                                <SectionCard
                                    key={sec.id}
                                    title={sec.label}
                                    content={content}
                                    icon={sec.icon}
                                />
                            );
                        })}
                    </div>
                ) : (
                    <div className="bg-yellow-50 border border-yellow-300 rounded-lg p-8 text-center">
                        <AlertCircle className="w-12 h-12 text-yellow-600 mx-auto mb-3" />
                        <p className="text-yellow-800 font-medium">
                            No summary content available
                        </p>
                        <p className="text-yellow-700 text-sm mt-2">
                            The article analysis did not return structured content
                        </p>
                    </div>
                )}

                {/* Info Footer */}
                <div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                    <p className="text-xs text-blue-800">
                        <strong>Note:</strong> This summary was automatically generated using AI.
                        Please refer to the original article for complete details and validation.
                    </p>
                </div>
            </main>

            <Footer />
            <BackToTopButton />
        </div>
    );
}