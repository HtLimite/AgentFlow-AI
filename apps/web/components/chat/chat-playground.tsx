"use client";

import { useState } from "react";
import { apiJson } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

export function ChatPlayground() {
  const [question, setQuestion] = useState("请介绍 AgentFlow-AI 的项目价值");
  const [answer, setAnswer] = useState("等待提问");
  const [loading, setLoading] = useState(false);

  async function send() {
    setLoading(true);
    try {
      const data = await apiJson<{ answer: string; usage: Record<string, number>; latency_ms: number }>("/api/chat/completions", {
        model: "demo-model",
        temperature: 0.7,
        messages: [{ role: "user", content: question }],
      });
      setAnswer(`${data.answer}\n\nToken：${data.usage.total_tokens}，耗时：${data.latency_ms}ms`);
    } catch (error) {
      setAnswer(error instanceof Error ? error.message : "请求失败");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid gap-4 xl:grid-cols-[280px_1fr_320px]">
      <Card>
        <h2 className="font-semibold">会话列表</h2>
        <div className="mt-4 space-y-2 text-sm text-slate-300">
          <div className="rounded-xl bg-white/10 p-3">多模型对话测试</div>
          <div className="rounded-xl p-3 hover:bg-white/10">RAG 引用验证</div>
        </div>
      </Card>
      <Card className="min-h-[620px]">
        <h2 className="font-semibold">Chat Playground</h2>
        <pre className="mt-5 min-h-[360px] whitespace-pre-wrap rounded-2xl bg-white/10 p-4 text-sm text-slate-200">{answer}</pre>
        <div className="mt-6 flex gap-3">
          <input className="flex-1 rounded-xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm outline-none" value={question} onChange={(event) => setQuestion(event.target.value)} />
          <Button onClick={send} disabled={loading}>{loading ? "发送中" : "发送"}</Button>
        </div>
      </Card>
      <Card>
        <h2 className="font-semibold">模型参数</h2>
        <div className="mt-4 space-y-4 text-sm text-slate-300">
          <div>Model：demo-model</div>
          <div>Temperature：0.7</div>
          <div>模式：后端可替换为真实供应商</div>
        </div>
      </Card>
    </div>
  );
}
