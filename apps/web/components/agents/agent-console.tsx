"use client";

import { useState } from "react";
import { apiJson } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

export function AgentConsole() {
  const [question, setQuestion] = useState("请调用知识库工具回答报销流程是什么？");
  const [result, setResult] = useState("等待运行 Agent");

  async function run() {
    const data = await apiJson<{ answer: string; tool_calls: unknown[] }>("/api/agents/1/chat", { question });
    setResult(`${data.answer}\n\n工具调用：\n${JSON.stringify(data.tool_calls, null, 2)}`);
  }

  return (
    <Card>
      <h2 className="text-xl font-semibold">Agent 工具调用演示</h2>
      <p className="mt-2 text-sm text-slate-400">调用后端 Agent Chat，展示工具输入、工具输出和最终回答。</p>
      <div className="mt-5 flex gap-3">
        <input className="flex-1 rounded-xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm" value={question} onChange={(event) => setQuestion(event.target.value)} />
        <Button onClick={run}>运行 Agent</Button>
      </div>
      <pre className="mt-4 whitespace-pre-wrap rounded-xl bg-slate-950/70 p-4 text-sm text-slate-200">{result}</pre>
    </Card>
  );
}
