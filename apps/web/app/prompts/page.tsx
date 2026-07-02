import { Card } from "@/components/ui/card";

export default function PromptsPage() {
  return (
    <div className="grid gap-4 xl:grid-cols-[360px_1fr]">
      <Card>
        <h2 className="font-semibold">Prompt 模板</h2>
        <div className="mt-4 space-y-2 text-sm text-slate-300">
          <div className="rounded-xl bg-white/10 p-3">RAG 问答模板</div>
          <div className="rounded-xl bg-white/10 p-3">Agent 工具调用模板</div>
        </div>
      </Card>
      <Card>
        <h2 className="font-semibold">模板编辑器</h2>
        <pre className="mt-4 overflow-auto rounded-xl bg-slate-950/80 p-4 text-sm text-slate-300">{`你是企业知识库助手。\n请只根据上下文回答。\n问题：{{question}}\n上下文：{{context}}`}</pre>
      </Card>
    </div>
  );
}
