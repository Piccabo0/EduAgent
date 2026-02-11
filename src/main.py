import os
from dotenv import load_dotenv
from chunking import split_into_chunks
from indexing import VectorIndexer
from retrieval import Retriever
from reranking import Reranker
from generation import ResponseGenerator

# 加载环境变量
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
if HF_TOKEN:
    os.environ["HF_TOKEN"] = HF_TOKEN

def main():
    
    # Path setup
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(current_dir), 'data')
    doc_file = os.path.join(data_dir, 'doc.md')
    
    # 1. 分片
    chunks = split_into_chunks(doc_file)
    # for i, chunk in enumerate(chunks):
    #     print(f"[{i}] {chunk}\n")
    
    # 2. 索引
    indexer = VectorIndexer()
    # embeddings = [indexer.embed_chunk(chunk) for chunk in chunks]
    # print(len(embeddings))
    # print(embeddings[0])
    indexer.build_index(chunks)
    
    # 3. 初始化召回和重排
    retriever = Retriever(indexer)
    # query = "哆啦A梦使用的3个秘密道具分别是什么？"
    # retrieved_chunks = retriever.retrieve(query, 5)
    # for i, chunk in enumerate(retrieved_chunks):
    #     print(f"[{i}] {chunk}\n")

    reranker = Reranker()
    # query = "哆啦A梦使用的3个秘密道具分别是什么？"
    # retrieved_chunks = retriever.retrieve(query, 5)
    # reranked_chunks = reranker.rerank(query, retrieved_chunks, 3)
    # for i, chunk in enumerate(reranked_chunks):
    #     print(f"[{i}] {chunk}\n")

    # 4. 单次生成回答
    generator = ResponseGenerator()
    query = "哆啦A梦使用的3个秘密道具分别是什么？"
    retrieved_chunks = retriever.retrieve(query, 5)
    reranked_chunks = reranker.rerank(query, retrieved_chunks, 3)
    answer = generator.generate(query, reranked_chunks)
    print(answer)

    # # 4. 交互循环
    # print("\n" + "=" * 60)
    # print("进入交互模式（输入 'quit' 退出）")
    # print("=" * 60)
    
    # while True:
    #     query = input("\n请输入问题: ").strip()
        
    #     if query.lower() in ['quit', 'exit', 'q']:
    #         print("感谢使用，再见！")
    #         break
        
    #     if not query:
    #         continue
        
    #     # 4.1 召回
    #     print("\n[4.1] 召回相关文本...")
    #     retrieved_chunks = retriever.retrieve(query, top_k=5)
    #     print(f"   检索到 {len(retrieved_chunks)} 个相关文本块")
        
    #     # 4.2 重排
    #     print("\n[4.2] 重排文本块...")
    #     reranked_chunks = reranker.rerank(query, retrieved_chunks, top_k=3)
    #     print(f"   重排后保留 {len(reranked_chunks)} 个最相关的文本块")
        
    #     # 4.3 生成
    #     print("\n[4.3] 生成回答...")
    #     answer = generator.generate(query, reranked_chunks)
        
    #     print("\n" + "-" * 60)
    #     print("回答:")
    #     print("-" * 60)
    #     print(answer)
    #     print("-" * 60)


if __name__ == "__main__":
    main()
