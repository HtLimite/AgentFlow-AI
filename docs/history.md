# 历史版本与阶段记录

本文档只记录历史阶段，不作为当前启动或验收入口。当前状态以 `docs/current-status.md` 为准，当前验收以 `docs/verification.md` 为准。

## V1.5：可演示作品包

定位：用于 GitHub 展示、简历项目、面试讲解和后续 V2 工程化开发。

完成内容：

- 模型供应商配置：固定选项输入、Base URL、密钥脱敏、连接测试。
- Chat Playground：后端 Chat Completion 接口、流式接口骨架。
- 知识库 RAG：文档上传、PDF/text 清洗、切片、本地向量检索、引用来源。
- Agent：Tool Registry、知识库工具、计算器、SQL 查询安全演示、HTTP 请求安全演示。
- Workflow：节点协议、默认工作流、运行链路、node_runs 展示。
- Prompt：模板、版本、变量渲染、测试。
- Eval：评测集、评测运行、评分和原因。
- Observability：调用量、Token、成本、耗时、失败率。
- Verification：系统体检接口、验收中心、验收脚本。
- Deployment：Docker Compose、PostgreSQL、Redis、MinIO、Nginx。
- CI：API compile/test 和 Web build。

## V2：真实工程基础态

目标：从“可演示作品”升级到“真实工程基础态”，重点补齐持久化、供应商适配、Embedding 门面、部署初始化、可观测数据落库和持久化优先验收。

完成内容：

| 模块 | 完成内容 |
|---|---|
| Knowledge | 知识库、文档、切片数据库优先；数据库不可用时 fallback 到内存演示 |
| Embedding | 新增 `EmbeddingService` 门面，默认本地确定性向量，可替换真实 Provider |
| Model Provider | 新增 Provider Adapter，Settings 测试接口可真实探测供应商可达性 |
| Chat | Chat Completion 可优先走已配置供应商，失败时 fallback 到本地演示回答 |
| Prompt | 新增 Prompt 持久化服务，支持模板、版本、变量渲染落库 |
| Workflow | 新增 Workflow definition、run、node_run 持久化服务 |
| Eval | 新增 Eval dataset、case、run 持久化服务 |
| Observability | LLM 调用日志、Token、成本、耗时写入数据库，Dashboard 数据库优先聚合 |
| Deploy | Docker PostgreSQL 初始化改为执行 `deploy/postgres/*.sql` 全部脚本 |
| Verify | 本地验收脚本升级为持久化优先验收 |

## V3：平台展示态

目标：把 V2 的“工程基础态”升级为“平台展示态”，重点体现 AI 应用工程化平台能力：可视化工作流、工具调用审计、Prompt/Eval 对比、在线 Demo 动线和完整验收。

完成内容：

| 模块 | 完成内容 |
|---|---|
| Workflow Canvas | `/workflows` 切换为轻量可视化工作流画布，展示节点、状态和输出详情 |
| Tool Audit | 新增工具调用审计服务，Agent 每次工具调用生成 trace_id、audit_id、耗时和状态 |
| Audit API | 新增 `/api/audit/tools`、`/api/audit/tools/summary`、`/api/audit/tools/{record_id}` |
| Audit Console | 新增 `/audit` 页面，展示工具调用列表、统计卡片和审计详情 |
| Eval Compare | `/evals` 切换为 Prompt / Eval 对比中心，可横向比较三组模型或 Prompt 效果 |
| Demo Route | 新增 `/demo` 演示动线页，适合录屏和面试展示 |
| Verification | 系统体检加入 V3 模块，验收脚本升级为 12 步 |
| Docs | 新增 V3 完成说明，README 同步 V3 平台展示态 |

## V4：工程增强态

目标：把 V3 的轻量展示能力升级成更接近商业产品的工程能力。

完成内容：

- React Flow 工作流画布基础版。
- 工具调用审计数据库持久化。
- pgvector SQL 检索基础能力。
- 多租户 RBAC 请求上下文。
- 本地验收脚本升级为 14 步。
- README 与 docs 文档结构整理。

## 原按周提交规划

| 周期 | 提交范围 |
|---|---|
| Week 1 | Monorepo、前端/后端启动骨架、Docker 基础、README、演示脚本、验收清单 |
| Week 2 | 知识库、文档上传、文档解析、文本切片、检索、RAG 问答、引用来源 |
| Week 3 | Tool Registry、知识库检索工具、计算器工具、SQL 工具安全框架、HTTP 工具安全框架、Agent 调用链路 |
| Week 4 | Prompt 模板、变量渲染、调用日志、成本估算、Dashboard 数据聚合 |
| Week 5 | 节点协议、执行器、节点运行记录、前端运行面板、React Flow 接入点 |
| Week 6 | 评测集、评测运行、演示文档、Roadmap、简历描述、面试讲解稿 |

## 已合并旧文档

以下文档内容已整合到本文或新的模块文档中，并从仓库中删除：

- `docs/release-v1.5.md`
- `docs/v2-completion.md`
- `docs/v2-execution-plan.md`
- `docs/v3-completion.md`
- `docs/final-checklist.md`
- `docs/weekly-commits.md`
- `docs/showcase-checklist.md`
- `docs/database.md`
- `docs/rag.md`
- `docs/agent.md`
- `docs/workflow.md`
- `docs/acceptance.md`
