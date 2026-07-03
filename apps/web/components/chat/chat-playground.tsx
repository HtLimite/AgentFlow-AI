"use client";

import { useEffect, useState } from "react";
import { apiGet, apiJson } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

type ChatResponse = {
  answer: string;
  usage: Record<string, number>;
  latency_ms: number;
  provider?: string | null;
  provider_id?: number | null;
  model?: string | null;
  model_source?: string;
  mode?: string;
  warning?: string | null;
};

type AIModelItem = {
  id: number;
  provider_id: number;
  model_name: string;
  model_type: string;
  enabled: boolean;
};

export function ChatPlayground() {
  const [question, setQuestion] = useState("请介绍 AgentFlow-AI 的项目价值");
  const [answer, setAnswer] = useState("等待提问");
  const [loading, setLoading] = useState(false);
  const [models, setModels] = useState<AIModelItem[]>([]);
  const [selectedModel, setSelectedModel] = useState("");
  const [modelError, setModelError] = useState("");

  async function loadModels() {
    try {
      const data = await apiGet<AIModelItem[]>("/api/model-providers/models/list");
      const chatModels = data.filter((item) => item.enabled && item.model_type === "chat");
      setModels(chatModels);
      if (!selectedModel && chatModels.length > 0) {
        setSelectedModel(chatModels[0].model_name);
      }
      setModelError(chatModels.length === 0 ? "还没有启用的 chat 模型，请先到设置页添加模型。" : "");
    } catch (error) {
      setModelError(error instanceof Error ? error.message : "模型列表加载失败");
    }
  }

  useEffect(() => {
    loadModels().catch((error) => setModelError(error.message));
  }, []);

  async function send() {
    setLoading(true);
    try {
      const data = await apiJson<ChatResponse>("/api/chat/completions", {
        model: selectedModel || undefined,
        temperature: 0.7,
        messages: [{ role: "user", content: question }],
      });
      const meta = [
        `Model：${data.model ?? selectedModel || "local-fallback"}`,
        `Provider：${data.provider ?? data.provider_id ?? "-"}`,
        `Mode：${data.mode ?? "-"}`,
        `Model Source：${data.model_source ?? "-"}`,
        `Token：${data.usage.total_tokens ?? 0}`,
        `耗时：${data.latency_ms}ms`,
      ];
      setAnswer(`${data.answer}\n\n${meta.join("\n")}${data.warning ? `\nWarning：${data.warning}` : ""}`);
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
          <Button onClick={send} disabled={loading || !selectedModel}>{loading ? "发送中" : "发送"}</Button>
        </div>
      </Card>
      <Card>
        <h2 className="font-semibold">模型参数</h2>
        <div className="mt-4 space-y-4 text-sm text-slate-300">
          <label className="block">
            <span className="mb-1 block text-xs text-slate-500">当前模型</span>
            <select className="w-full rounded-xl border border-white/10 bg-slate-950/60 px-3 py-2" value={selectedModel} onChange={(event) => setSelectedModel(event.target.value)}>
              {models.map((item) => (
                <option key={item.id} value={item.model_name}>{item.model_name}</option>
              ))}
            </select>
          </label>
          <div>Temperature：0.7</div>
          <div>模型来源：/api/model-providers/models/list</div>
          {modelError && <div className="rounded-xl bg-red-500/10 p-3 text-red-200">{modelError}</div>}
        </div>
      </Card>
    </div>
  );
}
