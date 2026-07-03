# 架构设计

AgentFlow-AI 采用前后端分离 + Monorepo 结构。

```txt
Next.js Web
  ↓ REST / SSE
FastAPI API
  ↓
PostgreSQL + pgvector / Redis / MinIO
  ↓
OpenAI-Compatible Model Providers
```

## 模块边界

- Web：管理台、Chat Playground、知识库、Agent、工作流、Prompt、评测与设置页面。
- API：统一路由、模型网关、RAG、Agent 工具调用、工作流执行、日志统计。
- PostgreSQL：业务数据、向量数据、调用日志。
- Redis：缓存、任务队列预留。
- MinIO：上传文档与解析产物存储。

## 第一阶段原则

先跑通 RAG 闭环，再扩展工作流、多租户和评测。
