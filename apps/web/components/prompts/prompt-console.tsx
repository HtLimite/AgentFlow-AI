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
  const [rendered, setRendered] = useState("等待测试 Prompt");

  async function load() {
    setItems(await apiGet<PromptItem[]>("/api/prompts"));
  }

  useEffect(() => {
    load().catch((error) => setRendered(error.message));
  }, []);

  async function test(id: number) {
    const data = await apiJson<{ rendered: string }>(`/api/prompts/${id}/test`, { variables: { question: "报销流程是什么？", context: "员工提交发票并审批。" } });
    setRendered(data.rendered);
  }

  return (
    <div className="grid gap-4 xl:grid-cols-[360px_1fr]">
      <Card>
        <h2 className="font-semibold">Prompt 模板</h2>
        <div className="mt-4 space-y-2 text-sm text-slate-300">
          {items.map((item) => (
            <button key={item.id} onClick={() => test(item.id)} className="block w-full rounded-xl bg-white/10 p-3 text-left hover:bg-white/15">
              {item.name}
              <div className="text-xs text-slate-500">{item.scenario}</div>
            </button>
          ))}
        </div>
      </Card>
      <Card>
        <h2 className="font-semibold">测试结果</h2>
        <pre className="mt-4 overflow-auto rounded-xl bg-slate-950/80 p-4 text-sm text-slate-300">{rendered}</pre>
      </Card>
    </div>
  );
}
