# 展示素材与录屏准备

## 截图清单

建议使用 16:9 宽屏截图，文件放在 `docs/assets/screenshots/`。

| 文件 | 页面 | 展示点 |
|---|---|---|
| `01-dashboard.png` | `/dashboard` | 调用量、Token、耗时、失败率 |
| `02-settings.png` | `/settings` | 模型供应商固定选项输入、密钥脱敏 |
| `03-chat.png` | `/chat` | Chat Playground |
| `04-knowledge-rag.png` | `/knowledge` | 知识库 RAG 问答和引用来源 |
| `05-agents-tool-calls.png` | `/agents` | Agent tool_calls、trace_id、persistent_audit_id |
| `06-workflows-react-flow.png` | `/workflows` | React Flow 画布、拖拽、连线、节点输出 |
| `07-audit.png` | `/audit` | 数据库优先审计记录 |
| `08-evals.png` | `/evals` | Eval 对比 |
| `09-verification.png` | `/verification` | V4 体检结果 |

## 录屏脚本

建议 3-5 分钟，按以下顺序：

1. 20 秒：项目定位，不是聊天 Demo，而是企业 AI 平台闭环。
2. 30 秒：Dashboard，展示调用量、Token、耗时、失败率。
3. 40 秒：Settings，展示多供应商与密钥脱敏。
4. 60 秒：Knowledge，上传文档并 RAG 问答，强调引用来源。
5. 40 秒：Agents，展示工具调用链路和持久化审计 ID。
6. 50 秒：Workflow，展示 React Flow 拖拽、连线和节点输出。
7. 30 秒：Audit，展示工具审计记录来源于数据库。
8. 30 秒：Eval，展示 Prompt / 模型横向对比。
9. 30 秒：Verification，展示 14 步验收通过。
10. 20 秒：总结技术栈与下一阶段 V5。

## README 嵌入建议

截图准备好后，在 README 的“演示路径”上方加入：

```md
## 项目截图

![Dashboard](docs/assets/screenshots/01-dashboard.png)
![Knowledge RAG](docs/assets/screenshots/04-knowledge-rag.png)
![Agent Tool Calls](docs/assets/screenshots/05-agents-tool-calls.png)
![Workflow Canvas](docs/assets/screenshots/06-workflows-react-flow.png)
![Verification](docs/assets/screenshots/09-verification.png)
```

## 展示关键词

- 企业 AI 落地闭环。
- 可追溯 RAG 引用。
- Agent 工具调用可观测。
- 工具调用审计持久化。
- React Flow 工作流编排。
- Prompt 版本与 Eval 对比。
- Token 成本统计。
- Docker + uv 本地持久化验收。
