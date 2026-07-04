"use client";

import { useEffect, useState } from "react";
import { apiGet, errorMessage } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

interface HealthResult {
  status: string;
  modules: Record<string, boolean>;
  counts: Record<string, number>;
  failed_modules?: string[];
}

interface ManualCheck {
  label: string;
  checked: boolean;
}

const DEFAULT_MANUAL_CHECKS: ManualCheck[] = [
  { label: "前端 pnpm dev:web 可启动", checked: false },
  { label: "后端 uvicorn 可启动", checked: false },
  { label: "Docker Compose 可构建", checked: false },
  { label: "Settings 可新增模型供应商", checked: false },
  { label: "Knowledge 可上传文档并问答", checked: false },
  { label: "Agent 可展示 tool_calls", checked: false },
  { label: "Workflow 可展示 node_runs", checked: false },
  { label: "Eval 可返回 score 与 cases", checked: false },
];

const STORAGE_KEY = "agentflow:verification:manual-checks";

export function VerificationConsole() {
  const [result, setResult] = useState<HealthResult | null>(null);
  const [error, setError] = useState("");
  const [running, setRunning] = useState(false);
  const [checks, setChecks] = useState<ManualCheck[]>(DEFAULT_MANUAL_CHECKS);

  // Restore manual check state from localStorage so progress persists across reloads.
  useEffect(() => {
    try {
      const raw = window.localStorage.getItem(STORAGE_KEY);
      if (!raw) return;
      const saved = JSON.parse(raw) as { label: string; checked: boolean }[];
      setChecks((current) =>
        current.map((item) => {
          const match = saved.find((s) => s.label === item.label);
          return match ? { ...item, checked: match.checked } : item;
        }),
      );
    } catch {
      // ignore corrupt storage
    }
  }, []);

  function toggleCheck(label: string) {
    setChecks((current) => {
      const next = current.map((item) => (item.label === label ? { ...item, checked: !item.checked } : item));
      try {
        window.localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
      } catch {
        // storage may be unavailable (private mode); keep in-memory state.
      }
      return next;
    });
  }

  async function run() {
    setRunning(true);
    setError("");
    try {
      const health = await apiGet<HealthResult>("/api/system/health/full");
      const failedModules = health.failed_modules ?? Object.entries(health.modules)
        .filter(([, ok]) => !ok)
        .map(([key]) => key);
      if (health.status !== "ok" || failedModules.length > 0) {
        // Only set the error card; do NOT render the partial module grid (avoids double-render).
        setResult(null);
        setError(`验收失败：${failedModules.length > 0 ? failedModules.join(", ") : health.status}`);
        return;
      }
      setResult(health);
    } catch (err) {
      setResult(null);
      setError(errorMessage(err, "验收失败"));
    } finally {
      setRunning(false);
    }
  }

  const checkedCount = checks.filter((item) => item.checked).length;

  return (
    <div className="space-y-4">
      <Card className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-xl font-semibold">项目验收中心</h2>
          <p className="mt-1 text-sm text-muted-foreground">用于检查所有阶段任务是否具备演示闭环。</p>
        </div>
        <Button onClick={run} disabled={running}>{running ? "体检中..." : "运行系统体检"}</Button>
      </Card>
      {error && <Card className="border-red-400/40 text-danger-foreground">{error}</Card>}
      {result && (
        <div className="grid gap-4 lg:grid-cols-2">
          <Card>
            <h3 className="font-semibold">模块状态</h3>
            <div className="mt-4 grid gap-2">
              {Object.entries(result.modules).map(([key, ok]) => (
                <div key={key} className="flex items-center justify-between rounded-xl bg-surface/60 px-4 py-3 text-sm">
                  <span>{key}</span>
                  <span className={ok ? "text-emerald-300" : "text-danger-foreground"}>{ok ? "通过" : "未通过"}</span>
                </div>
              ))}
            </div>
          </Card>
          <Card>
            <h3 className="font-semibold">模块数量</h3>
            <pre className="mt-4 rounded-xl bg-panel/70 p-4 text-sm text-foreground">{JSON.stringify(result.counts, null, 2)}</pre>
          </Card>
        </div>
      )}
      <Card>
        <div className="flex items-center justify-between">
          <h3 className="font-semibold">人工验收项</h3>
          <span className="text-xs text-muted-foreground">已勾选 {checkedCount}/{checks.length}</span>
        </div>
        <div className="mt-4 grid gap-2 md:grid-cols-2">
          {checks.map((item) => (
            <label key={item.label} className="flex cursor-pointer items-center gap-3 rounded-xl bg-surface/60 px-4 py-3 text-sm text-muted-foreground transition hover:bg-surface-strong">
              <input
                type="checkbox"
                checked={item.checked}
                onChange={() => toggleCheck(item.label)}
                className="h-4 w-4 accent-emerald-400"
              />
              <span className={item.checked ? "line-through text-muted-foreground/70" : ""}>{item.label}</span>
            </label>
          ))}
        </div>
      </Card>
    </div>
  );
}
