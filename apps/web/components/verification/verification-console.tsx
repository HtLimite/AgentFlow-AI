"use client";

import { useState } from "react";
import { apiGet } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

interface HealthResult {
  status: string;
  modules: Record<string, boolean>;
  counts: Record<string, number>;
  failed_modules?: string[];
}

const manualChecks = [
  "前端 pnpm dev:web 可启动",
  "后端 uvicorn 可启动",
  "Docker Compose 可构建",
  "Settings 可新增模型供应商",
  "Knowledge 可上传文档并问答",
  "Agent 可展示 tool_calls",
  "Workflow 可展示 node_runs",
  "Eval 可返回 score 与 cases",
];

export function VerificationConsole() {
  const [result, setResult] = useState<HealthResult | null>(null);
  const [error, setError] = useState("");

  async function run() {
    try {
      setError("");
      const health = await apiGet<HealthResult>("/api/system/health/full");
      setResult(health);
      const failedModules = health.failed_modules ?? Object.entries(health.modules)
        .filter(([, ok]) => !ok)
        .map(([key]) => key);
      if (health.status !== "ok" || failedModules.length > 0) {
        throw new Error(`验收失败：${failedModules.join(", ") || health.status}`);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "验收失败");
    }
  }

  return (
    <div className="space-y-4">
      <Card className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-xl font-semibold">项目验收中心</h2>
          <p className="mt-1 text-sm text-slate-400">用于检查所有阶段任务是否具备演示闭环。</p>
        </div>
        <Button onClick={run}>运行系统体检</Button>
      </Card>
      {error && <Card className="border-red-400/40 text-red-200">{error}</Card>}
      {result && (
        <div className="grid gap-4 lg:grid-cols-2">
          <Card>
            <h3 className="font-semibold">模块状态</h3>
            <div className="mt-4 grid gap-2">
              {Object.entries(result.modules).map(([key, ok]) => (
                <div key={key} className="flex items-center justify-between rounded-xl bg-white/10 px-4 py-3 text-sm">
                  <span>{key}</span>
                  <span className={ok ? "text-emerald-300" : "text-red-300"}>{ok ? "通过" : "未通过"}</span>
                </div>
              ))}
            </div>
          </Card>
          <Card>
            <h3 className="font-semibold">模块数量</h3>
            <pre className="mt-4 rounded-xl bg-slate-950/70 p-4 text-sm text-slate-200">{JSON.stringify(result.counts, null, 2)}</pre>
          </Card>
        </div>
      )}
      <Card>
        <h3 className="font-semibold">人工验收项</h3>
        <div className="mt-4 grid gap-2 md:grid-cols-2">
          {manualChecks.map((item) => (
            <div key={item} className="rounded-xl bg-white/10 px-4 py-3 text-sm text-slate-300">□ {item}</div>
          ))}
        </div>
      </Card>
    </div>
  );
}
