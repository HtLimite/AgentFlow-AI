# AgentFlow-AI 文档中心

这份文档用于解决仓库文档分散、口径不一致的问题。以后先看本页，再按目的进入对应文档。

## 1. 当前最该看的文档

| 文档 | 作用 | 适合场景 |
|---|---|---|
| `docs/current-status.md` | 当前项目真实状态、已完成能力、边界 | 判断现在能演示什么 |
| `docs/local-development.md` | Windows 本地启动、Docker 基础设施、常见命令 | 本地跑项目 |
| `docs/verification.md` | 验收命令、接口验收、构建测试、页面验收 | 检查是否跑通 |
| `docs/acceptance.md` | 阶段验收清单 | 提交前逐项勾选 |
| `docs/roadmap.md` | 下一阶段计划 | 继续推进 V3 / 生产化 |

## 2. 模块设计文档

| 文档 | 内容 |
|---|---|
| `docs/architecture.md` | 总体架构、模块边界 |
| `docs/database.md` | 表结构与持久化设计 |
| `docs/rag.md` | RAG、PDF 解析、文本清洗、引用来源 |
| `docs/agent.md` | Agent 与工具调用设计 |
| `docs/workflow.md` | Workflow 执行链路 |
| `docs/interview.md` | 面试讲解稿与项目表达 |

## 3. 阶段与历史文档

| 文档 | 定位 |
|---|---|
| `docs/release-v1.5.md` | V1.5 可演示作品包说明 |
| `docs/v2-completion.md` | V2 阶段完成说明，作为阶段记录保留 |
| `docs/v2-execution-plan.md` | V2 执行计划，已不作为当前操作入口 |
| `docs/final-checklist.md` | 早期最终交付清单，后续以 `acceptance.md` 为准 |
| `docs/weekly-commits.md` | 周提交记录 |
| `docs/showcase-checklist.md` | 截图、录屏、作品展示准备 |

## 4. 推荐阅读顺序

### 本地启动

```txt
README.md
→ docs/local-development.md
→ docs/verification.md
```

### 准备面试 / 展示项目

```txt
README.md
→ docs/current-status.md
→ docs/interview.md
→ docs/showcase-checklist.md
```

### 继续开发

```txt
README.md
→ docs/current-status.md
→ docs/roadmap.md
→ docs/architecture.md
→ 对应模块文档
```

## 5. 维护规则

- README 只放项目总览、快速启动、验收入口，不再堆大量细节。
- 当前真实状态统一写在 `docs/current-status.md`。
- 本地启动统一写在 `docs/local-development.md`。
- 验收命令统一写在 `docs/verification.md`。
- 阶段计划和历史记录可以保留，但不要作为当前操作入口。
- 新增功能后，至少同步更新 `current-status.md`、`verification.md` 或 `roadmap.md` 中对应一处。
