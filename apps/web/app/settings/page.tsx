import { Card } from "@/components/ui/card";

export default function SettingsPage() {
  return (
    <div className="grid gap-4 xl:grid-cols-2">
      <Card>
        <h2 className="font-semibold">模型供应商</h2>
        <p className="mt-2 text-sm text-slate-400">支持 OpenAI-Compatible Base URL，API Key 后端加密保存。</p>
        <div className="mt-4 rounded-xl bg-white/10 p-4 text-sm text-slate-300">DeepSeek / Qwen / Doubao / Kimi / Ollama</div>
      </Card>
      <Card>
        <h2 className="font-semibold">系统配置</h2>
        <p className="mt-2 text-sm text-slate-400">日志、成本、向量检索 TopK、RAG Prompt 默认值。</p>
      </Card>
    </div>
  );
}
