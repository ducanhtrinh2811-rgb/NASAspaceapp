from .config import WEAVIATE_CONFIG
import weaviate
from weaviate.classes.config import Property, DataType, Configure
from weaviate.classes.query import Filter
import os
import time


class WeaviateVectorStore:
    def __init__(self, max_retries=10, retry_delay=3):
        self.collection_name = WEAVIATE_CONFIG['collection_name']
        self.client = None
        
        # Dùng tên service trong Docker, không dùng localhost
        host = os.getenv('WEAVIATE_HOST', 'weaviate')
        port = int(os.getenv('WEAVIATE_PORT', 8080))
        grpc_port = int(os.getenv('WEAVIATE_GRPC_PORT', 50051))
        
        for attempt in range(max_retries):
            try:
                print(f"[INFO] Connecting to Weaviate at {host}:{port} (attempt {attempt + 1}/{max_retries})...")
                
                self.client = weaviate.connect_to_local(
                    host=host,
                    port=port,
                    grpc_port=grpc_port
                )
                
                self.client.is_ready()
                print(f"[SUCCESS] Connected to Weaviate at {host}:{port}!")
                break
                
            except Exception as e:
                print(f"[WARNING] Attempt {attempt + 1} failed: {str(e)[:100]}")
                if attempt < max_retries - 1:
                    print(f"[INFO] Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    raise Exception(f"Cannot connect to Weaviate at {host}:{port} after {max_retries} attempts")
        
        if not self.client.collections.exists(self.collection_name):
            self._create_collection()
        
        self.collection = self.client.collections.get(self.collection_name)
    def _create_collection(self):
        """Tạo collection với schema"""
        self.client.collections.create(
            name=self.collection_name,
            properties=[
                Property(name='doc_id', data_type=DataType.INT)
            ],
            vector_config=[
                Configure.Vectors.self_provided(name='title_vector'),
                Configure.Vectors.self_provided(name='summary_vector')
            ]
        )
        print(f"[INFO] Created collection: {self.collection_name}")

    def close(self):
        if self.client:
            self.client.close()
    
    def add_document(self, doc_id, title_embedding, summary_embedding):
        """Thêm document vào vector store với kiểm tra duplicate"""
        try:
            # Kiểm tra xem doc_id đã tồn tại chưa
            existing = self.collection.query.fetch_objects(
                filters=Filter.by_property("doc_id").equal(doc_id),
                limit=1
            )
            
            if existing.objects:
                print(f"[WARNING] Vector for doc_id {doc_id} already exists, skipping...")
                return
            
            self.collection.data.insert(
                properties={
                    'doc_id': doc_id,
                },
                vector={
                    'title_vector': title_embedding,
                    'summary_vector': summary_embedding
                }
            )
        except Exception as e:
            print(f"[ERROR] Failed to add document {doc_id}: {e}")
            raise
    
    def similarity_search(self, query_vector, k: int = 10):
        """Tìm kiếm documents tương tự"""
        response = self.collection.query.near_vector(
            near_vector=query_vector,
            limit=k,
            target_vector=['title_vector', 'summary_vector']
        )
        objects = response.objects
        
        # Loại bỏ duplicate doc_ids
        seen_ids = set()
        unique_doc_ids = []
        
        for obj in objects:
            doc_id = obj.properties.get('doc_id')
            if doc_id and doc_id not in seen_ids:
                unique_doc_ids.append(doc_id)
                seen_ids.add(doc_id)
        
        return unique_doc_ids
    
    def get_object_count(self):
        """Đếm số lượng objects trong collection"""
        try:
            response = self.collection.aggregate.over_all(total_count=True)
            count = response.total_count
            return count
        except Exception as e:
            print(f"[ERROR] Failed to count objects: {e}")
            return 0
    
    def clear_all(self):
        """Xóa toàn bộ dữ liệu trong vector store"""
        try:
            if self.client.collections.exists(self.collection_name):
                print(f"[INFO] Deleting collection: {self.collection_name}")
                self.client.collections.delete(self.collection_name)
                
                # Tạo lại collection
                self._create_collection()
                self.collection = self.client.collections.get(self.collection_name)
                print(f"[SUCCESS] Vector store cleared and recreated")
            else:
                print(f"[INFO] Collection {self.collection_name} does not exist")
                
        except Exception as e:
            print(f"[ERROR] Failed to clear vector store: {e}")
            raise
    
    def delete_by_doc_id(self, doc_id: int):
        """Xóa vectors của một document cụ thể"""
        try:
            result = self.collection.data.delete_many(
                where=Filter.by_property("doc_id").equal(doc_id)
            )
            print(f"[INFO] Deleted vectors for doc_id {doc_id}")
            return result
        except Exception as e:
            print(f"[ERROR] Failed to delete doc_id {doc_id}: {e}")
            raise
    
    def check_duplicates(self):
        """Kiểm tra duplicate doc_ids trong vector store"""
        try:
            all_objects = self.collection.query.fetch_objects(limit=10000)
            
            doc_ids = [obj.properties['doc_id'] for obj in all_objects.objects]
            
            from collections import Counter
            doc_id_counts = Counter(doc_ids)
            duplicates = {doc_id: count for doc_id, count in doc_id_counts.items() if count > 1}
            
            if duplicates:
                print("\n[WARNING] Found duplicate doc_ids in vector store:")
                for doc_id, count in duplicates.items():
                    print(f"  - doc_id {doc_id}: {count} times")
                return duplicates
            else:
                print("[INFO] No duplicates found in vector store")
                return {}
                
        except Exception as e:
            print(f"[ERROR] Failed to check duplicates: {e}")
            return {}