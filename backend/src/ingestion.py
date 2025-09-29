from .config import INGESTION_CONFIG
import requests
import pandas as pd
from .sql_db import SqlDB
from .vector_strore import WeaviateVectorStore
from .embedder import Embedder
import json
import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
import time

class Ingestion:
    def __init__(self):
        self.db = SqlDB()
        self.vectorstore = WeaviateVectorStore()
        self.embedder = Embedder()

    def close(self):
        self.vectorstore.close()

    def run(self):
        if not INGESTION_CONFIG['run']:
            print("[INFO] Ingestion is disabled in config.")
            return
        df = pd.read_csv(INGESTION_CONFIG['path'])

        categories = df['category'].unique().tolist()
        cat_map = {}
        for category in categories:
            obj = self.db.create_category(name=category)
            cat_map[category] = obj.id

        keywords = set()
        for row in df.itertuples(index=False):
            keys = row.keywords
            if not keys or pd.isna(keys):
                keys = []
            else:
                keys = [k.strip() for k in keys.split(',')]
            keywords.update(keys)
        keywords = list(keywords)
        keyword_map = {}
        for key in keywords:
            obj = self.db.create_keyword(name=key)
            keyword_map[key] = obj.id

        for i, row in enumerate(df.itertuples(index=False), start=1):
            title = row.Title
            link = row.Link
            summary = row.summary
            if not summary or pd.isna(summary):
                summary = ''
            
            keywords = row.keywords
            if not keywords or pd.isna(keywords):
                keywords = []
            else:
                keywords = set([key.strip() for key in keywords.split(',')])
                keywords = list(keywords)
                
            keyword_ids = [keyword_map[key] for key in keywords]


            category = row.category
            category_id = cat_map[category]

            doc = self.db.create_document(
                title=title,
                link=link,
                summary=summary,
                category_id=category_id,
                keyword_ids=keyword_ids
            )

            title_embedding, summary_embedding = self.embedder.embed_batch([title, summary])

            self.vectorstore.add_document(
                doc_id=doc.id,
                title_embedding=title_embedding,
                summary_embedding=summary_embedding
            )