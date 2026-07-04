"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { apiDelete, apiGet, apiJson, errorMessage } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { ConfirmDialog } from "@/components/ui/dialog";

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
  input_price: number | string | null;
  output_price: number | string | null;
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
  description: string;
};

type ProviderForm = {
  name: string;
  providerType: ProviderType;
  baseUrl: string;
  apiKey: string;
  enabled: boolean;
};

type ModelForm = {
  providerId: string;
  modelName: string;
  modelType: ModelType;
  contextWindow: string;
  inputPrice: string;
  outputPrice: string;
  enabled: boolean;
};

const PROVIDER_TYPE_OPTIONS: Array<{ value: ProviderType; label: string; description: string }> = [
  { value: "openai-compatible", label: "OpenAI-Compatible", description: "DeepSeek、Qwen、Kimi、OpenRouter、Doubao、火山方舟等兼容格式" },
  { value: "ollama", label: "Ollama", description: "本地 Ollama 服务，默认 http://localhost:11434/v1" },
  { value: "azure-openai", label: "Azure OpenAI", description: "Azure OpenAI 专用接入格式" },
];

const MODEL_TYPE_OPTIONS: Array<{ value: ModelType; label: string; hint: string }> = [
  { value: "chat", label: "Chat 对话模型", hint: "用于 Chat / Agent / Workflow LLM 节点" },
  { value: "embedding", label: "Embedding 向量模型", hint: "用于 RAG 文档向量化和查询向量化" },
  { value: "rerank", label: "Rerank 重排模型", hint: "用于 RAG 检索结果重排" },
];

const PROVIDER_PRESETS: ProviderPreset[] = [
  {
    key: "deepseek",
    label: "DeepSeek",
    name: "DeepSeek",
    providerType: "openai-compatible",
    baseUrl: "https://api.deepseek.com/v1",
    description: "DeepSeek 官方 OpenAI-Compatible 地址",
  },
  {
    key: "qwen",
    label: "通义千问 Qwen",
    name: "Qwen",
    providerType: "openai-compatible",
    baseUrl: "https://dashscope.aliyuncs.com/compatible-mode/v1",
    description: "阿里云 DashScope 兼容模式地址",
  },
  {
    key: "kimi",
    label: "Kimi / Moonshot",
    name: "Kimi",
    providerType: "openai-compatible",
    baseUrl: "https://api.moonshot.cn/v1",
    description: "Moonshot OpenAI-Compatible 地址",
  },
  {
    key: "openrouter",
    label: "OpenRouter",
    name: "OpenRouter",
    providerType: "openai-compatible",
    baseUrl: "https://openrouter.ai/api/v1",
    description: "OpenRouter 聚合模型平台地址",
  },
  {
    key: "volcengine-standard",
    label: "火山方舟 · 普通 API",
    name: "火山方舟普通 API",
    providerType: "openai-compatible",
    baseUrl: "https://ark.cn-beijing.volces.com/api/v3",
    description: "普通方舟 API Key 使用 /api/v3，模型名填控制台真实 model / endpoint id",
  },
  {
    key: "volcengine-coding",
    label: "火山方舟 · Coding Plan",
    name: "火山方舟 Coding Plan",
    providerType: "openai-compatible",
    baseUrl: "https://ark.cn-beijing.volces.com/api/coding/v3",
    description: "Coding Plan 使用 /api/coding/v3，避免误走普通 /api/v3",
  },
  {
    key: "volcengine-agent",
    label: "火山方舟 · Agent Plan",
    name: "火山方舟 Agent Plan",
    providerType: "openai-compatible",
    baseUrl: "https://ark.cn-beijing.volces.com/api/plan/v3",
    description: "Agent Plan 使用 /api/plan/v3，适合 Agent / Coding 工具类额度",
  },
  {
    key: "openai",
    label: "OpenAI",
    name: "OpenAI",
    providerType: "openai-compatible",
    baseUrl: "https://api.openai.com/v1",
    description: "OpenAI 官方 API 地址",
  },
  {
    key: "ollama",
    label: "Ollama 本地模型",
    name: "Ollama",
    providerType: "ollama",
    baseUrl: "http://localhost:11434/v1",
    description: "本地 Ollama OpenAI-Compatible 地址",
  },
  {
    key: "custom-openai-compatible",
    label: "自定义 OpenAI-Compatible",
    name: "自定义供应商",
    providerType: "openai-compatible",
    baseUrl: "https://example.com/v1",
    description: "用于中转站、私有网关或其他兼容 OpenAI 协议的服务",
  },
  {
    key: "custom-azure-openai",
    label: "自定义 Azure OpenAI",
    name: "Azure OpenAI",
    providerType: "azure-openai",
    baseUrl: "https://your-resource.openai.azure.com/openai/deployments/your-deployment",
    description: "用于 Azure OpenAI 资源地址",
  },
];

const initialProviderForm: ProviderForm = {
  name: "DeepSeek",
  providerType: "openai-compatible",
  baseUrl: "https://api.deepseek.com/v1",
  apiKey: "",
  enabled: true,
};

const initialModelForm: ModelForm = {
  providerId: "",
  modelName: "",
  modelType: "chat",
  contextWindow: "",
  inputPrice: "",
  outputPrice: "",
  enabled: true,
};

function toNullableNumber(value: string) {
  const trimmed = value.trim();
  return trimmed ? Number(trimmed) : null;
}

function displayPrice(value: number | string | null) {
  if (value === null || value === undefined || value === "") return "-";
  return String(value);
}

export function ModelProviderManager() {
  const [items, setItems] = useState<ProviderItem[]>([]);
  const [models, setModels] = useState<AIModelItem[]>([]);
  const [message, setMessage] = useState("等待操作");
  const [presetKey, setPresetKey] = useState("deepseek");
  const [form, setForm] = useState<ProviderForm>(initialProviderForm);
  const [modelForm, setModelForm] = useState<ModelForm>(initialModelForm);
  const [editingProviderId, setEditingProviderId] = useState<number | null>(null);
  const [editingModelId, setEditingModelId] = useState<number | null>(null);
  const [confirmRemove, setConfirmRemove] = useState<{ kind: "provider" | "model"; id: number; label: string } | null>(null);
  const [removing, setRemoving] = useState(false);

  const selectedPreset = useMemo(() => PROVIDER_PRESETS.find((item) => item.key === presetKey) ?? PROVIDER_PRESETS[0], [presetKey]);
  const providerTypeMeta = PROVIDER_TYPE_OPTIONS.find((item) => item.value === form.providerType);
  const modelTypeMeta = MODEL_TYPE_OPTIONS.find((item) => item.value === modelForm.modelType);
  const providerNameMap = useMemo(() => new Map(items.map((item) => [item.id, item.name])), [items]);
  const enabledChatModels = models.filter((item) => item.enabled && item.model_type === "chat").length;
  const enabledEmbeddingModels = models.filter((item) => item.enabled && item.model_type === "embedding").length;
  const enabledRerankModels = models.filter((item) => item.enabled && item.model_type === "rerank").length;

  const load = useCallback(async () => {
    const [providerData, modelData] = await Promise.all([
      apiGet<ProviderItem[]>("/api/model-providers"),
      apiGet<AIModelItem[]>("/api/model-providers/models/list"),
    ]);
    setItems(providerData);
    setModels(modelData);
    setModelForm((current) => {
      if (current.providerId || providerData.length === 0) {
        return current;
      }
      return { ...current, providerId: String(providerData[0].id) };
    });
  }, []);

  useEffect(() => {
    load().catch((error) => setMessage(errorMessage(error, "供应商与模型加载失败")));
  }, [load]);

  function applyPreset(nextPresetKey: string) {
    const nextPreset = PROVIDER_PRESETS.find((item) => item.key === nextPresetKey) ?? PROVIDER_PRESETS[0];
    setPresetKey(nextPreset.key);
    setEditingProviderId(null);
    setForm({
      name: nextPreset.name,
      providerType: nextPreset.providerType,
      baseUrl: nextPreset.baseUrl,
      apiKey: "",
      enabled: true,
    });
  }

  function resetProviderForm() {
    setEditingProviderId(null);
    setForm(initialProviderForm);
    setPresetKey("deepseek");
  }

  function resetModelForm(providerId = modelForm.providerId) {
    setEditingModelId(null);
    setModelForm({ ...initialModelForm, providerId });
  }

  function editProvider(item: ProviderItem) {
    setEditingProviderId(item.id);
    setPresetKey("custom-openai-compatible");
    setForm({
      name: item.name,
      providerType: item.provider_type,
      baseUrl: item.base_url,
      apiKey: "",
      enabled: item.enabled,
    });
    setMessage(`正在编辑供应商：${item.name}。API Key 留空则不修改。`);
  }

  function editModel(item: AIModelItem) {
    setEditingModelId(item.id);
    setModelForm({
      providerId: String(item.provider_id),
      modelName: item.model_name,
      modelType: item.model_type,
      contextWindow: item.context_window ? String(item.context_window) : "",
      inputPrice: item.input_price !== null && item.input_price !== undefined ? String(item.input_price) : "",
      outputPrice: item.output_price !== null && item.output_price !== undefined ? String(item.output_price) : "",
      enabled: item.enabled,
    });
    setMessage(`正在编辑模型：${item.model_name}`);
  }

  async function saveProvider() {
    if (!form.name.trim()) {
      setMessage("请填写供应商名称");
      return;
    }
    if (!form.baseUrl.trim()) {
      setMessage("请填写 Base URL");
      return;
    }
    if (!editingProviderId && !form.apiKey.trim()) {
      setMessage("新增供应商必须填写 API Key；保存后后端加密存储，不会明文回显");
      return;
    }

    const payload: Record<string, unknown> = {
      name: form.name.trim(),
      provider_type: form.providerType,
      base_url: form.baseUrl.trim(),
      enabled: form.enabled,
    };
    if (form.apiKey.trim()) {
      payload.api_key = form.apiKey.trim();
    }

    if (editingProviderId) {
      await apiJson<ProviderItem>(`/api/model-providers/${editingProviderId}`, payload, "PUT");
      setMessage("供应商已更新");
    } else {
      const created = await apiJson<ProviderItem>("/api/model-providers", payload);
      setModelForm((current) => ({ ...current, providerId: String(created.id) }));
      setMessage("模型供应商已保存，请继续添加该供应商下的真实模型名");
    }

    resetProviderForm();
    await load();
  }

  async function saveModel() {
    if (!modelForm.providerId) {
      setMessage("请先选择供应商");
      return;
    }
    if (!modelForm.modelName.trim()) {
      setMessage("请填写真实模型名，例如 deepseek-chat、qwen-plus、ark-code-latest、doubao-seed-1-6 等");
      return;
    }

    const payload = {
      provider_id: Number(modelForm.providerId),
      model_name: modelForm.modelName.trim(),
      model_type: modelForm.modelType,
      context_window: toNullableNumber(modelForm.contextWindow),
      input_price: toNullableNumber(modelForm.inputPrice),
      output_price: toNullableNumber(modelForm.outputPrice),
      enabled: modelForm.enabled,
    };

    if (editingModelId) {
      await apiJson<AIModelItem>(`/api/model-providers/models/${editingModelId}`, payload, "PUT");
      setMessage("模型已更新，Chat / RAG / Eval 会读取最新启用状态");
    } else {
      await apiJson<AIModelItem>("/api/model-providers/models", payload);
      setMessage("模型已保存；Chat 页面会自动从模型列表加载并支持切换");
    }

    resetModelForm(modelForm.providerId);
    await load();
  }

  async function testProvider(id: number) {
    const result = await apiJson<{ message: string }>(`/api/model-providers/${id}/test`, {});
    setMessage(result.message);
  }

  async function toggleProvider(item: ProviderItem) {
    await apiJson<ProviderItem>(`/api/model-providers/${item.id}`, { enabled: !item.enabled }, "PUT");
    setMessage(`${item.name} 已${item.enabled ? "停用" : "启用"}`);
    await load();
  }

  async function toggleModel(item: AIModelItem) {
    await apiJson<AIModelItem>(`/api/model-providers/models/${item.id}`, { enabled: !item.enabled }, "PUT");
    setMessage(`${item.model_name} 已${item.enabled ? "停用" : "启用"}`);
    await load();
  }

  async function removeProvider(item: ProviderItem) {
    await apiDelete(`/api/model-providers/${item.id}`);
    setMessage(`已删除供应商：${item.name}`);
    if (editingProviderId === item.id) resetProviderForm();
    await load();
  }

  async function removeModel(item: AIModelItem) {
    await apiDelete(`/api/model-providers/models/${item.id}`);
    setMessage(`已删除模型：${item.model_name}`);
    if (editingModelId === item.id) resetModelForm(modelForm.providerId);
    await load();
  }

  async function executeConfirmedRemove() {
    if (!confirmRemove) return;
    setRemoving(true);
    try {
      if (confirmRemove.kind === "provider") {
        const item = items.find((row) => row.id === confirmRemove.id);
        if (item) await removeProvider(item);
      } else {
        const item = models.find((row) => row.id === confirmRemove.id);
        if (item) await removeModel(item);
      }
      setConfirmRemove(null);
    } catch (error) {
      setMessage(errorMessage(error, "删除失败"));
    } finally {
      setRemoving(false);
    }
  }

  return (
    <div className="space-y-4">
      <Card>
        <h2 className="text-xl font-semibold">模型配置中心 · V5 完整管理</h2>
        <p className="mt-2 text-sm text-muted-foreground">
          当前阶段补齐供应商和模型的新增、编辑、启停、删除、连接测试；Chat / RAG / Eval / Workflow 会读取这里的启用模型。
        </p>
        <div className="mt-4 grid gap-3 md:grid-cols-4">
          <div className="rounded-xl bg-surface/60 p-3 text-sm text-muted-foreground">供应商 {items.length}</div>
          <div className="rounded-xl bg-surface/60 p-3 text-sm text-muted-foreground">Chat {enabledChatModels}</div>
          <div className="rounded-xl bg-surface/60 p-3 text-sm text-muted-foreground">Embedding {enabledEmbeddingModels}</div>
          <div className="rounded-xl bg-surface/60 p-3 text-sm text-muted-foreground">Rerank {enabledRerankModels}</div>
        </div>
        <div className="mt-4 rounded-xl bg-surface/60 p-3 text-sm text-muted-foreground">状态：{message}</div>
      </Card>

      <div className="grid gap-4 xl:grid-cols-2">
        <Card>
          <div className="flex items-start justify-between gap-3">
            <div>
              <h2 className="font-semibold">{editingProviderId ? "编辑模型供应商" : "新增模型供应商"}</h2>
              <p className="mt-2 text-sm text-muted-foreground">预设只负责快速填充，Base URL 仍可手动修正，避免火山方舟 Plan 地址被锁死。</p>
            </div>
            {editingProviderId && <Button onClick={resetProviderForm}>取消编辑</Button>}
          </div>
          <div className="mt-4 space-y-3">
            <label className="block text-sm text-muted-foreground">
              <span className="mb-1 block">供应商预设</span>
              <select className="w-full rounded-xl border border-border bg-panel/60 px-4 py-3 text-sm" value={presetKey} onChange={(event) => applyPreset(event.target.value)}>
                {PROVIDER_PRESETS.map((item) => (
                  <option key={item.key} value={item.key}>{item.label}</option>
                ))}
              </select>
            </label>

            <div className="rounded-xl bg-surface/60 p-3 text-xs text-muted-foreground">{selectedPreset.description}</div>

            <label className="block text-sm text-muted-foreground">
              <span className="mb-1 block">供应商名称</span>
              <input
                className="w-full rounded-xl border border-border bg-panel/60 px-4 py-3 text-sm"
                value={form.name}
                onChange={(event) => setForm({ ...form, name: event.target.value })}
                placeholder="供应商名称"
              />
            </label>

            <label className="block text-sm text-muted-foreground">
              <span className="mb-1 block">协议类型</span>
              <select
                className="w-full rounded-xl border border-border bg-panel/60 px-4 py-3 text-sm"
                value={form.providerType}
                onChange={(event) => setForm({ ...form, providerType: event.target.value as ProviderType })}
              >
                {PROVIDER_TYPE_OPTIONS.map((item) => (
                  <option key={item.value} value={item.value}>{item.label}</option>
                ))}
              </select>
              {providerTypeMeta ? <span className="mt-1 block text-xs text-muted-foreground/70">{providerTypeMeta.description}</span> : null}
            </label>

            <label className="block text-sm text-muted-foreground">
              <span className="mb-1 block">Base URL</span>
              <input
                className="w-full rounded-xl border border-border bg-panel/60 px-4 py-3 text-sm"
                value={form.baseUrl}
                onChange={(event) => setForm({ ...form, baseUrl: event.target.value })}
                placeholder="Base URL"
              />
            </label>

            <label className="block text-sm text-muted-foreground">
              <span className="mb-1 block">API Key{editingProviderId ? "，留空则不修改" : ""}</span>
              <input
                className="w-full rounded-xl border border-border bg-panel/60 px-4 py-3 text-sm"
                value={form.apiKey}
                onChange={(event) => setForm({ ...form, apiKey: event.target.value })}
                placeholder="API Key，仅提交后端加密保存"
                type="password"
              />
            </label>

            <label className="flex items-center gap-2 text-sm text-muted-foreground">
              <input type="checkbox" checked={form.enabled} onChange={(event) => setForm({ ...form, enabled: event.target.checked })} />
              启用供应商
            </label>

            <Button onClick={saveProvider}>{editingProviderId ? "更新供应商" : "保存供应商"}</Button>
          </div>
        </Card>

        <Card>
          <div className="flex items-start justify-between gap-3">
            <div>
              <h2 className="font-semibold">{editingModelId ? "编辑模型" : "新增模型"}</h2>
              <p className="mt-2 text-sm text-muted-foreground">模型名必须填写供应商真实支持的 model 参数。价格字段用于后续成本统计，可先留空。</p>
            </div>
            {editingModelId && <Button onClick={() => resetModelForm(modelForm.providerId)}>取消编辑</Button>}
          </div>
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            <label className="block text-sm text-muted-foreground">
              <span className="mb-1 block">所属供应商</span>
              <select className="w-full rounded-xl border border-border bg-panel/60 px-4 py-3 text-sm" value={modelForm.providerId} onChange={(event) => setModelForm({ ...modelForm, providerId: event.target.value })}>
                {items.map((item) => (
                  <option key={item.id} value={item.id}>{item.name}</option>
                ))}
              </select>
            </label>
            <label className="block text-sm text-muted-foreground">
              <span className="mb-1 block">模型类型</span>
              <select className="w-full rounded-xl border border-border bg-panel/60 px-4 py-3 text-sm" value={modelForm.modelType} onChange={(event) => setModelForm({ ...modelForm, modelType: event.target.value as ModelType })}>
                {MODEL_TYPE_OPTIONS.map((item) => (
                  <option key={item.value} value={item.value}>{item.label}</option>
                ))}
              </select>
              {modelTypeMeta ? <span className="mt-1 block text-xs text-muted-foreground/70">{modelTypeMeta.hint}</span> : null}
            </label>
            <label className="block text-sm text-muted-foreground md:col-span-2">
              <span className="mb-1 block">真实模型名</span>
              <input className="w-full rounded-xl border border-border bg-panel/60 px-4 py-3 text-sm" value={modelForm.modelName} onChange={(event) => setModelForm({ ...modelForm, modelName: event.target.value })} placeholder="例如 deepseek-chat、qwen-plus、ark-code-latest、doubao-seed-1-6" />
            </label>
            <label className="block text-sm text-muted-foreground">
              <span className="mb-1 block">上下文窗口，可选</span>
              <input className="w-full rounded-xl border border-border bg-panel/60 px-4 py-3 text-sm" value={modelForm.contextWindow} onChange={(event) => setModelForm({ ...modelForm, contextWindow: event.target.value })} placeholder="例如 128000" type="number" />
            </label>
            <label className="block text-sm text-muted-foreground">
              <span className="mb-1 block">输入价格，可选</span>
              <input className="w-full rounded-xl border border-border bg-panel/60 px-4 py-3 text-sm" value={modelForm.inputPrice} onChange={(event) => setModelForm({ ...modelForm, inputPrice: event.target.value })} placeholder="每 1K / 1M token 成本，按供应商口径" type="number" step="0.000001" />
            </label>
            <label className="block text-sm text-muted-foreground">
              <span className="mb-1 block">输出价格，可选</span>
              <input className="w-full rounded-xl border border-border bg-panel/60 px-4 py-3 text-sm" value={modelForm.outputPrice} onChange={(event) => setModelForm({ ...modelForm, outputPrice: event.target.value })} placeholder="每 1K / 1M token 成本，按供应商口径" type="number" step="0.000001" />
            </label>
            <label className="flex items-center gap-2 text-sm text-muted-foreground">
              <input type="checkbox" checked={modelForm.enabled} onChange={(event) => setModelForm({ ...modelForm, enabled: event.target.checked })} />
              启用模型
            </label>
          </div>
          <div className="mt-4"><Button onClick={saveModel}>{editingModelId ? "更新模型" : "保存模型"}</Button></div>
        </Card>
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        <Card>
          <h2 className="font-semibold">供应商列表</h2>
          <div className="mt-4 space-y-3">
            {items.length === 0 ? (
              <div className="rounded-xl bg-surface/30 p-4 text-sm text-muted-foreground">暂无供应商，请先新增。</div>
            ) : (
              items.map((item) => (
                <div key={item.id} className="rounded-xl border border-border bg-surface/30 p-4">
                  <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                    <div>
                      <div className="font-medium">{item.name}</div>
                      <div className="mt-1 break-all text-xs text-muted-foreground">{item.base_url}</div>
                      <div className="mt-1 text-xs text-muted-foreground/70">{item.provider_type} · {item.api_key_masked} · {item.enabled ? "enabled" : "disabled"}</div>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      <Button onClick={() => testProvider(item.id)}>测试</Button>
                      <Button onClick={() => editProvider(item)}>编辑</Button>
                      <Button onClick={() => toggleProvider(item)}>{item.enabled ? "停用" : "启用"}</Button>
                      <Button className="bg-danger hover:bg-danger/85" onClick={() => setConfirmRemove({ kind: "provider", id: item.id, label: item.name })}>删除</Button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </Card>

        <Card>
          <h2 className="font-semibold">模型列表</h2>
          <div className="mt-4 space-y-3">
            {models.length === 0 ? (
              <div className="rounded-xl bg-surface/30 p-4 text-sm text-muted-foreground">暂无模型，请先新增模型。</div>
            ) : (
              models.map((item) => (
                <div key={item.id} className="rounded-xl border border-border bg-surface/30 p-4 text-sm text-muted-foreground">
                  <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                    <div>
                      <div className="font-medium">{item.model_name}</div>
                      <div className="mt-1 text-xs text-muted-foreground/70">
                        {providerNameMap.get(item.provider_id) ?? `Provider #${item.provider_id}`} · {item.model_type} · {item.enabled ? "enabled" : "disabled"}
                      </div>
                      <div className="mt-1 text-xs text-muted-foreground/70">
                        上下文 {item.context_window ?? "-"} · 输入价 {displayPrice(item.input_price)} · 输出价 {displayPrice(item.output_price)}
                      </div>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      <Button onClick={() => editModel(item)}>编辑</Button>
                      <Button onClick={() => toggleModel(item)}>{item.enabled ? "停用" : "启用"}</Button>
                      <Button className="bg-danger hover:bg-danger/85" onClick={() => setConfirmRemove({ kind: "model", id: item.id, label: item.model_name })}>删除</Button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </Card>
      </div>

      <ConfirmDialog
        open={confirmRemove !== null}
        onOpenChange={(open) => { if (!open) setConfirmRemove(null); }}
        title={confirmRemove?.kind === "provider" ? "删除供应商" : "删除模型"}
        description={
          confirmRemove?.kind === "provider"
            ? `删除供应商「${confirmRemove.label}」会级联删除其下所有模型，确认继续？`
            : `确认删除模型「${confirmRemove?.label ?? ""}」？`
        }
        confirmText="删除"
        destructive
        loading={removing}
        onConfirm={executeConfirmedRemove}
      />
    </div>
  );
}
