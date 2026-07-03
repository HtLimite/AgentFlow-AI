"use client";

import { useEffect, useMemo, useState } from "react";
import { apiGet, apiJson } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

interface PromptItem {
  id: number;
  name: string;
  scenario: string;
  content: string;
  current_version?: number;
}

interface PromptVersion {
  version: number;
  content: string;
  change_note?: string | null;
  created_at?: string | null;
}

export function PromptConsole() {
  const [items, setItems] = useState<PromptItem[]>([]);
  const [versions, setVersions] = useState<PromptVersion[]>([]);
  const [selectedPromptId, setSelectedPromptId] = useState<number | null>(null);
  const [variablesText, setVariablesText] = useState("{\"question\":\"AgentFlow-AI 当前能力是什么？\"}");
  const [rendered, setRendered] = useState("请选择 Prompt，并填写 JSON 变量后渲染");
  const [form, setForm] = useState({ name: "", scenario: "general", content: "", changeNote: "update" });
  const [error, setError] = useState("");

  const selectedPrompt = useMemo(() => items.find((item) => item.id === selectedPromptId), [items, selectedPromptId]);

  async function load(preferredId = selectedPromptId) {
    const data = await apiGet<PromptItem[]>("/api/prompts");
    setItems(data);
    const nextId = data.some((item) => item.id === preferredId) ? preferredId : data[0]?.id ?? null;
    setSelectedPromptId(nextId);
    if (nextId) {
      await loadVersions(nextId);
      const next = data.find((item) => item.id === nextId);
      if (next) {
        setForm({ name: next.name, scenario: next.scenario, content: next.content, changeNote: "update" });
      }
    }
  }

  async function loadVersions(promptId = selectedPromptId) {
    if (!promptId) {
      setVersions([]);
      return;
    }
    const data = await apiGet<PromptVersion[]>(`/api/prompts/${promptId}/versions`);
    setVersions(data);
  }

  useEffect(() => {
    load().catch((err) => setError(err instanceof Error ? err.message : "Prompt 加载失败"));
  }, []);

  useEffect(() => {
    if (!selectedPrompt) return;
    setForm({ name: selectedPrompt.name, scenario: selectedPrompt.scenario, content: selectedPrompt.content, changeNote: "update" });
    loadVersions(selectedPrompt.id).catch((err) => setError(err instanceof Error ? err.message : "Prompt 版本加载失败"));
  }, [selectedPrompt?.id]);

  async function createPrompt() {
    if (!form.name.trim() || !form.content.trim()) {
      setError("请填写 Prompt 名称和内容");
      return;
    }
    const created = await apiJson<PromptItem>("/api/prompts", {
      name: form.name.trim(),
      scenario: form.scenario.trim() || "general",
      content: form.content,
    });
    setRendered(`已创建 Prompt：${created.name}`);
    setError("");
    await load(created.id);
  }

  async function updatePrompt() {
    if (!selectedPromptId) {
      setError("请先选择 Prompt");
      return;
    }
    if (!form.content.trim()) {
      setError("Prompt 内容不能为空");
      return;
    }
    const updated = await apiJson<PromptItem>(`/api/prompts/${selectedPromptId}`, {
      content: form.content,
      change_note: form.changeNote.trim() || "update",
    }, "PUT");
    setRendered(`已更新 Prompt：${updated.name} v${updated.current_version ?? "-"}`);
    setError("");
    await load(selectedPromptId);
  }

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
        <div className="flex items-center justify-between gap-3">
          <h2 className="font-semibold">Prompt 模板</h2>
          <Button onClick={() => void load(selectedPromptId)}>刷新</Button>
        </div>
        <div className="mt-4 space-y-2 text-sm text-slate-300">
          {items.length === 0 ? (
            <div className="rounded-xl bg-white/10 p-3 text-slate-400">暂无 Prompt，请在右侧新建。</div>
          ) : (
            items.map((item) => (
              <button key={item.id} onClick={() => setSelectedPromptId(item.id)} className={`block w-full rounded-xl p-3 text-left hover:bg-white/15 ${selectedPromptId === item.id ? "bg-blue-500/20" : "bg-white/10"}`}>
                {item.name}
                <div className="text-xs text-slate-500">{item.scenario} · v{item.current_version ?? 1}</div>
              </button>
            ))
          )}
        </div>

        <h3 className="mt-6 font-semibold">版本记录</h3>
        <div className="mt-3 space-y-2">
          {versions.length === 0 ? (
            <div className="rounded-xl bg-white/5 p-3 text-sm text-slate-500">暂无版本。</div>
          ) : (
            versions.slice(0, 6).map((item) => (
              <button key={item.version} className="block w-full rounded-xl bg-white/5 p-3 text-left text-xs text-slate-400" onClick={() => setForm((current) => ({ ...current, content: item.content, changeNote: `restore v${item.version}` }))}>
                v{item.version} · {item.change_note ?? "-"} · 点击载入内容
              </button>
            ))
          )}
        </div>
      </Card>

      <div className="space-y-4">
        <Card>
          <h2 className="font-semibold">创建 / 更新 Prompt</h2>
          {error && <div className="mt-3 rounded-xl bg-red-500/10 p-3 text-sm text-red-200">{error}</div>}
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            <label className="block text-sm text-slate-300">
              <span className="mb-1 block text-xs text-slate-500">名称</span>
              <input className="w-full rounded-xl border border-white/10 bg-slate-950/60 px-4 py-3" value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} />
            </label>
            <label className="block text-sm text-slate-300">
              <span className="mb-1 block text-xs text-slate-500">场景</span>
              <input className="w-full rounded-xl border border-white/10 bg-slate-950/60 px-4 py-3" value={form.scenario} onChange={(event) => setForm({ ...form, scenario: event.target.value })} />
            </label>
            <label className="block text-sm text-slate-300 md:col-span-2">
              <span className="mb-1 block text-xs text-slate-500">内容</span>
              <textarea className="min-h-40 w-full rounded-xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm text-slate-200" value={form.content} onChange={(event) => setForm({ ...form, content: event.target.value })} />
            </label>
            <label className="block text-sm text-slate-300 md:col-span-2">
              <span className="mb-1 block text-xs text-slate-500">更新说明</span>
              <input className="w-full rounded-xl border border-white/10 bg-slate-950/60 px-4 py-3" value={form.changeNote} onChange={(event) => setForm({ ...form, changeNote: event.target.value })} />
            </label>
          </div>
          <div className="mt-4 flex flex-wrap gap-3">
            <Button onClick={createPrompt}>新建 Prompt</Button>
            <Button onClick={updatePrompt} disabled={!selectedPromptId}>更新所选 Prompt</Button>
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
    </div>
  );
}
