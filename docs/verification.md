# 当前应该检验什么

按优先级检验以下 6 类。

## 1. 启动验收

```bash
pnpm dev:web
cd apps/api
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

检查：

- `http://localhost:3000` 可打开
- `http://localhost:8000/health` 返回 ok
- `http://localhost:8000/docs` 可打开

## 2. 系统体检

```bash
curl http://localhost:8000/api/system/health/full
```

也可以访问：

```txt
http://localhost:3000/verification
```

## 3. 核心接口验收

- `GET /api/model-providers`
- `POST /api/chat/completions`
- `GET /api/knowledge-bases`
- `POST /api/knowledge-bases/1/query`
- `GET /api/tools`
- `POST /api/agents/1/chat`
- `POST /api/workflows/1/run`
- `GET /api/prompts`
- `POST /api/evals/runs`

## 4. 页面验收

- `/settings`：新增模型供应商、脱敏展示、测试连接
- `/chat`：输入问题，返回后端回答
- `/knowledge`：上传文档、问答、展示引用来源
- `/agents`：运行 Agent，展示 tool_calls
- `/workflows`：运行工作流，展示 node_runs
- `/prompts`：模板渲染
- `/evals`：运行评测
- `/verification`：系统体检

## 5. 构建验收

```bash
pnpm --filter @agentflow/web build
cd apps/api
python -m compileall app
python -m pytest
```

## 6. Docker 验收

```bash
docker compose -f deploy/docker-compose.yml --env-file .env up -d --build
```

检查：

- Web: `http://localhost:3000`
- API: `http://localhost:8000/docs`
- Gateway: `http://localhost:8080`
