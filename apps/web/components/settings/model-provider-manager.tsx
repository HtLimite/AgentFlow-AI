"use client";

import { useEffect, useState } from "react";
import { apiGet, apiJson } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

interface ProviderItem {
  id: number;
  name: string;
  provider_type: string;
  base_url: string;
  api_key_masked: string;
  enabled: boolean;
}

export function ModelProviderManager() {
  const [items, setItems] = useState<ProviderItem[]>([]);
  const [message, setMessage] = useState("等待操作");
  const [form, setForm] = useState({
    name: "DeepSeek",
    providerType: "openai-compatible",
    baseUrl: "https://api.deepseek.com/v1",
    apiKey: "",
  });

  async function load() {
    const data = await apiGet<ProviderItem[]>("/api/model-providers");
    setItems(data);
  }

  useEffect(() => {
    load().catch((error) => setMessage(error.message));
  }, []);

  async function createProvider() {
    await apiJson("/api/model-providers", {
      name: form.name,
      provider_type: form.providerType,
      base_url: form.baseUrl,
      api_key: form.apiKey || "demo-key",
      enabled: true,
    });
    setMessage("模型供应商已保存");
    await load();
  }

  async function testProvider(id: number) {
    const result = await apiJson<{ message: string }>(`/api/model-providers/${id}/test`, {});
    setMessage(result.message);
  }

  return (
    <div className="grid gap-4 xl:grid-cols-[420px_1fr]">
      <Card>
        <h2 className="font-semibold">新增模型供应商</h2>
        <div className="mt-4 space-y-3">
          <input className="w-full rounded-xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm" value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} placeholder="供应商名称" />
          <input className="w-full rounded-xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm" value={form.providerType} onChange={(event) => setForm({ ...form, providerType: event.target.value })} placeholder="供应商类型" />
          <input className="w-full rounded-xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm" value={form.baseUrl} onChange={(event) => setForm({ ...form, baseUrl: event.target.value })} placeholder="Base URL" />
          <input className="w-full rounded-xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm" value={form.apiKey} onChange={(event) => setForm({ ...form, apiKey: event.target.value })} placeholder="API Key，仅提交后端加密保存" type="password" />
          <Button onClick={createProvider}>保存供应商</Button>
        </div>
        <div className="mt-4 rounded-xl bg-white/10 p-3 text-sm text-slate-300">状态：{message}</div>
      </Card>
      <Card>
        <h2 className="font-semibold">供应商列表</h2>
        <div className="mt-4 space-y-3">
          {items.map((item) => (
            <div key={item.id} className="rounded-xl border border-white/10 bg-white/[0.04] p-4">
              <div className="flex items-center justify-between gap-4">
                <div>
                  <div className="font-medium">{item.name}</div>
                  <div className="mt-1 text-xs text-slate-400">{item.base_url}</div>
                  <div className="mt-1 text-xs text-slate-500">{item.provider_type} · {item.api_key_masked}</div>
                </div>
                <Button onClick={() => testProvider(item.id)}>测试</Button>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
