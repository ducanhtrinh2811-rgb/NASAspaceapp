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
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from bs4 import BeautifulSoup
from pydantic import BaseModel
import requests
import re
import html
import json
import os
from typing import Dict, Any, List
from urllib.parse import urljoin

from .embedder import Embedder
from .sql_db import SqlDB
from .vector_strore import WeaviateVectorStore

app = FastAPI(title="backend")
embedder = Embedder()
db = SqlDB()
vectorstore = WeaviateVectorStore()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
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
    """Trích xuất nội dung bài báo"""
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
            if len(content["abstract"]) > 100:
                break
    
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
            for unwanted in body_tag.find_all(["script", "style", "nav", "header", "footer", "aside"]):
                unwanted.decompose()
            
            body_text = clean_text(body_tag.get_text(" ", strip=True))
            if len(body_text) > 500:
                content["body"] = body_text
                break
    
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
        body_limited = content["body"][:8000]
        parts.append(f"\nFULL TEXT:\n{body_limited}")
    
    content["full_text"] = "\n\n".join(parts)
    
    return content


def extract_pdf_url(soup: BeautifulSoup, base_url: str) -> str:
    """Tìm URL PDF"""
    pdf_url = ""
    
    meta_pdf = soup.find("meta", {"name": "citation_pdf_url"})
    if meta_pdf and meta_pdf.get("content"):
        return meta_pdf["content"]
    
    pdf_links = []
    for link in soup.find_all("a", href=True):
        href = link.get("href", "")
        text = link.get_text().strip().lower()
        
        if href.endswith(".pdf"):
            pdf_links.append(href)
            continue
        
        if any(keyword in text for keyword in ["pdf", "download pdf", "full text pdf"]):
            if ".pdf" in href or "pdf" in href.lower():
                pdf_links.append(href)
    
    if pdf_links:
        pdf_url = pdf_links[0]
        if pdf_url.startswith("/"):
            pdf_url = urljoin(base_url, pdf_url)
        elif not pdf_url.startswith("http"):
            pdf_url = urljoin(base_url, pdf_url)
    
    return pdf_url


def summarize_with_groq(text: str) -> Dict[str, str]:
    """Summarize với Groq API"""
    text = clean_text(text)
    if not text:
        return create_empty_summary()

    if len(text) > 10000:
        text = text[:10000] + "..."

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    if not GROQ_API_KEY:
        print("GROQ_API_KEY not found, using fallback")
        return create_fallback_summary(text)

    prompt = f"""You are an expert scientific article summarizer. Return ONLY valid JSON with these exact keys:
{{"Background": "**Context**\\n- Point 1\\n- Point 2", "KeyFindings": "**Results**\\n- Finding 1", "Methodology": "**Design**\\n- Method detail", "EthicalConsiderations": "", "Implications": "**Impact**\\n- Implication", "AdditionalNotes": "", "Conclusion": "**Summary**\\n- Key point"}}

Article: {text}"""

    try:
        res = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gemma-7b-it",
                "messages": [
                    {"role": "system", "content": "Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 2000,
            },
            timeout=60,
        )
        
        if res.status_code != 200:
            return create_fallback_summary(text)
        
        raw = res.json()["choices"][0]["message"]["content"].strip()
        
        if raw.startswith("```"):
            raw = re.sub(r'^```(?:json)?\s*', '', raw)
            raw = re.sub(r'\s*```$', '', raw)
        
        json_match = re.search(r'\{[\s\S]*\}', raw)
        if json_match:
            summary_json = json.loads(json_match.group())
            return validate_and_format_summary(summary_json)
        
        return create_fallback_summary(text)

    except Exception as e:
        print(f"Groq error: {e}")
        return create_fallback_summary(text)


def validate_and_format_summary(summary: Dict[str, Any]) -> Dict[str, str]:
    """Validate summary format"""
    required_keys = [
        "Background", "KeyFindings", "Methodology", 
        "EthicalConsiderations", "Implications", 
        "AdditionalNotes", "Conclusion"
    ]
    
    result = {}
    for key in required_keys:
        val = summary.get(key, "")
        if isinstance(val, list):
            val = format_list_as_subsections(val, key)
        elif not isinstance(val, str):
            val = str(val) if val else ""
        
        if val and "**" not in val and len(val) > 20:
            val = auto_format_subsection(val, key)
        
        result[key] = val
    
    return result


def auto_format_subsection(text: str, section_name: str) -> str:
    """Auto format text"""
    if not text:
        return ""
    
    sentences = [s.strip() + "." for s in text.split('.') if s.strip()]
    if not sentences:
        return text
    
    heading_map = {
        "Background": "Study Context",
        "KeyFindings": "Main Results",
        "Methodology": "Study Design",
        "Implications": "Key Implications",
        "Conclusion": "Summary"
    }
    
    heading = heading_map.get(section_name, "Overview")
    result = f"**{heading}**\n"
    
    for sentence in sentences[:5]:
        result += f"- {sentence}\n"
    
    return result.strip()


def format_list_as_subsections(items: List, section_name: str) -> str:
    """Format list"""
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
    """Empty summary"""
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
    """Fallback summary"""
    parts = text.split("FULL TEXT:")
    abstract = ""
    body = ""
    
    if len(parts) > 1:
        abstract = parts[0].replace("ABSTRACT:", "").strip()
        body = parts[1].strip()
    else:
        body = text
    
    background_text = abstract if abstract else body[:800]
    background = auto_format_subsection(background_text, "Background")
    
    body_preview = body[:600] if body else ""
    findings = auto_format_subsection(body_preview, "KeyFindings") if body_preview else ""
    
    return {
        "Background": background,
        "KeyFindings": findings,
        "Methodology": "**Note**\n- Full analysis unavailable.",
        "EthicalConsiderations": "",
        "Implications": "",
        "AdditionalNotes": "**Important**\n- Automated summary.",
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
    """Crawl article and return summary"""
    try:
        print(f"\nFetching URL: {url}")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        resp = requests.get(url, headers=headers, timeout=20)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, "html.parser")

        # Get title
        title = ""
        title_tag = soup.find("h1") or soup.find("title")
        if title_tag:
            title = clean_text(title_tag.get_text())
        
        if not title:
            title = "Article Title Unavailable"
        
        # Get authors
        authors = []
        for meta in soup.find_all("meta", {"name": "citation_author"}):
            if meta.get("content"):
                authors.append(meta["content"].strip())
        
        if not authors:
            author_tags = soup.find_all(class_=re.compile(r"author", re.I))
            for tag in author_tags[:10]:
                author_text = clean_text(tag.get_text())
                if author_text and len(author_text) < 100:
                    authors.append(author_text)

        # Extract PDF URL
        pdf_url = extract_pdf_url(soup, url)

        # Extract content
        content = extract_article_content(soup)
        
        # Summarize with Groq
        summary = summarize_with_groq(content['full_text'])

        return {
            "status": "success",
            "data": {
                "title": html.unescape(title),
                "authors": authors[:15],
                "summary": summary,
                "pdf_url": pdf_url
            }
        }
        
    except requests.Timeout:
        return {"status": "error", "error": "Request timeout"}
    except requests.HTTPError as e:
        return {"status": "error", "error": f"HTTP Error: {str(e)}"}
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "error": str(e)}


class ChatRequest(BaseModel):
    question: str
    article_title: str
    article_context: str


@app.post("/chat_article")
def chat_article(body: ChatRequest):
    """Chat with Groq API"""
    try:
        GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        
        if not GROQ_API_KEY:
            return {"status": "error", "answer": "API key not configured"}
        
        context = f"""Article: {body.article_title}

Content: {body.article_context[:3000]}

Question: {body.question}

Answer based on the article."""

        res = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gemma-7b-it",
                "messages": [{"role": "user", "content": context}],
                "temperature": 0.5,
                "max_tokens": 500,
            },
            timeout=30,
        )
        
        if res.status_code != 200:
            return {"status": "error", "answer": "AI request failed"}
        
        answer = res.json()["choices"][0]["message"]["content"].strip()
        
        return {"status": "success", "answer": answer}
        
    except Exception as e:
        return {"status": "error", "answer": f"Error: {str(e)}"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from FastAPI!"}


# Serve frontend
frontend_path = os.path.join(os.path.dirname(__file__), "../frontend/dist")

if os.path.exists(frontend_path):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_path, "assets")), name="assets")
    
    @app.get("/{full_path:path}")
    def serve_vue(full_path: str):
        index_file = os.path.join(frontend_path, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"error": "Frontend not found"}