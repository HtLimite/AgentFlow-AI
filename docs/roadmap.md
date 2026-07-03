# Roadmap

## 当前阶段

当前阶段是 **V3 平台展示态 / 可本地演示态**：目标是让项目具备更强的平台展示感，可以本地启动、演示主链路、展示可视化工作流、追踪工具调用审计，并通过 V3 验收脚本。

## V3 已完成

| 模块 | 状态 | 说明 |
|---|---|---|
| 本地验收 | 已完成 | `scripts\verify-local.cmd` / `bash scripts/verify-local.sh` 升级为 12 步验收 |
| Web 构建 | 已完成 | `pnpm --filter @agentflow/web build` |
| API 测试 | 已完成 | `cd apps/api && python -m pytest` |
| 文档中心 | 已完成 | README、current-status、v3-completion 已同步 |
| 可视化工作流 | 已完成 | `/workflows` 轻量画布、节点状态、节点输出 |
| 工具调用审计 | 已完成 | `/audit`、`/api/audit/tools`、trace_id、audit_id |
| Eval 对比 | 已完成 | `/evals` 三组 Prompt/模型横向评测对比 |
| Demo 动线 | 已完成 | `/demo` 在线演示路线与讲解词 |

## V4：生产化工作流与审计

目标：把 V3 的轻量展示能力升级成更接近商业产品的工程能力。

- 接入 React Flow 真拖拽画布。
- 支持 Start / Knowledge / LLM / Condition / HTTP / End 节点拖拽。
- 支持节点配置面板。
- 保存 workflow definition。
- 工具调用审计持久化。
- 审计日志筛选、分页、详情和导出。

验收：

```txt
用户可以拖拽节点组成知识库问答工作流，运行后看到每个节点输入输出；工具调用审计可筛选、可追踪、可持久化。
```

## V5：真实 RAG 与模型调用增强

目标：从演示/适配器闭环升级到更接近真实 AI 应用。

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

## V6：企业化能力

目标：补齐企业系统关键能力。

- 多租户 tenant_id 链路。
- RBAC 权限。
- 配置变更审计。
- 工具调用安全策略强化。
- HTTP 工具 SSRF 防护增强。
- SQL 工具只读策略增强。
- 数据脱敏。

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

验收：

```txt
GitHub 首页 1 分钟能看懂项目价值；面试 3 分钟能讲清楚架构、RAG、Agent、Workflow 和可观测性。
```
