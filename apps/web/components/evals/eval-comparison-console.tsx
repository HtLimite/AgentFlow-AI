"use client";

import { useEffect, useMemo, useState } from "react";
import { apiGet, apiJson, errorMessage } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

interface EvalDataset {
  id: number;
  name: string;
  description?: string;
  case_count: number;
}

interface AIModelItem {
  id: number;
  model_name: string;
  model_type: string;
  enabled: boolean;
}

interface EvalCase {
  question: string;
  answer: string;
  score: number;
  reason: string;
}

interface EvalRun {
  id: number;
  status: string;
  model: string;
  score: number;
  source?: string;
  cases: EvalCase[];
}

interface Candidate {
  label: string;
  model: string;
}

export function EvalComparisonConsole() {
  const [datasets, setDatasets] = useState<EvalDataset[]>([]);
  const [models, setModels] = useState<AIModelItem[]>([]);
  const [datasetId, setDatasetId] = useState<number | null>(null);
  const [candidates, setCandidates] = useState<Candidate[]>([
    { label: "候选 1", model: "" },
    { label: "候选 2", model: "" },
    { label: "候选 3", model: "" },
  ]);
  const [runs, setRuns] = useState<EvalRun[]>([]);
  const [error, setError] = useState("");
  const [running, setRunning] = useState(false);
  const [loading, setLoading] = useState(true);

  async function load() {
    try {
      setError("");
      const [datasetData, modelData] = await Promise.all([
        apiGet<EvalDataset[]>("/api/evals/datasets"),
        apiGet<AIModelItem[]>("/api/model-providers/models/list"),
      ]);
      const chatModels = modelData.filter((item) => item.enabled && item.model_type === "chat");
      setDatasets(datasetData);
      setModels(chatModels);
      setDatasetId((current) => (current && datasetData.some((item) => item.id === current) ? current : datasetData[0]?.id ?? null));
      setCandidates((current) => {
        // Default the first three candidates to real chat models when available.
        const defaults = chatModels.slice(0, 3).map((item) => item.model_name);
        return current.map((item, index) => ({ ...item, model: item.model || defaults[index] || "" }));
      });
    } catch (err) {
      setError(errorMessage(err, "评测初始化失败"));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, []);

  async function runCompare() {
    if (!datasetId) {
      setError("请先选择评测集");
      return;
    }
    const activeCandidates = candidates.filter((item) => item.model);
    if (activeCandidates.length === 0) {
      setError("请至少配置一个候选模型");
      return;
    }
    setRunning(true);
    setError("");
    try {
      const results = await Promise.all(
        activeCandidates.map((item) => apiJson<EvalRun>("/api/evals/runs", { dataset_id: datasetId, model: item.model })),
      );
      setRuns(results);
    } catch (err) {
      setError(errorMessage(err, "评测对比失败"));
    } finally {
      setRunning(false);
    }
  }

  const best = runs.reduce<EvalRun | null>((prev, item) => (prev === null || item.score > prev.score ? item : prev), null);

  // Align cases by question text rather than by index, so runs returning
  // different orderings or subsets still map scores to the right question.
  const allQuestions = useMemo(() => {
    const seen = new Set<string>();
    const ordered: string[] = [];
    for (const run of runs) {
      for (const c of run.cases) {
        if (!seen.has(c.question)) {
          seen.add(c.question);
          ordered.push(c.question);
        }
      }
    }
    return ordered;
  }, [runs]);

  const caseFor = (run: EvalRun, question: string): EvalCase | undefined =>
    run.cases.find((c) => c.question === question);

  return (
    <div className="space-y-4">
      <Card className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-xl font-semibold">Prompt / Eval 对比中心</h2>
          <p className="mt-1 text-sm text-muted-foreground">用同一评测集横向比较不同 Prompt 或模型版本，辅助调优决策。</p>
        </div>
        <Button onClick={runCompare} disabled={running || !datasetId}>
          {running ? "对比中..." : "运行对比"}
        </Button>
      </Card>

      {error && <Card className="border-red-400/40 text-danger-foreground">{error}</Card>}

      <Card>
        <div className="grid gap-3 md:grid-cols-2">
          <label className="block text-sm text-muted-foreground">
            <span className="mb-1 block text-xs text-muted-foreground/70">评测集</span>
            <select
              className="w-full rounded-xl border border-border bg-panel/60 px-4 py-3"
              value={datasetId ?? ""}
              onChange={(event) => setDatasetId(Number(event.target.value))}
            >
              {datasets.length === 0 && <option value="">暂无评测集</option>}
              {datasets.map((item) => (
                <option key={item.id} value={item.id}>{item.name} · {item.case_count} cases</option>
              ))}
            </select>
          </label>
        </div>
        <div className="mt-4 grid gap-3 md:grid-cols-3">
          {candidates.map((candidate, index) => (
            <label key={index} className="block text-sm text-muted-foreground">
              <span className="mb-1 block text-xs text-muted-foreground/70">{candidate.label}</span>
              <select
                className="w-full rounded-xl border border-border bg-panel/60 px-4 py-3"
                value={candidate.model}
                onChange={(event) => setCandidates((current) => current.map((item, i) => (i === index ? { ...item, model: event.target.value } : item)))}
              >
                <option value="">local-fallback / 自动</option>
                {models.map((item) => (
                  <option key={item.id} value={item.model_name}>{item.model_name}</option>
                ))}
              </select>
            </label>
          ))}
        </div>
        {loading && <div className="mt-3 text-xs text-muted-foreground/70">加载评测集与模型中...</div>}
      </Card>

      {runs.length > 0 && (
        <div className="grid gap-4 md:grid-cols-3">
          {candidates.filter((item) => item.model).map((candidate) => {
            const run = runs.find((item) => item.model === candidate.model);
            const isBest = best?.model === candidate.model;
            return (
              <Card key={candidate.model} className={isBest ? "border-emerald-300/60" : ""}>
                <div className="text-sm text-muted-foreground">{candidate.label}</div>
                <div className="mt-2 text-lg font-semibold">{candidate.model}</div>
                <div className="mt-4 text-4xl font-bold">{run ? run.score : "--"}</div>
                <div className="mt-2 text-sm text-muted-foreground">{run ? `${run.status} · ${run.source ?? "memory"}` : "等待运行"}</div>
                {isBest && <div className="mt-4 rounded-full bg-emerald-400/15 px-3 py-1 text-sm text-emerald-200">当前最佳</div>}
              </Card>
            );
          })}
        </div>
      )}

      {runs.length > 0 && (
        <Card>
          <h3 className="font-semibold">逐题对比</h3>
          <div className="mt-4 overflow-x-auto">
            <table className="w-full min-w-[760px] text-left text-sm">
              <thead className="text-muted-foreground">
                <tr>
                  <th className="border-b border-border py-3 pr-4">问题</th>
                  {runs.map((run) => (
                    <th key={run.model} className="border-b border-border py-3 pr-4">{run.model}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {allQuestions.map((question) => (
                  <tr key={question}>
                    <td className="border-b border-border py-3 pr-4 text-muted-foreground">{question}</td>
                    {runs.map((run) => {
                      const c = caseFor(run, question);
                      return (
                        <td key={run.model} className="border-b border-border py-3 pr-4">
                          <div className="font-semibold">{c ? c.score : "--"}</div>
                          <div className="mt-1 text-xs text-muted-foreground">{c?.reason ?? ""}</div>
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  );
}
