"use client";

import { useState } from "react";
import { apiJson } from "@/lib/api-client";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const demoLogs = `Bind for 0.0.0.0:80 failed: port is already allocated
psycopg.OperationalError: connection refused
container agentflow-api exited (1)`;

const demoFiles = `deploy/docker-compose.yml
services:
  postgres:
    image: pgvector/pgvector:pg16
  redis:
    image: redis:7-alpine`;

const demoServices = `agentflow-postgres running healthy
agentflow-api exited connection refused`;

type Signal = {
  id: string;
  category: string;
  title: string;
  severity: "critical" | "warning" | "info" | "ok";
  detail: string;
  evidence: string;
};

type Action = {
  title: string;
  reason: string;
  steps: string[];
  command: string;
  risk: string;
};

type Artifact = {
  name: string;
  language: string;
  content: string;
};

type DiagnosisSource = "manual_input" | "demo_sample";

type DiagnosisResult = {
  project_name: string;
  runtime: string;
  source: DiagnosisSource;
  summary: string;
  readiness_score: number;
  severity: "critical" | "warning" | "ok";
  signals: Signal[];
  likely_causes: string[];
  actions: Action[];
  artifacts: Artifact[];
  next_verification: string[];
  mode: string;
};

function severityVariant(severity: Signal["severity"] | DiagnosisResult["severity"]) {
  if (severity === "critical") return "danger";
  if (severity === "warning") return "warning";
  if (severity === "info") return "info";
  return "success";
}

function splitFileInput(value: string) {
  const [firstLine, ...rest] = value.split(/\r?\n/);
  const path = firstLine?.trim() || "diagnosis-notes.txt";
  const content = rest.join("\n").trim();
  if (!content) return [];
  return [{ path, content }];
}

function parseServiceInput(value: string) {
  return value
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => {
      const [name = "", status = "", ...detail] = line.split(/\s+/);
      return { name, status, detail: detail.join(" ") };
    })
    .filter((item) => item.name || item.status || item.detail);
}

export function ProjectDiagnosisConsole() {
  const [projectName, setProjectName] = useState("AgentFlow-AI");
  const [runtime, setRuntime] = useState("Windows 本地 uv + Docker PostgreSQL / Redis / MinIO");
  const [logs, setLogs] = useState("");
  const [fileInput, setFileInput] = useState("");
  const [serviceInput, setServiceInput] = useState("");
  const [source, setSource] = useState<DiagnosisSource>("manual_input");
  const [result, setResult] = useState<DiagnosisResult | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function loadDemo() {
    setLogs(demoLogs);
    setFileInput(demoFiles);
    setServiceInput(demoServices);
    setSource("demo_sample");
    setResult(null);
    setError("");
  }

  function clearInput() {
    setLogs("");
    setFileInput("");
    setServiceInput("");
    setSource("manual_input");
    setResult(null);
    setError("");
  }

  async function analyze() {
    setLoading(true);
    setError("");
    try {
      const response = await apiJson<DiagnosisResult>("/api/project-diagnosis/analyze", {
        project_name: projectName,
        runtime,
        source,
        logs,
        files: splitFileInput(fileInput),
        services: parseServiceInput(serviceInput),
      });
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "项目诊断失败");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-5">
      <Card className="overflow-hidden">
        <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
          <div>
            <Badge variant="info">Project Diagnosis</Badge>
            <h2 className="mt-4 text-3xl font-bold tracking-tight text-foreground">项目诊断与部署排错助手</h2>
            <p className="mt-3 max-w-3xl text-sm leading-7 text-muted-foreground">
              当前是手动诊断工具，不会自动读取你的本机 Docker、GitHub 或服务器日志。请粘贴真实日志、服务状态和关键配置片段后再分析。
            </p>
          </div>
          <div className="rounded-2xl border border-warning/30 bg-warning-soft p-4">
            <div className="text-sm font-semibold text-warning-foreground">避免误判</div>
            <p className="mt-2 text-sm leading-6 text-warning-foreground/80">
              页面默认不再填入故障样例；“加载演示样例”只用于展示功能效果，结果会标记为 demo_sample。
            </p>
          </div>
        </div>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>诊断输入</CardTitle>
          <CardDescription>先粘贴真实输出。不要只输入“后端启动报错 / Nginx 502 报错 / 数据库连接失败日志”这类占位说明。</CardDescription>
        </CardHeader>

        <div className="grid gap-4 lg:grid-cols-2">
          <label className="block text-sm text-muted-foreground">
            <span className="mb-1 block">项目名称</span>
            <input className="w-full rounded-xl border border-border bg-panel px-4 py-3 text-foreground outline-none focus:border-primary/50" value={projectName} onChange={(event) => setProjectName(event.target.value)} />
          </label>
          <label className="block text-sm text-muted-foreground">
            <span className="mb-1 block">运行环境</span>
            <input className="w-full rounded-xl border border-border bg-panel px-4 py-3 text-foreground outline-none focus:border-primary/50" value={runtime} onChange={(event) => setRuntime(event.target.value)} />
          </label>
        </div>

        <div className="mt-4 grid gap-4 xl:grid-cols-[1.15fr_0.85fr]">
          <label className="block text-sm text-muted-foreground">
            <span className="mb-1 block">错误日志 / docker ps / 启动输出</span>
            <textarea
              className="min-h-60 w-full rounded-xl border border-border bg-panel px-4 py-3 font-mono text-sm text-foreground outline-none focus:border-primary/50"
              value={logs}
              onChange={(event) => { setLogs(event.target.value); setSource("manual_input"); }}
              placeholder="粘贴真实日志，例如：端口占用、connection refused、build failed、container exited..."
            />
          </label>

          <div className="space-y-4">
            <label className="block text-sm text-muted-foreground">
              <span className="mb-1 block">服务状态，每行：name status detail</span>
              <textarea
                className="min-h-28 w-full rounded-xl border border-border bg-panel px-4 py-3 font-mono text-sm text-foreground outline-none focus:border-primary/50"
                value={serviceInput}
                onChange={(event) => { setServiceInput(event.target.value); setSource("manual_input"); }}
                placeholder="agentflow-postgres running healthy"
              />
            </label>
            <label className="block text-sm text-muted-foreground">
              <span className="mb-1 block">关键文件片段，第一行写路径</span>
              <textarea
                className="min-h-28 w-full rounded-xl border border-border bg-panel px-4 py-3 font-mono text-sm text-foreground outline-none focus:border-primary/50"
                value={fileInput}
                onChange={(event) => { setFileInput(event.target.value); setSource("manual_input"); }}
                placeholder="deploy/docker-compose.yml&#10;services: ..."
              />
            </label>
          </div>
        </div>

        <div className="mt-4 flex flex-wrap items-center gap-3">
          <Button onClick={analyze} disabled={loading}>{loading ? "分析中..." : "开始诊断"}</Button>
          <Button variant="outline" onClick={loadDemo}>加载演示样例</Button>
          <Button variant="ghost" onClick={clearInput}>清空输入</Button>
          <Badge variant={source === "demo_sample" ? "warning" : "info"}>source: {source}</Badge>
        </div>
        {error ? <div className="mt-4 rounded-xl border border-danger/30 bg-danger-soft p-3 text-sm text-danger-foreground">{error}</div> : null}
      </Card>

      {result ? (
        <section className="space-y-5">
          <Card>
            <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
              <div className="min-w-0">
                <div className="flex flex-wrap gap-2">
                  <Badge variant={severityVariant(result.severity)}>{result.severity}</Badge>
                  <Badge variant={result.source === "demo_sample" ? "warning" : "info"}>source: {result.source}</Badge>
                </div>
                <h3 className="mt-3 text-xl font-semibold leading-8 text-foreground">{result.summary}</h3>
                <p className="mt-2 text-sm text-muted-foreground">mode: {result.mode}</p>
              </div>
              <div className="shrink-0 rounded-2xl border border-border bg-panel/70 px-6 py-4 text-center">
                <div className="text-3xl font-bold text-foreground">{result.readiness_score}</div>
                <div className="text-xs text-muted-foreground">可用度评分</div>
              </div>
            </div>
          </Card>

          <div className="grid gap-5 xl:grid-cols-[1fr_1fr]">
            <Card>
              <CardHeader>
                <CardTitle>发现的问题</CardTitle>
                <CardDescription>按阻塞程度识别日志、配置和服务状态中的异常信号。</CardDescription>
              </CardHeader>
              <div className="space-y-3">
                {result.signals.map((item) => (
                  <div key={`${item.id}-${item.title}`} className="rounded-xl border border-border bg-panel/50 p-4">
                    <div className="flex flex-wrap items-center gap-2">
                      <Badge variant={severityVariant(item.severity)}>{item.severity}</Badge>
                      <span className="font-medium text-foreground">{item.title}</span>
                      <span className="text-xs text-muted-foreground">{item.category}</span>
                    </div>
                    <p className="mt-2 text-sm leading-6 text-muted-foreground">{item.detail}</p>
                    <pre className="mt-3 max-h-40 overflow-auto whitespace-pre-wrap break-words rounded-lg bg-background/60 p-3 text-xs text-muted-foreground">{item.evidence}</pre>
                  </div>
                ))}
              </div>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>优先修复动作</CardTitle>
                <CardDescription>按本次错误模式给出的下一步命令。</CardDescription>
              </CardHeader>
              <div className="space-y-4">
                {result.actions.map((item) => (
                  <div key={item.title} className="rounded-xl border border-border bg-panel/50 p-4">
                    <div className="font-semibold text-foreground">{item.title}</div>
                    <p className="mt-1 text-sm text-muted-foreground">{item.reason}</p>
                    <ol className="mt-3 list-decimal space-y-1 pl-5 text-sm text-muted-foreground">
                      {item.steps.map((step) => <li key={step}>{step}</li>)}
                    </ol>
                    <pre className="mt-3 overflow-x-auto rounded-lg bg-background/60 p-3 text-xs text-foreground">{item.command}</pre>
                  </div>
                ))}
              </div>
            </Card>
          </div>

          <div className="grid gap-5 xl:grid-cols-[0.8fr_1.2fr]">
            <Card>
              <CardHeader>
                <CardTitle>验收命令</CardTitle>
                <CardDescription>修复后按这些命令确认项目真的变得可用。</CardDescription>
              </CardHeader>
              <div className="space-y-2">
                {result.next_verification.map((command) => (
                  <pre key={command} className="overflow-x-auto rounded-lg bg-background/60 p-3 text-xs text-foreground">{command}</pre>
                ))}
              </div>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>生成的诊断产物</CardTitle>
                <CardDescription>可复制到部署记录或 issue 里。</CardDescription>
              </CardHeader>
              <div className="space-y-3">
                {result.artifacts.map((artifact) => (
                  <details key={artifact.name} className="rounded-xl border border-border bg-panel/50 p-4">
                    <summary className="cursor-pointer text-sm font-semibold text-foreground">{artifact.name}</summary>
                    <pre className="mt-3 max-h-80 overflow-auto whitespace-pre-wrap break-words rounded-lg bg-background/60 p-3 text-xs text-muted-foreground">{artifact.content}</pre>
                  </details>
                ))}
              </div>
            </Card>
          </div>
        </section>
      ) : (
        <Card className="flex min-h-64 items-center justify-center text-center">
          <div>
            <div className="text-lg font-semibold text-foreground">等待诊断</div>
            <p className="mt-2 max-w-xl text-sm leading-6 text-muted-foreground">粘贴真实日志后点击“开始诊断”。想看效果时再点“加载演示样例”。</p>
          </div>
        </Card>
      )}
    </div>
  );
}
