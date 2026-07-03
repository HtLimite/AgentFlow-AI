"use client";

import { useState } from "react";
import { apiJson } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

interface EvalRun {
  id: number;
  status: string;
  model: string;
  score: number;
  source?: string;
  cases: Array<{ question: string; answer: string; score: number; reason: string }>;
}

const candidates = [
  { label: "Prompt A · 稳健版", model: "demo-model-stable" },
  { label: "Prompt B · 简洁版", model: "demo-model-fast" },
  { label: "Prompt C · 严谨版", model: "demo-model-strict" },
];

export function EvalComparisonConsole() {
  const [runs, setRuns] = useState<EvalRun[]>([]);
  const [error, setError] = useState("");

  async function runCompare() {
    try {
      setError("");
      const results = await Promise.all(
        candidates.map((item) => apiJson<EvalRun>("/api/evals/runs", { dataset_id: 1, model: item.model }))
      );
      setRuns(results);
    } catch (err) {
      setError(err instanceof Error ? err.message : "评测对比失败");
    }
  }

  const best = runs.reduce<EvalRun | null>((prev, item) => (prev === null || item.score > prev.score ? item : prev), null);
  const firstCases = runs.at(0)?.cases ?? [];

  return (
    <div className="space-y-4">
      <Card className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-xl font-semibold">V3 Prompt / Eval 对比中心</h2>
          <p className="mt-1 text-sm text-slate-400">用同一评测集横向比较不同 Prompt 或模型版本，辅助调优决策。</p>
        </div>
        <Button onClick={runCompare}>运行三组对比</Button>
      </Card>

      {error && <Card className="border-red-400/40 text-red-200">{error}</Card>}

      <div className="grid gap-4 md:grid-cols-3">
        {candidates.map((candidate) => {
          const run = runs.find((item) => item.model === candidate.model);
          const isBest = best?.model === candidate.model;
          return (
            <Card key={candidate.model} className={isBest ? "border-emerald-300/60" : ""}>
              <div className="text-sm text-slate-400">{candidate.label}</div>
              <div className="mt-2 text-lg font-semibold">{candidate.model}</div>
              <div className="mt-4 text-4xl font-bold">{run ? run.score : "--"}</div>
              <div className="mt-2 text-sm text-slate-400">{run ? `${run.status} · ${run.source ?? "memory"}` : "等待运行"}</div>
              {isBest && <div className="mt-4 rounded-full bg-emerald-400/15 px-3 py-1 text-sm text-emerald-200">当前最佳</div>}
            </Card>
          );
        })}
      </div>

      <Card>
        <h3 className="font-semibold">逐题对比</h3>
        <div className="mt-4 overflow-x-auto">
          <table className="w-full min-w-[760px] text-left text-sm">
            <thead className="text-slate-400">
              <tr>
                <th className="border-b border-white/10 py-3 pr-4">问题</th>
                {runs.map((run) => (
                  <th key={run.model} className="border-b border-white/10 py-3 pr-4">{run.model}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {firstCases.map((item, index) => (
                <tr key={item.question}>
                  <td className="border-b border-white/10 py-3 pr-4 text-slate-300">{item.question}</td>
                  {runs.map((run) => (
                    <td key={run.model} className="border-b border-white/10 py-3 pr-4">
                      <div className="font-semibold">{run.cases[index]?.score ?? "--"}</div>
                      <div className="mt-1 text-xs text-slate-400">{run.cases[index]?.reason ?? ""}</div>
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
          {!runs.length && <div className="rounded-xl bg-white/5 p-6 text-sm text-slate-400">点击“运行三组对比”后查看结果。</div>}
        </div>
      </Card>
    </div>
  );
}
