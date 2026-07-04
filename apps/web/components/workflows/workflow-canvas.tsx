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
import { apiGet, apiJson, errorMessage } from "@/lib/api-client";
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
type WorkflowEdge = Edge & { condition?: string };

type WorkflowItem = {
  id: number;
  name: string;
  enabled: boolean;
  node_count: number;
  edge_count: number;
};

type WorkflowDetail = {
  id: number;
  name: string;
  definition: { nodes: Array<{ id: string; type: string; data: Record<string, unknown> }>; edges: Array<{ source: string; target: string; condition?: string | null }> };
  enabled: boolean;
};

type KnowledgeBaseItem = {
  id: number;
  name: string;
  document_count: number;
  chunk_count: number;
};

const initialNodes: WorkflowNode[] = [
  { id: "start_1", type: "input", position: { x: 40, y: 160 }, data: { label: "Start", nodeType: "start", description: "接收用户输入" } },
  { id: "knowledge_1", position: { x: 280, y: 80 }, data: { label: "Knowledge", nodeType: "knowledge", description: "检索当前选择的知识库", config: { top_k: 3 } } },
  { id: "llm_1", position: { x: 560, y: 160 }, data: { label: "LLM", nodeType: "llm", description: "生成回答", config: { prompt: "根据上游结果回答用户问题" } } },
  { id: "end_1", type: "output", position: { x: 820, y: 160 }, data: { label: "End", nodeType: "end", description: "输出结果" } },
];

const initialEdges: WorkflowEdge[] = [
  { id: "e-start-knowledge", source: "start_1", target: "knowledge_1", animated: true },
  { id: "e-knowledge-llm", source: "knowledge_1", target: "llm_1", animated: true },
  { id: "e-llm-end", source: "llm_1", target: "end_1", animated: true },
];

const NODE_TYPE_OPTIONS = [
  { type: "start", label: "Start", description: "接收用户输入" },
  { type: "knowledge", label: "Knowledge", description: "检索知识库", defaultConfig: { top_k: 3 } },
  { type: "llm", label: "LLM", description: "调用大模型生成回答", defaultConfig: { prompt: "根据上游结果回答用户问题" } },
  { type: "condition", label: "Condition", description: "条件分支", defaultConfig: { key: "", operator: "equals", value: "" } },
  { type: "http", label: "HTTP", description: "调用外部 API", defaultConfig: { method: "GET", url: "" } },
  { type: "end", label: "End", description: "输出结果" },
] as const;

const OPERATOR_OPTIONS = ["equals", "not_equals", "contains", "gt", "lt", "gte", "lte"] as const;

function buildDefinition(nodes: WorkflowNode[], edges: WorkflowEdge[], kbId: number | null) {
  return {
    nodes: nodes.map((node) => ({
      id: node.id,
      type: node.data.nodeType,
      data: node.data.nodeType === "knowledge" && kbId
        ? { ...(node.data.config ?? {}), kb_id: kbId }
        : node.data.config ?? {},
    })),
    edges: edges.map((edge) => ({ source: edge.source, target: edge.target, condition: edge.condition ?? null })),
  };
}

function nodeClassName(isActive: boolean, isSelected: boolean) {
  if (isSelected) return "border-primary bg-primary/15";
  if (isActive) return "border-emerald-300 bg-emerald-500/20";
  return "border-border bg-panel";
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
  const [message, setMessage] = useState("拖拽节点、连线、编辑配置后运行或保存。");
  const [running, setRunning] = useState(false);
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);

  const activeNodeIds = useMemo(() => new Set(result?.node_runs?.map((item) => item.node_id) ?? []), [result]);
  const selectedRun = result?.node_runs?.find((item) => item.node_id === selected);
  const selectedNode = nodes.find((node) => node.id === selected) ?? null;
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
    loadRuntimeOptions()
      .catch((err) => setError(errorMessage(err, "运行时配置加载失败")))
      .finally(() => setLoading(false));
  }, [loadRuntimeOptions]);

  async function loadWorkflowDetail(id: number) {
    try {
      setError("");
      const detail = await apiGet<WorkflowDetail>(`/api/workflows/${id}`);
      const mappedNodes: WorkflowNode[] = (detail.definition.nodes ?? []).map((node, index) => {
        const meta = NODE_TYPE_OPTIONS.find((item) => item.type === node.type);
        const row = index * 200;
        return {
          id: node.id,
          type: node.type === "start" ? "input" : node.type === "end" ? "output" : undefined,
          position: { x: 40 + row, y: 160 },
          data: {
            label: meta?.label ?? node.type,
            nodeType: node.type,
            description: meta?.description ?? "",
            config: node.data ?? {},
          },
        };
      });
      const mappedEdges: WorkflowEdge[] = (detail.definition.edges ?? []).map((edge, index) => ({
        id: `e-${edge.source}-${edge.target}-${index}`,
        source: edge.source,
        target: edge.target,
        condition: edge.condition ?? undefined,
        animated: true,
        label: edge.condition ?? undefined,
      }));
      setNodes(mappedNodes.length > 0 ? mappedNodes : initialNodes);
      setEdges(mappedEdges);
      setSelected(mappedNodes[0]?.id ?? "start_1");
      setMessage(`已加载工作流「${detail.name}」到画布。`);
    } catch (err) {
      setError(errorMessage(err, "加载工作流定义失败"));
    }
  }

  async function run() {
    if (!selectedWorkflowId) {
      setError("请先选择工作流");
      return;
    }
    if (!question.trim()) {
      setError("请输入工作流输入问题");
      return;
    }
    setRunning(true);
    setError("");
    try {
      const data = await apiJson<WorkflowRunResult>(`/api/workflows/${selectedWorkflowId}/run`, {
        input: { question },
        definition,
      });
      setResult(data);
      setSelected(data.node_runs?.[0]?.node_id ?? nodes[0]?.id ?? "start_1");
      setMessage(`工作流运行完成，状态：${data.status}。`);
    } catch (err) {
      setError(errorMessage(err, "工作流运行失败"));
    } finally {
      setRunning(false);
    }
  }

  async function saveAsNewWorkflow() {
    const name = window.prompt("输入新工作流名称", "我的工作流");
    if (!name?.trim()) return;
    setSaving(true);
    setError("");
    try {
      await apiJson("/api/workflows", { name: name.trim(), definition, enabled: true });
      setMessage(`工作流「${name}」已保存。`);
      await loadRuntimeOptions();
    } catch (err) {
      setError(errorMessage(err, "保存工作流失败（需要数据库可用）"));
    } finally {
      setSaving(false);
    }
  }

  async function updateCurrentWorkflow() {
    if (!selectedWorkflowId) {
      setError("请先选择要更新的工作流");
      return;
    }
    setSaving(true);
    setError("");
    try {
      await apiJson(`/api/workflows/${selectedWorkflowId}`, { definition }, "PUT");
      setMessage(`工作流 #${selectedWorkflowId} 定义已更新。`);
    } catch (err) {
      setError(errorMessage(err, "更新工作流失败（需要数据库可用）"));
    } finally {
      setSaving(false);
    }
  }

  function addNode(nodeType: string) {
    const meta = NODE_TYPE_OPTIONS.find((item) => item.type === nodeType);
    if (!meta) return;
    const id = `${nodeType}_${Date.now()}`;
    setNodes((items) => [
      ...items,
      {
        id,
        type: nodeType === "start" ? "input" : nodeType === "end" ? "output" : undefined,
        position: { x: 200 + Math.random() * 200, y: 300 + Math.random() * 120 },
        data: {
          label: meta.label,
          nodeType,
          description: meta.description,
          config: "defaultConfig" in meta && meta.defaultConfig ? { ...meta.defaultConfig } : {},
        },
      },
    ]);
    setSelected(id);
  }

  function deleteSelectedNode() {
    if (!selectedNode) return;
    if (selectedNode.data.nodeType === "start" || selectedNode.data.nodeType === "end") {
      setMessage("Start / End 节点不可删除。");
      return;
    }
    setNodes((items) => items.filter((node) => node.id !== selected));
    setEdges((items) => items.filter((edge) => edge.source !== selected && edge.target !== selected));
    setSelected(nodes[0]?.id ?? "start_1");
    setMessage(`已删除节点 ${selectedNode.data.label}。`);
  }

  function updateNodeField(field: "label" | "description", value: string) {
    if (!selectedNode) return;
    setNodes((items) => items.map((node) => (node.id === selected ? { ...node, data: { ...node.data, [field]: value } } : node)));
  }

  function updateNodeConfig(key: string, value: unknown) {
    if (!selectedNode) return;
    setNodes((items) => items.map((node) => (node.id === selected ? { ...node, data: { ...node.data, config: { ...(node.data.config ?? {}), [key]: value } } } : node)));
  }

  function updateEdgeCondition(edgeId: string, condition: string) {
    setEdges((items) => items.map((edge) => (edge.id === edgeId ? { ...edge, condition: condition || undefined, label: condition || undefined } : edge)));
  }

  return (
    <div className="space-y-4">
      <Card className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-xl font-semibold">React Flow 拖拽工作流画布</h2>
          <p className="mt-1 text-sm text-muted-foreground">拖拽节点、连线、编辑配置，可保存为新工作流或更新当前工作流定义后运行。</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button onClick={() => addNode("http")}>添加 HTTP 节点</Button>
          <Button onClick={() => addNode("condition")}>添加 Condition 节点</Button>
          <Button onClick={saveAsNewWorkflow} disabled={saving}>{saving ? "保存中..." : "另存为新工作流"}</Button>
          <Button onClick={updateCurrentWorkflow} disabled={saving || !selectedWorkflowId}>更新当前定义</Button>
          <Button onClick={run} disabled={running || !selectedWorkflowId || !question.trim()}>{running ? "运行中..." : "运行当前画布"}</Button>
        </div>
      </Card>

      <Card>
        <div className="grid gap-3 md:grid-cols-4">
          <label className="block text-sm text-muted-foreground">
            <span className="mb-1 block text-xs text-muted-foreground/70">工作流</span>
            <select
              className="w-full rounded-xl border border-border bg-panel/60 px-4 py-3"
              value={selectedWorkflowId ?? ""}
              onChange={(event) => {
                const id = Number(event.target.value);
                setSelectedWorkflowId(id);
                void loadWorkflowDetail(id);
              }}
            >
              {loading && <option value="">加载中...</option>}
              {workflows.map((item) => (
                <option key={item.id} value={item.id}>{item.name} · {item.node_count} 节点</option>
              ))}
            </select>
          </label>
          <label className="block text-sm text-muted-foreground">
            <span className="mb-1 block text-xs text-muted-foreground/70">知识库</span>
            <select className="w-full rounded-xl border border-border bg-panel/60 px-4 py-3" value={selectedKbId ?? ""} onChange={(event) => setSelectedKbId(Number(event.target.value))}>
              {knowledgeBases.map((item) => (
                <option key={item.id} value={item.id}>{item.name}</option>
              ))}
            </select>
          </label>
          <label className="block text-sm text-muted-foreground md:col-span-2">
            <span className="mb-1 block text-xs text-muted-foreground/70">输入问题</span>
            <input className="w-full rounded-xl border border-border bg-panel/60 px-4 py-3" value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="输入本次工作流问题" />
          </label>
        </div>
      </Card>

      {error && <Card className="border-red-400/40 text-danger-foreground">{error}</Card>}
      {message && !error && <Card className="text-sm text-muted-foreground">{message}</Card>}

      <Card>
        <div className="h-[520px] overflow-hidden rounded-2xl border border-border bg-panel">
          <ReactFlow
            nodes={nodes.map((node) => ({
              ...node,
              className: `rounded-xl border px-4 py-3 text-foreground shadow-xl ${nodeClassName(activeNodeIds.has(node.id), selected === node.id)}`,
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
          <div className="flex items-center justify-between">
            <h3 className="font-semibold">节点编辑</h3>
            {selectedNode && <Button onClick={deleteSelectedNode} className="!bg-danger-soft !text-danger-foreground">删除节点</Button>}
          </div>
          {selectedNode ? (
            <div className="mt-4 space-y-3 text-sm">
              <label className="block text-muted-foreground">
                <span className="mb-1 block text-xs text-muted-foreground/70">节点标签</span>
                <input className="w-full rounded-xl border border-border bg-panel/60 px-3 py-2" value={selectedNode.data.label} onChange={(event) => updateNodeField("label", event.target.value)} />
              </label>
              <label className="block text-muted-foreground">
                <span className="mb-1 block text-xs text-muted-foreground/70">描述</span>
                <input className="w-full rounded-xl border border-border bg-panel/60 px-3 py-2" value={selectedNode.data.description} onChange={(event) => updateNodeField("description", event.target.value)} />
              </label>
              <NodeConfigEditor node={selectedNode} onConfig={updateNodeConfig} />
              <div className="rounded-xl bg-surface/30 p-3 text-xs text-muted-foreground">类型：{selectedNode.data.nodeType} · ID：{selectedNode.id}</div>
            </div>
          ) : (
            <div className="mt-4 rounded-xl bg-surface/30 p-4 text-sm text-muted-foreground">点击画布节点进行编辑。</div>
          )}
        </Card>
        <Card>
          <h3 className="font-semibold">节点运行输出</h3>
          <pre className="mt-4 max-h-96 overflow-auto whitespace-pre-wrap rounded-xl bg-panel/70 p-4 text-sm text-foreground">
            {JSON.stringify(selectedRun ?? { node_id: selected, message: "运行后查看节点输出" }, null, 2)}
          </pre>
        </Card>
        <Card>
          <h3 className="font-semibold">连线条件</h3>
          <div className="mt-4 space-y-2">
            {edges.length === 0 && <div className="rounded-xl bg-surface/30 p-4 text-sm text-muted-foreground">暂无连线。</div>}
            {edges.map((edge) => (
              <div key={edge.id} className="flex items-center gap-2 rounded-xl bg-surface/30 px-3 py-2 text-xs text-muted-foreground">
                <span className="flex-1">{edge.source} → {edge.target}</span>
                <select
                  className="rounded-lg border border-border bg-panel/60 px-2 py-1"
                  value={edge.condition ?? ""}
                  onChange={(event) => updateEdgeCondition(edge.id, event.target.value)}
                >
                  <option value="">无（默认）</option>
                  <option value="true">true</option>
                  <option value="false">false</option>
                </select>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}

function NodeConfigEditor({ node, onConfig }: { node: WorkflowNode; onConfig: (key: string, value: unknown) => void }) {
  const config = node.data.config ?? {};
  const type = node.data.nodeType;

  if (type === "knowledge") {
    return (
      <label className="block text-muted-foreground">
        <span className="mb-1 block text-xs text-muted-foreground/70">top_k</span>
        <input type="number" min={1} max={20} className="w-full rounded-xl border border-border bg-panel/60 px-3 py-2" value={String(config.top_k ?? 3)} onChange={(event) => onConfig("top_k", Number(event.target.value))} />
      </label>
    );
  }

  if (type === "llm") {
    return (
      <div className="space-y-3">
        <label className="block text-muted-foreground">
          <span className="mb-1 block text-xs text-muted-foreground/70">Prompt 模板</span>
          <textarea className="min-h-20 w-full rounded-xl border border-border bg-panel/60 px-3 py-2" value={String(config.prompt ?? "")} onChange={(event) => onConfig("prompt", event.target.value)} />
        </label>
        <label className="block text-muted-foreground">
          <span className="mb-1 block text-xs text-muted-foreground/70">模型名（可选，覆盖默认）</span>
          <input className="w-full rounded-xl border border-border bg-panel/60 px-3 py-2" value={String(config.model ?? "")} onChange={(event) => onConfig("model", event.target.value)} placeholder="留空用默认 chat 模型" />
        </label>
        <label className="block text-muted-foreground">
          <span className="mb-1 block text-xs text-muted-foreground/70">Temperature</span>
          <input type="number" step={0.1} min={0} max={2} className="w-full rounded-xl border border-border bg-panel/60 px-3 py-2" value={String(config.temperature ?? 0.7)} onChange={(event) => onConfig("temperature", Number(event.target.value))} />
        </label>
      </div>
    );
  }

  if (type === "condition") {
    return (
      <div className="space-y-3">
        <label className="block text-muted-foreground">
          <span className="mb-1 block text-xs text-muted-foreground/70">输入字段 key</span>
          <input className="w-full rounded-xl border border-border bg-panel/60 px-3 py-2" value={String(config.key ?? "")} onChange={(event) => onConfig("key", event.target.value)} placeholder="例如 value / n" />
        </label>
        <label className="block text-muted-foreground">
          <span className="mb-1 block text-xs text-muted-foreground/70">运算符</span>
          <select className="w-full rounded-xl border border-border bg-panel/60 px-3 py-2" value={String(config.operator ?? "equals")} onChange={(event) => onConfig("operator", event.target.value)}>
            {OPERATOR_OPTIONS.map((op) => <option key={op} value={op}>{op}</option>)}
          </select>
        </label>
        <label className="block text-muted-foreground">
          <span className="mb-1 block text-xs text-muted-foreground/70">比较值</span>
          <input className="w-full rounded-xl border border-border bg-panel/60 px-3 py-2" value={String(config.value ?? "")} onChange={(event) => onConfig("value", event.target.value)} />
        </label>
      </div>
    );
  }

  if (type === "http") {
    return (
      <div className="space-y-3">
        <label className="block text-muted-foreground">
          <span className="mb-1 block text-xs text-muted-foreground/70">Method</span>
          <select className="w-full rounded-xl border border-border bg-panel/60 px-3 py-2" value={String(config.method ?? "GET")} onChange={(event) => onConfig("method", event.target.value)}>
            <option value="GET">GET</option>
            <option value="POST">POST</option>
            <option value="PUT">PUT</option>
            <option value="DELETE">DELETE</option>
          </select>
        </label>
        <label className="block text-muted-foreground">
          <span className="mb-1 block text-xs text-muted-foreground/70">URL</span>
          <input className="w-full rounded-xl border border-border bg-panel/60 px-3 py-2" value={String(config.url ?? "")} onChange={(event) => onConfig("url", event.target.value)} placeholder="https://..." />
        </label>
      </div>
    );
  }

  return <div className="rounded-xl bg-surface/30 p-3 text-xs text-muted-foreground">该节点类型无可编辑配置。</div>;
}
