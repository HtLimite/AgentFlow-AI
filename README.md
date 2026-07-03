# AgentFlow-AI

企业级 AI Agent 工作流与知识库平台，面向企业知识库、客服运营、内部提效、流程自动化和开发者项目诊断场景。

```txt
模型接入 → 文档解析 → 知识库 RAG → 项目诊断 → Agent 工具调用 → 工作流画布 → 工具审计 → Prompt 管理 → 效果评测 → Docker 部署
```

## 当前状态

当前项目已推进到 **V6 项目诊断闭环态 / 本地持久化演示态**。

已经可以本地验证：

- Next.js 管理台与 FastAPI 后端。
- Docker 基础设施：PostgreSQL、Redis、MinIO。
- 本地 uv 后端连接 Docker PostgreSQL，走数据库优先持久化链路。
- 模型供应商配置、固定选项输入、密钥脱敏。
- Chat、Knowledge、Project Diagnosis、Agent、Tools、Workflow、Prompt、Eval、Dashboard 主链路。
- 项目诊断：输入日志、关键配置片段、服务状态，输出阻塞原因、修复动作、验收命令和诊断报告。
- PDF 解析、文本清洗、RAG 问答、引用来源展示。
- React Flow 工作流画布、工具调用审计持久化、Prompt/Eval 对比中心、Demo 动线。
- pgvector SQL 检索基础能力、多租户 RBAC 请求上下文。
- Windows 本地 16 步验收脚本、前端构建、后端测试。

当前真实状态和边界见：`docs/current-status.md`。

## 技术栈

- 前端：Next.js、React、TypeScript、Tailwind CSS、React Flow
- 后端：FastAPI、SQLAlchemy、PostgreSQL、pgvector、Redis、MinIO
- AI：OpenAI-Compatible API、Embedding、RAG、Agent Tools、SSE Streaming
- 工程：pnpm workspace、uv、Docker Compose、GitHub Actions

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

这不是只跑内存 Demo。V6 主验收路径要求数据库真实可连，内存 fallback 只作为兜底。

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

项目诊断专项检查：

```bash
curl http://localhost:8000/api/project-diagnosis/demo
```

详细验收见：`docs/verification.md`。

## 演示路径

| 模块 | 路径 | 演示点 |
|---|---|---|
| Demo | `/demo` | 在线 Demo 演示动线与讲解词 |
| Showcase | `/showcase` | 作品展示与面试讲解入口 |
| Dashboard | `/dashboard` | 调用量、Token、耗时、失败率看板 |
| Project Diagnosis | `/diagnosis` | 粘贴日志、配置片段和服务状态，输出阻塞原因、修复动作、验收命令和诊断报告 |
| Settings | `/settings` | 模型供应商固定选项、连接测试、密钥脱敏 |
| Chat | `/chat` | 调用后端 Chat 接口 |
| Knowledge | `/knowledge` | 文档上传、清洗、切片、RAG 问答、引用来源 |
| Agents | `/agents` | Agent 调用工具并返回 trace_id / persistent_audit_id |
| Workflows | `/workflows` | React Flow 工作流画布、拖拽、连线、节点输出 |
| Audit | `/audit` | 数据库优先的工具调用审计记录、统计和详情 |
| Prompts | `/prompts` | Prompt 变量渲染与测试 |
| Evals | `/evals` | Prompt / Eval 三组对比中心 |
| Verification | `/verification` | 系统体检与阶段验收 |

## 文档入口

统一入口：`docs/README.md`

| 文档 | 作用 |
|---|---|
| `docs/current-status.md` | 当前项目真实状态与边界 |
| `docs/local-development.md` | Windows 本地启动和 Docker 基础设施 |
| `docs/verification.md` | 验收命令、验收步骤和常见问题 |
| `docs/roadmap.md` | 下一阶段计划 |
| `docs/architecture.md` | 总体架构和模块边界 |
| `docs/modules.md` | RAG、Agent、Workflow、数据库等模块设计 |
| `docs/showcase.md` | 截图、录屏和作品展示准备 |
| `docs/interview.md` | 面试讲解稿和简历写法 |
| `docs/history.md` | V1.5 / V2 / V3 / V4 历史记录 |

## 当前边界

当前版本是本地可演示的工程增强版，仍不是完整生产级平台。后续重点：

- 接入真实 GitHub 仓库读取、Docker API / 日志自动采集，让项目诊断从“粘贴输入”升级为“自动采集”。
- 接入真实 Embedding Provider、Rerank 和真实模型评测。
- 完善 Chat / RAG / Agent / Workflow 的真实模型流式输出。
- 对每个业务路由强制执行租户隔离和 RBAC 鉴权。
- 完善审计日志筛选、分页、导出和配置变更审计。
- 强化 SQL / HTTP 等高风险工具的生产级安全策略。
- 准备在线部署、截图、GIF 和演示视频。

## 简历关键词

RAG、Embedding、pgvector、SSE、OpenAI-Compatible API、Agent Tool Calling、Persistent Tool Audit、Project Diagnosis、Prompt Versioning、React Flow Workflow Canvas、LLM Observability、Eval Compare、RBAC Context、Docker Compose。
