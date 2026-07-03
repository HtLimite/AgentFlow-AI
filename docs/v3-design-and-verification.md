# V3 设计与验证总纲

## 当前定位

AgentFlow-AI 当前是 **V3 平台展示态 / 本地持久化演示态**。

它不是纯内存 Demo，也不是完整生产级平台。主运行方式是：

```txt
Docker 基础设施 + 本地 uv 后端 + 本地 Next.js 前端
```

内存 fallback 只作为数据库不可用时的兜底，不作为 V2/V3 主验收结论。

## 架构总览

```txt
Browser
  -> Next.js Web Console
  -> FastAPI API Layer
  -> Service Layer
  -> PostgreSQL / Redis / MinIO
```

核心服务层包括：

- Knowledge / RAG
- Agent / Tool Registry
- Workflow Engine
- Prompt Service
- Eval Service
- Observability Service
- Tool Audit Service

## 模块设计口径

### Knowledge / RAG

已完成：文档上传、文本清洗、切片、数据库优先保存、RAG 问答、citations 返回。

边界：真实 Embedding Provider 和 pgvector SQL 相似度检索仍属于后续增强。

### Agent / Tool Audit

已完成：Agent 工具调用、trace_id、audit_id、latency_ms、工具审计页面和审计接口。

边界：审计日志持久化、筛选、分页、导出属于 V4。

### Workflow

已完成：轻量可视化工作流画布、节点运行状态、节点输出展示、后端 workflow run / node_run 服务。

边界：React Flow 真拖拽画布、节点配置面板、复杂分支属于 V4。

### Prompt / Eval

已完成：Prompt 模板、变量渲染、Eval 运行、三组 Prompt / Model 对比中心。

边界：真实 LLM-as-Judge 评分属于后续增强。

### Dashboard / Observability

已完成：调用量、Token、成本、耗时等看板展示，数据库可用时优先走持久化聚合。

边界：真实供应商 usage 统计需要真实模型响应继续联调。

## 现阶段验证顺序

按照以下顺序验收：

```txt
1. 启动 Docker 基础设施
2. 启动 uv 后端
3. 启动前端
4. 检查持久化健康接口
5. 执行 verify 脚本
6. 执行前端构建和后端测试
7. 手工验收 V3 页面
```

详细命令见：`docs/verification.md`。

## 必须验证的核心接口

最关键的是：

```txt
GET /api/system/persistence/health
```

它用于确认当前不是只跑内存 fallback，而是后端已连接数据库并能检查核心表。

然后执行：

```txt
scripts\verify-local.cmd
```

或：

```txt
bash scripts/verify-local.sh
```

## 页面验收清单

| 页面 | 验证点 |
|---|---|
| `/demo` | 演示动线 |
| `/showcase` | 项目展示 |
| `/dashboard` | 观测看板 |
| `/settings` | 模型供应商配置 |
| `/knowledge` | RAG 问答和 citations |
| `/agents` | trace_id、audit_id、tool_calls |
| `/workflows` | 可视化画布和节点输出 |
| `/audit` | 工具调用审计 |
| `/prompts` | Prompt 变量渲染 |
| `/evals` | 三组评测对比 |
| `/verification` | 系统体检 |

## 当前不能夸大的边界

以下内容不能说成已经完整生产化：

- React Flow 真拖拽画布。
- 审计日志数据库持久化和筛选。
- 真实 pgvector SQL 相似度检索。
- 真实 Embedding Provider。
- 完整真实模型流式输出。
- 多租户 RBAC 页面。
- 在线部署和演示视频。

## 推荐验收结论

可以这样表述：

```txt
当前项目已完成 V3 平台展示态。
本地通过 Docker 启动基础设施，通过 uv 启动 FastAPI，通过 pnpm 启动 Next.js。
系统已具备数据库优先持久化验证、RAG 问答、Agent 工具审计、可视化工作流、Prompt/Eval 对比和 Dashboard 可观测能力。
主验收以持久化健康接口和 13 步 verify 脚本为准。
```
