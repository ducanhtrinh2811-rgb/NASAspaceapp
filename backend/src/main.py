from .ingestion import Ingestion
from .config import INGESTION_CONFIG

if INGESTION_CONFIG['run']:
    ingestion = Ingestion()
    ingestion.run()
    ingestion.close()
    del ingestion


from fastapi import FastAPI, Query
from .embedder import Embedder
from .sql_db import SqlDB
from .vector_strore import WeaviateVectorStore
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from bs4 import BeautifulSoup
import requests
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title='backend')
embedder = Embedder()
db = SqlDB()
vectorstore = WeaviateVectorStore()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/categories')
def get_categories():
    categories = db.get_categories()
    return {
        'status': 'success',
        'data': categories
    }

@app.get('/categories/{category_id}/documents')
def get_documents(category_id: int):
    docs = db.get_documents_by_category(category_id=category_id)
    return {
        'status': 'success',
        'data': docs
    }

class SearchRequest(BaseModel):
    query: str
    limit: int

@app.post('/search')
def search_documents(body: SearchRequest):
    try:
        query_vector = embedder.embed(body.query)
        doc_ids = vectorstore.similarity_search(
            query_vector=query_vector,
            k=body.limit
        )
        docs = db.get_documents_by_ids(doc_ids)
        return {
            'status': 'success',
            'data': docs
        }
    except Exception as e:
        return {
            'status': 'error',
            'data': str(e)
        }
    
@app.get("/article_content")
def get_article_content(url: str = Query(...)):
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        }
        res = requests.get(url, headers=headers, timeout=5)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        # Lấy main-content
        main_tag = soup.find("main", id="main-content")
        main_html = str(main_tag) if main_tag else "<p>No content found</p>"

        # Lấy style trong head
        styles = soup.find_all("style")
        style_text = "\n".join([s.get_text() for s in styles])

        # Lấy link CSS (chỉ lấy href)
        links = [l["href"] for l in soup.find_all("link", rel="stylesheet") if l.get("href")]

        return {
            "status": "success",
            "data": {
                "html": main_html,
                "style": style_text,
                "links": links
            }
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}