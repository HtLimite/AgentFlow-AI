# AgentFlow-AI 最终作品版

## 定位

AgentFlow-AI 是面向求职展示的企业级 AI 应用工程项目。

项目覆盖：模型配置、文档解析、知识库问答、项目诊断与部署排错、Agent 工具调用、React Flow 工作流、审计记录、Prompt 管理、效果评测、Dashboard 和本地 Docker 基础设施。

## 最有价值的真实场景

```txt
项目启动失败 / Docker 服务异常 / Nginx 502 / 数据库连不上
→ 打开 /diagnosis
→ 粘贴日志、关键配置、服务状态
→ 输出阻塞原因、修复动作、验收命令和诊断报告
```

这个场景用于解决“页面很多但感觉没用”的问题：先把项目收束到开发者真实排错闭环，而不是继续堆泛 Agent 模块。

## 演示路线

```txt
/showcase
/diagnosis
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

项目诊断接口专项验收：

```bash
curl http://localhost:8000/api/project-diagnosis/demo
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
重点体现的是 AI 应用工程化能力，不是只做一个聊天页面。
其中 /diagnosis 把项目收束到真实可感知的 DevOps 排错场景：基于日志、配置片段和服务状态输出问题信号、优先修复动作、验收命令和诊断报告。
```

## 边界

当前适合作为作品展示和本地演示，不等同于线上商业 SaaS。继续产品化时，需要补充公开部署、演示视频、完整账号体系、更强的真实 GitHub / Docker / 日志自动采集能力，以及更完整的生产运维安全策略。
