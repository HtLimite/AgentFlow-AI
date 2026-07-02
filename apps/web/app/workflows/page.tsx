import { Card } from "@/components/ui/card";

const nodes = ["Start", "Knowledge", "LLM", "Condition", "HTTP", "End"];

export default function WorkflowsPage() {
  return (
    <Card>
      <h2 className="text-xl font-semibold">工作流编排</h2>
      <p className="mt-2 text-sm text-slate-400">V2/V3 接入 React Flow，这里先预留画布与节点配置面板。</p>
      <div className="mt-6 grid gap-3 md:grid-cols-3 xl:grid-cols-6">
        {nodes.map((node) => (
          <div key={node} className="rounded-2xl border border-white/10 bg-slate-950/70 p-4 text-center text-sm">{node}</div>
        ))}
      </div>
      <div className="mt-6 h-96 rounded-2xl border border-dashed border-white/15 bg-white/[0.03] p-6 text-sm text-slate-400">工作流画布区域</div>
    </Card>
  );
}
