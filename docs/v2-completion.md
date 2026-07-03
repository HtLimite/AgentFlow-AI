# V2 完成说明

## V2 目标

V2 目标是把 V1.5 的“可演示作品”升级为“真实工程基础态”。本阶段重点不是继续堆页面，而是补齐持久化、真实供应商适配、Embedding 门面、部署初始化、可观测数据落库和 V2 验收脚本。

## 已完成范围

| 模块 | V2 完成内容 |
|---|---|
| Knowledge | 知识库、文档、切片数据库优先；数据库不可用时 fallback 到内存演示 |
| Embedding | 新增 `EmbeddingService` 门面，默认本地确定性向量，可替换真实 Provider |
| Model Provider | 新增 Provider Adapter，Settings 测试接口可真实探测供应商可达性 |
| Chat | Chat Completion 可优先走已配置供应商，失败时 fallback 到本地演示回答 |
| Prompt | 新增 Prompt 持久化服务，支持模板、版本、变量渲染落库 |
| Workflow | 新增 Workflow definition、run、node_run 持久化服务 |
| Eval | 新增 Eval dataset、case、run 持久化服务 |
| Observability | LLM 调用日志、Token、成本、耗时写入数据库，Dashboard 数据库优先聚合 |
| Deploy | Docker PostgreSQL 初始化改为执行 `deploy/postgres/*.sql` 全部脚本 |
| Verify | 本地验收脚本升级为 10 步 V2 验收 |

## 数据库脚本

- `deploy/postgres/init.sql`：基础表与 pgvector 初始化
- `deploy/postgres/002_tenant_audit.sql`：租户与审计扩展
- `deploy/postgres/003_v2_persistence.sql`：Prompt / Workflow / Eval / Observability 持久化表

Docker 新库启动时会按文件名顺序执行全部 SQL 脚本。

## V2 验收命令

```bash
pnpm build:web
cd apps/api
python -m compileall app
python -m pytest
```

接口验收：

```bash
bash scripts/verify-local.sh
```

Windows：

```cmd
scripts\verify-local.cmd
```

## V2 验收接口覆盖

- `GET /health`
- `GET /api/system/health/full`
- `GET /api/dashboard/summary`
- `GET /api/knowledge-bases`
- `POST /api/knowledge-bases/1/query`
- `GET /api/tools`
- `POST /api/agents/1/chat`
- `GET /api/prompts`
- `POST /api/workflows/1/run`
- `POST /api/evals/runs`

## 仍可继续增强

V2 已经完成真实工程基础，但以下内容可以作为 V3 或生产化增强：

- React Flow 拖拽工作流画布
- 真实 pgvector 相似度 SQL 查询
- 更完整的模型流式输出
- 多租户 RBAC 页面
- 工具调用审计详情页
- 在线 Demo 与演示视频
