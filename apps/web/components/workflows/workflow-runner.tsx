"use client";

import { useState } from "react";
import { apiJson } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

export function WorkflowRunner() {
  const [result, setResult] = useState("等待运行工作流");

  async function run() {
    const data = await apiJson("/api/workflows/1/run", { input: { question: "报销流程是什么？" } });
    setResult(JSON.stringify(data, null, 2));
  }

  return (
    <Card>
      <h2 className="text-xl font-semibold">工作流编排</h2>
      <p className="mt-2 text-sm text-slate-400">V1.5：后端执行器已可返回节点运行链路，V2 接 React Flow 画布。</p>
      <div className="mt-6 grid gap-3 md:grid-cols-3 xl:grid-cols-6">
        {["Start", "Knowledge", "LLM", "Condition", "HTTP", "End"].map((node) => (
          <div key={node} className="rounded-2xl border border-white/10 bg-slate-950/70 p-4 text-center text-sm">{node}</div>
        ))}
      </div>
      <Button className="mt-6" onClick={run}>运行工作流</Button>
      <pre className="mt-4 whitespace-pre-wrap rounded-xl bg-slate-950/70 p-4 text-sm text-slate-200">{result}</pre>
    </Card>
  );
}
