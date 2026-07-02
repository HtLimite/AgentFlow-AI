# RAG 设计

## 当前实现

当前版本实现轻量 RAG 闭环：

```txt
文档上传 → 文本解析 → PDF 文本提取 → chunk 切分 → 本地确定性向量 → 检索排序 → RAG 回答 → 引用来源展示
```

## 文档解析策略

- txt / md：按 UTF-8 / GB18030 解码，并清理不可见控制字符
- PDF：使用 pypdf 提取页面文本
- 扫描版 PDF：如果没有可提取文本，会返回 400，提示先 OCR
- 二进制保护：不再把 `%PDF-1.7`、压缩流或乱码内容写入知识库切片

## 为什么先用本地向量

求职项目第一阶段的重点是展示完整工程闭环和模块边界。本地向量服务具备确定性、无需外部模型依赖、便于离线演示。后续可以替换为真实 Embedding 模型和 pgvector。

## 生产替换点

- `app/services/document_parser.py`：替换或增强 PDF、Word、Excel、OCR 解析能力
- `app/services/vector_service.py`：替换为真实 Embedding Provider
- `app/services/knowledge_service.py`：将内存数据替换为 PostgreSQL + pgvector
- `deploy/postgres/init.sql`：已经预留 `knowledge_chunk.embedding VECTOR(1536)`

## 回答结构

RAG 接口返回：

```json
{
  "answer": "最终回答",
  "citations": [
    {
      "document": "来源文档",
      "content": "命中片段",
      "score": 0.91,
      "chunk_index": 0
    }
  ],
  "debug": {
    "strategy": "local_vector"
  }
}
```
