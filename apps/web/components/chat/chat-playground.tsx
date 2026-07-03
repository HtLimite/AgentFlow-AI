"use client";

import { useEffect, useState } from "react";
import { API_BASE_URL, apiGet, apiJson } from "@/lib/api-client";
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
  stream_supported?: boolean;
  warning?: string | null;
};

type AIModelItem = {
  id: number;
  provider_id: number;
  model_name: string;
  model_type: string;
  enabled: boolean;
};

type StreamEvent = {
  type?: "meta" | "delta" | "done" | "error";
  content?: string;
  message?: string;
  model?: string;
  mode?: string;
  model_source?: string;
  total_tokens?: number;
};

export function ChatPlayground() {
  const [question, setQuestion] = useState("请介绍 AgentFlow-AI 的项目价值");
  const [answer, setAnswer] = useState("等待提问");
  const [loading, setLoading] = useState(false);
  const [models, setModels] = useState<AIModelItem[]>([]);
  const [selectedModel, setSelectedModel] = useState("");
  const [modelError, setModelError] = useState("");
  const [streamMode, setStreamMode] = useState(true);

  async function loadModels() {
    try {
      const data = await apiGet<AIModelItem[]>("/api/model-providers/models/list");
      const chatModels = data.filter((item) => item.enabled && item.model_type === "chat");
      setModels(chatModels);
      setSelectedModel((current) => (current && chatModels.some((item) => item.model_name === current) ? current : chatModels[0]?.model_name ?? ""));
      setModelError(chatModels.length === 0 ? "还没有启用的 chat 模型；可先走本地 fallback，或到设置页添加模型。" : "");
    } catch (error) {
      setModelError(error instanceof Error ? error.message : "模型列表加载失败");
    }
  }

  useEffect(() => {
    loadModels().catch((error) => setModelError(error.message));
  }, []);

  async function send() {
    if (!question.trim()) {
      setAnswer("请输入问题");
      return;
    }
    setLoading(true);
    setAnswer("发送中...");
    try {
      if (streamMode) {
        await sendStream();
      } else {
        await sendOnce();
      }
    } catch (error) {
      setAnswer(error instanceof Error ? error.message : "请求失败");
    } finally {
      setLoading(false);
    }
  }

  async function sendOnce() {
    const data = await apiJson<ChatResponse>("/api/chat/completions", {
      model: selectedModel || undefined,
      temperature: 0.7,
      messages: [{ role: "user", content: question }],
    });
    const activeModel = (data.model ?? selectedModel) || "local-fallback";
    const meta = [
      `Model：${activeModel}`,
      `Provider：${data.provider ?? data.provider_id ?? "-"}`,
      `Mode：${data.mode ?? "-"}`,
      `Model Source：${data.model_source ?? "-"}`,
      `Stream Supported：${data.stream_supported ? "yes" : "no"}`,
      `Token：${data.usage.total_tokens ?? 0}`,
      `耗时：${data.latency_ms}ms`,
    ];
    setAnswer(`${data.answer}\n\n${meta.join("\n")}${data.warning ? `\nWarning：${data.warning}` : ""}`);
  }

  async function sendStream() {
    const response = await fetch(`${API_BASE_URL}/api/chat/completions/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model: selectedModel || undefined,
        temperature: 0.7,
        messages: [{ role: "user", content: question }],
      }),
    });
    if (!response.ok || !response.body) {
      const text = await response.text();
      throw new Error(`STREAM /api/chat/completions/stream failed: ${response.status} ${text}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    let content = "";
    let meta = "";
    let doneMeta = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const chunks = buffer.split("\n\n");
      buffer = chunks.pop() ?? "";
      for (const chunk of chunks) {
        const line = chunk.split("\n").find((item) => item.startsWith("data: "));
        if (!line) continue;
        const payload = line.replace(/^data: /, "");
        if (payload === "[DONE]") continue;
        const event = JSON.parse(payload) as StreamEvent;
        if (event.type === "meta") {
          const modelLabel = (event.model ?? selectedModel) || "local-fallback";
          meta = `Model：${modelLabel}\nMode：${event.mode ?? "-"}\nModel Source：${event.model_source ?? "-"}`;
        }
        if (event.type === "delta") {
          content += event.content ?? "";
          setAnswer(`${content}\n\n${meta}`);
        }
        if (event.type === "done") {
          doneMeta = `\nToken：${event.total_tokens ?? 0}`;
        }
        if (event.type === "error") {
          throw new Error(event.message ?? "流式请求失败");
        }
      }
    }

    setAnswer(`${content || "无输出"}\n\n${meta}${doneMeta}\nStream：SSE`);
  }

  return (
    <div className="grid gap-4 xl:grid-cols-[280px_1fr_320px]">
      <Card>
        <h2 className="font-semibold">会话列表</h2>
        <div className="mt-4 space-y-2 text-sm text-slate-300">
          <div className="rounded-xl bg-white/10 p-3">多模型对话测试</div>
          <div className="rounded-xl p-3 hover:bg-white/10">流式输出验证</div>
          <div className="rounded-xl p-3 hover:bg-white/10">本地 fallback 验证</div>
        </div>
      </Card>
      <Card className="min-h-[620px]">
        <h2 className="font-semibold">Chat Playground</h2>
        <pre className="mt-5 min-h-[360px] whitespace-pre-wrap rounded-2xl bg-white/10 p-4 text-sm text-slate-200">{answer}</pre>
        <div className="mt-6 flex gap-3">
          <input className="flex-1 rounded-xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm outline-none" value={question} onChange={(event) => setQuestion(event.target.value)} />
          <Button onClick={send} disabled={loading || !question.trim()}>{loading ? "发送中" : streamMode ? "流式发送" : "发送"}</Button>
        </div>
      </Card>
      <Card>
        <h2 className="font-semibold">模型参数</h2>
        <div className="mt-4 space-y-4 text-sm text-slate-300">
          <label className="block">
            <span className="mb-1 block text-xs text-slate-500">当前模型</span>
            <select className="w-full rounded-xl border border-white/10 bg-slate-950/60 px-3 py-2" value={selectedModel} onChange={(event) => setSelectedModel(event.target.value)}>
              <option value="">local-fallback / 自动默认</option>
              {models.map((item) => (
                <option key={item.id} value={item.model_name}>{item.model_name}</option>
              ))}
            </select>
          </label>
          <label className="flex items-center gap-2">
            <input type="checkbox" checked={streamMode} onChange={(event) => setStreamMode(event.target.checked)} />
            使用 SSE 流式接口
          </label>
          <div>Temperature：0.7</div>
          <div>可用 Chat 模型：{models.length}</div>
          <div>模型来源：/api/model-providers/models/list</div>
          <Button onClick={loadModels}>刷新模型</Button>
          {modelError && <div className="rounded-xl bg-red-500/10 p-3 text-red-200">{modelError}</div>}
        </div>
      </Card>
    </div>
  );
}
