# AgentFlow-AI V1.5 Release Note

## 发布定位

V1.5 是 AgentFlow-AI 的可演示作品版本，目标是用于 GitHub 展示、简历项目、面试讲解和后续 V2 生产化开发。

## 核心能力

- 模型供应商配置：固定选项输入、Base URL、密钥脱敏、连接测试
- Chat Playground：后端 Chat Completion 接口、流式接口骨架
- 知识库 RAG：文档上传、PDF/text 清洗、切片、本地向量检索、引用来源
- Agent：Tool Registry、知识库工具、计算器、SQL 查询安全演示、HTTP 请求安全演示
- Workflow：节点协议、默认工作流、运行链路、node_runs 展示
- Prompt：模板、版本、变量渲染、测试
- Eval：评测集、评测运行、评分和原因
- Observability：调用量、Token、成本、耗时、失败率
- Verification：系统体检接口、验收中心、验收脚本
- Deployment：Docker Compose、PostgreSQL、Redis、MinIO、Nginx
- CI：Full CI 覆盖 API compile/test 和 Web build

## 本地验收命令

```bash
pnpm install
pnpm build:web
cd apps/api
python -m compileall app
python -m pytest
```

接口验收：

```bash
bash scripts/verify-local.sh
```

Windows：

```cmd
scripts\verify-local.cmd
```

## 推荐演示顺序

1. 打开 `/dashboard` 讲系统定位。
2. 打开 `/settings` 讲多模型供应商与密钥安全。
3. 打开 `/knowledge` 上传文档并运行 RAG 问答。
4. 打开 `/agents` 展示 tool_calls。
5. 打开 `/workflows` 展示 node_runs。
6. 打开 `/prompts` 展示 Prompt 渲染。
7. 打开 `/evals` 展示评测评分。
8. 打开 `/verification` 展示完整系统体检。

## 已知边界

- 当前版本优先保证演示闭环，部分数据仍使用内存实现。
- 真实模型供应商调用需要在本地填入有效密钥后继续联调。
- 真实 Embedding + pgvector 是 V2 重点。
- React Flow 拖拽画布是 V3 重点。

## 下一版本目标

V2 目标是从“作品演示态”升级到“工程生产化基础态”：

- 数据持久化
- 真实 Embedding
- pgvector 检索
- 模型真实调用
- 调用日志落库
- Prompt / Eval / Workflow 落库
