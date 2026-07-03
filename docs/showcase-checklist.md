# 展示素材清单

## 截图清单

建议使用 16:9 宽屏截图，文件放在 `docs/assets/screenshots/`。

- `01-dashboard.png`：数据看板
- `02-settings.png`：模型供应商固定选项输入
- `03-chat.png`：Chat Playground
- `04-knowledge-rag.png`：知识库 RAG 问答和引用来源
- `05-agents-tool-calls.png`：Agent tool_calls
- `06-workflows-node-runs.png`：Workflow node_runs
- `07-prompts.png`：Prompt 变量渲染
- `08-evals.png`：Eval 评分
- `09-verification.png`：系统体检

## 录屏脚本

建议 3-5 分钟，按以下顺序：

1. 20 秒：项目定位，不是聊天 Demo，而是企业 AI 平台闭环。
2. 40 秒：Settings，展示多供应商与密钥脱敏。
3. 60 秒：Knowledge，上传文档并 RAG 问答。
4. 40 秒：Agents，展示工具调用链路。
5. 40 秒：Workflow，展示节点运行链路。
6. 30 秒：Eval，展示评测结果。
7. 30 秒：Verification，展示系统体检。
8. 20 秒：总结技术栈与后续 V2。

## README 嵌入建议

截图准备好后，在 README 的“演示路径”上方加入：

```md
## 项目截图

![Dashboard](docs/assets/screenshots/01-dashboard.png)
![Knowledge RAG](docs/assets/screenshots/04-knowledge-rag.png)
![Agent Tool Calls](docs/assets/screenshots/05-agents-tool-calls.png)
![Verification](docs/assets/screenshots/09-verification.png)
```

## 面试讲解关键词

- 企业 AI 落地闭环
- 可追溯 RAG 引用
- Agent 工具调用可观测
- Prompt 版本与评测
- Token 成本统计
- Workflow 节点协议
- Docker 一键部署
