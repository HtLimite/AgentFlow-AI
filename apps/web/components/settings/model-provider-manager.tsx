"use client";

import { useEffect, useMemo, useState } from "react";
import { apiGet, apiJson } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

interface ProviderItem {
  id: number;
  name: string;
  provider_type: ProviderType;
  base_url: string;
  api_key_masked: string;
  enabled: boolean;
}

type ProviderType = "openai-compatible" | "ollama" | "azure-openai";

type ProviderPreset = {
  key: string;
  label: string;
  name: string;
  providerType: ProviderType;
  baseUrl: string;
  editable: boolean;
  description: string;
};

const PROVIDER_TYPE_OPTIONS: Array<{ value: ProviderType; label: string; description: string }> = [
  { value: "openai-compatible", label: "OpenAI-Compatible", description: "DeepSeek、Qwen、Kimi、OpenRouter、Doubao 等兼容格式" },
  { value: "ollama", label: "Ollama", description: "本地 Ollama 服务，默认 http://localhost:11434/v1" },
  { value: "azure-openai", label: "Azure OpenAI", description: "Azure OpenAI 专用接入格式" },
];

const PROVIDER_PRESETS: ProviderPreset[] = [
  {
    key: "deepseek",
    label: "DeepSeek",
    name: "DeepSeek",
    providerType: "openai-compatible",
    baseUrl: "https://api.deepseek.com/v1",
    editable: false,
    description: "DeepSeek 官方 OpenAI-Compatible 地址",
  },
  {
    key: "qwen",
    label: "通义千问 Qwen",
    name: "Qwen",
    providerType: "openai-compatible",
    baseUrl: "https://dashscope.aliyuncs.com/compatible-mode/v1",
    editable: false,
    description: "阿里云 DashScope 兼容模式地址",
  },
  {
    key: "kimi",
    label: "Kimi / Moonshot",
    name: "Kimi",
    providerType: "openai-compatible",
    baseUrl: "https://api.moonshot.cn/v1",
    editable: false,
    description: "Moonshot OpenAI-Compatible 地址",
  },
  {
    key: "openrouter",
    label: "OpenRouter",
    name: "OpenRouter",
    providerType: "openai-compatible",
    baseUrl: "https://openrouter.ai/api/v1",
    editable: false,
    description: "OpenRouter 聚合模型平台地址",
  },
  {
    key: "doubao",
    label: "火山方舟 Doubao",
    name: "Doubao",
    providerType: "openai-compatible",
    baseUrl: "https://ark.cn-beijing.volces.com/api/v3",
    editable: false,
    description: "火山方舟 OpenAI-Compatible 地址",
  },
  {
    key: "openai",
    label: "OpenAI",
    name: "OpenAI",
    providerType: "openai-compatible",
    baseUrl: "https://api.openai.com/v1",
    editable: false,
    description: "OpenAI 官方 API 地址",
  },
  {
    key: "ollama",
    label: "Ollama 本地模型",
    name: "Ollama",
    providerType: "ollama",
    baseUrl: "http://localhost:11434/v1",
    editable: false,
    description: "本地 Ollama OpenAI-Compatible 地址",
  },
  {
    key: "custom-openai-compatible",
    label: "自定义 OpenAI-Compatible",
    name: "自定义供应商",
    providerType: "openai-compatible",
    baseUrl: "https://example.com/v1",
    editable: true,
    description: "用于中转站、私有网关或其他兼容 OpenAI 协议的服务",
  },
  {
    key: "custom-azure-openai",
    label: "自定义 Azure OpenAI",
    name: "Azure OpenAI",
    providerType: "azure-openai",
    baseUrl: "https://your-resource.openai.azure.com/openai/deployments/your-deployment",
    editable: true,
    description: "用于 Azure OpenAI 资源地址",
  },
];

export function ModelProviderManager() {
  const [items, setItems] = useState<ProviderItem[]>([]);
  const [message, setMessage] = useState("等待操作");
  const [presetKey, setPresetKey] = useState("deepseek");
  const [form, setForm] = useState({
    name: "DeepSeek",
    providerType: "openai-compatible" as ProviderType,
    baseUrl: "https://api.deepseek.com/v1",
    apiKey: "",
  });

  const selectedPreset = useMemo(() => PROVIDER_PRESETS.find((item) => item.key === presetKey) ?? PROVIDER_PRESETS[0], [presetKey]);
  const providerTypeMeta = PROVIDER_TYPE_OPTIONS.find((item) => item.value === form.providerType);

  async function load() {
    const data = await apiGet<ProviderItem[]>("/api/model-providers");
    setItems(data);
  }

  useEffect(() => {
    load().catch((error) => setMessage(error.message));
  }, []);

  function applyPreset(nextPresetKey: string) {
    const nextPreset = PROVIDER_PRESETS.find((item) => item.key === nextPresetKey) ?? PROVIDER_PRESETS[0];
    setPresetKey(nextPreset.key);
    setForm((current) => ({
      ...current,
      name: nextPreset.name,
      providerType: nextPreset.providerType,
      baseUrl: nextPreset.baseUrl,
    }));
  }

  async function createProvider() {
    if (!form.apiKey.trim()) {
      setMessage("请填写 API Key；保存后只会在后端加密存储，不会明文回显");
      return;
    }
    await apiJson("/api/model-providers", {
      name: form.name,
      provider_type: form.providerType,
      base_url: form.baseUrl,
      api_key: form.apiKey,
      enabled: true,
    });
    setMessage("模型供应商已保存");
    setForm((current) => ({ ...current, apiKey: "" }));
    await load();
  }

  async function testProvider(id: number) {
    const result = await apiJson<{ message: string }>(`/api/model-providers/${id}/test`, {});
    setMessage(result.message);
  }

  return (
    <div className="grid gap-4 xl:grid-cols-[460px_1fr]">
      <Card>
        <h2 className="font-semibold">新增模型供应商</h2>
        <p className="mt-2 text-sm text-slate-400">固定格式字段已改为选项输入：供应商预设、协议类型都会限制范围，避免随便填导致后端脏数据。</p>
        <div className="mt-4 space-y-3">
          <label className="block text-sm text-slate-300">
            <span className="mb-1 block">供应商预设</span>
            <select className="w-full rounded-xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm" value={presetKey} onChange={(event) => applyPreset(event.target.value)}>
              {PROVIDER_PRESETS.map((item) => (
                <option key={item.key} value={item.key}>{item.label}</option>
              ))}
            </select>
          </label>

          <div className="rounded-xl bg-white/10 p-3 text-xs text-slate-400">{selectedPreset.description}</div>

          <label className="block text-sm text-slate-300">
            <span className="mb-1 block">供应商名称</span>
            <input
              className="w-full rounded-xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm disabled:cursor-not-allowed disabled:opacity-60"
              value={form.name}
              onChange={(event) => setForm({ ...form, name: event.target.value })}
              placeholder="供应商名称"
              disabled={!selectedPreset.editable}
            />
          </label>

          <label className="block text-sm text-slate-300">
            <span className="mb-1 block">协议类型</span>
            <select
              className="w-full rounded-xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm disabled:cursor-not-allowed disabled:opacity-60"
              value={form.providerType}
              onChange={(event) => setForm({ ...form, providerType: event.target.value as ProviderType })}
              disabled={!selectedPreset.editable}
            >
              {PROVIDER_TYPE_OPTIONS.map((item) => (
                <option key={item.value} value={item.value}>{item.label}</option>
              ))}
            </select>
            {providerTypeMeta ? <span className="mt-1 block text-xs text-slate-500">{providerTypeMeta.description}</span> : null}
          </label>

          <label className="block text-sm text-slate-300">
            <span className="mb-1 block">Base URL</span>
            <input
              className="w-full rounded-xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm disabled:cursor-not-allowed disabled:opacity-60"
              value={form.baseUrl}
              onChange={(event) => setForm({ ...form, baseUrl: event.target.value })}
              placeholder="Base URL"
              disabled={!selectedPreset.editable}
            />
          </label>

          <label className="block text-sm text-slate-300">
            <span className="mb-1 block">API Key</span>
            <input className="w-full rounded-xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm" value={form.apiKey} onChange={(event) => setForm({ ...form, apiKey: event.target.value })} placeholder="API Key，仅提交后端加密保存" type="password" />
          </label>

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
