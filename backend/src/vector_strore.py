from .config import WEAVIATE_CONFIG
import weaviate
from weaviate.classes.config import Property, DataType, Configure


class WeaviateVectorStore:
    def __init__(self):
        self.client = weaviate.connect_to_local(
            host=WEAVIATE_CONFIG['host'],
            port=WEAVIATE_CONFIG['port'],
            grpc_port=WEAVIATE_CONFIG['grpc_port']
        )
        self.collection_name = WEAVIATE_CONFIG['collection_name']

        if not self.client.collections.exists(self.collection_name):
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
        
        self.collection = self.client.collections.get(self.collection_name)

    def close(self):
        if self.client:
            self.client.close()
    
    def add_document(self, doc_id, title_embedding, summary_embedding):
        self.collection.data.insert(
            properties={
                'doc_id': doc_id,
            },
            vector={
                'title_vector': title_embedding,
                'summary_vector': summary_embedding
            }
        )
    
    def similarity_search(
        self,
        query_vector,
        k: int = 10
    ):
        response = self.collection.query.near_vector(
            near_vector=query_vector,
            limit=k,
            target_vector=['title_vector', 'summary_vector']
        )
        objects = response.objects
        return [
            obj.properties['doc_id'] 
            for obj in objects 
            if obj.properties.get('doc_id', None)
        ]