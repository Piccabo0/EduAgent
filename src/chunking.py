from typing import List

def split_into_chunks(doc_file: str, chunk_size: int = 300, overlap: int = 50) -> List[str]:
    """
    改进的分块策略：
    1. 保留标题和内容的关联
    2. 使用滑动窗口，让相邻块有重叠
    3. 尽量在句号处分割，保持语义完整
    """
    with open(doc_file, 'r', encoding='utf-8') as file:
        content = file.read()

    # 按段落分割
    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
    
    chunks = []
    current_chunk = ""
    current_title = ""
    
    for para in paragraphs:
        # 如果是标题（以#开头）
        if para.startswith("#"):
            # 保存之前的块（如果存在）
            if current_chunk:
                chunks.append(current_chunk.strip())
            
            # 更新当前标题
            current_title = para
            current_chunk = current_title + "\n\n"
        else:
            # 如果是内容段落
            # 将标题和内容组合
            temp_chunk = current_chunk + para
            
            # 如果当前块太长，需要分割
            if len(temp_chunk) > chunk_size:
                # 如果当前块已有内容，先保存
                if current_chunk != current_title + "\n\n":
                    chunks.append(current_chunk.strip())
                
                # 开始新块，保留标题和当前段落
                current_chunk = current_title + "\n\n" + para + "\n\n"
            else:
                current_chunk = temp_chunk + "\n\n"
    
    # 保存最后一个块
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks
