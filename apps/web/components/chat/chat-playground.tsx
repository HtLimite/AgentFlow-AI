"use client";

import { useEffect, useMemo, useState } from "react";
import { API_BASE_URL, apiGet, apiJson, errorMessage } from "@/lib/api-client";
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

type ChatMessage = { role: "user" | "assistant"; content: string; ts: number };
type ChatSession = { id: string; title: string; messages: ChatMessage[]; createdAt: number };

const SESSIONS_KEY = "agentflow-chat-sessions";
const ACTIVE_KEY = "agentflow-chat-active";

function loadSessions(): ChatSession[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = window.localStorage.getItem(SESSIONS_KEY);
    return raw ? (JSON.parse(raw) as ChatSession[]) : [];
  } catch {
    return [];
  }
}

function saveSessions(sessions: ChatSession[]) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(SESSIONS_KEY, JSON.stringify(sessions));
}

function newSession(): ChatSession {
  const now = Date.now();
  return { id: `s-${now}-${Math.random().toString(36).slice(2, 8)}`, title: "新会话", messages: [], createdAt: now };
}

export function ChatPlayground() {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [models, setModels] = useState<AIModelItem[]>([]);
  const [selectedModel, setSelectedModel] = useState("");
  const [modelError, setModelError] = useState("");
  const [streamMode, setStreamMode] = useState(true);
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeId, setActiveId] = useState<string>("");
  const [streamingAnswer, setStreamingAnswer] = useState("");

  const activeSession = useMemo(() => sessions.find((item) => item.id === activeId) ?? null, [sessions, activeId]);

  // Hydrate sessions from localStorage once on mount.
  useEffect(() => {
    const stored = loadSessions();
    const list = stored.length > 0 ? stored : [newSession()];
    setSessions(list);
    const storedActive = typeof window !== "undefined" ? window.localStorage.getItem(ACTIVE_KEY) : null;
    setActiveId(storedActive && list.some((item) => item.id === storedActive) ? storedActive : list[0].id);
  }, []);

  // Persist sessions + active id whenever they change.
  useEffect(() => {
    if (sessions.length > 0) saveSessions(sessions);
  }, [sessions]);
  useEffect(() => {
    if (activeId && typeof window !== "undefined") window.localStorage.setItem(ACTIVE_KEY, activeId);
  }, [activeId]);

  async function loadModels() {
    try {
      const data = await apiGet<AIModelItem[]>("/api/model-providers/models/list");
      const chatModels = data.filter((item) => item.enabled && item.model_type === "chat");
      setModels(chatModels);
      setSelectedModel((current) => (current && chatModels.some((item) => item.model_name === current) ? current : chatModels[0]?.model_name ?? ""));
      setModelError(chatModels.length === 0 ? "还没有启用的 chat 模型；可先走本地 fallback，或到设置页添加模型。" : "");
    } catch (error) {
      setModelError(errorMessage(error, "模型列表加载失败"));
    }
  }

  useEffect(() => {
    loadModels().catch((error) => setModelError(errorMessage(error, "模型列表加载失败")));
  }, []);

  function patchSession(id: string, updater: (session: ChatSession) => ChatSession) {
    setSessions((current) => current.map((item) => (item.id === id ? updater(item) : item)));
  }

  function createSession() {
    const session = newSession();
    setSessions((current) => [session, ...current]);
    setActiveId(session.id);
    setQuestion("");
    setStreamingAnswer("");
  }

  function deleteSession(id: string) {
    setSessions((current) => {
      const next = current.filter((item) => item.id !== id);
      const fallback = next.length > 0 ? next : [newSession()];
      if (id === activeId) setActiveId(fallback[0].id);
      return fallback;
    });
  }

  async function send() {
    if (!question.trim() || !activeSession) return;
    setLoading(true);
    const draft = question;
    const userMsg: ChatMessage = { role: "user", content: draft, ts: Date.now() };
    patchSession(activeSession.id, (session) => ({
      ...session,
      title: session.messages.length === 0 ? draft.trim().slice(0, 24) : session.title,
      messages: [...session.messages, userMsg],
    }));
    setStreamingAnswer("发送中...");
    try {
      const answer = streamMode ? await sendStream(draft) : await sendOnce(draft);
      const assistantMsg: ChatMessage = { role: "assistant", content: answer, ts: Date.now() };
      patchSession(activeSession.id, (session) => ({ ...session, messages: [...session.messages, assistantMsg] }));
      setQuestion("");
    } catch (error) {
      const message = errorMessage(error, "请求失败");
      patchSession(activeSession.id, (session) => ({ ...session, messages: [...session.messages, { role: "assistant", content: `出错：${message}`, ts: Date.now() }] }));
    } finally {
      setStreamingAnswer("");
      setLoading(false);
    }
  }

  async function sendOnce(prompt: string): Promise<string> {
    const data = await apiJson<ChatResponse>("/api/chat/completions", {
      model: selectedModel || undefined,
      temperature: 0.7,
      messages: [{ role: "user", content: prompt }],
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
    return `${data.answer}\n\n${meta.join("\n")}${data.warning ? `\nWarning：${data.warning}` : ""}`;
  }

  async function sendStream(prompt: string): Promise<string> {
    const response = await fetch(`${API_BASE_URL}/api/chat/completions/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model: selectedModel || undefined,
        temperature: 0.7,
        messages: [{ role: "user", content: prompt }],
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
        let event: StreamEvent;
        try {
          event = JSON.parse(payload) as StreamEvent;
        } catch {
          // Skip malformed SSE payloads instead of aborting the whole stream.
          continue;
        }
        if (event.type === "meta") {
          const modelLabel = (event.model ?? selectedModel) || "local-fallback";
          meta = `Model：${modelLabel}\nMode：${event.mode ?? "-"}\nModel Source：${event.model_source ?? "-"}`;
        }
        if (event.type === "delta") {
          content += event.content ?? "";
          setStreamingAnswer(`${content}\n\n${meta}`);
        }
        if (event.type === "done") {
          doneMeta = `\nToken：${event.total_tokens ?? 0}`;
        }
        if (event.type === "error") {
          throw new Error(event.message ?? "流式请求失败");
        }
      }
    }

    return `${content || "无输出"}\n\n${meta}${doneMeta}\nStream：SSE`;
  }

  return (
    <div className="grid gap-4 xl:grid-cols-[280px_1fr_320px]">
      <Card>
        <div className="flex items-center justify-between gap-3">
          <h2 className="font-semibold">会话列表</h2>
          <Button size="sm" onClick={createSession}>新建</Button>
        </div>
        <div className="mt-4 space-y-2 text-sm">
          {sessions.length === 0 ? (
            <div className="rounded-xl bg-surface/30 p-3 text-muted-foreground">暂无会话，点击「新建」开始对话。</div>
          ) : (
            sessions.map((session) => (
              <div
                key={session.id}
                className={`group flex cursor-pointer items-center justify-between gap-2 rounded-xl border p-3 transition ${activeId === session.id ? "border-primary/40 bg-primary/10" : "border-border bg-surface/30 hover:bg-surface/60"}`}
                onClick={() => { setActiveId(session.id); setStreamingAnswer(""); }}
              >
                <div className="min-w-0 flex-1">
                  <div className="truncate font-medium text-foreground">{session.title || "新会话"}</div>
                  <div className="text-xs text-muted-foreground/70">{session.messages.length} 条消息</div>
                </div>
                <button
                  type="button"
                  className="shrink-0 rounded-lg px-2 py-1 text-xs text-muted-foreground/70 opacity-0 transition hover:bg-danger-soft hover:text-danger-foreground group-hover:opacity-100"
                  onClick={(event) => { event.stopPropagation(); deleteSession(session.id); }}
                  title="删除会话"
                >
                  删除
                </button>
              </div>
            ))
          )}
        </div>
      </Card>
      <Card className="min-h-[620px]">
        <h2 className="font-semibold">Chat Playground</h2>
        <div className="mt-5 min-h-[360px] space-y-3 overflow-auto rounded-2xl bg-surface/30 p-4 text-sm">
          {activeSession && activeSession.messages.length > 0 ? (
            activeSession.messages.map((message, idx) => (
              <div key={idx} className={`whitespace-pre-wrap rounded-xl p-3 ${message.role === "user" ? "bg-primary/10 text-foreground" : "bg-surface/60 text-foreground"}`}>
                <div className="mb-1 text-xs text-muted-foreground/70">{message.role === "user" ? "我" : "AI"}</div>
                {message.content}
              </div>
            ))
          ) : (
            <div className="text-muted-foreground">输入问题后开始对话，会话记录会保存在浏览器本地。</div>
          )}
          {streamingAnswer && activeSession && activeSession.messages.length > 0 && (
            <div className="whitespace-pre-wrap rounded-xl bg-surface/60 p-3 text-muted-foreground">
              <div className="mb-1 text-xs text-muted-foreground/70">AI（生成中）</div>
              {streamingAnswer}
            </div>
          )}
        </div>
        <div className="mt-6 flex gap-3">
          <input
            className="flex-1 rounded-xl border border-border bg-panel/60 px-4 py-3 text-sm text-foreground outline-none"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            onKeyDown={(event) => { if (event.key === "Enter" && !loading) void send(); }}
            placeholder="输入问题，Enter 发送"
          />
          <Button onClick={send} disabled={loading || !question.trim()}>{loading ? "发送中" : streamMode ? "流式发送" : "发送"}</Button>
        </div>
      </Card>
      <Card>
        <h2 className="font-semibold">模型参数</h2>
        <div className="mt-4 space-y-4 text-sm text-muted-foreground">
          <label className="block">
            <span className="mb-1 block text-xs text-muted-foreground/70">当前模型</span>
            <select className="w-full rounded-xl border border-border bg-panel/60 px-3 py-2 text-foreground" value={selectedModel} onChange={(event) => setSelectedModel(event.target.value)}>
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
          {modelError && <div className="rounded-xl bg-danger-soft p-3 text-danger-foreground">{modelError}</div>}
          <p className="text-xs text-muted-foreground/70">会话记录保存在浏览器 localStorage，刷新页面不丢失；切换会话可对比不同问题的回答。</p>
        </div>
      </Card>
    </div>
  );
}
