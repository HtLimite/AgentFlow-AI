# AgentFlow-AI

企业级 AI Agent 工作流与知识库平台，面向企业知识库、客服运营、内部提效和流程自动化场景。

## 项目定位

AgentFlow-AI 不是简单的 AI 聊天 Demo，而是围绕企业 AI 落地的完整闭环：

```txt
模型接入 → 文档解析 → 知识库 RAG → Agent 工具调用 → 工作流编排 → Prompt 管理 → 调用日志 → 成本统计 → 效果评测 → Docker 部署
```

## 技术栈

- 前端：Next.js、React、TypeScript、Tailwind CSS
- 后端：FastAPI、SQLAlchemy、PostgreSQL、pgvector、Redis、MinIO
- AI：OpenAI-Compatible API、Embedding、RAG、Agent Tools、SSE Streaming
- 工程：pnpm workspace、Docker Compose、GitHub Actions

## 当前已完成

- [x] Monorepo 工程结构
- [x] Next.js 管理台骨架
- [x] Dashboard / Chat / Knowledge / Agent / Workflow / Prompt / Eval / Settings 页面
- [x] FastAPI 后端入口与路由分层
- [x] 多模型配置接口骨架
- [x] Chat 普通接口与 SSE 流式接口骨架
- [x] 知识库 RAG 查询接口骨架
- [x] Agent 工具调用链路骨架
- [x] Docker Compose：web / api / postgres / redis / minio / nginx
- [x] GitHub Actions：web build / api compile

## 快速开始

### 1. 克隆仓库

```bash
git clone git@github.com:HtLimite/AgentFlow-AI.git
cd AgentFlow-AI
cp .env.example .env
```

### 2. 本地启动前端

```bash
pnpm install
pnpm dev:web
```

访问：`http://localhost:3000`

### 3. 本地启动后端

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -e .
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问：`http://localhost:8000/docs`

### 4. Docker Compose 一键启动

```bash
docker compose -f deploy/docker-compose.yml --env-file .env up -d --build
```

服务端口：

| 服务 | 地址 |
|---|---|
| Web | http://localhost:3000 |
| API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| MinIO Console | http://localhost:9001 |
| Nginx Gateway | http://localhost:8080 |

## 仓库结构

```txt
agentflow-ai/
├─ apps/
│  ├─ web/                 # Next.js 前端管理台
│  └─ api/                 # FastAPI 后端服务
├─ packages/
│  ├─ shared/              # 共享说明/类型预留
│  └─ prompts/             # 默认 Prompt 模板
├─ deploy/                 # Docker Compose / Nginx / Postgres 初始化
├─ docs/                   # 架构、数据库、RAG、Agent、Workflow、面试文档
├─ .github/workflows/      # CI
├─ README.md
└─ .env.example
```

## 核心演示场景

1. 配置 DeepSeek / Qwen / OpenAI-Compatible 模型供应商。
2. 在 Chat Playground 测试普通对话与流式输出。
3. 创建知识库，上传文档，解析切片并向量化。
4. 发起 RAG 问答，展示答案、引用文档、引用片段和相似度。
5. 创建 Agent，绑定知识库检索、SQL 查询、HTTP 请求等工具。
6. 使用工作流画布组合 Start、Knowledge、LLM、Condition、HTTP、End 节点。
7. 查看调用日志、Token 消耗、成本趋势和失败率。
8. 使用评测集比较不同模型和 Prompt 版本。

## Git 提交规范

使用 Conventional Commits：

```txt
<type>(<scope>): <subject>
```

示例：

```txt
feat(api): 新增知识库查询接口
feat(web): 实现 RAG 引用来源面板
fix(agent): 修复工具调用状态未记录问题
chore(repo): 调整 monorepo 工程配置
```

## Roadmap

- V1：多模型聊天 + 知识库 RAG 闭环
- V2：Agent 工具调用 + 调用日志 + 成本统计
- V3：React Flow 工作流编排 + Prompt 版本管理 + 评测集
- V4：多租户、权限、脱敏、在线 Demo、项目官网

## 面试关键词

RAG、Embedding、pgvector、SSE、OpenAI-Compatible API、Agent Tool Calling、Prompt Versioning、Workflow Engine、LLM Observability、Cost Dashboard、Docker Compose。
