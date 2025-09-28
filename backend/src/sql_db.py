from .config import POSTGRES_CONFIG
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from .models import Base, Category, Keyword, Document
from typing import List

class SqlDB:
    def __init__(self):
        try:
            self.engine = create_engine(
                f"postgresql+psycopg2://{POSTGRES_CONFIG['user']}:{POSTGRES_CONFIG['password']}"
                f"@{POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']}/{POSTGRES_CONFIG['dbname']}",
                echo=False
            )
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            inspector = inspect(self.engine)
            if not inspector.get_table_names():
                Base.metadata.create_all(bind=self.engine)
    
        except SQLAlchemyError as e:
            raise RuntimeError(f"Cannot connect to database: {e}")
            
    def get_session(self):
        return self.SessionLocal()

    def create_category(self, name: str):
        with self.get_session() as db:
            category = Category(name=name)
            db.add(category)
            db.commit()
            db.refresh(category)
            return category
    
    def get_category_by_name(self, name: str):
        with self.get_session() as db:
            cat = db.query(Category).filter_by(name=name).first()
            if cat:
                return cat
            return None
    
    def get_categories(self):
        with self.get_session() as db:
            return db.query(Category).all()
    
    def get_category_by_id(self, id: int):
        with self.get_session() as db:
            cat = db.query(Category).filter_by(id=id).first()
            if cat:
                return cat
            return None

    def create_keyword(self, name: str):
        with self.get_session() as db:
            keyword = Keyword(name=name)
            db.add(keyword)
            db.commit()
            db.refresh(keyword)
            return keyword
    
    def get_keyword_by_name(self, name: str):
        with self.get_session() as db:
            keyword = db.query(Keyword).filter_by(name=name).first()
            if keyword:
                return keyword
            return None
    
    def get_keywords(self):
        with self.get_session() as db:
            return db.query(Keyword).all()

    def get_keyword_by_id(self, id: int):
        with self.get_session() as db:
            keyword = db.query(Keyword).filter_by(id=id).first()
            if keyword:
                return keyword
            return None
    def get_keywords_by_ids(self, ids: List[int]):
        with self.get_session() as db:
            keywords = db.query(Keyword).filter(Keyword.id.in_(ids)).all()
            if len(keywords) != len(ids):
                return None
            return keywords



    def create_document(
        self, 
        title: str, 
        summary: str, 
        link: str, 
        category_id: int,
        keyword_ids: List[int]
    ):
        with self.get_session() as db:
            category = self.get_category_by_id(category_id)
            if not category:
                return None
            keywords = self.get_keywords_by_ids(keyword_ids)
            if not keywords:
                return None
            doc = Document(
                title=title, 
                summary=summary, 
                link=link, 
                category_id=category.id,
                keywords=keywords
            )
            db.add(doc)
            db.commit()
            db.refresh(doc)
            return doc
        
    def get_documents_by_category(self, category_id: int):
        with self.get_session() as db:
            return db.query(Document) \
                .filter(Document.category_id == category_id) \
                .all()
    
    def get_documents_by_ids(self, ids: List[int]):
        with self.get_session() as db:
            return db.query(Document) \
                .filter(Document.id.in_(ids)) \
                .all()
