# Agent 设计

## 工具调用流程

```txt
用户问题 → 读取 Agent 配置 → 判断可用工具 → 执行工具 → 记录 tool_call_log → 汇总工具结果 → LLM 生成最终答案
```

## 第一阶段工具

- `knowledge_search`：知识库检索
- `sql_query`：只读 SQL 查询
- `http_request`：HTTP API 请求
- `calculator`：计算器

## 安全策略

- SQL 工具仅允许 SELECT
- HTTP 工具需要 SSRF 防护
- 工具调用必须记录输入、输出、状态和耗时
- API Key 不回显、不进日志
