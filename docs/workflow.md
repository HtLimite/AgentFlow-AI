# 工作流设计

V1 先预留页面与执行器骨架，V2/V3 接入 React Flow。

## 节点类型

- Start
- Knowledge
- LLM
- Condition
- HTTP
- End

## 执行逻辑

```txt
读取 definition → 找 Start → 沿 edge 执行节点 → 保存节点输入输出 → End 停止 → 保存 workflow_run
```

第一版不做循环、并行和人工审批，先保证可演示与可扩展。
