import { Card } from "@/components/ui/card";

export default function EvalsPage() {
  return (
    <Card>
      <h2 className="text-xl font-semibold">模型评测集</h2>
      <p className="mt-2 text-sm text-slate-400">用于比较不同模型、不同 Prompt 版本的准确率、成本和响应时间。</p>
      <div className="mt-6 grid gap-4 md:grid-cols-3">
        <div className="rounded-xl bg-white/10 p-4">平均得分 86.5</div>
        <div className="rounded-xl bg-white/10 p-4">平均耗时 1.9s</div>
        <div className="rounded-xl bg-white/10 p-4">单次成本 $0.003</div>
      </div>
    </Card>
  );
}
