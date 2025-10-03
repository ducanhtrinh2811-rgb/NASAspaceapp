# src/main.py
from .ingestion import Ingestion
from .config import INGESTION_CONFIG

# Tự động ingest nếu config bật
if INGESTION_CONFIG.get("run"):
    ingestion = Ingestion()
    ingestion.run()
    ingestion.close()
    del ingestion

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from bs4 import BeautifulSoup
from pydantic import BaseModel
import requests
import re
import html
import json
from typing import Dict, Any, List

from .embedder import Embedder
from .sql_db import SqlDB
from .vector_strore import WeaviateVectorStore

app = FastAPI(title="backend")
embedder = Embedder()
db = SqlDB()
vectorstore = WeaviateVectorStore()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Helpers ----------
def clean_text(s: str) -> str:
    if not s:
        return ""
    return re.sub(r"\s+", " ", s).strip()


def extract_article_content(soup: BeautifulSoup) -> Dict[str, str]:
    """
    Trích xuất nội dung bài báo khoa học một cách thông minh.
    """
    content = {
        "abstract": "",
        "body": "",
        "full_text": ""
    }
    
    # 1. Tìm abstract
    abstract_selectors = [
        {"name": "div", "class_": ["abstract", "Abstract", "article-abstract"]},
        {"name": "section", "attrs": {"id": re.compile(r"abstract", re.I)}},
        {"name": "p", "class_": "abstract"},
        {"name": "div", "attrs": {"id": re.compile(r"abstract", re.I)}},
    ]
    
    for selector in abstract_selectors:
        abstract_tag = soup.find(**selector)
        if abstract_tag:
            content["abstract"] = clean_text(abstract_tag.get_text(" ", strip=True))
            if len(content["abstract"]) > 100:  # Đủ dài mới chấp nhận
                break
    
    # Nếu không tìm thấy, tìm meta description
    if not content["abstract"]:
        meta_abstract = soup.find("meta", {"name": "description"}) or \
                       soup.find("meta", {"property": "og:description"})
        if meta_abstract and meta_abstract.get("content"):
            content["abstract"] = clean_text(meta_abstract["content"])
    
    # 2. Tìm body content
    body_selectors = [
        {"name": "article"},
        {"name": "main"},
        {"name": "div", "class_": re.compile(r"article-body|content-body|article-text", re.I)},
        {"name": "div", "attrs": {"id": re.compile(r"article-body|content", re.I)}},
    ]
    
    body_tag = None
    for selector in body_selectors:
        body_tag = soup.find(**selector)
        if body_tag:
            # Loại bỏ các thẻ không cần thiết
            for unwanted in body_tag.find_all(["script", "style", "nav", "header", "footer", "aside"]):
                unwanted.decompose()
            
            body_text = clean_text(body_tag.get_text(" ", strip=True))
            if len(body_text) > 500:  # Đủ dài mới chấp nhận
                content["body"] = body_text
                break
    
    # Fallback: lấy toàn bộ body
    if not content["body"]:
        body_tag = soup.find("body")
        if body_tag:
            for unwanted in body_tag.find_all(["script", "style", "nav", "header", "footer", "aside"]):
                unwanted.decompose()
            content["body"] = clean_text(body_tag.get_text(" ", strip=True))
    
    # 3. Tạo full_text
    parts = []
    if content["abstract"]:
        parts.append(f"ABSTRACT:\n{content['abstract']}")
    if content["body"]:
        # Giới hạn body để tránh quá dài
        body_limited = content["body"][:8000]
        parts.append(f"\nFULL TEXT:\n{body_limited}")
    
    content["full_text"] = "\n\n".join(parts)
    
    return content


def summarize_with_ollama_json(text: str, model: str = "gemma:7b") -> Dict[str, str]:
    """
    Summarize with Ollama and force JSON structured output with detailed subsections.
    """
    text = clean_text(text)
    if not text:
        return create_empty_summary()

    # Giới hạn độ dài text
    if len(text) > 10000:
        text = text[:10000] + "..."

    prompt = f"""You are an expert scientific article summarizer. Analyze the following scientific article and create a structured JSON summary.

CRITICAL FORMATTING RULES:
1. Return ONLY valid JSON - no markdown, no explanations, just pure JSON
2. Each section must use this exact format with subsections:
   - Start with descriptive subheading: **SubheadingName**
   - Follow with bullet points: - Point text here
   - Separate subsections with blank line

3. Required JSON structure (all keys must exist):
{{
  "Background": "**Context**\\n- First point\\n- Second point\\n\\n**Objectives**\\n- Point here",
  "KeyFindings": "**Main Results**\\n- Finding 1\\n- Finding 2",
  "Methodology": "**Study Design**\\n- Design detail\\n\\n**Procedures**\\n- Procedure detail",
  "EthicalConsiderations": "**Ethical Aspects**\\n- Point if available, empty string if none",
  "Implications": "**Clinical Implications**\\n- Implication point",
  "AdditionalNotes": "**Limitations**\\n- Point if any, empty string if none",
  "Conclusion": "**Key Takeaways**\\n- Conclusion point"
}}

CONTENT GUIDELINES:
- Background: Context, previous research, study objectives
- KeyFindings: Main results and discoveries (be specific with numbers/data if available)
- Methodology: Study design, sample size, procedures, analysis methods
- EthicalConsiderations: IRB approval, consent, animal welfare (leave empty if not mentioned)
- Implications: Clinical/practical implications, significance
- AdditionalNotes: Limitations, future research, funding (leave empty if not mentioned)
- Conclusion: Main takeaways and final remarks

ARTICLE TEXT:
{text}

Return ONLY the JSON object, nothing else:"""

    try:
        print(f"🔄 Calling Ollama with {len(text)} chars...")
        res = requests.post(
            "http://host.docker.internal:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 2000,
                }
            },
            timeout=180,
        )
        
        if res.status_code != 200:
            print(f"❌ Ollama API error: {res.status_code}")
            return create_fallback_summary(text)
        
        raw = res.json().get("response", "").strip()
        print(f"📝 Ollama raw response length: {len(raw)} chars")
        
        # Clean response
        raw = raw.strip()
        
        # Remove markdown code blocks if present
        if raw.startswith("```"):
            raw = re.sub(r'^```(?:json)?\s*', '', raw)
            raw = re.sub(r'\s*```$', '', raw)
        
        # Try to extract JSON
        json_match = re.search(r'\{[\s\S]*\}', raw)
        if json_match:
            try:
                summary_json = json.loads(json_match.group())
                print("✅ Successfully parsed JSON from Ollama")
                
                # Validate and format
                summary_json = validate_and_format_summary(summary_json)
                return summary_json
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON parse error: {e}")
                print(f"Raw response preview: {raw[:200]}...")
                return create_fallback_summary(text)
        else:
            print("❌ No JSON found in response")
            return create_fallback_summary(text)

    except requests.Timeout:
        print("❌ Ollama timeout")
        return create_fallback_summary(text)
    except Exception as e:
        print(f"❌ Ollama API error: {e}")
        return create_fallback_summary(text)


def validate_and_format_summary(summary: Dict[str, Any]) -> Dict[str, str]:
    """
    Đảm bảo summary có đủ các keys và format đúng.
    """
    required_keys = [
        "Background",
        "KeyFindings",
        "Methodology",
        "EthicalConsiderations",
        "Implications",
        "AdditionalNotes",
        "Conclusion",
    ]
    
    result = {}
    for key in required_keys:
        val = summary.get(key, "")
        
        # Convert list to string format
        if isinstance(val, list):
            val = format_list_as_subsections(val, key)
        elif not isinstance(val, str):
            val = str(val) if val else ""
        
        # Ensure has subsection format if not empty
        if val and "**" not in val and len(val) > 20:
            val = auto_format_subsection(val, key)
        
        result[key] = val
    
    return result


def auto_format_subsection(text: str, section_name: str) -> str:
    """
    Tự động format text thành subsection với heading.
    """
    if not text:
        return ""
    
    # Split into sentences
    sentences = [s.strip() + "." for s in text.split('.') if s.strip()]
    
    if not sentences:
        return text
    
    # Create formatted output
    heading_map = {
        "Background": "Study Context",
        "KeyFindings": "Main Results",
        "Methodology": "Study Design",
        "Implications": "Key Implications",
        "Conclusion": "Summary"
    }
    
    heading = heading_map.get(section_name, "Overview")
    result = f"**{heading}**\n"
    
    for sentence in sentences[:5]:  # Limit to 5 sentences
        result += f"- {sentence}\n"
    
    return result.strip()


def format_list_as_subsections(items: List, section_name: str) -> str:
    """
    Format a list into subsections with bullet points.
    """
    if not items:
        return ""
    
    heading_map = {
        "Background": "Key Points",
        "KeyFindings": "Main Findings",
        "Methodology": "Methods",
        "Implications": "Implications"
    }
    
    heading = heading_map.get(section_name, "Summary")
    result = f"**{heading}**\n"
    
    for item in items:
        result += f"- {str(item)}\n"
    
    return result.strip()


def create_empty_summary() -> Dict[str, str]:
    """
    Tạo summary rỗng với đúng format.
    """
    return {
        "Background": "",
        "KeyFindings": "",
        "Methodology": "",
        "EthicalConsiderations": "",
        "Implications": "",
        "AdditionalNotes": "",
        "Conclusion": "",
    }


def create_fallback_summary(text: str) -> Dict[str, str]:
    """
    Tạo summary fallback từ text gốc khi Ollama thất bại.
    """
    print("⚠️ Creating fallback summary from raw text")
    
    # Tách abstract và body nếu có
    parts = text.split("FULL TEXT:")
    abstract = ""
    body = ""
    
    if len(parts) > 1:
        abstract = parts[0].replace("ABSTRACT:", "").strip()
        body = parts[1].strip()
    else:
        body = text
    
    # Tạo Background từ abstract hoặc phần đầu
    background_text = abstract if abstract else body[:800]
    background = auto_format_subsection(background_text, "Background")
    
    # Tạo KeyFindings từ body
    body_preview = body[:600] if body else ""
    findings = auto_format_subsection(body_preview, "KeyFindings") if body_preview else ""
    
    return {
        "Background": background,
        "KeyFindings": findings,
        "Methodology": "**Note**\n- Full analysis unavailable. Please check the original article.",
        "EthicalConsiderations": "",
        "Implications": "",
        "AdditionalNotes": "**Important**\n- This is an automated summary. Some details may be incomplete.",
        "Conclusion": "",
    }


# ---------- APIs ----------
@app.get("/categories")
def get_categories():
    return {"status": "success", "data": db.get_categories()}


@app.get("/categories/{category_id}/documents")
def get_documents(category_id: int):
    return {"status": "success", "data": db.get_documents_by_category(category_id)}


class SearchRequest(BaseModel):
    query: str
    limit: int


@app.post("/search")
def search_documents(body: SearchRequest):
    try:
        query_vector = embedder.embed(body.query)
        doc_ids = vectorstore.similarity_search(query_vector=query_vector, k=body.limit)
        docs = db.get_documents_by_ids(doc_ids)
        return {"status": "success", "data": docs}
    except Exception as e:
        return {"status": "error", "data": str(e)}


@app.get("/article_content")
def get_article_content(url: str = Query(...)):
    """
    Crawl bài báo và trả về tóm tắt có cấu trúc với subsections (dùng cho Page4).
    """
    try:
        print(f"\n🌐 Fetching URL: {url}")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        resp = requests.get(url, headers=headers, timeout=20)
        resp.raise_for_status()
        
        print(f"✅ HTTP {resp.status_code} - Content length: {len(resp.text)}")
        
        soup = BeautifulSoup(resp.text, "html.parser")

        # Lấy tiêu đề
        title = ""
        title_tag = soup.find("h1") or soup.find("title")
        if title_tag:
            title = clean_text(title_tag.get_text())
        
        if not title:
            title = "Article Title Unavailable"
        
        print(f"📰 Title: {title[:100]}")
        
        # Lấy tác giả
        authors = []
        
        # Method 1: Meta tags
        for meta in soup.find_all("meta", {"name": "citation_author"}):
            if meta.get("content"):
                authors.append(meta["content"].strip())
        
        # Method 2: Author tags
        if not authors:
            author_tags = soup.find_all(class_=re.compile(r"author", re.I))
            for tag in author_tags[:10]:  # Limit to 10
                author_text = clean_text(tag.get_text())
                if author_text and len(author_text) < 100:
                    authors.append(author_text)
        
        print(f"👥 Authors found: {len(authors)}")

        # Trích xuất nội dung
        content = extract_article_content(soup)
        
        print(f"📄 Content extracted:")
        print(f"   - Abstract: {len(content['abstract'])} chars")
        print(f"   - Body: {len(content['body'])} chars")
        print(f"   - Full: {len(content['full_text'])} chars")
        
        if len(content['full_text']) < 200:
            print("⚠️ Warning: Very short content extracted")
        
        # Tạo tóm tắt CÓ CẤU TRÚC với subsections bằng Ollama
        summary = summarize_with_ollama_json(content['full_text'])

        return {
            "status": "success",
            "data": {
                "title": html.unescape(title),
                "authors": authors[:15],  # Limit authors
                "summary": summary
            }
        }
        
    except requests.Timeout:
        print("❌ Request timeout")
        return {"status": "error", "error": "Request timeout - URL took too long to respond"}
    except requests.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        return {"status": "error", "error": f"HTTP Error: {str(e)}"}
    except Exception as e:
        print(f"❌ ERROR in /article_content: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "error": str(e)}


@app.get("/article_content_smart")
def get_article_content_smart(url: str = Query(...)):
    """
    Alias for /article_content
    """
    return get_article_content(url)