# AgentFlow-AI 文档中心

本文档是唯一入口，用于避免 README、阶段记录和模块设计文档口径分散。新读者先看本页，再按目的进入对应文档。

## 当前推荐阅读顺序

### 本地启动 / 验收

```txt
README.md
→ docs/local-development.md
→ docs/verification.md
```

### 判断项目当前完成度

```txt
README.md
→ docs/current-status.md
→ docs/roadmap.md
```

### 准备面试 / 简历 / 展示

```txt
README.md
→ docs/current-status.md
→ docs/interview.md
→ docs/showcase.md
```

### 继续开发

```txt
README.md
→ docs/current-status.md
→ docs/roadmap.md
→ docs/architecture.md
→ docs/modules.md
```

## 当前保留文档

| 文档 | 定位 | 维护规则 |
|---|---|---|
| `docs/current-status.md` | 当前真实状态、边界、可验证能力 | 功能完成后优先更新 |
| `docs/local-development.md` | 本地开发、Docker 基础设施、uv 后端启动 | 启动命令变更时更新 |
| `docs/verification.md` | 14 步验收、构建测试、页面验收 | 验收脚本变更时同步 |
| `docs/roadmap.md` | V4 之后的增强计划 | 阶段推进后更新 |
| `docs/architecture.md` | 总体架构、目录边界、运行链路 | 架构变化时更新 |
| `docs/modules.md` | 数据库、RAG、Agent、Workflow、Prompt、Eval 设计 | 模块能力变化时更新 |
| `docs/showcase.md` | 截图、录屏、GitHub 展示素材 | 准备作品包装时更新 |
| `docs/interview.md` | 面试讲解稿、简历项目描述 | 面试表达变化时更新 |
| `docs/history.md` | 历史版本、阶段记录、已合并旧文档 | 只追加，不作为当前操作入口 |

## 已整合 / 删除的旧文档

以下文档不再单独维护，内容已合并到 `docs/history.md`、`docs/modules.md`、`docs/showcase.md` 或 `docs/verification.md`：

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

## 文档维护规则

1. README 只放项目总览、快速启动、验收入口和文档入口。
2. 当前真实状态统一写在 `docs/current-status.md`。
3. 启动命令统一写在 `docs/local-development.md`。
4. 验收步骤统一写在 `docs/verification.md`。
5. 模块设计统一写在 `docs/modules.md`，避免每个模块散落一份小文档。
6. 阶段历史统一写在 `docs/history.md`，不要作为当前操作入口。
7. 新增功能后，至少同步更新 `current-status.md`、`verification.md` 或 `roadmap.md` 中对应一处。
