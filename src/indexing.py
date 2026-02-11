from typing import List
import chromadb
from sentence_transformers import SentenceTransformer

class VectorIndexer:
    
    def __init__(self, model_path: str = "shibing624/text2vec-base-chinese"):

        self.embedding_model = SentenceTransformer(model_path, cache_folder="d:/MyProject/EduAgent/models")
        self.chromadb_client = chromadb.EphemeralClient()
        self.collection = self.chromadb_client.get_or_create_collection(name="documents")
    
    def embed_chunk(self, chunk: str) -> List[float]:

        embedding = self.embedding_model.encode(chunk, normalize_embeddings=True)
        return embedding.tolist()
    
    def embed_chunks(self, chunks: List[str]) -> List[List[float]]:

        return [self.embed_chunk(chunk) for chunk in chunks]
    
    def save_embeddings(self, chunks: List[str], embeddings: List[List[float]]) -> None:

        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            self.collection.add(
                documents=[chunk],
                embeddings=[embedding],
                ids=[str(i)]
            )
    
    def build_index(self, chunks: List[str]) -> None:

        embeddings = self.embed_chunks(chunks)
        self.save_embeddings(chunks, embeddings)
