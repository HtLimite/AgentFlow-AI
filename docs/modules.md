# 模块设计

本文档统一维护数据库、RAG、Agent、Workflow、Prompt、Eval 和可观测性设计，避免模块文档分散后口径过期。

## 1. 数据库与持久化

当前使用 PostgreSQL + pgvector，V4 主链路要求数据库真实可连，内存 fallback 只作为开发兜底。

### 核心表

| 表 | 作用 |
|---|---|
| `sys_user` | 用户表 |
| `tenant` / RBAC 相关表 | 租户、角色、权限上下文 |
| `ai_model_provider` | 模型供应商 |
| `ai_model` | 模型配置 |
| `knowledge_base` | 知识库 |
| `knowledge_document` | 知识库文档 |
| `knowledge_chunk` | 文本切片与向量 |
| `agent` | Agent 配置 |
| `agent_tool` | 工具定义 |
| `tool_audit_log` | 工具调用持久化审计 |
| `llm_call_log` | 模型调用日志 |
| `prompt_template` | Prompt 模板 |
| `prompt_version` | Prompt 版本 |
| `workflow_run` | 工作流运行 |
| `workflow_node_run` | 工作流节点运行 |
| `eval_dataset` / `eval_run` | 评测数据集与运行记录 |

### 向量索引

```sql
CREATE INDEX idx_knowledge_chunk_embedding
ON knowledge_chunk
USING hnsw (embedding vector_cosine_ops);
```

## 2. RAG 设计

### 当前流程

```txt
文档上传 → 文本解析 → PDF 文本提取 → chunk 切分 → 向量写入 → SQL 相似度检索 → RAG 回答 → 引用来源展示
```

### 文档解析策略

- txt / md：按 UTF-8 / GB18030 解码，并清理不可见控制字符。
- PDF：使用 pypdf 提取页面文本。
- 扫描版 PDF：如果没有可提取文本，会返回明确错误，提示先 OCR。
- 二进制保护：不再把 `%PDF-1.7`、压缩流或乱码内容写入知识库切片。

### 回答结构

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
    "strategy": "pgvector_sql"
  }
}
```

## 3. Agent 与工具调用

### 内置工具

- `knowledge_search`：知识库检索。
- `calculator`：安全计算器。
- `sql_query`：只读 SQL 查询演示。
- `http_request`：HTTP 请求安全演示。

### 调用流程

```txt
用户问题 → Agent 选择工具 → 构建工具参数 → Tool Registry 执行 → 写入 tool_audit_log → 返回 tool_calls → 生成最终回答
```

### 可观测字段

```json
{
  "trace_id": "trace_xxx",
  "tool_calls": [
    {
      "tool_name": "knowledge_search",
      "input": {},
      "output": {},
      "status": "success",
      "persistent_audit_id": 1,
      "error_message": null
    }
  ]
}
```

### 安全边界

- SQL 工具只允许 SELECT。
- HTTP 工具禁止本地地址和高风险内网地址。
- 计算器只允许基础表达式 AST。
- 未注册工具返回 failed 状态。
- 生产化阶段仍需继续强化 SSRF、SQL 只读策略和审计策略。

## 4. Workflow 设计

### 当前实现

当前版本已经从串行执行器升级到 React Flow 工作流画布基础版。

### 节点类型

- `start`：输入节点。
- `knowledge`：知识库检索节点。
- `llm`：回答生成节点。
- `condition`：条件节点预留。
- `http`：HTTP 节点预留。
- `end`：结束节点。

### Definition 示例

```json
{
  "nodes": [
    { "id": "start_1", "type": "start", "data": {} },
    { "id": "knowledge_1", "type": "knowledge", "data": { "kb_id": 1, "top_k": 3 } },
    { "id": "llm_1", "type": "llm", "data": { "prompt": "根据知识库结果回答：{{question}}" } },
    { "id": "end_1", "type": "end", "data": {} }
  ],
  "edges": [
    { "source": "start_1", "target": "knowledge_1" },
    { "source": "knowledge_1", "target": "llm_1" },
    { "source": "llm_1", "target": "end_1" }
  ]
}
```

### 执行流程

```txt
读取 definition → 找 Start → 沿 edge 执行节点 → 保存节点输入输出 → End 停止 → 返回 node_runs
```

## 5. Prompt / Eval

### Prompt

- 支持 Prompt 模板。
- 支持变量渲染。
- 支持版本记录。
- 支持页面测试。

### Eval

- 支持评测数据集。
- 支持评测运行。
- 支持三组 Prompt / 模型横向对比。
- 当前仍是演示评测，真实 LLM-as-Judge 放在 V5。

## 6. Dashboard / Observability

当前 Dashboard 聚合：

- 今日调用量。
- Token 消耗。
- 平均耗时。
- 失败率。
- 数据来源：数据库优先。

后续增强：

- 真实供应商 token / cost / latency 采集。
- 按模型、供应商、租户、业务模块筛选。
- 失败原因分类和趋势图。
