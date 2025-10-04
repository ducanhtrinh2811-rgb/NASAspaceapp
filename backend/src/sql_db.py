from .config import POSTGRES_CONFIG
from sqlalchemy import create_engine, inspect, func
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
        db = self.get_session()
        try:
            category = db.query(Category).filter_by(name=name).first()
            if category:
                return category
            category = Category(name=name)
            db.add(category)
            db.commit()
            db.refresh(category)
            return category
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
    
    def get_category_by_name(self, name: str):
        db = self.get_session()
        try:
            return db.query(Category).filter_by(name=name).first()
        finally:
            db.close()
    
    def get_categories(self):
        db = self.get_session()
        try:
            return db.query(Category).all()
        finally:
            db.close()
    
    def get_category_by_id(self, id: int):
        db = self.get_session()
        try:
            return db.query(Category).filter_by(id=id).first()
        finally:
            db.close()

    def create_keyword(self, name: str):
        db = self.get_session()
        try:
            keyword = db.query(Keyword).filter_by(name=name).first()
            if keyword:
                return keyword
            keyword = Keyword(name=name)
            db.add(keyword)
            db.commit()
            db.refresh(keyword)
            return keyword
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
    
    def get_keyword_by_name(self, name: str):
        db = self.get_session()
        try:
            return db.query(Keyword).filter_by(name=name).first()
        finally:
            db.close()
    
    def get_keywords(self):
        db = self.get_session()
        try:
            return db.query(Keyword).all()
        finally:
            db.close()

    def get_keyword_by_id(self, id: int):
        db = self.get_session()
        try:
            return db.query(Keyword).filter_by(id=id).first()
        finally:
            db.close()
    
    def get_keywords_by_ids(self, ids: List[int]):
        db = self.get_session()
        try:
            keywords = db.query(Keyword).filter(Keyword.id.in_(ids)).all()
            if len(keywords) != len(ids):
                return None
            return keywords
        finally:
            db.close()

    def create_document(
        self, 
        title: str, 
        summary: str, 
        link: str, 
        category_id: int,
        keyword_ids: List[int]
    ):
        db = self.get_session()
        try:
            # Kiểm tra duplicate link
            existing = db.query(Document).filter_by(link=link).first()
            if existing:
                print(f"[WARNING] Document with link already exists: {title[:50]}...")
                print(f"[INFO] Updating document ID: {existing.id}")
                
                # Cập nhật thông tin
                existing.title = title
                existing.summary = summary
                existing.category_id = category_id
                
                # Cập nhật keywords
                keywords = db.query(Keyword).filter(Keyword.id.in_(keyword_ids)).all()
                existing.keywords = keywords
                
                db.commit()
                db.refresh(existing)
                return existing
            
            # Kiểm tra category tồn tại
            category = db.query(Category).filter_by(id=category_id).first()
            if not category:
                print(f"[ERROR] Category {category_id} not found")
                return None

            # Kiểm tra keywords tồn tại
            keywords = db.query(Keyword).filter(Keyword.id.in_(keyword_ids)).all()
            if len(keywords) != len(keyword_ids):
                print(f"[ERROR] Some keywords not found")
                return None

            # Tạo document mới
            doc = Document(
                title=title,
                summary=summary,
                link=link,
                category=category,
                keywords=keywords
            )
            db.add(doc)
            db.commit()
            db.refresh(doc)
            return doc
        except Exception as e:
            db.rollback()
            print(f"[ERROR] Failed to create document: {e}")
            raise
        finally:
            db.close()
        
    def get_documents_by_category(self, category_id: int):
        db = self.get_session()
        try:
            docs = db.query(Document).filter(Document.category_id == category_id).all()
            
            # Loại bỏ duplicate dựa trên link
            seen_links = set()
            unique_docs = []
            
            for doc in docs:
                if doc.link not in seen_links:
                    seen_links.add(doc.link)
                    unique_docs.append(doc)
            
            return unique_docs
        finally:
            db.close()
    
    def get_documents_by_ids(self, ids: List[int]):
        db = self.get_session()
        try:
            docs = db.query(Document).filter(Document.id.in_(ids)).all()
            
            # Sắp xếp theo thứ tự ids và loại bỏ duplicate
            docs_dict = {d.id: d for d in docs}
            ordered_docs = []
            seen_ids = set()
            
            for doc_id in ids:
                if doc_id in docs_dict and doc_id not in seen_ids:
                    ordered_docs.append(docs_dict[doc_id])
                    seen_ids.add(doc_id)
            
            return ordered_docs
        finally:
            db.close()
    
    # Thêm các methods mới
    def get_all_documents(self):
        db = self.get_session()
        try:
            return db.query(Document).all()
        finally:
            db.close()
    
    def get_document_count(self):
        db = self.get_session()
        try:
            return db.query(Document).count()
        finally:
            db.close()
    
    def clear_all_data(self):
        db = self.get_session()
        try:
            print("[INFO] Clearing database...")
            
            # Xóa theo thứ tự để tránh foreign key constraint
            db.query(Document).delete()
            db.query(Keyword).delete()
            db.query(Category).delete()
            
            db.commit()
            print("[SUCCESS] Database cleared successfully!")
            
        except Exception as e:
            db.rollback()
            print(f"[ERROR] Failed to clear database: {e}")
            raise
        finally:
            db.close()
    
    def check_duplicates(self):
        db = self.get_session()
        try:
            # Tìm các link xuất hiện nhiều hơn 1 lần
            duplicates = (
                db.query(
                    Document.link,
                    func.count(Document.id).label('count')
                )
                .group_by(Document.link)
                .having(func.count(Document.id) > 1)
                .all()
            )
            
            if duplicates:
                print("\n[WARNING] Found duplicate documents:")
                for link, count in duplicates:
                    print(f"  - {link[:80]}... ({count} times)")
                    
                    # Hiển thị chi tiết
                    docs = db.query(Document).filter_by(link=link).all()
                    for doc in docs:
                        print(f"    ID: {doc.id}, Title: {doc.title[:60]}...")
                
                return duplicates
            else:
                print("[INFO] No duplicate documents found!")
                return []
        finally:
            db.close()
    
    def remove_duplicates(self, keep='first'):
        db = self.get_session()
        try:
            # Tìm duplicates
            duplicates = (
                db.query(Document.link, func.count(Document.id))
                .group_by(Document.link)
                .having(func.count(Document.id) > 1)
                .all()
            )
            
            if not duplicates:
                print("[INFO] No duplicates to remove")
                return 0
            
            removed_count = 0
            for link, count in duplicates:
                docs = db.query(Document).filter_by(link=link).order_by(Document.id).all()
                
                if keep == 'first':
                    to_keep = docs[0]
                    to_remove = docs[1:]
                else:
                    to_keep = docs[-1]
                    to_remove = docs[:-1]
                
                print(f"\n[INFO] Processing: {to_keep.title[:60]}...")
                print(f"  Keeping ID: {to_keep.id}")
                print(f"  Removing IDs: {[d.id for d in to_remove]}")
                
                for doc in to_remove:
                    db.delete(doc)
                    removed_count += 1
            
            db.commit()
            print(f"\n[SUCCESS] Removed {removed_count} duplicate documents")
            return removed_count
            
        except Exception as e:
            db.rollback()
            print(f"[ERROR] Failed to remove duplicates: {e}")
            raise
        finally:
            db.close()