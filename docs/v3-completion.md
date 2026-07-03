# V3 完成说明

## V3 目标

V3 目标是把 V2 的“工程基础态”升级为“平台展示态”，重点体现 AI 应用工程化平台能力：可视化工作流、工具调用审计、Prompt/Eval 对比、在线 Demo 动线和完整验收。

## 已完成范围

| 模块 | V3 完成内容 |
|---|---|
| Workflow Canvas | `/workflows` 切换为轻量可视化工作流画布，展示节点、状态和输出详情 |
| Tool Audit | 新增工具调用审计服务，Agent 每次工具调用生成 trace_id、audit_id、耗时和状态 |
| Audit API | 新增 `/api/audit/tools`、`/api/audit/tools/summary`、`/api/audit/tools/{id}` |
| Audit Console | 新增 `/audit` 页面，展示工具调用列表、统计卡片和审计详情 |
| Eval Compare | `/evals` 切换为 Prompt / Eval 对比中心，可横向比较三组模型或 Prompt 效果 |
| Demo Route | 新增 `/demo` 演示动线页，适合录屏和面试展示 |
| Verification | 系统体检加入 V3 模块，验收脚本升级为 12 步 |
| Docs | 新增 V3 完成说明，README 同步 V3 平台展示态 |

## V3 新增页面

- `/demo`：在线 Demo 演示动线
- `/workflows`：可视化工作流画布
- `/audit`：工具调用审计控制台
- `/evals`：Prompt / Eval 对比中心
- `/verification`：V3 系统体检

## V3 新增接口

- `GET /api/audit/tools/summary`
- `GET /api/audit/tools`
- `GET /api/audit/tools/{record_id}`
- `POST /api/agents/1/chat`：返回 `trace_id` 和带审计信息的 `tool_calls`

## V3 验收命令

```bash
pnpm build:web
cd apps/api
python -m compileall app
python -m pytest
```

接口验收：

```bash
bash scripts/verify-local.sh
```

Windows：

```cmd
scripts\verify-local.cmd
```

## V3 验收重点

1. `/demo` 能打开并展示完整演示路线。
2. `/workflows` 能看到可视化节点画布，运行后有节点输出。
3. `/audit` 能看到工具调用审计记录。
4. `/agents` 运行后返回 `trace_id` 和 `audit_id`。
5. `/evals` 能运行三组评测对比。
6. `/verification` 体检中包含 tool_audit、workflow_canvas、eval_compare。

## 下一阶段建议

V4 可以继续做商业化增强：

- React Flow 真拖拽画布
- 审计日志持久化与筛选
- 多租户 RBAC 页面
- 真实 LLM-as-Judge 评测
- 在线部署和演示视频
- GitHub README 截图/GIF
