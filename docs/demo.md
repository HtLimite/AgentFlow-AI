# AgentFlow-AI 演示脚本

## 启动

```bash
pnpm dev:web
cd apps/api
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

打开：

- Web: `http://localhost:3000`
- API Docs: `http://localhost:8000/docs`

## 1. Settings：模型供应商

进入 `/settings`：

1. 新增 OpenAI-Compatible 供应商。
2. 保存后列表只展示脱敏后的密钥。
3. 点击测试，确认配置可用。

面试讲法：

> 模型配置没有写死在代码里，而是通过后台动态配置供应商，敏感字段后端加密保存，前端只展示脱敏结果。

## 2. Knowledge：RAG 闭环

进入 `/knowledge`：

1. 默认有一个企业制度知识库。
2. 上传 txt / md 文档。
3. 系统自动解析、切片。
4. 输入问题：`报销流程是什么？`
5. 查看答案和引用来源。

面试讲法：

> 我没有只返回大模型答案，而是展示命中文档、片段内容和相似度，方便用户校验，降低幻觉风险。

## 3. Agents：工具调用链路

进入 `/agents`：

1. 输入问题。
2. 点击运行 Agent。
3. 查看 tool_calls，包括工具名、输入、输出和状态。

面试讲法：

> Agent 不是黑盒聊天，而是有工具调用链路记录，方便排查问题和做审计。

## 4. Workflows：节点执行链路

进入 `/workflows`：

1. 点击运行工作流。
2. 查看 Start、LLM、End 等节点运行记录。

## 5. Prompts：模板测试

进入 `/prompts`：

1. 点击模板。
2. 后端根据变量渲染模板。
3. 查看最终 Prompt。

## 6. Evals：评测运行

进入 `/evals`：

1. 点击运行评测。
2. 查看总分、逐题得分和原因。

面试讲法：

> 企业 AI 应用不能靠感觉调 Prompt，必须用评测集比较模型、Prompt 和版本效果。
