# EduAgent

基于 RAG（Retrieval-Augmented Generation）框架的教育智能体系统。

## 项目结构

```
EduAgent/
├── src/                    # 源代码目录
│   ├── __init__.py        # 包初始化文件
│   ├── main.py            # 主程序入口
│   ├── chunking.py        # 文本分片模块
│   ├── indexing.py        # 向量索引模块
│   ├── retrieval.py       # 文本召回模块
│   ├── reranking.py       # 结果重排模块
│   └── generation.py      # 回答生成模块
├── data/                   # 数据目录
│   └── doc.md             # 示例文档（包含"哆啦A梦与超级赛亚人"故事）
├── requirements.txt        # 项目依赖
└── README.md              # 项目说明文档
```

## 核心模块说明

### 1. 分片模块 (chunking.py)
- **功能**：将原始文档分割成多个文本块
- **关键函数**：`split_into_chunks(doc_file, separator)`
- **作用**：提高索引和检索的精度

### 2. 索引模块 (indexing.py)
- **功能**：为文本块生成向量嵌入并保存到向量数据库
- **关键类**：`VectorIndexer`
- **使用的模型**：`shibing624/text2vec-base-chinese`（中文向量模型）
- **向量库**：ChromaDB（开源向量数据库）

### 3. 召回模块 (retrieval.py)
- **功能**：根据用户查询检索最相关的文本块
- **关键类**：`Retriever`
- **检索方式**：基于向量相似度的 K-NN 搜索

### 4. 重排模块 (reranking.py)
- **功能**：对检索结果进行重新排序，提高相关性
- **关键类**：`Reranker`
- **使用的模型**：`cross-encoder/mmarco-mMiniLMv2-L12-H384-v1`（交叉编码器）

### 5. 生成模块 (generation.py)
- **功能**：使用大语言模型生成最终的回答
- **关键类**：`ResponseGenerator`
- **使用的模型**：Google Gemini 2.5 Flash
- **需要**：Google API 密钥（需在 .env 文件中配置）

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本使用

```bash
python src/main.py
```

### 示例交互

```
请输入问题: 哆啦A梦使用的3个秘密道具分别是什么？

[4.1] 召回相关文本...
[4.2] 重排文本块...
[4.3] 生成回答...

回答:
根据提供的片段，哆啦A梦使用的3个秘密道具分别是：
1. 复制斗篷：可以临时赋予超级战力。
2. 时间停止手表：能暂停时间五秒。
3. 精神与时光屋便携版：可在一分钟中完成一年修行。
```

## 系统流程

```
用户查询
  ↓
[分片] 文档 → 文本块
  ↓
[索引] 文本块 → 向量 → 数据库
  ↓
[召回] 查询向量 → 相似度搜索 → 候选块
  ↓
[重排] 候选块 → 交叉编码器评分 → 排序
  ↓
[生成] 最相关块 + 查询 → LLM → 回答
  ↓
最终回答
```

## 依赖包说明

- `sentence-transformers`: 提供向量嵌入和交叉编码器功能
- `chromadb`: 开源向量数据库
- `google-genai`: Google AI Studio API 客户端
- `python-dotenv`: 环境变量管理
- `numpy`: 数值计算库
- `torch`: PyTorch 深度学习框架

## 环境配置

需要在项目根目录创建 `.env` 文件，并配置 Google API 密钥：

```
GOOGLE_API_KEY=your_api_key_here
```

## 功能特性

✅ 模块化设计，易于扩展  
✅ 支持中文文本处理  
✅ 基于向量相似度的精准检索  
✅ 使用交叉编码器的智能重排  
✅ 集成大语言模型的自然回答生成  
✅ 完整的 RAG 流程实现  

## 后续扩展方向

- [ ] 支持更多语言的文档
- [ ] 添加多种向量模型选择
- [ ] 实现批量处理功能
- [ ] 添加缓存机制优化性能
- [ ] Web 界面集成
- [ ] 结果的相关性评估

## 许可证

MIT License
