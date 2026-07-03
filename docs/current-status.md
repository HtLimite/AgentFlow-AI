# 当前项目状态

更新时间：2026-07-03

## 一句话状态

AgentFlow-AI 当前处于 **V3 平台展示态 / 可本地演示态**：前后端、主要页面、后端核心接口、RAG 演示链路、Agent 工具调用、工具调用审计、可视化工作流画布、Prompt、Eval 对比、Dashboard、Docker 基础设施和本地验收脚本已经具备；真实生产级能力仍需继续增强。

## 当前可验证能力

| 模块 | 当前状态 | 可验证方式 |
|---|---|---|
| API Health | 已可用 | `GET /health` |
| System Health | 已可用 | `GET /api/system/health/full` |
| Demo Route | 已可用 | `/demo` 演示动线页 |
| Showcase | 已可用 | `/showcase` 作品展示页 |
| Dashboard | 已可用 | `/dashboard` 页面、`/api/dashboard/summary` |
| Settings | 已可用 | `/settings` 新增供应商、固定选项输入、密钥脱敏 |
| Chat | 演示 + 供应商扩展点 | `/chat` 页面 |
| Knowledge / RAG | 已可演示 | `/knowledge` 上传 txt/md/pdf、问答、引用来源 |
| PDF 解析 | 已修复二进制与控制字符乱码 | 上传 PDF 后重新问答 |
| Agent Tools | 已可演示并返回 trace | `/agents`、`/api/agents/1/chat` |
| Tool Audit | 已可演示 | `/audit`、`/api/audit/tools` |
| Tools | 已可演示 | `knowledge_search`、`calculator`、`sql_query`、`http_request` |
| Prompt | 已可演示 | `/prompts` |
| Workflow | 已升级为轻量可视化画布 | `/workflows` |
| Eval Compare | 已升级为三组对比中心 | `/evals` |
| Local Verification | 已升级为 12 步 V3 验收 | `scripts\verify-local.cmd` 或 `bash scripts/verify-local.sh` |
| Web Build | 已可验证 | `pnpm --filter @agentflow/web build` |
| API Test | 已可验证 | `cd apps/api && python -m pytest` |

## 当前本地运行模式

推荐模式：

```txt
Windows 本地跑 web/api
Docker 跑 postgres / redis / minio
```

原因：完整功能需要数据库、缓存、对象存储基础设施；但前后端本地启动更方便开发调试。

## 当前仍需增强

这些不要在面试或 README 中说成“已经生产可用”：

- React Flow 真拖拽式工作流画布。
- 审计日志数据库持久化、筛选和导出。
- 真实 Embedding + pgvector 相似度 SQL 检索。
- 更完整的真实模型流式输出。
- 多租户 RBAC 权限页面。
- 工具调用生产级安全策略。
- 在线部署、截图、演示视频。

## 面试表达口径

推荐表述：

```txt
这是一个企业级 AI Agent / RAG / Workflow 平台的本地可演示平台展示版。
当前已跑通模型配置、文档解析、RAG 问答、Agent 工具调用、工具调用审计、可视化工作流画布、Prompt、Eval 对比、Dashboard 和 Docker 部署链路。
后续重点会继续增强 React Flow 真拖拽画布、审计持久化、真实 pgvector 检索和多租户权限。
```

避免表述：

```txt
已经是完整生产级平台。
已经实现所有真实向量检索和多租户权限。
所有模块都已经完全持久化、完全生产可用。
```
