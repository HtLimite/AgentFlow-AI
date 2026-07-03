"use client";

import { useMemo, useState } from "react";
import {
  addEdge,
  Background,
  Controls,
  MiniMap,
  ReactFlow,
  useEdgesState,
  useNodesState,
  type Connection,
  type Edge,
  type Node,
} from "@xyflow/react";
import { apiJson } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

interface WorkflowRunResult {
  status: string;
  source?: string;
  run_id?: number;
  node_runs: Array<{
    node_id: string;
    node_type: string;
    status: string;
    input?: unknown;
    output: unknown;
  }>;
}

type WorkflowNodeData = {
  label: string;
  nodeType: string;
  description: string;
  config?: Record<string, unknown>;
};

const initialNodes: Array<Node<WorkflowNodeData>> = [
  {
    id: "start_1",
    type: "input",
    position: { x: 40, y: 160 },
    data: { label: "Start", nodeType: "start", description: "接收用户输入" },
  },
  {
    id: "knowledge_1",
    position: { x: 280, y: 80 },
    data: { label: "Knowledge", nodeType: "knowledge", description: "检索知识库", config: { kb_id: 1, top_k: 3 } },
  },
  {
    id: "llm_1",
    position: { x: 560, y: 160 },
    data: { label: "LLM", nodeType: "llm", description: "生成回答", config: { prompt: "根据知识库结果回答：{{question}}" } },
  },
  {
    id: "condition_1",
    position: { x: 820, y: 80 },
    data: { label: "Condition", nodeType: "condition", description: "质量判断", config: { expression: "score >= 0.7" } },
  },
  {
    id: "end_1",
    type: "output",
    position: { x: 1040, y: 160 },
    data: { label: "End", nodeType: "end", description: "输出结果" },
  },
];

const initialEdges: Edge[] = [
  { id: "e-start-knowledge", source: "start_1", target: "knowledge_1", animated: true },
  { id: "e-knowledge-llm", source: "knowledge_1", target: "llm_1", animated: true },
  { id: "e-llm-condition", source: "llm_1", target: "condition_1", animated: true },
  { id: "e-condition-end", source: "condition_1", target: "end_1", animated: true },
];

function buildDefinition(nodes: Array<Node<WorkflowNodeData>>, edges: Edge[]) {
  return {
    nodes: nodes.map((node) => ({ id: node.id, type: node.data.nodeType, data: node.data.config ?? {} })),
    edges: edges.map((edge) => ({ source: edge.source, target: edge.target })),
  };
}

function nodeClassName(isActive: boolean, isSelected: boolean) {
  if (isSelected) {
    return "border-blue-300 bg-blue-500/20";
  }
  if (isActive) {
    return "border-emerald-300 bg-emerald-500/20";
  }
  return "border-slate-700 bg-slate-900";
}

export function WorkflowCanvas() {
  const [nodes, setNodes, onNodesChange] = useNodesState<WorkflowNodeData>(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [result, setResult] = useState<WorkflowRunResult | null>(null);
  const [selected, setSelected] = useState<string>("start_1");
  const [error, setError] = useState("");

  const activeNodeIds = useMemo(() => new Set(result?.node_runs?.map((item) => item.node_id) ?? []), [result]);
  const selectedRun = result?.node_runs?.find((item) => item.node_id === selected);
  const selectedNode = nodes.find((node) => node.id === selected);
  const definition = useMemo(() => buildDefinition(nodes, edges), [nodes, edges]);

  async function run() {
    try {
      setError("");
      const data = await apiJson<WorkflowRunResult>("/api/workflows/1/run", {
        input: { question: "报销流程是什么？" },
        definition,
      });
      setResult(data);
      setSelected(data.node_runs?.[0]?.node_id ?? nodes[0]?.id ?? "start_1");
    } catch (err) {
      setError(err instanceof Error ? err.message : "工作流运行失败");
    }
  }

  function addDemoNode() {
    const id = `http_${Date.now()}`;
    setNodes((items) => [
      ...items,
      {
        id,
        position: { x: 620, y: 360 },
        data: { label: "HTTP", nodeType: "http", description: "调用外部 API", config: { method: "GET", url: "https://example.com/api/demo" } },
      },
    ]);
  }

  return (
    <div className="space-y-4">
      <Card className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-xl font-semibold">V4 React Flow 拖拽工作流画布</h2>
          <p className="mt-1 text-sm text-slate-400">支持节点拖拽、连线、运行状态高亮、节点输出详情和 definition JSON 预览。</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button onClick={addDemoNode}>添加 HTTP 节点</Button>
          <Button onClick={run}>运行当前画布</Button>
        </div>
      </Card>

      {error && <Card className="border-red-400/40 text-red-200">{error}</Card>}

      <Card>
        <div className="h-[520px] overflow-hidden rounded-2xl border border-white/10 bg-slate-950">
          <ReactFlow
            nodes={nodes.map((node) => ({
              ...node,
              className: `rounded-xl border px-4 py-3 text-white shadow-xl ${nodeClassName(activeNodeIds.has(node.id), selected === node.id)}`,
            }))}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={(connection: Connection) => setEdges((items) => addEdge({ ...connection, animated: true }, items))}
            onNodeClick={(_, node) => setSelected(node.id)}
            fitView
          >
            <Background />
            <Controls />
            <MiniMap pannable zoomable />
          </ReactFlow>
        </div>
      </Card>

      <div className="grid gap-4 xl:grid-cols-3">
        <Card>
          <h3 className="font-semibold">选中节点</h3>
          <pre className="mt-4 max-h-96 overflow-auto whitespace-pre-wrap rounded-xl bg-slate-950/70 p-4 text-sm text-slate-200">
            {JSON.stringify(selectedNode?.data ?? { node_id: selected }, null, 2)}
          </pre>
        </Card>
        <Card>
          <h3 className="font-semibold">节点运行输出</h3>
          <pre className="mt-4 max-h-96 overflow-auto whitespace-pre-wrap rounded-xl bg-slate-950/70 p-4 text-sm text-slate-200">
            {JSON.stringify(selectedRun ?? { node_id: selected, message: "运行后查看节点输出" }, null, 2)}
          </pre>
        </Card>
        <Card>
          <h3 className="font-semibold">当前 Definition</h3>
          <pre className="mt-4 max-h-96 overflow-auto whitespace-pre-wrap rounded-xl bg-slate-950/70 p-4 text-sm text-slate-200">
            {JSON.stringify({ status: result?.status ?? "idle", run_id: result?.run_id, source: result?.source, definition }, null, 2)}
          </pre>
        </Card>
      </div>
    </div>
  );
}
