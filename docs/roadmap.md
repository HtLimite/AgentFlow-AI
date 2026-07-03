# Roadmap

## 当前阶段

当前阶段已推进到 **V5 真实模型运行时增强态 / 本地持久化演示态**。V5 基础版在 V4 的 React Flow 工作流画布、工具调用审计数据库持久化、pgvector SQL 检索基础能力和多租户 RBAC 请求上下文上，继续补齐 Provider 流式调用、Provider Embedding、Rerank 基础链路和 Judge 评分协议。

## V4 已完成基础能力

| 能力 | 状态 | 说明 |
|---|---|---|
| React Flow 工作流画布 | 已完成基础版 | 支持拖拽、连线、MiniMap、Controls、运行当前画布 |
| 工具调用审计持久化 | 已完成基础版 | 新增 `tool_audit_log` 表和数据库优先审计接口 |
| pgvector SQL 检索 | 已完成基础版 | 文档切片写入 `embedding` 列，查询优先走 SQL 相似度 |
| 多租户 RBAC 上下文 | 已完成基础版 | 基于请求头提供 tenant、user、role、permissions |
| 持久化验收 | 已完成 | 验收脚本升级为 14 步，包含 RBAC 与审计持久化检查 |
| 文档整理 | 已完成基础版 | 当前入口统一到 README 与 `docs/README.md` |

## V5：真实模型与评测增强

目标：从演示/适配器闭环升级到更接近真实 AI 应用。

| 能力 | 状态 | 说明 |
|---|---|---|
| 真实 Chat Provider | 已完成基础版 | OpenAI-Compatible `/chat/completions` 调用 |
| Provider 流式输出 | 已完成基础版 | `/api/chat/completions/stream` 支持供应商 SSE |
| Provider Embedding | 已完成基础版 | 配置 `embedding` 模型后，RAG 写入优先调用供应商 embedding |
| 本地 Embedding fallback | 已完成 | 无供应商时使用 1536 维确定性本地向量 |
| Rerank 基础链路 | 已完成基础版 | RAG 候选结果进入本地 rerank，可替换真实 rerank provider |
| Judge 评分协议 | 已完成基础版 | Eval 输出 `judge_mode`、`matched_terms`、`total_terms` 等结构 |
| 运行时健康检查 | 已完成 | `/api/system/model-runtime/health` 展示 chat / embedding / rerank 能力 |
| 15 步验收 | 已完成 | 验收脚本新增模型运行时检查 |

验收：

```txt
配置 DeepSeek / Qwen / Kimi 任一 OpenAI-Compatible 供应商后，Chat 可以真实回答；配置 embedding 模型后，新上传文档会优先使用供应商 embedding；RAG 结果进入 rerank；Eval 使用 Judge 评分协议；Dashboard 能看到调用日志与成本数据。
```

## V6：企业化能力

目标：补齐企业系统关键能力。

- RBAC 对每个业务路由强制鉴权。
- 多租户管理页面和角色权限页面。
- 配置变更审计。
- 审计日志筛选、分页、导出。
- 工具调用安全策略强化。
- HTTP 工具 SSRF 防护增强。
- SQL 工具只读策略增强。
- 数据脱敏和敏感字段策略。
- API 错误码和参数校验统一。
- 真实 Rerank Provider 与真实 LLM-as-Judge Provider 接入。

验收：

```txt
不同租户数据隔离；高风险工具调用被拒绝；审计日志可以追踪配置变更、知识库上传、Agent 工具调用；评测可使用真实 judge 模型。
```

## V7：作品发布

目标：从本地项目升级为可公开展示作品。

- README 增加截图 / GIF。
- `/showcase` 页面补齐项目亮点展示。
- 录制 3-5 分钟演示视频。
- 部署在线 Demo。
- 准备简历项目描述和面试讲解版本。
- 补充中文项目介绍图和架构图。

验收：

```txt
GitHub 首页 1 分钟能看懂项目价值；面试 3 分钟能讲清楚架构、RAG、Agent、Workflow 和可观测性。
```
