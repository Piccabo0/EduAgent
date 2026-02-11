from typing import List
from sentence_transformers import SentenceTransformer


class Retriever:
    
    def __init__(self, indexer):

        self.indexer = indexer
        self.embedding_model = indexer.embedding_model
        self.collection = indexer.collection
    
    def retrieve(self, query: str, top_k: int = 5) -> List[str]:

        query_embedding = self.indexer.embed_chunk(query)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        return results['documents'][0]
