# Roadmap

## 当前阶段

当前阶段是 **V2 工程基础态 / 可本地演示态**：目标是让项目可以本地启动、可以演示主链路、可以通过基础验收，并具备继续生产化的清晰扩展点。

## V2 收尾优先级

| 优先级 | 事项 | 目标 |
|---|---|---|
| P0 | 保证 `scripts\verify-local.cmd` 稳定通过 | 本地最小验收稳定 |
| P0 | 保证 `pnpm --filter @agentflow/web build` 通过 | 前端生产构建可用 |
| P0 | 保证 `cd apps/api && python -m pytest` 通过 | 后端基础测试可用 |
| P1 | 文档中心统一口径 | README / docs 不再互相冲突 |
| P1 | 截图与演示视频 | 支撑 GitHub 作品展示 |

## V3：真实 RAG 与模型调用

目标：从演示闭环升级到更接近真实 AI 应用。

- 接入真实 Embedding Provider。
- 使用 pgvector 做真实向量相似度 SQL 检索。
- 支持 Rerank 可选链路。
- Chat / RAG / Agent / Workflow 支持真实模型回答。
- 完善流式输出和错误回退策略。
- 记录真实 token、cost、latency。

验收：

```txt
配置 DeepSeek / Qwen / Kimi 任一供应商后，Chat 和 RAG 可以真实回答，Dashboard 能看到调用日志与成本数据。
```

## V4：可视化 Workflow

目标：把当前工作流执行链路升级为可拖拽编排。

- 接入 React Flow。
- 支持 Start / Knowledge / LLM / Condition / HTTP / End 节点。
- 支持节点配置面板。
- 保存 workflow definition。
- 展示 node_run 输入、输出、耗时、错误。

验收：

```txt
用户可以拖拽节点组成一个知识库问答工作流，运行后看到每个节点的输入输出和执行状态。
```

## V5：企业化能力

目标：补齐企业系统关键能力。

- 多租户 tenant_id 链路。
- RBAC 权限。
- 审计日志页面。
- 工具调用安全策略强化。
- HTTP 工具 SSRF 防护增强。
- SQL 工具只读策略增强。
- 数据脱敏。

验收：

```txt
不同租户数据隔离；高风险工具调用被拒绝；审计日志可以追踪配置变更、知识库上传、Agent 工具调用。
```

## V6：作品发布

目标：从本地项目升级为可展示作品。

- README 增加截图 / GIF。
- `/showcase` 页面补齐项目亮点展示。
- 录制 3-5 分钟演示视频。
- 部署在线 Demo。
- 准备简历项目描述和面试讲解版本。

验收：

```txt
GitHub 首页 1 分钟能看懂项目价值；面试 3 分钟能讲清楚架构、RAG、Agent、Workflow 和可观测性。
```
