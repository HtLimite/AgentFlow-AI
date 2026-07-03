# Agent 设计

## 当前实现

当前版本实现 Tool Registry 和 4 个内置工具：

- `knowledge_search`：知识库检索
- `calculator`：安全计算器
- `sql_query`：只读 SQL 查询演示
- `http_request`：HTTP 请求安全演示

## 调用流程

```txt
用户问题 → Agent 选择工具 → 构建工具参数 → Tool Registry 执行 → 返回 tool_calls → 生成最终回答
```

## 可观测性

每次工具调用返回：

```json
{
  "tool_name": "knowledge_search",
  "input": {},
  "output": {},
  "status": "success",
  "error_message": null
}
```

## 安全边界

- SQL 工具只允许 SELECT
- HTTP 工具禁止本地地址
- 计算器只允许基础表达式 AST
- 未注册工具返回 failed 状态
