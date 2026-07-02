import { Card } from "@/components/ui/card";

const metrics = [
  { label: "今日调用", value: "1,284", change: "+18%" },
  { label: "Token 消耗", value: "2.4M", change: "+9%" },
  { label: "平均耗时", value: "1.8s", change: "-12%" },
  { label: "失败率", value: "0.7%", change: "-0.4%" }
];

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {metrics.map((item) => (
          <Card key={item.label}>
            <div className="text-sm text-slate-400">{item.label}</div>
            <div className="mt-3 text-3xl font-bold">{item.value}</div>
            <div className="mt-2 text-sm text-emerald-300">{item.change}</div>
          </Card>
        ))}
      </section>
      <section className="grid gap-4 xl:grid-cols-3">
        <Card className="xl:col-span-2">
          <h2 className="font-semibold">调用趋势</h2>
          <div className="mt-4 h-72 rounded-xl border border-dashed border-white/10 bg-gradient-to-br from-blue-500/20 to-fuchsia-500/10 p-5 text-sm text-slate-300">这里后续接入 Recharts / ECharts 展示 Token、成本和失败率趋势。</div>
        </Card>
        <Card>
          <h2 className="font-semibold">最近错误</h2>
          <ul className="mt-4 space-y-3 text-sm text-slate-300">
            <li>Embedding 超时 · 已重试</li>
            <li>模型供应商限流 · 已降级</li>
            <li>文档解析失败 · 等待处理</li>
          </ul>
        </Card>
      </section>
    </div>
  );
}
