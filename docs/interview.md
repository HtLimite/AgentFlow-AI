# 面试讲解稿

## 一句话

AgentFlow-AI 是一个企业级 AI Agent 工作流与知识库平台，覆盖模型接入、RAG、工具调用、工作流、Prompt 管理、调用日志、成本统计、评测和 Docker 部署。

## 讲解顺序

1. 为什么做这个项目
2. 解决什么企业问题
3. 整体架构是什么
4. RAG 怎么实现
5. Agent 怎么调用工具
6. 工作流怎么执行
7. Prompt 怎么管理
8. 日志和成本怎么统计
9. 评测怎么做
10. 部署怎么做

## 核心表达

企业落地 AI 不只是接一个聊天接口，真正的问题是知识怎么接入、工具怎么调用、流程怎么控制、结果怎么评估、成本怎么观测、权限怎么隔离。所以我把 AgentFlow-AI 设计成完整的企业级 AI 应用平台。

## 简历写法

```txt
AgentFlow-AI｜企业级 AI Agent 工作流与知识库平台
技术栈：Next.js、React、TypeScript、FastAPI、PostgreSQL、pgvector、Redis、MinIO、Docker、OpenAI-Compatible API、SSE

项目描述：
面向企业知识管理、客服运营和内部提效场景的 AI Agent 平台，支持模型供应商配置、知识库 RAG 问答、Agent 工具调用、工作流编排、Prompt 模板管理、模型调用日志、Token 成本统计、效果评测和 Docker 一键部署。

核心亮点：
- 设计模型供应商配置模块，支持动态配置、连接测试、敏感字段加密保存和脱敏展示。
- 实现知识库 RAG 闭环，支持文档上传、文本解析、chunk 切分、本地向量检索、问答和引用来源展示。
- 基于 Tool Registry 实现 Agent 工具调用机制，内置知识库检索、计算器、只读 SQL、安全 HTTP 工具。
- 设计 Workflow 节点协议和串行执行器，支持 Start、Knowledge、LLM、Condition、HTTP、End 节点运行链路。
- 实现 Prompt 模板、版本记录、变量渲染和测试能力，方便管理不同业务场景提示词。
- 实现调用日志、Token 消耗、响应耗时、成本估算和 Dashboard 数据聚合。
- 设计 Eval 评测模块，用于比较模型和 Prompt 的回答质量、稳定性和成本。
```

## 演示话术

> 这个项目的重点不是“能聊天”，而是完整的企业 AI 落地链路。比如知识库问答需要可追溯引用，Agent 调工具需要可观测链路，Prompt 调优需要版本和评测，模型调用需要成本和错误统计。
