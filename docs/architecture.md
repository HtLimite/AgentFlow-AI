# 架构设计

AgentFlow-AI 采用前后端分离 + Monorepo 结构，当前推荐运行模式是本地 Web/API + Docker 基础设施。

```txt
Next.js Web
  ↓ REST / SSE
FastAPI API
  ↓
PostgreSQL + pgvector / Redis / MinIO
  ↓
OpenAI-Compatible Model Providers
```

## 目录边界

```txt
apps/
  web/        Next.js 管理台
  api/        FastAPI 后端
deploy/
  postgres/   数据库初始化与迁移 SQL
  docker-compose.yml
docs/
  README.md   文档中心入口
scripts/
  dev-*.cmd   Windows 本地启动脚本
  verify-*    本地验收脚本
```

## 模块边界

| 模块 | 责任 |
|---|---|
| Web | 管理台、Chat、知识库、Agent、Workflow、Prompt、Eval、Settings、Audit、Dashboard |
| API | 统一路由、模型网关、RAG、Agent 工具调用、工作流执行、日志统计、RBAC 上下文 |
| PostgreSQL | 业务数据、知识库数据、向量数据、调用日志、工具审计 |
| pgvector | 知识库 chunk 向量存储与 SQL 相似度检索 |
| Redis | 缓存、任务队列预留 |
| MinIO | 上传文档与解析产物存储 |
| Model Provider | OpenAI-Compatible Chat / Embedding 扩展点 |

## 核心运行链路

### RAG

```txt
上传文档
→ 文本/PDF 解析
→ 清洗控制字符和二进制内容
→ chunk 切分
→ 生成本地确定性向量或真实 Embedding
→ 写入 PostgreSQL / pgvector
→ SQL 相似度检索
→ 生成回答和引用来源
```

### Agent

```txt
用户问题
→ Agent 选择工具
→ Tool Registry 执行工具
→ 写入 tool_audit_log
→ 返回 trace_id / persistent_audit_id / tool_calls
→ 汇总最终回答
```

### Workflow

```txt
React Flow 画布配置
→ 保存节点与连线 definition
→ 后端按 edge 执行节点
→ 保存 node_runs
→ 前端展示每个节点输入输出
```

### Observability

```txt
模型调用 / Agent 工具调用 / Workflow 运行
→ 写入日志和审计表
→ Dashboard 聚合调用量、Token、耗时、失败率和来源
```

## 当前设计原则

- 当前状态统一以 `docs/current-status.md` 为准。
- 本地启动统一以 `docs/local-development.md` 为准。
- 验收统一以 `docs/verification.md` 和脚本输出为准。
- 模块细节统一维护在 `docs/modules.md`，避免散落多个过期小文档。
