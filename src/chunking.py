from typing import List
import re

def split_into_chunks(doc_file: str, use_semantic: bool = True, chunk_size: int = 500, overlap: int = 100) -> List[str]:
    """
    文档分块的统一入口
    
    Args:
        doc_file: 文档文件路径
        use_semantic: 是否使用语义分块（按标题），默认True
        chunk_size: 字符数分块时的大小（仅在use_semantic=False时使用）
        overlap: 字符数分块时的重叠（仅在use_semantic=False时使用）
    
    Returns:
        List[str]: 分割后的文本块列表
    """
    if use_semantic:
        return split_into_chunks_by_title(doc_file)
    else:
        return split_into_chunks_by_chars(doc_file, chunk_size, overlap)

def split_into_chunks_by_title(file_path: str) -> List[str]:
    """
    基于标题的语义分块，适用于KMC知识库结构
    每个chunk包含一个完整的教学模块：标题 + 【知识点】 + 【易错点】 + 【启发式教学建议】
    
    Args:
        file_path: 文档文件路径
    
    Returns:
        List[str]: 分割后的文本块列表，每个块包含完整的教学模块
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except FileNotFoundError:
        print(f"文件未找到: {file_path}")
        return []
    except Exception as e:
        print(f"读取文件时出错: {e}")
        return []
    
    # 按行分割内容
    lines = content.split('\n')
    
    chunks = []
    current_chunk = []
    
    # 匹配标题的正则表达式 (# ## ### 等)
    title_pattern = re.compile(r'^#+\s+(.+)$')
    
    for line in lines:
        line = line.strip()
        
        # 检查是否是标题行
        if title_pattern.match(line):
            # 如果当前chunk不为空，保存它
            if current_chunk:
                chunk_text = '\n'.join(current_chunk).strip()
                if chunk_text:
                    chunks.append(chunk_text)
                current_chunk = []
            
            # 开始新的chunk
            current_chunk.append(line)
        else:
            # 添加到当前chunk
            if line:  # 只添加非空行
                current_chunk.append(line)
            elif current_chunk and current_chunk[-1]:  # 保留段落间的空行
                current_chunk.append('')
    
    # 添加最后一个chunk
    if current_chunk:
        chunk_text = '\n'.join(current_chunk).strip()
        if chunk_text:
            chunks.append(chunk_text)
    
    return chunks

def split_into_chunks_by_chars(file_path: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
    """
    基于字符数的传统分块方法（备用方案）
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except FileNotFoundError:
        print(f"文件未找到: {file_path}")
        return []
    except Exception as e:
        print(f"读取文件时出错: {e}")
        return []
    
    # 移除多余的空白字符
    content = ' '.join(content.split())
    
    chunks = []
    start = 0
    
    while start < len(content):
        # 计算当前块的结束位置
        end = start + chunk_size
        
        # 如果不是最后一块，尝试在合适位置分割
        if end < len(content):
            # 寻找最近的句子结束符或标点符号
            punctuation = ['。', '！', '？', '.', '!', '?', '\n', '；', ';']
            best_split = end
            
            # 在chunk_size的前100个字符内寻找合适的分割点
            search_start = max(start + chunk_size - 100, start + chunk_size // 2)
            for i in range(end, search_start - 1, -1):
                if i < len(content) and content[i] in punctuation:
                    best_split = i + 1
                    break
            
            end = best_split
        
        # 提取当前块
        chunk = content[start:end].strip()
        if chunk:  # 只添加非空块
            chunks.append(chunk)
        
        # 计算下一块的开始位置（考虑重叠）
        start = end - overlap
        
        # 避免无限循环
        if start >= end:
            start = end
    
    return chunks
