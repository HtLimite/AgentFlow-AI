# 当前项目状态

更新时间：2026-07-03

## 一句话状态

AgentFlow-AI 当前处于 **V4 工程增强态 / 本地持久化演示态**：前后端、主要页面、后端核心接口、RAG 演示链路、Agent 工具调用、工具调用审计持久化、React Flow 工作流画布、Prompt、Eval 对比、Dashboard、Docker 基础设施、本地 14 步验收、pgvector SQL 检索基础能力和 RBAC 请求上下文已经具备；真实生产级能力仍需继续增强。

## 当前可验证能力

| 模块 | 当前状态 | 可验证方式 |
|---|---|---|
| API Health | 已可用 | `GET /health` |
| System Health | 已可用 | `GET /api/system/health/full` |
| Persistence Health | 已可用 | `GET /api/system/persistence/health` |
| RBAC Context | 已可用 | `GET /api/system/rbac/context` |
| Demo Route | 已可用 | `/demo` 演示动线页 |
| Showcase | 已可用 | `/showcase` 作品展示页 |
| Dashboard | 已可用 | `/dashboard` 页面、`GET /api/dashboard/summary` |
| Settings | 已可用 | `/settings` 新增供应商、固定选项输入、密钥脱敏 |
| Chat | 演示 + 供应商扩展点 | `/chat` 页面 |
| Knowledge / RAG | 已可演示 | `/knowledge` 上传 txt/md/pdf、问答、引用来源 |
| PDF 解析 | 已修复二进制与控制字符乱码 | 上传 PDF 后重新问答 |
| pgvector SQL 检索 | 已完成基础版 | RAG 查询优先走 SQL 相似度链路 |
| Agent Tools | 已可演示并返回 trace | `/agents`、`POST /api/agents/1/chat` |
| Tool Audit | 已完成数据库优先基础版 | `/audit`、`GET /api/audit/tools` |
| Tools | 已可演示 | `knowledge_search`、`calculator`、`sql_query`、`http_request` |
| Prompt | 已可演示 | `/prompts` |
| Workflow | 已升级为 React Flow 画布基础版 | `/workflows` |
| Eval Compare | 已升级为三组对比中心 | `/evals` |
| Local Verification | 已升级为 14 步 V4 验收 | `scripts\verify-local.cmd` 或 `bash scripts/verify-local.sh` |
| Web Build | 已可验证 | `pnpm --filter @agentflow/web build` |
| API Test | 已可验证 | `cd apps/api && uv run python -m pytest` |

## 当前本地运行模式

推荐模式：

```txt
Windows 本地跑 web/api
Docker 跑 PostgreSQL / Redis / MinIO
```

原因：完整功能需要数据库、缓存、对象存储基础设施；但前后端本地启动更方便开发调试。

## 当前仍需增强

这些不要在面试或 README 中说成“已经生产可用”：

- 真实 Embedding Provider、Rerank 和真实 LLM-as-Judge 评测。
- Chat / RAG / Agent / Workflow 的真实模型流式输出和错误回退。
- RBAC 对全部业务路由的强制鉴权。
- 审计日志筛选、分页、导出和配置变更审计。
- SQL / HTTP 等高风险工具的生产级安全策略。
- 多租户管理页面、角色权限页面。
- 在线部署、截图、GIF 和演示视频。

## 面试表达口径

推荐表述：

```txt
这是一个企业级 AI Agent / RAG / Workflow 平台的本地可演示工程增强版。
当前已跑通模型配置、文档解析、RAG 问答、Agent 工具调用、工具调用审计持久化、React Flow 工作流画布、Prompt、Eval 对比、Dashboard、Docker 基础设施、pgvector SQL 检索基础能力和 RBAC 请求上下文。
后续重点会继续增强真实模型调用、真实 Embedding / Rerank、生产级权限、安全策略、审计检索和在线展示。
```

避免表述：

```txt
已经是完整生产级平台。
已经实现所有真实模型调用、完整权限系统和完整安全策略。
所有模块都已经完全生产可用。
```
