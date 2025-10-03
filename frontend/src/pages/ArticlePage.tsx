import { useNavigate, useLocation } from "react-router-dom";
import { useEffect, useState } from "react";
import { ArrowLeft, AlertCircle } from "lucide-react";
import { getArticleSummary } from "../services/ArticleService";
import { LoadingState } from "../components/LoadingState";
import type { ArticleSummary } from "../types";

function parseSubsections(content: string): { heading: string; items: string[] }[] {
    if (!content) return [];

    const sections: { heading: string; items: string[] }[] = [];
    const lines = content.split('\n');
    let currentHeading = '';
    let currentItems: string[] = [];

    for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed) continue;

        const headingMatch = trimmed.match(/^\*\*(.+?)\*\*:?\s*/);

        if (headingMatch) {
            if (currentHeading || currentItems.length > 0) {
                sections.push({ heading: currentHeading, items: currentItems });
            }
            currentHeading = headingMatch[1].trim();
            const remaining = trimmed.substring(headingMatch[0].length).trim();
            currentItems = remaining ? [remaining.replace(/^-\s*/, '')] : [];
        } else {
            const item = trimmed.replace(/^-\s*/, '');
            if (item) currentItems.push(item);
        }
    }

    if (currentHeading || currentItems.length > 0) {
        sections.push({ heading: currentHeading, items: currentItems });
    }

    return sections.filter(s => s.items.length > 0);
}

export default function ArticlePage() {
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

        getArticleSummary(url)
            .then((data) => {
                setArticle(data);
                setLoading(false);
            })
            .catch((err) => {
                console.error("Error:", err);
                setError(err.message || "Failed to load article");
                setLoading(false);
            });
    }, [location.search]);

    if (loading) {
        return <LoadingState message="Loading article..." submessage="Please wait" />;
    }

    if (error || !article) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center max-w-md">
                    <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
                    <p className="text-red-600 text-lg font-medium mb-2">{error || "Failed to load"}</p>
                    <button
                        onClick={() => navigate("/home")}
                        className="px-6 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                    >
                        Back to Home
                    </button>
                </div>
            </div>
        );
    }

    const sections = [
        { id: "Background", label: "Background" },
        { id: "KeyFindings", label: "Key Findings" },
        { id: "Methodology", label: "Methodology" },
        { id: "EthicalConsiderations", label: "Ethical Considerations" },
        { id: "Implications", label: "Implications" },
        { id: "AdditionalNotes", label: "Additional Notes" },
        { id: "Conclusion", label: "Conclusion" },
    ];

    return (
        <div className="min-h-screen bg-gray-50 p-6">
            <div className="max-w-4xl mx-auto">
                <button
                    onClick={() => navigate("/home")}
                    className="mb-6 flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg shadow-sm hover:bg-gray-50 transition"
                >
                    <ArrowLeft className="w-4 h-4" />
                    Back
                </button>

                <div className="bg-white rounded-lg shadow-md p-8 mb-6">
                    <div className="inline-block bg-blue-600 text-white text-xs font-bold px-3 py-1 rounded mb-4">
                        ARTICLE
                    </div>

                    <h1 className="text-4xl font-bold text-gray-900 mb-4">
                        {article.title}
                    </h1>

                    {article.authors.length > 0 && (
                        <p className="text-lg text-gray-600">
                            <span className="font-semibold">Authors:</span> {article.authors.join(", ")}
                        </p>
                    )}
                </div>

                {sections.map((sec) => {
                    const content = article.summary[sec.id as keyof ArticleSummary["summary"]];
                    if (!content) return null;

                    const subsections = parseSubsections(content);

                    return (
                        <section key={sec.id} className="bg-white rounded-lg shadow-md p-6 mb-6">
                            <h2 className="text-2xl font-bold text-blue-700 mb-4 pb-2 border-b border-gray-200">
                                {sec.label}
                            </h2>

                            {subsections.length > 0 ? (
                                <div className="space-y-4">
                                    {subsections.map((sub, idx) => (
                                        <div key={idx}>
                                            {sub.heading && (
                                                <h3 className="text-lg font-semibold text-gray-800 mb-2">
                                                    {sub.heading}
                                                </h3>
                                            )}
                                            <ul className="space-y-2 ml-4">
                                                {sub.items.map((item, i) => (
                                                    <li key={i} className="flex gap-2 text-gray-700">
                                                        <span className="text-blue-600">•</span>
                                                        <span>{item}</span>
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <p className="text-gray-800 leading-relaxed whitespace-pre-line">
                                    {content}
                                </p>
                            )}
                        </section>
                    );
                })}
            </div>
        </div>
    );
}