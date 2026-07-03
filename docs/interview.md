# 面试讲解稿

## 一句话

AgentFlow-AI 是一个企业级 AI Agent 工作流与知识库平台，覆盖模型接入、RAG、工具调用、工作流编排、Prompt 管理、调用日志、成本统计、效果评测、审计持久化、RBAC 上下文和 Docker 部署。

## 讲解顺序

1. 为什么做这个项目。
2. 解决什么企业问题。
3. 整体架构是什么。
4. RAG 怎么实现。
5. Agent 怎么调用工具。
6. 工具调用怎么审计和追踪。
7. Workflow 怎么用 React Flow 编排。
8. Prompt 怎么管理。
9. 日志、成本和 Dashboard 怎么统计。
10. Eval 怎么做。
11. 本地持久化和 Docker 怎么验收。
12. 还有哪些生产化边界。

## 核心表达

企业落地 AI 不只是接一个聊天接口，真正的问题是知识怎么接入、工具怎么调用、流程怎么控制、结果怎么评估、成本怎么观测、权限怎么隔离、审计怎么追踪。所以我把 AgentFlow-AI 设计成完整的企业级 AI 应用平台。

## 简历写法

```txt
AgentFlow-AI｜企业级 AI Agent 工作流与知识库平台
技术栈：Next.js、React、TypeScript、React Flow、FastAPI、PostgreSQL、pgvector、Redis、MinIO、Docker、uv、OpenAI-Compatible API、SSE

项目描述：
面向企业知识管理、客服运营和内部提效场景的 AI Agent 平台，支持模型供应商配置、知识库 RAG 问答、Agent 工具调用、React Flow 工作流编排、Prompt 模板管理、模型调用日志、Token 成本统计、效果评测、工具调用审计持久化和 Docker 本地部署。

核心亮点：
- 设计模型供应商配置模块，支持动态配置、连接测试、敏感字段加密保存和脱敏展示。
- 实现知识库 RAG 闭环，支持文档上传、PDF 文本提取、chunk 切分、pgvector SQL 检索、问答和引用来源展示。
- 基于 Tool Registry 实现 Agent 工具调用机制，内置知识库检索、计算器、只读 SQL、安全 HTTP 工具。
- 实现工具调用审计持久化，Agent 调用返回 trace_id 和 persistent_audit_id，审计控制台支持查看调用记录与统计。
- 基于 React Flow 实现工作流画布基础版，支持节点拖拽、连线、MiniMap、Controls 和运行当前画布。
- 实现 Prompt 模板、版本记录、变量渲染和测试能力，方便管理不同业务场景提示词。
- 实现调用日志、Token 消耗、响应耗时、成本估算和 Dashboard 数据聚合。
- 设计 Eval 评测模块，用于比较模型和 Prompt 的回答质量、稳定性和成本。
- 使用 Docker Compose 提供 PostgreSQL、Redis、MinIO 基础设施，uv 启动 FastAPI，本地 14 步脚本完成持久化验收。
```

## 演示话术

> 这个项目的重点不是“能聊天”，而是完整的企业 AI 落地链路。比如知识库问答需要可追溯引用，Agent 调工具需要可观测和可审计，Prompt 调优需要版本和评测，模型调用需要成本和错误统计，工作流需要可视化编排，企业场景还需要租户和权限上下文。
