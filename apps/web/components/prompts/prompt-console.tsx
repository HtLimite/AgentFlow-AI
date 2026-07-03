"use client";

import { useEffect, useState } from "react";
import { apiGet, apiJson } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

interface PromptItem {
  id: number;
  name: string;
  scenario: string;
  content: string;
}

export function PromptConsole() {
  const [items, setItems] = useState<PromptItem[]>([]);
  const [selectedPromptId, setSelectedPromptId] = useState<number | null>(null);
  const [variablesText, setVariablesText] = useState("{}");
  const [rendered, setRendered] = useState("请选择 Prompt，并填写 JSON 变量后渲染");

  async function load() {
    const data = await apiGet<PromptItem[]>("/api/prompts");
    setItems(data);
    setSelectedPromptId((current) => (current && data.some((item) => item.id === current) ? current : data[0]?.id ?? null));
  }

  useEffect(() => {
    load().catch((error) => setRendered(error.message));
  }, []);

  async function test() {
    if (!selectedPromptId) {
      setRendered("请先选择 Prompt");
      return;
    }
    let variables: Record<string, unknown> = {};
    try {
      variables = JSON.parse(variablesText || "{}");
    } catch {
      setRendered("变量不是合法 JSON");
      return;
    }
    const data = await apiJson<{ rendered: string }>(`/api/prompts/${selectedPromptId}/test`, { variables });
    setRendered(data.rendered);
  }

  return (
    <div className="grid gap-4 xl:grid-cols-[360px_1fr]">
      <Card>
        <h2 className="font-semibold">Prompt 模板</h2>
        <div className="mt-4 space-y-2 text-sm text-slate-300">
          {items.map((item) => (
            <button key={item.id} onClick={() => setSelectedPromptId(item.id)} className={`block w-full rounded-xl p-3 text-left hover:bg-white/15 ${selectedPromptId === item.id ? "bg-blue-500/20" : "bg-white/10"}`}>
              {item.name}
              <div className="text-xs text-slate-500">{item.scenario}</div>
            </button>
          ))}
        </div>
      </Card>
      <Card>
        <h2 className="font-semibold">测试变量</h2>
        <textarea className="mt-4 min-h-32 w-full rounded-xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm text-slate-200" value={variablesText} onChange={(event) => setVariablesText(event.target.value)} />
        <Button className="mt-4" onClick={test} disabled={!selectedPromptId}>渲染 Prompt</Button>
        <h2 className="mt-6 font-semibold">测试结果</h2>
        <pre className="mt-4 overflow-auto rounded-xl bg-slate-950/80 p-4 text-sm text-slate-300">{rendered}</pre>
      </Card>
    </div>
  );
}
