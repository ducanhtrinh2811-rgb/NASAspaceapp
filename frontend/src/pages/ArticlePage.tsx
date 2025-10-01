import { useNavigate, useLocation } from "react-router-dom";
import { useEffect, useState } from "react";
import type { ArticleData } from "../types";

export default function ArticlePage() {
  const navigate = useNavigate();
  const location = useLocation();
  const [article, setArticle] = useState<ArticleData | null>(null);

  useEffect(() => {
    const searchParams = new URLSearchParams(location.search);
    const url = searchParams.get("url");
    if (!url) return;

    fetch(`http://localhost:8000/article_content?url=${encodeURIComponent(url)}`)
      .then(res => res.json())
      .then(data => {
        if (data.status === "success") {
          setArticle(data.data); // ✅ lấy từ data.data
        }
      })
      .catch(err => console.error(err));
  }, [location.search]);

  return (
    <div className="min-h-screen relative bg-neutral-50 p-6">
      {/* Back button góc trên trái */}
      <button
        onClick={() => navigate("/home")}
        className="absolute top-4 left-4 px-4 py-2 bg-blue-500 text-white rounded-lg shadow hover:bg-blue-600 transition"
      >
        Back
      </button>

      {/* Gắn link CSS */}
      {article?.links.map((href) => (
        <link key={href} rel="stylesheet" href={href} />
      ))}

      {/* Gắn CSS inline */}
      {article?.style && <style>{article.style}</style>}

      {/* Render main-content */}
      {article ? (
        <div
          id="article-main"
          className="mt-16"
          dangerouslySetInnerHTML={{ __html: article.html }}
        />
      ) : (
        <p>Loading article...</p>
      )}
    </div>
  );
}