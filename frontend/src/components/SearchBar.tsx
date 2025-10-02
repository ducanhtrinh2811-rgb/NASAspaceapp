import { useState } from "react";
import { Input } from "../components/Input";
import { useNavigate } from "react-router-dom";

export function SearchBar() {   // ✅ đổi từ TopBar thành SearchBar
  const [query, setQuery] = useState("");
  const navigate = useNavigate();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      navigate(`/search?q=${query}`);
    }
  };

  return (
    <div className="sticky top-0 z-50 bg-white shadow-md border-b px-6 py-3 flex items-center justify-between">
      {/* Search Bar */}
      <form onSubmit={handleSearch} className="flex-1 max-w-lg">
        <Input
          type="text"
          placeholder="Search..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="w-full"
        />
      </form>

      {/* Navigation */}
      <nav className="ml-6 flex space-x-6 font-medium text-gray-700">
        <a href="/home" className="hover:text-blue-600 transition">Home</a>
        <a href="/topics" className="hover:text-blue-600 transition">Topics</a>
        <a href="/about" className="hover:text-blue-600 transition">About</a>
        <a href="/feedback" className="hover:text-blue-600 transition">Feedback</a>
      </nav>
    </div>
  );
}
