# 当前项目状态

更新时间：2026-07-03

## 一句话状态

AgentFlow-AI 当前处于 **V5 真实模型运行时增强态 / 本地持久化演示态**：在 V4 的 React Flow 工作流画布、工具审计持久化、pgvector SQL 检索和 RBAC 上下文基础上，继续补齐 OpenAI-Compatible Provider 流式调用、Provider Embedding、Rerank 基础链路、Judge 评分协议和 15 步运行时验收；没有真实 API Key 时仍保留本地 fallback。

## 当前可验证能力

| 模块 | 当前状态 | 可验证方式 |
|---|---|---|
| API Health | 已可用 | `GET /health` |
| System Health | 已可用 | `GET /api/system/health/full` |
| Persistence Health | 已可用 | `GET /api/system/persistence/health` |
| Model Runtime Health | 已新增 | `GET /api/system/model-runtime/health` |
| RBAC Context | 已可用 | `GET /api/system/rbac/context` |
| Demo Route | 已可用 | `/demo` 演示动线页 |
| Showcase | 已可用 | `/showcase` 作品展示页 |
| Dashboard | 已可用 | `/dashboard` 页面、`GET /api/dashboard/summary` |
| Settings | 已可用 | `/settings` 新增供应商、固定选项输入、密钥脱敏 |
| Chat | 已支持供应商调用和本地 fallback | `/chat`、`POST /api/chat/completions` |
| Chat Streaming | 已支持 Provider SSE 基础链路 | `POST /api/chat/completions/stream` |
| Knowledge / RAG | 已可演示 | `/knowledge` 上传 txt/md/pdf、问答、引用来源 |
| Provider Embedding | 已支持配置后优先调用 | 新增 `embedding` 模型后重新上传文档 |
| pgvector SQL + Rerank | 已完成基础版 | RAG 查询返回 `pgvector_sql_rerank` 或 fallback 策略 |
| Agent Tools | 已可演示并返回 trace | `/agents`、`POST /api/agents/1/chat` |
| Tool Audit | 已完成数据库优先基础版 | `/audit`、`GET /api/audit/tools` |
| Tools | 已可演示 | `knowledge_search`、`calculator`、`sql_query`、`http_request` |
| Prompt | 已可演示 | `/prompts` |
| Workflow | 已升级为 React Flow 画布基础版 | `/workflows` |
| Eval Compare / Judge | 已升级为 Judge 协议基础版 | `/evals`、`POST /api/evals/runs` |
| Local Verification | 已升级为 15 步 V5 验收 | `scripts\verify-local.cmd` 或 `bash scripts/verify-local.sh` |
| Web Build | 已可验证 | `pnpm --filter @agentflow/web build` |
| API Test | 已可验证 | `cd apps/api && uv run python -m pytest` |

## 当前本地运行模式

推荐模式：

```txt
Windows 本地跑 web/api
Docker 跑 PostgreSQL / Redis / MinIO
```

原因：完整功能需要数据库、缓存、对象存储基础设施；但前后端本地启动更方便开发调试。

## 真实模型配置建议

至少配置一个 `chat` 模型用于 Chat / Agent / Workflow 真实回答。

推荐再配置一个 `embedding` 模型，用于新上传文档时写入真实 embedding。没有 embedding 模型时，系统会使用本地确定性 embedding fallback，保证本地演示可运行。

## 当前仍需增强

这些不要在面试或 README 中说成“已经生产可用”：

- 真实 Rerank Provider 接入，目前是本地 rerank 基础链路。
- 真正的 LLM-as-Judge Provider 调用，目前是兼容 Judge 协议的 heuristic_judge。
- RBAC 对全部业务路由的强制鉴权。
- 审计日志筛选、分页、导出和配置变更审计。
- SQL / HTTP 等高风险工具的生产级安全策略。
- 多租户管理页面、角色权限页面。
- 在线部署、截图、GIF 和演示视频。

## 面试表达口径

推荐表述：

```txt
这是一个企业级 AI Agent / RAG / Workflow 平台的本地可演示工程增强版。
当前已跑通模型配置、真实 OpenAI-Compatible Chat 调用、Provider 流式输出基础链路、Provider Embedding 接入、RAG + pgvector SQL + Rerank、Agent 工具调用、工具调用审计持久化、React Flow 工作流画布、Prompt、Eval Judge 协议、Dashboard、Docker 基础设施和 15 步本地验收。
没有真实 API Key 时系统会回退到本地 fallback，保证项目可以稳定演示。
```

避免表述：

```txt
已经是完整生产级平台。
已经实现所有生产级权限系统和完整安全策略。
Rerank 和 LLM-as-Judge 都已经是真实模型在线调用。
```
