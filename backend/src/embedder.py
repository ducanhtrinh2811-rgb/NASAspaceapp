from .config import HUGGING_FACE_MODEL_NAME
from sentence_transformers import SentenceTransformer

class Embedder:
    def __init__(self):
        self.model = SentenceTransformer(HUGGING_FACE_MODEL_NAME)
    
    def embed(self, text):
        return self.model.encode(text, normalize_embeddings=True, convert_to_numpy=True).tolist()

    def embed_batch(self, texts):
        return self.model.encode(texts, normalize_embeddings=True, convert_to_numpy=True).tolist()