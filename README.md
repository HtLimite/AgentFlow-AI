# AgentFlow-AI

企业级 AI Agent 工作流与知识库平台，面向企业知识库、客服运营、内部提效和流程自动化场景。

```txt
模型接入 → 文档解析 → 知识库 RAG → Agent 工具调用 → 工作流画布 → 工具审计 → Prompt 管理 → 效果评测 → Docker 部署
```

## 当前状态

当前项目已推进到 **V3 平台展示态 / 本地持久化演示态**。

已经可以本地验证：

- Next.js 管理台与 FastAPI 后端。
- Docker 基础设施：PostgreSQL、Redis、MinIO。
- 本地 uv 后端连接 Docker PostgreSQL，走数据库优先持久化链路。
- 模型供应商配置、固定选项输入、密钥脱敏。
- Chat、Knowledge、Agent、Tools、Workflow、Prompt、Eval、Dashboard 主链路。
- PDF 解析、文本清洗、RAG 问答、引用来源展示。
- V3 可视化工作流画布、工具调用审计、Prompt/Eval 对比中心、在线 Demo 动线。
- Windows 本地验收脚本、前端构建、后端测试。

当前真实状态和边界见：`docs/current-status.md`、`docs/v2-completion.md`、`docs/v3-completion.md`。

## 技术栈

- 前端：Next.js、React、TypeScript、Tailwind CSS
- 后端：FastAPI、SQLAlchemy、PostgreSQL、pgvector、Redis、MinIO
- AI：OpenAI-Compatible API、Embedding、RAG、Agent Tools、SSE Streaming
- 工程：pnpm workspace、Docker Compose、GitHub Actions

## 快速开始

```bash
git clone git@github.com:HtLimite/AgentFlow-AI.git
cd AgentFlow-AI
cp .env.example .env
pnpm install
```

Windows PowerShell 可用：

```powershell
Copy-Item .env.example .env
```

## uv 后端环境

后端位于 `apps/api`，要求 Python 3.12+，推荐用 `uv` 创建和管理虚拟环境。

首次安装后端依赖：

```bash
cd apps/api
uv sync
```

Windows 本地启动 FastAPI：

```cmd
scripts\dev-api-uv.cmd
```

也可以手动启动：

```bash
cd apps/api
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

如果本机还没有安装 `uv`，先安装后再执行上述命令：

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## 推荐本地启动

推荐方式：**Docker 启动 PostgreSQL / Redis / MinIO，本地 uv 启动 FastAPI，本地 pnpm 启动 Next.js**。

这不是只跑内存 Demo。V2/V3 主验收路径要求数据库真实可连，内存 fallback 只作为兜底。

基础设施：

```cmd
scripts\dev-infra.cmd
```

后端：

```cmd
scripts\dev-api-uv.cmd
```

前端：

```bash
pnpm dev:web
```

访问：

```txt
Web: http://localhost:3000
API: http://localhost:8000
Swagger: http://localhost:8000/docs
```

完整说明见：`docs/local-development.md`。

## 本地验收

Windows：

```cmd
scripts\verify-local.cmd
```

Linux / macOS / Git Bash：

```bash
bash scripts/verify-local.sh
```

构建与测试：

```bash
pnpm --filter @agentflow/web build
cd apps/api
uv run python -m compileall app
uv run python -m pytest
```

严格持久化检查：

```bash
curl http://localhost:8000/api/system/persistence/health
```

详细验收见：`docs/verification.md`、`docs/acceptance.md` 和 `docs/v3-completion.md`。

## 演示路径

| 模块 | 路径 | 演示点 |
|---|---|---|
| Demo | `/demo` | 在线 Demo 演示动线与讲解词 |
| Showcase | `/showcase` | 作品展示与面试讲解入口 |
| Dashboard | `/dashboard` | 调用量、Token、耗时、失败率看板 |
| Settings | `/settings` | 模型供应商固定选项、连接测试、密钥脱敏 |
| Chat | `/chat` | 调用后端 Chat 接口 |
| Knowledge | `/knowledge` | 文档上传、清洗、切片、RAG 问答、引用来源 |
| Agents | `/agents` | Agent 调用工具并返回 trace_id / audit_id |
| Workflows | `/workflows` | V3 可视化工作流画布与节点输出 |
| Audit | `/audit` | 工具调用审计记录、统计和详情 |
| Prompts | `/prompts` | Prompt 变量渲染与测试 |
| Evals | `/evals` | Prompt / Eval 三组对比中心 |
| Verification | `/verification` | 系统体检与阶段验收 |

## 文档入口

统一入口：`docs/README.md`

| 文档 | 作用 |
|---|---|
| `docs/current-status.md` | 当前项目真实状态与边界 |
| `docs/v3-completion.md` | V3 完成说明与验收范围 |
| `docs/v2-completion.md` | V2 工程基础态说明 |
| `docs/local-development.md` | Windows 本地启动和 Docker 基础设施 |
| `docs/verification.md` | 验收命令与验收标准 |
| `docs/acceptance.md` | 阶段验收清单 |
| `docs/roadmap.md` | 下一阶段计划 |
| `docs/architecture.md` | 架构设计 |
| `docs/database.md` | 数据库设计 |
| `docs/rag.md` | RAG 与 PDF 解析设计 |
| `docs/agent.md` | Agent 工具调用设计 |
| `docs/workflow.md` | Workflow 执行设计 |
| `docs/interview.md` | 面试讲解稿 |

## 当前边界

当前版本仍不是完整生产级平台，以下属于后续 V4 / 生产化增强：

- React Flow 真拖拽工作流画布。
- 审计日志数据库持久化与筛选。
- 真实 pgvector 相似度 SQL 检索。
- 更完整的模型流式输出。
- 多租户 RBAC 页面。
- 在线部署、截图、演示视频。

## 简历关键词

RAG、Embedding、pgvector、SSE、OpenAI-Compatible API、Agent Tool Calling、Tool Audit、Prompt Versioning、Workflow Canvas、LLM Observability、Eval Compare、Docker Compose。