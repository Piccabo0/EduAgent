from typing import List
from sentence_transformers import CrossEncoder

class Reranker:
    
    def __init__(self, model_name: str = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"):

        self.cross_encoder = CrossEncoder(model_name, cache_folder="d:/MyProject/EduAgent/models")
    
    def rerank(self, query: str, chunks: List[str], top_k: int = 3) -> List[str]:

        # 为每个 (query, chunk) 对生成得分
        pairs = [(query, chunk) for chunk in chunks]
        scores = self.cross_encoder.predict(pairs)
        
        # 按得分降序排序
        scored_chunks = list(zip(chunks, scores))
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        
        # 返回前 top_k 个
        return [chunk for chunk, _ in scored_chunks][:top_k]
