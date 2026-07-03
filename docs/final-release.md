# AgentFlow-AI 最终作品版

## 定位

AgentFlow-AI 是面向求职展示的企业级 AI 应用工程项目。

项目覆盖：模型配置、文档解析、知识库问答、Agent 工具调用、React Flow 工作流、审计记录、Prompt 管理、效果评测、Dashboard 和本地 Docker 基础设施。

## 演示路线

```txt
/showcase
/settings
/chat
/knowledge
/agents
/workflows
/audit
/evals
/dashboard
/verification
```

## 本地验收

```cmd
scripts\dev-infra.cmd
scripts\dev-api-uv.cmd
pnpm dev:web
scripts\verify-local.cmd
```

构建测试：

```bash
pnpm --filter @agentflow/web build
cd apps/api
uv run python -m compileall app
uv run python -m pytest
```

## 面试讲解

```txt
这是一个企业级 AI 应用平台的本地持久化最终演示版。
重点体现的是 AI 应用工程化能力，而不是只做一个聊天页面。
```

## 边界

当前适合作为作品展示和本地演示，不等同于线上商业 SaaS。继续产品化时，需要补充公开部署、演示视频、完整账号体系和更多生产运维能力。
