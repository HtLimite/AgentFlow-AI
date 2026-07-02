"use client";

import { useState } from "react";
import { apiJson } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

export function EvalConsole() {
  const [result, setResult] = useState("等待运行评测");

  async function run() {
    const data = await apiJson("/api/evals/runs", { model: "demo-model", cases: ["报销流程是什么？", "如何查看售后状态？"] });
    setResult(JSON.stringify(data, null, 2));
  }

  return (
    <Card>
      <h2 className="text-xl font-semibold">模型评测集</h2>
      <p className="mt-2 text-sm text-slate-400">运行演示评测，输出分数、原因和逐题结果。</p>
      <Button className="mt-5" onClick={run}>运行评测</Button>
      <pre className="mt-4 whitespace-pre-wrap rounded-xl bg-slate-950/70 p-4 text-sm text-slate-200">{result}</pre>
    </Card>
  );
}
