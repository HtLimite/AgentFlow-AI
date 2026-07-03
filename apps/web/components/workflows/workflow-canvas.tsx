"use client";

import { useState } from "react";
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
    output: unknown;
  }>;
}

const nodes = [
  { id: "start_1", type: "start", title: "Start", x: 4, y: 38, desc: "接收用户输入" },
  { id: "knowledge_1", type: "knowledge", title: "Knowledge", x: 24, y: 18, desc: "检索知识库" },
  { id: "llm_1", type: "llm", title: "LLM", x: 50, y: 38, desc: "生成回答" },
  { id: "condition_1", type: "condition", title: "Condition", x: 70, y: 18, desc: "质量判断" },
  { id: "end_1", type: "end", title: "End", x: 86, y: 38, desc: "输出结果" },
];

const definition = {
  nodes: [
    { id: "start_1", type: "start", data: {} },
    { id: "knowledge_1", type: "knowledge", data: { kb_id: 1, top_k: 3 } },
    { id: "llm_1", type: "llm", data: { prompt: "根据知识库结果回答：{{question}}" } },
    { id: "end_1", type: "end", data: {} },
  ],
  edges: [
    { source: "start_1", target: "knowledge_1" },
    { source: "knowledge_1", target: "llm_1" },
    { source: "llm_1", target: "end_1" },
  ],
};

export function WorkflowCanvas() {
  const [result, setResult] = useState<WorkflowRunResult | null>(null);
  const [selected, setSelected] = useState<string>("start_1");
  const [error, setError] = useState("");

  async function run() {
    try {
      setError("");
      const data = await apiJson<WorkflowRunResult>("/api/workflows/1/run", {
        input: { question: "报销流程是什么？" },
        definition,
      });
      setResult(data);
      setSelected(data.node_runs?.[0]?.node_id ?? "start_1");
    } catch (err) {
      setError(err instanceof Error ? err.message : "工作流运行失败");
    }
  }

  const activeNodeIds = new Set(result?.node_runs?.map((item) => item.node_id) ?? []);
  const selectedRun = result?.node_runs?.find((item) => item.node_id === selected);

  return (
    <div className="space-y-4">
      <Card className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-xl font-semibold">V3 可视化工作流画布</h2>
          <p className="mt-1 text-sm text-slate-400">无需新增依赖的轻量画布：节点、运行状态、输出详情一屏展示。</p>
        </div>
        <Button onClick={run}>运行画布工作流</Button>
      </Card>

      {error && <Card className="border-red-400/40 text-red-200">{error}</Card>}

      <Card>
        <div className="relative h-[360px] overflow-hidden rounded-2xl border border-white/10 bg-slate-950/80">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(59,130,246,0.18),transparent_28%),radial-gradient(circle_at_70%_30%,rgba(16,185,129,0.12),transparent_26%)]" />
          <svg className="absolute inset-0 h-full w-full" viewBox="0 0 100 100" preserveAspectRatio="none">
            <path d="M 16 47 C 22 28, 28 28, 33 28" stroke="rgba(148,163,184,.45)" strokeWidth="0.5" fill="none" />
            <path d="M 39 31 C 45 34, 48 42, 50 47" stroke="rgba(148,163,184,.45)" strokeWidth="0.5" fill="none" />
            <path d="M 62 47 C 67 37, 69 31, 70 28" stroke="rgba(148,163,184,.45)" strokeWidth="0.5" fill="none" />
            <path d="M 79 31 C 83 35, 86 41, 88 47" stroke="rgba(148,163,184,.45)" strokeWidth="0.5" fill="none" />
          </svg>
          {nodes.map((node) => {
            const isSelected = selected === node.id;
            const isActive = activeNodeIds.has(node.id);
            return (
              <button
                key={node.id}
                onClick={() => setSelected(node.id)}
                className={`absolute w-40 rounded-2xl border p-4 text-left shadow-xl transition ${
                  isSelected ? "border-blue-300 bg-blue-500/20" : isActive ? "border-emerald-300/70 bg-emerald-500/10" : "border-white/10 bg-slate-900/90"
                }`}
                style={{ left: `${node.x}%`, top: `${node.y}%` }}
              >
                <div className="text-xs uppercase tracking-[0.2em] text-slate-400">{node.type}</div>
                <div className="mt-2 font-semibold text-white">{node.title}</div>
                <div className="mt-1 text-xs text-slate-400">{node.desc}</div>
                <div className={`mt-3 inline-flex rounded-full px-2 py-1 text-xs ${isActive ? "bg-emerald-400/20 text-emerald-200" : "bg-white/10 text-slate-300"}`}>
                  {isActive ? "已运行" : "待运行"}
                </div>
              </button>
            );
          })}
        </div>
      </Card>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <h3 className="font-semibold">运行摘要</h3>
          <pre className="mt-4 whitespace-pre-wrap rounded-xl bg-slate-950/70 p-4 text-sm text-slate-200">
            {JSON.stringify({ status: result?.status ?? "idle", run_id: result?.run_id, source: result?.source, nodes: result?.node_runs?.length ?? 0 }, null, 2)}
          </pre>
        </Card>
        <Card>
          <h3 className="font-semibold">选中节点输出</h3>
          <pre className="mt-4 max-h-80 overflow-auto whitespace-pre-wrap rounded-xl bg-slate-950/70 p-4 text-sm text-slate-200">
            {JSON.stringify(selectedRun ?? { node_id: selected, message: "运行后查看节点输出" }, null, 2)}
          </pre>
        </Card>
      </div>
    </div>
  );
}
