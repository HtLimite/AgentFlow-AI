"use client";

import { useEffect, useState } from "react";
import { apiGet, apiJson, errorMessage } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

type AgentItem = {
  id: number;
  name: string;
  description?: string;
  tools?: string[];
  source?: string;
};

export function AgentConsole() {
  const [agents, setAgents] = useState<AgentItem[]>([]);
  const [selectedAgentId, setSelectedAgentId] = useState<number | null>(null);
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState("请选择 Agent 并输入问题");
  const [running, setRunning] = useState(false);

  async function loadAgents() {
    const data = await apiGet<AgentItem[]>("/api/agents");
    setAgents(data);
    setSelectedAgentId((current) => (current && data.some((item) => item.id === current) ? current : data[0]?.id ?? null));
  }

  useEffect(() => {
    loadAgents().catch((error) => setResult(errorMessage(error, "Agent 列表加载失败")));
  }, []);

  async function run() {
    if (!selectedAgentId) {
      setResult("请先选择 Agent");
      return;
    }
    if (!question.trim()) {
      setResult("请输入问题、SELECT 语句、计算表达式或完整 http/https URL");
      return;
    }
    setRunning(true);
    setResult("运行中...");
    try {
      const data = await apiJson<{ answer: string; tool_calls: unknown[] }>(`/api/agents/${selectedAgentId}/chat`, { question });
      setResult(`${data.answer}\n\n工具调用：\n${JSON.stringify(data.tool_calls, null, 2)}`);
    } catch (error) {
      setResult(errorMessage(error, "Agent 运行失败"));
    } finally {
      setRunning(false);
    }
  }

  const selectedAgent = agents.find((item) => item.id === selectedAgentId);

  return (
    <Card>
      <h2 className="text-xl font-semibold">Agent 工具调用</h2>
      <p className="mt-2 text-sm text-muted-foreground">从后端 Agent 列表读取当前 Agent，不固定 /api/agents/1。工具选择由后端根据输入动态判断。</p>
      <div className="mt-5 grid gap-3 md:grid-cols-[260px_1fr_auto]">
        <select className="rounded-xl border border-border bg-panel/60 px-4 py-3 text-sm" value={selectedAgentId ?? ""} onChange={(event) => setSelectedAgentId(Number(event.target.value))}>
          {agents.length === 0 && <option value="">加载中...</option>}
          {agents.map((agent) => (
            <option key={agent.id} value={agent.id}>{agent.name}</option>
          ))}
        </select>
        <input className="rounded-xl border border-border bg-panel/60 px-4 py-3 text-sm" value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="输入问题、SELECT 查询、计算表达式或完整 URL" />
        <Button onClick={run} disabled={running || !selectedAgentId || !question.trim()}>{running ? "运行中" : "运行 Agent"}</Button>
      </div>
      {selectedAgent && (
        <div className="mt-4 rounded-xl bg-surface/60 p-3 text-xs text-muted-foreground">
          {selectedAgent.description ?? "无描述"} · 工具：{selectedAgent.tools?.join(", ") || "-"} · 来源：{selectedAgent.source ?? "runtime"}
        </div>
      )}
      <pre className="mt-4 whitespace-pre-wrap rounded-xl bg-panel/70 p-4 text-sm text-foreground">{result}</pre>
    </Card>
  );
}
