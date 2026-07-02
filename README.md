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

## 当前版本

当前版本按 6 周开发计划一次性推进到 **V1.5 可演示作品包**：

- Week 1：工程骨架、项目包装、演示脚本、验收清单
- Week 2：知识库 RAG 闭环
- Week 3：Agent 工具调用机制
- Week 4：Prompt、日志、成本与可观测性
- Week 5：Workflow 执行器与节点协议
- Week 6：Eval 评测、部署完善、简历与面试材料

## 已完成功能

- [x] Monorepo 工程结构
- [x] Next.js 管理台
- [x] FastAPI 后端入口与路由分层
- [x] 模型供应商 CRUD
- [x] 模型供应商固定选项输入
- [x] 密钥加密保存与脱敏回显
- [x] Chat 普通接口与流式接口骨架
- [x] 知识库创建、文档上传、文本清洗、文本切片、RAG 问答、引用来源展示
- [x] Agent 工具调用链路演示
- [x] Prompt 模板测试演示
- [x] Workflow 执行器演示
- [x] Eval 评测运行演示
- [x] 系统体检与验收中心
- [x] Docker Compose：web / api / postgres / redis / minio / nginx
- [x] GitHub Actions：web build / api compile / api test
- [x] 架构、数据库、RAG、Agent、Workflow、面试讲解、验收文档

## 快速开始

```bash
git clone git@github.com:HtLimite/AgentFlow-AI.git
cd AgentFlow-AI
cp .env.example .env
```

前端：

```bash
pnpm install
pnpm dev:web
```

后端：

```bash
cd apps/api
python -m venv .venv
.venv\Scripts\activate
pip install -e .
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Docker：

```bash
docker compose -f deploy/docker-compose.yml --env-file .env up -d --build
```

## 演示路径

| 模块 | 路径 | 演示点 |
|---|---|---|
| Dashboard | `/dashboard` | 调用量、Token、耗时、失败率看板 |
| Settings | `/settings` | 模型供应商固定选项、连接测试、密钥脱敏 |
| Chat | `/chat` | 调用后端 Chat Completion 接口 |
| Knowledge | `/knowledge` | 文档上传、清洗、切片、RAG 问答、引用来源 |
| Agents | `/agents` | Agent 调用知识库工具并展示 tool_calls |
| Workflows | `/workflows` | 工作流节点运行链路 |
| Prompts | `/prompts` | Prompt 变量渲染与测试 |
| Evals | `/evals` | 评测运行与逐题评分 |
| Verification | `/verification` | 系统体检与阶段验收 |

## 本地验收

后端体检：

```bash
curl http://localhost:8000/api/system/health/full
```

Linux / macOS / Git Bash：

```bash
bash scripts/verify-local.sh
```

Windows CMD：

```cmd
scripts\verify-local.cmd
```

构建与测试：

```bash
pnpm build:web
cd apps/api
python -m compileall app
python -m pytest
```

## 当前边界

为了让项目快速达到“可启动、可演示、可讲解”的求职作品状态，当前版本部分模块采用轻量实现：

- 知识库演示数据重启后恢复默认值
- Prompt / Eval 演示数据暂未全部持久化
- Workflow 先返回节点运行链路，后续接 React Flow 画布
- 真实外部模型调用保留扩展点，建议在本地联调供应商

## Roadmap

- V2：知识库持久化、MinIO 文件存储、真实 Embedding、pgvector 检索
- V2：模型调用日志、Token 成本统计、Agent Tool Registry 标准协议
- V3：React Flow 工作流画布、Prompt 版本管理、LLM-as-Judge 自动评测
- V4：多租户、RBAC 权限、审计日志、数据脱敏、在线 Demo、项目官网

## 简历关键词

RAG、Embedding、pgvector、SSE、OpenAI-Compatible API、Agent Tool Calling、Prompt Versioning、Workflow Engine、LLM Observability、Cost Dashboard、Docker Compose。
