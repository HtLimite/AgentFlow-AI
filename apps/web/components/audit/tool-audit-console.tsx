"use client";

import { useEffect, useState } from "react";
import { apiGet } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

interface AuditRecord {
  id: number;
  trace_id: string;
  agent_id: number | null;
  tool_name: string;
  input: unknown;
  output: unknown;
  status: string;
  latency_ms: number;
  error_message: string | null;
  created_at: string;
}

interface AuditSummary {
  total_calls: number;
  failed_calls: number;
  success_rate: number;
  avg_latency_ms: number;
  tool_counts: Record<string, number>;
}

export function ToolAuditConsole() {
  const [records, setRecords] = useState<AuditRecord[]>([]);
  const [summary, setSummary] = useState<AuditSummary | null>(null);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [error, setError] = useState("");

  async function load() {
    try {
      setError("");
      const [list, stats] = await Promise.all([
        apiGet<AuditRecord[]>("/api/audit/tools"),
        apiGet<AuditSummary>("/api/audit/tools/summary"),
      ]);
      setRecords(list);
      setSummary(stats);
      setSelectedId(list[0]?.id ?? null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "审计数据加载失败");
    }
  }

  useEffect(() => {
    void load();
  }, []);

  const selected = records.find((item) => item.id === selectedId) ?? records[0];

  return (
    <div className="space-y-4">
      <Card className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-xl font-semibold">V3 工具调用审计</h2>
          <p className="mt-1 text-sm text-slate-400">追踪 Agent 每次工具调用的输入、输出、状态、耗时和 trace_id。</p>
        </div>
        <Button onClick={load}>刷新审计</Button>
      </Card>

      {error && <Card className="border-red-400/40 text-red-200">{error}</Card>}

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <div className="text-sm text-slate-400">调用总数</div>
          <div className="mt-2 text-2xl font-bold">{summary?.total_calls ?? 0}</div>
        </Card>
        <Card>
          <div className="text-sm text-slate-400">成功率</div>
          <div className="mt-2 text-2xl font-bold">{Math.round((summary?.success_rate ?? 1) * 100)}%</div>
        </Card>
        <Card>
          <div className="text-sm text-slate-400">失败数</div>
          <div className="mt-2 text-2xl font-bold">{summary?.failed_calls ?? 0}</div>
        </Card>
        <Card>
          <div className="text-sm text-slate-400">平均耗时</div>
          <div className="mt-2 text-2xl font-bold">{summary?.avg_latency_ms ?? 0}ms</div>
        </Card>
      </div>

      <div className="grid gap-4 xl:grid-cols-[420px_1fr]">
        <Card>
          <h3 className="font-semibold">调用记录</h3>
          <div className="mt-4 space-y-2">
            {records.map((item) => (
              <button
                key={item.id}
                onClick={() => setSelectedId(item.id)}
                className={`w-full rounded-xl border p-4 text-left text-sm transition ${selected?.id === item.id ? "border-blue-300 bg-blue-500/10" : "border-white/10 bg-white/5 hover:border-white/20"}`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium">#{item.id} · {item.tool_name}</span>
                  <span className={item.status === "success" ? "text-emerald-300" : "text-red-300"}>{item.status}</span>
                </div>
                <div className="mt-2 text-xs text-slate-400">trace: {item.trace_id}</div>
                <div className="mt-1 text-xs text-slate-500">{item.latency_ms}ms · {item.created_at}</div>
              </button>
            ))}
          </div>
        </Card>

        <Card>
          <h3 className="font-semibold">审计详情</h3>
          <pre className="mt-4 max-h-[620px] overflow-auto whitespace-pre-wrap rounded-xl bg-slate-950/70 p-4 text-sm text-slate-200">
            {JSON.stringify(selected ?? { message: "暂无审计记录" }, null, 2)}
          </pre>
        </Card>
      </div>
    </div>
  );
}
