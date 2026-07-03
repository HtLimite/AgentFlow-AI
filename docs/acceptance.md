# 阶段验收清单

本清单只记录当前阶段应该检查的事项。详细命令见 `docs/verification.md`，本地启动见 `docs/local-development.md`。

## 1. 启动验收

- [ ] Docker Desktop 已启动。
- [ ] `postgres / redis / minio` 容器已启动。
- [ ] 后端 `http://localhost:8000/health` 返回 `ok`。
- [ ] 后端 `http://localhost:8000/docs` 可打开。
- [ ] 前端 `http://localhost:3000` 可打开。

## 2. 自动验收

- [ ] Windows 可执行 `scripts\verify-local.cmd`。
- [ ] 验证脚本 6 步全部输出 `PASS`。
- [ ] `cd apps/api && python -m compileall app` 通过。
- [ ] `cd apps/api && python -m pytest` 通过。
- [ ] `pnpm --filter @agentflow/web build` 通过。

## 3. 页面验收

- [ ] `/dashboard` 可展示看板数据。
- [ ] `/settings` 可新增模型供应商，供应商类型为固定选项，API Key 脱敏展示。
- [ ] `/chat` 可输入问题并收到回答。
- [ ] `/knowledge` 可上传 txt / md / pdf，问答展示引用来源。
- [ ] `/agents` 可展示工具调用 `tool_calls`。
- [ ] `/workflows` 可运行工作流链路。
- [ ] `/prompts` 可测试 Prompt 变量渲染。
- [ ] `/evals` 可运行评测并返回分数。
- [ ] `/verification` 可展示系统体检结果。

## 4. PDF / RAG 专项验收

- [ ] 上传 PDF 后不再出现 `%PDF-1.7`、`FlateDecode` 这类二进制内容。
- [ ] 上传 PDF 后不再出现 `由PDA回调` 这类控制字符。
- [ ] 扫描版 PDF 无文本时能返回明确错误，而不是入库乱码。
- [ ] RAG 回答里有 `citations`、`document`、`score`、`chunk_index`。

## 5. 作品验收

- [ ] README 能说明项目定位、启动方式、验收入口。
- [ ] `docs/README.md` 能作为文档中心入口。
- [ ] `docs/current-status.md` 能说明当前真实状态与边界。
- [ ] `docs/roadmap.md` 能说明下一步计划。
- [ ] 截图与演示视频准备情况记录在 `docs/showcase-checklist.md`。

## 6. 当前不作为通过标准的事项

这些属于后续 V3 / 生产化增强，当前阶段不要求全部完成：

- [ ] 真实 Embedding + pgvector 相似度 SQL 检索。
- [ ] React Flow 拖拽式工作流画布。
- [ ] 多租户 RBAC。
- [ ] 在线 Demo。
- [ ] 完整生产级审计检索。
