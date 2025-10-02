import { useParams, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { getDocumentsByCategory } from "../services/DocumentService";
import type { Document } from "../types";
import { Footer } from "../components/Footer";
import { BackToTopButton } from "../components/BackToTopButton";

// Map id → topic name
const topicNames: Record<string, string> = {
  "1": "Vertebrate",
  "2": "Plants",
  "3": "Microbes",
  "4": "Fungi",
  "5": "Human Cell & Biomedical",
  "6": "Systems Biology & Tools",
};

export default function TopicPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [docs, setDocs] = useState<Document[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    if (!id) return;
    const fetchDocs = async () => {
      setLoading(true);
      try {
        const results = await getDocumentsByCategory(Number(id));
        setDocs(results);
      } catch (err) {
        console.error("Failed to load documents:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchDocs();
  }, [id]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      // sau này có thể gắn vào searchDocuments
      console.log("Searching:", searchQuery);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex flex-col">
      {/* Navbar */}
      <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-200 shadow-sm">
        <div className="container mx-auto px-6 py-3 flex items-center justify-between">
          {/* Logo */}
          <button
            onClick={() => navigate("/")}
            className="flex items-center space-x-2 font-bold text-xl text-blue-600"
          >
            🚀 AstroMorphosis
          </button>

          {/* SearchBar */}
          <div className="flex-1 px-6">
            <form onSubmit={handleSearch} className="relative">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search documents..."
                className="w-full px-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-400"
              />
              <button
                type="submit"
                className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-500 hover:text-blue-600"
              >
                🔍
              </button>
            </form>
          </div>

          {/* Nav */}
          <nav className="flex space-x-6 font-medium text-gray-700">
            <a href="/#topics" className="hover:text-blue-600">Topics</a>
            <a href="/#about" className="hover:text-blue-600">About</a>
            <a href="/#feedback" className="hover:text-blue-600">Feedback</a>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <div className="container mx-auto px-6 py-8 flex-1">
        <h1 className="text-4xl font-bold text-center mb-8">
          {topicNames[id ?? ""] || `Topic ${id}`}
        </h1>

        {loading && <p className="text-center text-blue-500">Loading...</p>}

        {!loading && docs.length > 0 && (
          <ul className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {docs.map((doc) => (
              <li
                key={doc.id}
                onClick={() =>
                  navigate(`/article?url=${encodeURIComponent(doc.link)}`)
                }
                className="cursor-pointer bg-white p-6 rounded-xl shadow-lg border-t-4 border-blue-500 hover:shadow-xl transition"
              >
                <h3 className="font-bold text-xl mb-2">{doc.title}</h3>
                <p className="text-gray-600 text-sm line-clamp-3">
                  {doc.summary}
                </p>
              </li>
            ))}
          </ul>
        )}

        {!loading && docs.length === 0 && (
          <p className="text-center text-gray-500">No documents found.</p>
        )}
      </div>

      <Footer />
      <BackToTopButton />
    </div>
  );
}
