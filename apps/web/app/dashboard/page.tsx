import { Card } from "@/components/ui/card";
import { apiGet } from "@/lib/api-client";

type DashboardSummary = {
  calls_today: number;
  tokens_today: number;
  cost_today: number;
  avg_latency_ms: number;
  failure_rate: number;
  knowledge_bases?: number;
  agents?: number;
  workflow_runs?: number;
  source?: string;
};

type LlmLog = {
  id: number;
  provider: string | null;
  model: string | null;
  scenario: string | null;
  status: string | null;
  error_message: string | null;
  latency_ms: number | null;
  total_tokens: number | null;
  created_at: string | null;
};

function formatTokens(value: number) {
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(2)}M`;
  if (value >= 1_000) return `${(value / 1_000).toFixed(1)}K`;
  return String(value);
}

function formatLatency(value: number) {
  if (!value) return "0ms";
  if (value >= 1000) return `${(value / 1000).toFixed(2)}s`;
  return `${Math.round(value)}ms`;
}

function formatFailureRate(value: number) {
  return `${(value * 100).toFixed(2)}%`;
}

async function getDashboardData() {
  try {
    const [summary, logs] = await Promise.all([
      apiGet<DashboardSummary>("/api/dashboard/summary"),
      apiGet<LlmLog[]>("/api/dashboard/llm-logs"),
    ]);
    return { summary, logs, error: "" };
  } catch (error) {
    return {
      summary: {
        calls_today: 0,
        tokens_today: 0,
        cost_today: 0,
        avg_latency_ms: 0,
        failure_rate: 0,
        knowledge_bases: 0,
        agents: 0,
        workflow_runs: 0,
        source: "unavailable",
      },
      logs: [],
      error: error instanceof Error ? error.message : "Dashboard 数据加载失败",
    };
  }
}

export default async function DashboardPage() {
  const { summary, logs, error } = await getDashboardData();
  const metrics = [
    { label: "今日调用", value: String(summary.calls_today), hint: "来自 llm_call_log" },
    { label: "Token 消耗", value: formatTokens(summary.tokens_today), hint: "真实累计 token" },
    { label: "平均耗时", value: formatLatency(summary.avg_latency_ms), hint: "真实平均 latency" },
    { label: "失败率", value: formatFailureRate(summary.failure_rate), hint: "status != success" },
  ];
  const failedLogs = logs.filter((item) => item.status && item.status !== "success").slice(0, 5);

  return (
    <div className="space-y-6">
      {error && <Card className="border-red-400/40 text-danger-foreground">{error}</Card>}
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {metrics.map((item) => (
          <Card key={item.label}>
            <div className="text-sm text-muted-foreground">{item.label}</div>
            <div className="mt-3 text-3xl font-bold">{item.value}</div>
            <div className="mt-2 text-xs text-muted-foreground/70">{item.hint}</div>
          </Card>
        ))}
      </section>
      <section className="grid gap-4 xl:grid-cols-3">
        <Card className="xl:col-span-2">
          <h2 className="font-semibold">调用明细</h2>
          <div className="mt-4 overflow-hidden rounded-xl border border-border">
            <table className="w-full text-left text-sm">
              <thead className="bg-surface/60 text-muted-foreground">
                <tr>
                  <th className="p-3">场景</th>
                  <th className="p-3">模型</th>
                  <th className="p-3">Token</th>
                  <th className="p-3">耗时</th>
                  <th className="p-3">状态</th>
                </tr>
              </thead>
              <tbody>
                {logs.length === 0 ? (
                  <tr>
                    <td className="p-4 text-muted-foreground" colSpan={5}>暂无真实调用记录。先在 Chat / RAG / Agent 页面运行一次，再回到 Dashboard。</td>
                  </tr>
                ) : (
                  logs.slice(0, 8).map((item) => (
                    <tr key={item.id} className="border-t border-border">
                      <td className="p-3">{item.scenario ?? "-"}</td>
                      <td className="p-3">{item.model ?? "-"}</td>
                      <td className="p-3">{item.total_tokens ?? 0}</td>
                      <td className="p-3">{formatLatency(item.latency_ms ?? 0)}</td>
                      <td className="p-3">{item.status ?? "unknown"}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </Card>
        <Card>
          <h2 className="font-semibold">最近错误</h2>
          <ul className="mt-4 space-y-3 text-sm text-muted-foreground">
            {failedLogs.length === 0 ? (
              <li className="text-muted-foreground">暂无失败调用。</li>
            ) : (
              failedLogs.map((item) => (
                <li key={item.id}>{item.scenario ?? "unknown"} · {item.error_message ?? item.status}</li>
              ))
            )}
          </ul>
          <div className="mt-6 rounded-xl bg-surface/30 p-4 text-xs text-muted-foreground">
            数据源：{summary.source ?? "database"}。不再显示固定演示数字。
          </div>
        </Card>
      </section>
    </div>
  );
}
