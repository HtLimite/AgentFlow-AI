# V2 执行计划

V2 目标：从“可演示作品”升级到“真实工程基础”。

## Sprint 1：数据持久化

目标：把当前内存数据逐步落库。

任务：

- 知识库表、文档表、切片表落库
- Prompt 模板与版本落库
- Eval 数据集与运行记录落库
- Workflow definition 与 run/node_run 落库
- Dashboard 从日志表聚合

验收：

- 重启服务后知识库和 Prompt 不丢失
- `/verification` 模块状态保持通过

## Sprint 2：真实 Embedding + pgvector

目标：替换本地确定性向量。

任务：

- 定义 Embedding Provider 接口
- 支持 OpenAI-Compatible embedding endpoint
- 写入 `knowledge_chunk.embedding`
- 增加 pgvector cosine 检索
- 增加 embedding 失败重试与状态字段

验收：

- 上传文档后生成真实向量
- RAG 问答返回相似度排序
- 可切换本地向量与真实向量

## Sprint 3：真实模型调用

目标：Chat / RAG / Agent / Workflow 能调用真实模型。

任务：

- 定义 Chat Provider Adapter
- 支持 OpenAI-Compatible chat completions
- 支持流式输出
- 保存调用日志、Token、耗时、错误
- Settings 测试接口改为真实连接测试

验收：

- 配置 DeepSeek / Qwen / Kimi 任一供应商后可真实回答
- 调用日志可在 Dashboard 看到

## Sprint 4：Workflow 画布

目标：从执行器升级到可视化编排。

任务：

- 接入 React Flow
- 节点配置面板
- Start / Knowledge / LLM / Condition / HTTP / End 节点
- 保存 definition
- 前端展示 node_runs

验收：

- 拖拽节点组成工作流
- 运行后可查看每个节点输入输出

## Sprint 5：工程化安全与权限

目标：接近企业系统基础。

任务：

- tenant_id 链路
- audit_log 审计
- SQL 工具只读策略强化
- HTTP 工具 SSRF 规则强化
- API 参数校验与错误码统一

验收：

- 所有工具调用有审计记录
- 高风险请求被拒绝并返回明确错误

## Sprint 6：发布与在线 Demo

目标：形成完整作品发布。

任务：

- README 增加截图/GIF
- 录制演示视频
- 部署在线 Demo
- 准备简历版本和面试讲稿

验收：

- GitHub 首页可直接理解项目价值
- 面试 3 分钟内可讲清楚架构与亮点
