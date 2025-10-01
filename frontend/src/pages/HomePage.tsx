import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import type { Document } from "../types";
import { getCategories } from "../services/CategoryService";
import { getDocumentsByCategory, searchDocuments } from "../services/DocumentService";
import { useHomeState } from "../contexts/HomeStateContext";

export default function HomePage() {
  const navigate = useNavigate();

  // Sử dụng context để lưu state toàn cục cho HomePage
  const {
    categories,
    searchQuery,
    searchResults,
    isSearching,
    setCategories,
    setSearchQuery,
    setSearchResults,
    setIsSearching
  } = useHomeState();

  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        // Chỉ fetch khi categories trống
        if (categories.length === 0) {
          const cats = await getCategories();
          setCategories(cats);
        }
      } catch (err) {
        console.error("Failed to load categories:", err);
      }
    };
    fetchCategories();
  }, [categories.length, setCategories]);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    const query = searchQuery.trim();

    if (!query) {
      setIsSearching(false);
      setSearchResults([]);
      return;
    }

    setIsSearching(true);
    setLoading(true);

    try {
      const results = await searchDocuments({ query, limit: 100 });
      setSearchResults(results);
    } catch (err) {
      console.error("Search failed:", err);
      setSearchResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleCategoryClick = async (catId: number) => {
    setIsSearching(true);
    setLoading(true);
    try {
      const docs = await getDocumentsByCategory(catId);
      setSearchResults(docs);
    } finally {
      setLoading(false);
    }
  };

  const handleDocumentClick = (doc: Document) => {
    // Chỉ navigate sang ArticlePage, không cần truyền state
    navigate(`/article?url=${encodeURIComponent(doc.link)}`);
  };

  return (
    <div className="min-h-screen bg-neutral-50 flex flex-col items-center p-4">
      <h1 className="text-3xl font-extrabold text-gray-800 mt-8 mb-6">
        Document Search
      </h1>

      {/* Search Bar */}
      <form
        onSubmit={handleSearch}
        className={`transition-all duration-500 rounded-xl shadow-lg border-2 border-transparent focus-within:border-blue-400 ${
          isSearching ? "mt-6 w-full max-w-md" : "mt-20 w-full max-w-xl"
        }`}
      >
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder={
            isSearching
              ? "Search..."
              : "Enter keywords to search documents..."
          }
          className={`w-full px-5 py-3 text-gray-700 bg-white rounded-xl focus:outline-none transition-all duration-500 placeholder-gray-400 ${
            isSearching ? "text-base py-2" : "text-xl py-4 shadow-xl"
          }`}
        />
      </form>

      {/* Categories */}
      {!isSearching && (
        <div className="flex flex-col items-center justify-center flex-1 space-y-4 mt-20">
          <h2 className="text-2xl font-semibold text-gray-600 mb-4">
            Browse by Category
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-2xl">
            {categories.map((cat) => (
              <button
                key={cat.id}
                onClick={() => handleCategoryClick(cat.id)}
                className="w-56 bg-white py-4 px-6 rounded-xl shadow-md border border-gray-200 hover:shadow-xl hover:bg-blue-50 hover:border-blue-300 transition-all transform hover:scale-105 font-medium text-gray-700 text-lg"
              >
                {cat.name}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Search / Category Results */}
      {isSearching && (
        <div className="flex flex-col items-center mt-6 w-full">
          <div className="flex flex-wrap justify-center gap-2 mt-4 max-w-xl">
            {categories.map((cat) => (
              <button
                key={cat.id}
                onClick={() => handleCategoryClick(cat.id)}
                className="bg-white px-3 py-1 rounded-full shadow-sm border border-gray-200 hover:bg-blue-100 transition text-sm font-medium text-gray-700"
              >
                {cat.name}
              </button>
            ))}
          </div>

          {loading && (
            <div className="mt-8 flex items-center space-x-2 text-blue-500">
              <svg
                className="animate-spin h-5 w-5"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              <p>Loading results...</p>
            </div>
          )}

          {!loading && searchResults.length > 0 && (
            <ul className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-8 w-full max-w-6xl">
              {searchResults.map((doc) => (
                <li
                  key={doc.id}
                  onClick={() => handleDocumentClick(doc)}
                  className="cursor-pointer bg-white p-6 rounded-xl shadow-lg border-t-4 border-blue-500 hover:shadow-xl transition transform hover:-translate-y-1"
                >
                  <h3 className="font-bold text-xl text-gray-800 mb-2">
                    {doc.title}
                  </h3>
                  <p className="text-gray-600 text-sm mb-4 line-clamp-3">
                    {doc.summary}
                  </p>
                  <div className="text-blue-500 hover:text-blue-600 hover:underline mt-2 inline-flex items-center space-x-1 font-medium">
                    <span>View document</span>
                  </div>
                </li>
              ))}
            </ul>
          )}

          {!loading && searchResults.length === 0 && (
            <p className="mt-8 text-gray-500 text-lg">
              No documents found matching your criteria.
            </p>
          )}
        </div>
      )}
    </div>
  );
}
