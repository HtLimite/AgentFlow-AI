"use client";

import { useEffect, useState } from "react";
import { apiGet, apiJson } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

type EvalDataset = {
  id: number;
  name: string;
  description?: string;
  case_count: number;
};

type AIModelItem = {
  id: number;
  model_name: string;
  model_type: string;
  enabled: boolean;
};

export function EvalConsole() {
  const [datasets, setDatasets] = useState<EvalDataset[]>([]);
  const [models, setModels] = useState<AIModelItem[]>([]);
  const [datasetId, setDatasetId] = useState<number | null>(null);
  const [model, setModel] = useState("");
  const [casesText, setCasesText] = useState("");
  const [result, setResult] = useState("请选择评测集和模型后运行评测");

  async function load() {
    const [datasetData, modelData] = await Promise.all([
      apiGet<EvalDataset[]>("/api/evals/datasets"),
      apiGet<AIModelItem[]>("/api/model-providers/models/list"),
    ]);
    const chatModels = modelData.filter((item) => item.enabled && item.model_type === "chat");
    setDatasets(datasetData);
    setModels(chatModels);
    setDatasetId((current) => (current && datasetData.some((item) => item.id === current) ? current : datasetData[0]?.id ?? null));
    setModel((current) => current || chatModels[0]?.model_name || "");
  }

  useEffect(() => {
    load().catch((error) => setResult(error.message));
  }, []);

  async function run() {
    if (!datasetId) {
      setResult("请先选择评测集");
      return;
    }
    if (!model) {
      setResult("请先在设置页添加并启用 chat 模型");
      return;
    }
    const cases = casesText
      .split("\n")
      .map((item) => item.trim())
      .filter(Boolean);
    const data = await apiJson("/api/evals/runs", { dataset_id: datasetId, model, cases: cases.length > 0 ? cases : undefined });
    setResult(JSON.stringify(data, null, 2));
  }

  return (
    <Card>
      <h2 className="text-xl font-semibold">模型评测集</h2>
      <p className="mt-2 text-sm text-slate-400">从评测集接口和模型列表读取配置，不固定 demo-model 或固定题目。</p>
      <div className="mt-5 grid gap-3 md:grid-cols-2">
        <label className="block text-sm text-slate-300">
          <span className="mb-1 block text-xs text-slate-500">评测集</span>
          <select className="w-full rounded-xl border border-white/10 bg-slate-950/60 px-4 py-3" value={datasetId ?? ""} onChange={(event) => setDatasetId(Number(event.target.value))}>
            {datasets.map((item) => (
              <option key={item.id} value={item.id}>{item.name} · {item.case_count} cases</option>
            ))}
          </select>
        </label>
        <label className="block text-sm text-slate-300">
          <span className="mb-1 block text-xs text-slate-500">评测模型</span>
          <select className="w-full rounded-xl border border-white/10 bg-slate-950/60 px-4 py-3" value={model} onChange={(event) => setModel(event.target.value)}>
            {models.map((item) => (
              <option key={item.id} value={item.model_name}>{item.model_name}</option>
            ))}
          </select>
        </label>
        <label className="block text-sm text-slate-300 md:col-span-2">
          <span className="mb-1 block text-xs text-slate-500">临时覆盖题目，可选，一行一个。不填则使用评测集内置 cases。</span>
          <textarea className="min-h-28 w-full rounded-xl border border-white/10 bg-slate-950/60 px-4 py-3" value={casesText} onChange={(event) => setCasesText(event.target.value)} placeholder="可选：输入本次临时评测题目" />
        </label>
      </div>
      <Button className="mt-5" onClick={run} disabled={!datasetId || !model}>运行评测</Button>
      <pre className="mt-4 whitespace-pre-wrap rounded-xl bg-slate-950/70 p-4 text-sm text-slate-200">{result}</pre>
    </Card>
  );
}
