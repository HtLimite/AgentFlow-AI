# 数据库设计

第一阶段使用 PostgreSQL + pgvector。

核心表：

- `sys_user`：用户表
- `ai_model_provider`：模型供应商
- `ai_model`：模型配置
- `knowledge_base`：知识库
- `knowledge_document`：知识库文档
- `knowledge_chunk`：文本切片与向量
- `agent`：Agent 配置
- `agent_tool`：工具定义
- `llm_call_log`：模型调用日志

向量索引：

```sql
CREATE INDEX idx_knowledge_chunk_embedding
ON knowledge_chunk
USING hnsw (embedding vector_cosine_ops);
```

后续会补充 Alembic 迁移、Prompt 版本、工作流运行、评测集、审计日志。
