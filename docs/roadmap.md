# Roadmap

## 当前阶段

当前阶段已推进到 **V4 工程增强态 / 本地持久化演示态**。V4 基础版已经补齐 React Flow 工作流画布、工具调用审计数据库持久化、pgvector SQL 检索基础能力和多租户 RBAC 请求上下文。

## V4 已完成基础能力

| 能力 | 状态 | 说明 |
|---|---|---|
| React Flow 工作流画布 | 已完成基础版 | 支持拖拽、连线、MiniMap、Controls、运行当前画布 |
| 工具调用审计持久化 | 已完成基础版 | 新增 `tool_audit_log` 表和数据库优先审计接口 |
| pgvector SQL 检索 | 已完成基础版 | 文档切片写入 `embedding` 列，查询优先走 SQL 相似度 |
| 多租户 RBAC 上下文 | 已完成基础版 | 基于请求头提供 tenant、user、role、permissions |
| 持久化验收 | 已完成 | 验收脚本升级为 14 步，包含 RBAC 与审计持久化检查 |
| 文档整理 | 已完成基础版 | 当前入口统一到 README 与 `docs/README.md` |

验收：

```txt
用户可以拖拽节点组成知识库问答工作流；Agent 工具调用写入 tool_audit_log；RAG 优先使用 pgvector SQL 检索；接口能读取 tenant/RBAC 上下文；本地 14 步验收通过。
```

## V5：真实模型与评测增强

目标：从演示/适配器闭环升级到更接近真实 AI 应用。

- 接入真实 Embedding Provider。
- 支持 Rerank 可选链路。
- Chat / RAG / Agent / Workflow 支持真实模型回答。
- 完善流式输出和错误回退策略。
- 记录真实 token、cost、latency。
- 引入真实 LLM-as-Judge 评测。
- 增加模型供应商联调文档和失败排查。

验收：

```txt
配置 DeepSeek / Qwen / Kimi 任一供应商后，Chat 和 RAG 可以真实回答，Dashboard 能看到调用日志与成本数据。
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

验收：

```txt
不同租户数据隔离；高风险工具调用被拒绝；审计日志可以追踪配置变更、知识库上传、Agent 工具调用。
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
