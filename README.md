# AgentFlow-AI

企业级 AI Agent 工作流与知识库平台，面向企业知识库、客服运营、内部提效和流程自动化场景。

```txt
模型接入 → 文档解析 → 知识库 RAG → Agent 工具调用 → 工作流执行 → Prompt 管理 → 调用日志 → 效果评测 → Docker 部署
```

## 当前状态

当前项目处于 **V2 工程基础态 / 可本地演示态**。

已经可以本地验证：

- Next.js 管理台与 FastAPI 后端。
- 模型供应商配置、固定选项输入、密钥脱敏。
- Chat、Knowledge、Agent、Tools、Workflow、Prompt、Eval、Dashboard 主链路。
- PDF 解析、文本清洗、RAG 问答、引用来源展示。
- Windows 本地验收脚本、前端构建、后端测试。
- Docker Compose 基础设施：PostgreSQL、Redis、MinIO、API、Web、Nginx。

当前真实状态和边界见：`docs/current-status.md`。

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

## 推荐本地启动

推荐方式：前后端本地启动，PostgreSQL / Redis / MinIO 用 Docker 启动。

```bash
docker compose -f deploy/docker-compose.yml --env-file .env up -d postgres redis minio
```

后端：

```bash
cd apps/api
python -m venv .venv
.venv\Scripts\activate
pip install -e .
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
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
python -m compileall app
python -m pytest
```

详细验收见：`docs/verification.md` 和 `docs/acceptance.md`。

## 演示路径

| 模块 | 路径 | 演示点 |
|---|---|---|
| Showcase | `/showcase` | 作品展示与面试讲解入口 |
| Dashboard | `/dashboard` | 调用量、Token、耗时、失败率看板 |
| Settings | `/settings` | 模型供应商固定选项、连接测试、密钥脱敏 |
| Chat | `/chat` | 调用后端 Chat 接口 |
| Knowledge | `/knowledge` | 文档上传、清洗、切片、RAG 问答、引用来源 |
| Agents | `/agents` | Agent 调用知识库工具并展示 tool_calls |
| Workflows | `/workflows` | 工作流节点运行链路 |
| Prompts | `/prompts` | Prompt 变量渲染与测试 |
| Evals | `/evals` | 评测运行与逐题评分 |
| Verification | `/verification` | 系统体检与阶段验收 |

## 文档入口

统一入口：`docs/README.md`

| 文档 | 作用 |
|---|---|
| `docs/current-status.md` | 当前项目真实状态与边界 |
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

当前版本不是完整生产级平台，以下属于后续增强：

- 真实 Embedding + pgvector 相似度 SQL 检索。
- 更完整的模型流式输出。
- React Flow 拖拽工作流画布。
- 多租户 RBAC 与审计详情页。
- 在线 Demo、截图、演示视频。

## 简历关键词

RAG、Embedding、pgvector、SSE、OpenAI-Compatible API、Agent Tool Calling、Prompt Versioning、Workflow Engine、LLM Observability、Cost Dashboard、Docker Compose。
