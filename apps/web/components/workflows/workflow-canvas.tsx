"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
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
import { apiGet, apiJson } from "@/lib/api-client";
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

type WorkflowNodeData = Record<string, unknown> & {
  label: string;
  nodeType: string;
  description: string;
  config?: Record<string, unknown>;
};

type WorkflowNode = Node<WorkflowNodeData>;
type WorkflowEdge = Edge;

type WorkflowItem = {
  id: number;
  name: string;
  enabled: boolean;
  node_count: number;
  edge_count: number;
};

type KnowledgeBaseItem = {
  id: number;
  name: string;
  document_count: number;
  chunk_count: number;
};

const initialNodes: WorkflowNode[] = [
  {
    id: "start_1",
    type: "input",
    position: { x: 40, y: 160 },
    data: { label: "Start", nodeType: "start", description: "接收用户输入" },
  },
  {
    id: "knowledge_1",
    position: { x: 280, y: 80 },
    data: { label: "Knowledge", nodeType: "knowledge", description: "检索当前选择的知识库", config: { top_k: 3 } },
  },
  {
    id: "llm_1",
    position: { x: 560, y: 160 },
    data: { label: "LLM", nodeType: "llm", description: "生成回答", config: { prompt: "根据上游结果回答用户问题" } },
  },
  {
    id: "condition_1",
    position: { x: 820, y: 80 },
    data: { label: "Condition", nodeType: "condition", description: "质量判断", config: {} },
  },
  {
    id: "end_1",
    type: "output",
    position: { x: 1040, y: 160 },
    data: { label: "End", nodeType: "end", description: "输出结果" },
  },
];

const initialEdges: WorkflowEdge[] = [
  { id: "e-start-knowledge", source: "start_1", target: "knowledge_1", animated: true },
  { id: "e-knowledge-llm", source: "knowledge_1", target: "llm_1", animated: true },
  { id: "e-llm-condition", source: "llm_1", target: "condition_1", animated: true },
  { id: "e-condition-end", source: "condition_1", target: "end_1", animated: true },
];

function buildDefinition(nodes: WorkflowNode[], edges: WorkflowEdge[], kbId: number | null) {
  return {
    nodes: nodes.map((node) => ({
      id: node.id,
      type: node.data.nodeType,
      data: node.data.nodeType === "knowledge" && kbId
        ? { ...(node.data.config ?? {}), kb_id: kbId }
        : node.data.config ?? {},
    })),
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
  const [nodes, setNodes, onNodesChange] = useNodesState<WorkflowNode>(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState<WorkflowEdge>(initialEdges);
  const [workflows, setWorkflows] = useState<WorkflowItem[]>([]);
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBaseItem[]>([]);
  const [selectedWorkflowId, setSelectedWorkflowId] = useState<number | null>(null);
  const [selectedKbId, setSelectedKbId] = useState<number | null>(null);
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<WorkflowRunResult | null>(null);
  const [selected, setSelected] = useState<string>("start_1");
  const [error, setError] = useState("");

  const activeNodeIds = useMemo(() => new Set(result?.node_runs?.map((item) => item.node_id) ?? []), [result]);
  const selectedRun = result?.node_runs?.find((item) => item.node_id === selected);
  const selectedNode = nodes.find((node) => node.id === selected);
  const definition = useMemo(() => buildDefinition(nodes, edges, selectedKbId), [nodes, edges, selectedKbId]);

  const loadRuntimeOptions = useCallback(async () => {
    const [workflowData, kbData] = await Promise.all([
      apiGet<WorkflowItem[]>("/api/workflows"),
      apiGet<KnowledgeBaseItem[]>("/api/knowledge-bases"),
    ]);
    setWorkflows(workflowData);
    setKnowledgeBases(kbData);
    setSelectedWorkflowId((current) => (current && workflowData.some((item) => item.id === current) ? current : workflowData[0]?.id ?? null));
    setSelectedKbId((current) => (current && kbData.some((item) => item.id === current) ? current : kbData[0]?.id ?? null));
  }, []);

  useEffect(() => {
    loadRuntimeOptions().catch((err) => setError(err instanceof Error ? err.message : "运行时配置加载失败"));
  }, [loadRuntimeOptions]);

  async function run() {
    if (!selectedWorkflowId) {
      setError("请先选择工作流");
      return;
    }
    if (!question.trim()) {
      setError("请输入工作流输入问题");
      return;
    }
    try {
      setError("");
      const data = await apiJson<WorkflowRunResult>(`/api/workflows/${selectedWorkflowId}/run`, {
        input: { question },
        definition,
      });
      setResult(data);
      setSelected(data.node_runs?.[0]?.node_id ?? nodes[0]?.id ?? "start_1");
    } catch (err) {
      setError(err instanceof Error ? err.message : "工作流运行失败");
    }
  }

  function addHttpNode() {
    const id = `http_${Date.now()}`;
    setNodes((items) => [
      ...items,
      {
        id,
        position: { x: 620, y: 360 },
        data: { label: "HTTP", nodeType: "http", description: "调用外部 API；请在 definition 中配置真实 URL", config: { method: "GET", url: "" } },
      },
    ]);
  }

  return (
    <div className="space-y-4">
      <Card className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-xl font-semibold">React Flow 拖拽工作流画布</h2>
          <p className="mt-1 text-sm text-slate-400">工作流、知识库和输入问题均从运行时选择，不固定 workflow_id、kb_id 或测试问题。</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button onClick={addHttpNode}>添加 HTTP 节点</Button>
          <Button onClick={run} disabled={!selectedWorkflowId || !question.trim()}>运行当前画布</Button>
        </div>
      </Card>

      <Card>
        <div className="grid gap-3 md:grid-cols-3">
          <label className="block text-sm text-slate-300">
            <span className="mb-1 block text-xs text-slate-500">工作流</span>
            <select className="w-full rounded-xl border border-white/10 bg-slate-950/60 px-4 py-3" value={selectedWorkflowId ?? ""} onChange={(event) => setSelectedWorkflowId(Number(event.target.value))}>
              {workflows.map((item) => (
                <option key={item.id} value={item.id}>{item.name}</option>
              ))}
            </select>
          </label>
          <label className="block text-sm text-slate-300">
            <span className="mb-1 block text-xs text-slate-500">知识库</span>
            <select className="w-full rounded-xl border border-white/10 bg-slate-950/60 px-4 py-3" value={selectedKbId ?? ""} onChange={(event) => setSelectedKbId(Number(event.target.value))}>
              {knowledgeBases.map((item) => (
                <option key={item.id} value={item.id}>{item.name}</option>
              ))}
            </select>
          </label>
          <label className="block text-sm text-slate-300">
            <span className="mb-1 block text-xs text-slate-500">输入问题</span>
            <input className="w-full rounded-xl border border-white/10 bg-slate-950/60 px-4 py-3" value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="输入本次工作流问题" />
          </label>
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
            {JSON.stringify({ status: result?.status ?? "idle", run_id: result?.run_id, source: result?.source, workflow_id: selectedWorkflowId, kb_id: selectedKbId, definition }, null, 2)}
          </pre>
        </Card>
      </div>
    </div>
  );
}
