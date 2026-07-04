"use client";

import { useEffect, useMemo, useState } from "react";
import { API_BASE_URL, apiGet, errorMessage } from "@/lib/api-client";
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
  const [statusFilter, setStatusFilter] = useState("all");
  const [toolFilter, setToolFilter] = useState("all");
  const [keyword, setKeyword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [offset, setOffset] = useState(0);
  const PAGE_SIZE = 50;

  async function load(targetOffset = offset) {
    setRefreshing(true);
    try {
      setError("");
      const [list, stats] = await Promise.all([
        apiGet<AuditRecord[]>(`/api/audit/tools?limit=${PAGE_SIZE}&offset=${targetOffset}`),
        apiGet<AuditSummary>("/api/audit/tools/summary"),
      ]);
      setRecords(list);
      setSummary(stats);
      setSelectedId((current) => (current && list.some((item) => item.id === current) ? current : list[0]?.id ?? null));
    } catch (err) {
      setError(errorMessage(err, "审计数据加载失败"));
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }

  useEffect(() => {
    void load(0);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function nextPage() {
    const next = offset + PAGE_SIZE;
    setOffset(next);
    void load(next);
  }

  function prevPage() {
    const prev = Math.max(0, offset - PAGE_SIZE);
    setOffset(prev);
    void load(prev);
  }

  function exportCsv() {
    const params = new URLSearchParams();
    if (statusFilter !== "all") params.set("status", statusFilter);
    if (toolFilter !== "all") params.set("tool_name", toolFilter);
    const query = params.toString() ? `?${params.toString()}` : "";
    window.open(`${API_BASE_URL}/api/audit/tools/export${query}`, "_blank");
  }

  const toolOptions = useMemo(() => Array.from(new Set(records.map((item) => item.tool_name))).sort(), [records]);
  const filteredRecords = useMemo(() => {
    const normalizedKeyword = keyword.trim().toLowerCase();
    return records.filter((item) => {
      if (statusFilter !== "all" && item.status !== statusFilter) return false;
      if (toolFilter !== "all" && item.tool_name !== toolFilter) return false;
      if (!normalizedKeyword) return true;
      return [
        item.trace_id,
        item.tool_name,
        item.status,
        item.error_message ?? "",
        JSON.stringify(item.input),
        JSON.stringify(item.output),
      ].join(" ").toLowerCase().includes(normalizedKeyword);
    });
  }, [records, statusFilter, toolFilter, keyword]);

  // Keep selectedId in sync with the filtered list: if the current selection
  // is hidden by the active filter, fall back to the first visible record.
  useEffect(() => {
    if (filteredRecords.length === 0) return;
    const stillVisible = filteredRecords.some((item) => item.id === selectedId);
    if (!stillVisible) {
      setSelectedId(filteredRecords[0].id);
    }
  }, [filteredRecords, selectedId]);

  const selected = records.find((item) => item.id === selectedId) ?? null;
  const dash = "--";

  return (
    <div className="space-y-4">
      <Card className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-xl font-semibold">工具调用审计</h2>
          <p className="mt-1 text-sm text-slate-400">追踪 Agent 每次工具调用的输入、输出、状态、耗时和 trace_id，支持筛选定位异常。</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button onClick={() => load(offset)} disabled={refreshing}>{refreshing ? "刷新中..." : "刷新审计"}</Button>
          <Button onClick={exportCsv} variant="secondary">导出 CSV</Button>
        </div>
      </Card>

      {error && <Card className="border-red-400/40 text-red-200">{error}</Card>}

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <div className="text-sm text-slate-400">调用总数</div>
          <div className="mt-2 text-2xl font-bold">{loading ? dash : summary?.total_calls ?? 0}</div>
        </Card>
        <Card>
          <div className="text-sm text-slate-400">成功率</div>
          <div className="mt-2 text-2xl font-bold">
            {loading ? dash : `${Math.round((summary?.success_rate ?? 0) * 100)}%`}
          </div>
        </Card>
        <Card>
          <div className="text-sm text-slate-400">失败数</div>
          <div className="mt-2 text-2xl font-bold">{loading ? dash : summary?.failed_calls ?? 0}</div>
        </Card>
        <Card>
          <div className="text-sm text-slate-400">平均耗时</div>
          <div className="mt-2 text-2xl font-bold">{loading ? dash : `${summary?.avg_latency_ms ?? 0}ms`}</div>
        </Card>
      </div>

      <Card>
        <div className="grid gap-3 md:grid-cols-3">
          <label className="block text-sm text-slate-300">
            <span className="mb-1 block text-xs text-slate-500">状态</span>
            <select className="w-full rounded-xl border border-white/10 bg-slate-950/60 px-4 py-3" value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>
              <option value="all">全部状态</option>
              <option value="success">success</option>
              <option value="failed">failed</option>
            </select>
          </label>
          <label className="block text-sm text-slate-300">
            <span className="mb-1 block text-xs text-slate-500">工具</span>
            <select className="w-full rounded-xl border border-white/10 bg-slate-950/60 px-4 py-3" value={toolFilter} onChange={(event) => setToolFilter(event.target.value)}>
              <option value="all">全部工具</option>
              {toolOptions.map((tool) => (
                <option key={tool} value={tool}>{tool}</option>
              ))}
            </select>
          </label>
          <label className="block text-sm text-slate-300">
            <span className="mb-1 block text-xs text-slate-500">关键字 / trace_id</span>
            <input className="w-full rounded-xl border border-white/10 bg-slate-950/60 px-4 py-3" value={keyword} onChange={(event) => setKeyword(event.target.value)} placeholder="搜索 trace、工具、输入、输出" />
          </label>
        </div>
      </Card>

      <div className="grid gap-4 xl:grid-cols-[420px_1fr]">
        <Card>
          <h3 className="font-semibold">调用记录 · {filteredRecords.length}/{records.length}</h3>
          <div className="mt-4 space-y-2">
            {loading ? (
              <div className="rounded-xl bg-white/5 p-4 text-sm text-slate-400">加载中...</div>
            ) : filteredRecords.length === 0 ? (
              <div className="rounded-xl bg-white/5 p-4 text-sm text-slate-400">当前筛选条件下暂无记录。</div>
            ) : (
              filteredRecords.map((item) => (
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
              ))
            )}
          </div>
          <div className="mt-4 flex items-center justify-between text-xs text-slate-400">
            <span>第 {offset + 1} - {offset + records.length} 条</span>
            <div className="flex gap-2">
              <Button size="sm" variant="secondary" onClick={prevPage} disabled={refreshing || offset === 0}>上一页</Button>
              <Button size="sm" variant="secondary" onClick={nextPage} disabled={refreshing || records.length < PAGE_SIZE}>下一页</Button>
            </div>
          </div>
        </Card>

        <Card>
          <h3 className="font-semibold">审计详情</h3>
          <pre className="mt-4 max-h-[620px] overflow-auto whitespace-pre-wrap rounded-xl bg-slate-950/70 p-4 text-sm text-slate-200">
            {selected ? JSON.stringify(selected, null, 2) : "{\n  \"message\": \"暂无审计记录\"\n}"}
          </pre>
        </Card>
      </div>
    </div>
  );
}
