# 验收与验证

## 验收目标

本项目当前验收分为四层：

```txt
启动验收 → 接口验收 → 构建测试 → 页面验收
```

优先顺序：先跑接口脚本，再跑构建与测试，最后做页面手工验收。

## 1. 接口验收

Windows：

```cmd
scripts\verify-local.cmd
```

Linux / macOS / Git Bash：

```bash
bash scripts/verify-local.sh
```

当前 Windows 脚本输出为 ASCII 摘要，避免中文响应在终端乱码。

### 当前覆盖项

| 步骤 | 验证内容 | 接口 |
|---|---|---|
| 1 | 后端健康检查 | `GET /health` |
| 2 | 系统模块健康检查 | `GET /api/system/health/full` |
| 3 | 知识库 RAG 问答 | `POST /api/knowledge-bases/1/query` |
| 4 | 工具列表 | `GET /api/tools` |
| 5 | Agent 工具调用 | `POST /api/agents/1/chat` |
| 6 | Eval 评测运行 | `POST /api/evals/runs` |

### 期望输出

```txt
[1/6] Health
PASS status=ok service=agentflow-api

[2/6] Full system health
PASS modules=... knowledge_bases=1 tools=4 eval_datasets=1 workflow_nodes=4

[3/6] Knowledge query
PASS citations=1 strategy=local_vector top_k=3 first_score=0.6 first_document=demo-policy.md

[4/6] Tool list
PASS count=4 tools=knowledge_search,calculator,sql_query,http_request

[5/6] Agent chat
PASS agent_id=1 tool_calls=1 first_tool=knowledge_search status=success

[6/6] Eval run
PASS id=1 status=completed score=87.5 cases=2

AgentFlow-AI local verification completed.
```

## 2. 后端测试

```bash
cd apps/api
python -m compileall app
python -m pytest
```

根目录脚本：

```bash
pnpm test:api
```

## 3. 前端构建

```bash
pnpm --filter @agentflow/web build
```

或：

```bash
pnpm build:web
```

用于验证：

- Next.js 是否能生产构建。
- TypeScript 是否通过。
- 页面和组件 import 是否正常。

## 4. Docker 验收

启动基础设施：

```bash
docker compose -f deploy/docker-compose.yml --env-file .env up -d postgres redis minio
```

完整 Docker 启动：

```bash
docker compose -f deploy/docker-compose.yml --env-file .env up -d --build
```

检查：

```bash
docker ps
curl http://localhost:8000/health
```

完整 Docker 模式下可访问：

```txt
http://localhost:8080
```

## 5. 页面验收

| 页面 | 验收点 |
|---|---|
| `/dashboard` | 可看到调用量、Token、耗时、失败率等看板信息 |
| `/settings` | 可新增供应商，供应商固定格式字段为下拉选项，API Key 脱敏回显 |
| `/chat` | 可发送问题并收到后端回答 |
| `/knowledge` | 可上传 txt/md/pdf，问答返回引用来源 |
| `/agents` | 可看到 Agent 调用工具链路 |
| `/workflows` | 可运行工作流节点链路 |
| `/prompts` | 可测试 Prompt 变量渲染 |
| `/evals` | 可运行评测并得到分数 |
| `/verification` | 页面内系统体检通过 |

## 6. 常见判断

### 接口全部 PASS，但页面空白

优先检查前端环境：

```bash
pnpm install
pnpm dev:web
```

### Health 通过，但 Settings 保存失败

大概率是数据库未启动。执行：

```bash
docker compose -f deploy/docker-compose.yml --env-file .env up -d postgres redis minio
```

### Knowledge 能返回，但问题显示乱码

先拉最新代码，再重新执行：

```bash
git pull origin main
scripts\verify-local.cmd
```

新脚本不再打印中文 JSON，避免 Windows 终端显示层乱码。
