# 数据库设计

第一阶段使用 PostgreSQL + pgvector，当前演示服务中部分数据使用内存结构，方便离线演示；生产化时按本设计落库。

## 核心表

- `sys_user`：用户表
- `ai_model_provider`：模型供应商
- `ai_model`：模型配置
- `knowledge_base`：知识库
- `knowledge_document`：知识库文档
- `knowledge_chunk`：文本切片与向量
- `agent`：Agent 配置
- `agent_tool`：工具定义
- `llm_call_log`：模型调用日志
- `prompt_template`：Prompt 模板
- `prompt_version`：Prompt 版本
- `workflow_run`：工作流运行
- `eval_run`：评测运行

## 向量索引

```sql
CREATE INDEX idx_knowledge_chunk_embedding
ON knowledge_chunk
USING hnsw (embedding vector_cosine_ops);
```

## 当前演示与生产迁移关系

- 内存 PromptService → `prompt_template` / `prompt_version`
- 内存 ObservabilityService → `llm_call_log`
- 内存 KnowledgeService → `knowledge_base` / `knowledge_document` / `knowledge_chunk`
- 内存 WorkflowEngine → `workflow_run` / `workflow_node_run`
