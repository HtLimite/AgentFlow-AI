# 工作流设计

## 当前实现

当前版本实现了工作流节点协议和串行执行器。

## 节点类型

- `start`：输入节点
- `knowledge`：知识库检索节点
- `llm`：回答生成节点
- `condition`：条件节点预留
- `http`：HTTP 节点预留
- `end`：结束节点

## Definition 示例

```json
{
  "nodes": [
    { "id": "start_1", "type": "start", "data": {} },
    { "id": "knowledge_1", "type": "knowledge", "data": { "kb_id": 1, "top_k": 3 } },
    { "id": "llm_1", "type": "llm", "data": { "prompt": "根据知识库结果回答：{{question}}" } },
    { "id": "end_1", "type": "end", "data": {} }
  ],
  "edges": [
    { "source": "start_1", "target": "knowledge_1" },
    { "source": "knowledge_1", "target": "llm_1" },
    { "source": "llm_1", "target": "end_1" }
  ]
}
```

## 执行流程

```txt
读取 definition → 找 Start → 沿 edge 执行节点 → 保存节点输入输出 → End 停止 → 返回 node_runs
```

## 后续升级

- React Flow 画布
- 条件分支
- 节点失败策略
- 并行节点
- 人工确认节点
