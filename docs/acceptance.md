# 验收清单

## 基础启动

- [ ] `pnpm dev:web` 可启动前端
- [ ] `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000` 可启动后端
- [ ] `GET /health` 返回 ok
- [ ] `http://localhost:8000/docs` 可打开

## 页面验收

- [ ] `/dashboard` 可展示看板
- [ ] `/settings` 可新增模型供应商并脱敏展示
- [ ] `/chat` 可调用后端 Chat 接口
- [ ] `/knowledge` 可显示知识库、上传文档、问答并展示引用
- [ ] `/agents` 可展示 tool_calls
- [ ] `/workflows` 可展示节点运行链路
- [ ] `/prompts` 可渲染 Prompt 变量
- [ ] `/evals` 可运行评测并返回分数

## Docker 验收

- [ ] postgres 容器启动
- [ ] redis 容器启动
- [ ] minio 容器启动
- [ ] api 容器启动
- [ ] web 容器启动
- [ ] nginx 通过 8080 转发

## 作品验收

- [ ] README 有项目定位、技术栈、快速开始、演示路径
- [ ] docs 有架构、数据库、RAG、Agent、Workflow、面试材料
- [ ] commit 按功能点提交，不是改一点提交一次
- [ ] 可以录制 3-5 分钟演示视频
