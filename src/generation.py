from typing import List
import os
from dotenv import load_dotenv
from google import genai


class ResponseGenerator:
    
    def __init__(self, model_name: str = "gemini-2.5-flash"):

        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
    
    def generate(self, query: str, chunks: List[str]) -> str:

        chunks_text = "\n\n".join(chunks)
        prompt = f"""你是一位知识助手，请根据用户的问题和下列片段生成准确的回答。

        用户问题: {query}

        相关片段:
        {chunks_text}

        请基于上述内容作答，不要编造信息。"""
        
        print(f"{prompt}\n\n---\n")

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )
        
        return response.text
