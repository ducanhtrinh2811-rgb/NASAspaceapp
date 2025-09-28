from .ingestion import Ingestion
from .config import INGESTION_CONFIG

if INGESTION_CONFIG['run']:
    ingestion = Ingestion()
    ingestion.run()
    ingestion.close()
    del ingestion


from fastapi import FastAPI
from .embedder import Embedder
from .sql_db import SqlDB
from .vector_strore import WeaviateVectorStore
from pydantic import BaseModel

app = FastAPI(title='backend')
embedder = Embedder()
db = SqlDB()
vectorstore = WeaviateVectorStore()

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
        query_vector = embedder.embed(body['query'])
        doc_ids = vectorstore.similarity_search(
            query_vector=query_vector,
            k=body['limit']
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