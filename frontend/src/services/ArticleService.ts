export async function fetchArticleContent(url: string) {
  const res = await fetch(url, {
    headers: {
      "User-Agent": "Mozilla/5.0",
      "Accept": "text/html",
    },
  });
  if (!res.ok) throw new Error("Failed to fetch article");
  const text = await res.text();
  const parser = new DOMParser();
  const doc = parser.parseFromString(text, "text/html");

  const main = doc.querySelector("main#main-content");
  const styleTags = Array.from(doc.querySelectorAll("style"));
  const css = styleTags.map(s => s.innerHTML).join("\n");

  return {
    html: main?.innerHTML || "",
    css,
  };
}
