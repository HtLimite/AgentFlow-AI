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

interface AIModelItem {
  id: number;
  provider_id: number;
  model_name: string;
  model_type: ModelType;
  context_window: number | null;
  enabled: boolean;
}

type ProviderType = "openai-compatible" | "ollama" | "azure-openai";
type ModelType = "chat" | "embedding" | "rerank";

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

const MODEL_TYPE_OPTIONS: Array<{ value: ModelType; label: string }> = [
  { value: "chat", label: "Chat 对话模型" },
  { value: "embedding", label: "Embedding 向量模型" },
  { value: "rerank", label: "Rerank 重排模型" },
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
  const [models, setModels] = useState<AIModelItem[]>([]);
  const [message, setMessage] = useState("等待操作");
  const [presetKey, setPresetKey] = useState("deepseek");
  const [form, setForm] = useState({
    name: "DeepSeek",
    providerType: "openai-compatible" as ProviderType,
    baseUrl: "https://api.deepseek.com/v1",
    apiKey: "",
  });
  const [modelForm, setModelForm] = useState({
    providerId: "",
    modelName: "",
    modelType: "chat" as ModelType,
    contextWindow: "",
  });

  const selectedPreset = useMemo(() => PROVIDER_PRESETS.find((item) => item.key === presetKey) ?? PROVIDER_PRESETS[0], [presetKey]);
  const providerTypeMeta = PROVIDER_TYPE_OPTIONS.find((item) => item.value === form.providerType);
  const providerNameMap = useMemo(() => new Map(items.map((item) => [item.id, item.name])), [items]);

  async function load() {
    const [providerData, modelData] = await Promise.all([
      apiGet<ProviderItem[]>("/api/model-providers"),
      apiGet<AIModelItem[]>("/api/model-providers/models/list"),
    ]);
    setItems(providerData);
    setModels(modelData);
    if (!modelForm.providerId && providerData.length > 0) {
      setModelForm((current) => ({ ...current, providerId: String(providerData[0].id) }));
    }
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
    const created = await apiJson<ProviderItem>("/api/model-providers", {
      name: form.name,
      provider_type: form.providerType,
      base_url: form.baseUrl,
      api_key: form.apiKey,
      enabled: true,
    });
    setMessage("模型供应商已保存，请继续在右侧添加该供应商下的真实模型名");
    setForm((current) => ({ ...current, apiKey: "" }));
    setModelForm((current) => ({ ...current, providerId: String(created.id) }));
    await load();
  }

  async function createModel() {
    if (!modelForm.providerId) {
      setMessage("请先选择供应商");
      return;
    }
    if (!modelForm.modelName.trim()) {
      setMessage("请填写真实模型名，例如 deepseek-chat、qwen-plus、doubao-seed-1-6 等");
      return;
    }
    await apiJson<AIModelItem>("/api/model-providers/models", {
      provider_id: Number(modelForm.providerId),
      model_name: modelForm.modelName.trim(),
      model_type: modelForm.modelType,
      context_window: modelForm.contextWindow ? Number(modelForm.contextWindow) : null,
      enabled: true,
    });
    setMessage("模型已保存；Chat 页面会自动从模型列表加载并支持切换");
    setModelForm((current) => ({ ...current, modelName: "", contextWindow: "" }));
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
        <p className="mt-2 text-sm text-slate-400">先保存供应商，再添加它下面可调用的真实模型名。Chat 页面切换的是模型，不是只切供应商。</p>
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
      <div className="space-y-4">
        <Card>
          <h2 className="font-semibold">新增模型</h2>
          <p className="mt-2 text-sm text-slate-400">模型名必须填写供应商真实支持的 model 参数。保存后，Chat 页面会在下拉框中显示。</p>
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            <label className="block text-sm text-slate-300">
              <span className="mb-1 block">所属供应商</span>
              <select className="w-full rounded-xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm" value={modelForm.providerId} onChange={(event) => setModelForm({ ...modelForm, providerId: event.target.value })}>
                {items.map((item) => (
                  <option key={item.id} value={item.id}>{item.name}</option>
                ))}
              </select>
            </label>
            <label className="block text-sm text-slate-300">
              <span className="mb-1 block">模型类型</span>
              <select className="w-full rounded-xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm" value={modelForm.modelType} onChange={(event) => setModelForm({ ...modelForm, modelType: event.target.value as ModelType })}>
                {MODEL_TYPE_OPTIONS.map((item) => (
                  <option key={item.value} value={item.value}>{item.label}</option>
                ))}
              </select>
            </label>
            <label className="block text-sm text-slate-300 md:col-span-2">
              <span className="mb-1 block">真实模型名</span>
              <input className="w-full rounded-xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm" value={modelForm.modelName} onChange={(event) => setModelForm({ ...modelForm, modelName: event.target.value })} placeholder="例如 deepseek-chat、qwen-plus、kimi-k2-0711-preview" />
            </label>
            <label className="block text-sm text-slate-300">
              <span className="mb-1 block">上下文窗口，可选</span>
              <input className="w-full rounded-xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm" value={modelForm.contextWindow} onChange={(event) => setModelForm({ ...modelForm, contextWindow: event.target.value })} placeholder="例如 128000" type="number" />
            </label>
          </div>
          <div className="mt-4"><Button onClick={createModel}>保存模型</Button></div>
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
        <Card>
          <h2 className="font-semibold">模型列表</h2>
          <div className="mt-4 space-y-3">
            {models.length === 0 ? (
              <div className="rounded-xl bg-white/[0.04] p-4 text-sm text-slate-400">暂无模型，请先新增模型。</div>
            ) : (
              models.map((item) => (
                <div key={item.id} className="rounded-xl border border-white/10 bg-white/[0.04] p-4 text-sm text-slate-300">
                  <div className="font-medium">{item.model_name}</div>
                  <div className="mt-1 text-xs text-slate-500">{providerNameMap.get(item.provider_id) ?? `Provider #${item.provider_id}`} · {item.model_type} · {item.enabled ? "enabled" : "disabled"}</div>
                </div>
              ))
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}
