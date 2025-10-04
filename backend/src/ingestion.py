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
        
        # ✅ THÊM: Kiểm tra xem đã có dữ liệu chưa
        try:
            existing_categories = self.db.get_categories()
            if len(existing_categories) > 0:
                print(f"[WARNING] Database already has {len(existing_categories)} categories.")
                print("[WARNING] Data may already exist. Skipping ingestion to avoid duplicates.")
                print("[INFO] To re-ingest:")
                print("  1. Clear the database using clear_database.py")
                print("  2. Or set INGESTION_CONFIG['run'] = False")
                return
        except Exception as e:
            print(f"[INFO] Checking database: {e}")
            print("[INFO] Proceeding with ingestion...")
        
        print("[INFO] Starting data ingestion...")
        df = pd.read_csv(INGESTION_CONFIG['path'])
        print(f"[INFO] Loaded {len(df)} documents from CSV")

        # ✅ Tạo categories với kiểm tra trùng
        categories = df['category'].unique().tolist()
        cat_map = {}
        print(f"[INFO] Creating {len(categories)} categories...")
        for category in categories:
            obj = self.db.create_category(name=category)
            cat_map[category] = obj.id
        print(f"[SUCCESS] Created {len(cat_map)} categories")

        # ✅ Tạo keywords với kiểm tra trùng
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
        print(f"[INFO] Creating {len(keywords)} keywords...")
        for key in keywords:
            if key:  # ✅ Bỏ qua keyword rỗng
                obj = self.db.create_keyword(name=key)
                keyword_map[key] = obj.id
        print(f"[SUCCESS] Created {len(keyword_map)} keywords")

        # ✅ Tạo documents
        print(f"[INFO] Creating {len(df)} documents...")
        success_count = 0
        for i, row in enumerate(df.itertuples(index=False), start=1):
            try:
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
                    
                keyword_ids = [keyword_map[key] for key in keywords if key in keyword_map]

                category = row.category
                category_id = cat_map[category]

                # ✅ Tạo document
                doc = self.db.create_document(
                    title=title,
                    link=link,
                    summary=summary,
                    category_id=category_id,
                    keyword_ids=keyword_ids
                )

                # ✅ Tạo embeddings
                title_embedding, summary_embedding = self.embedder.embed_batch([title, summary])

                # ✅ Thêm vào vector store
                self.vectorstore.add_document(
                    doc_id=doc.id,
                    title_embedding=title_embedding,
                    summary_embedding=summary_embedding
                )
                
                success_count += 1
                if i % 10 == 0:
                    print(f"[PROGRESS] Processed {i}/{len(df)} documents...")
                    
            except Exception as e:
                print(f"[ERROR] Failed to process document {i}: {title[:50]}... - {e}")
                continue
        
        print(f"[SUCCESS] Ingestion completed! {success_count}/{len(df)} documents created.")