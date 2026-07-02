# RAG 设计

## 流程

```txt
上传文档 → MinIO 存储 → 文档解析 → 文本清洗 → Chunk 切分 → Embedding → pgvector 入库 → 问题向量化 → TopK 检索 → 组装上下文 → LLM 回答 → 引用来源展示
```

## 切分策略

- `chunk_size`: 800 字符
- `chunk_overlap`: 150 字符
- V2 增加 Markdown 标题切分与 Rerank

## 输出要求

RAG 回答必须展示：

- 直接答案
- 引用文档
- 引用片段
- 相似度分数
- chunk index

目标是降低幻觉，并让面试演示时能够说明“答案可核验”。
