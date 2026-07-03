"use client";

import { useEffect, useState } from "react";
import { API_BASE_URL, apiGet, apiJson } from "@/lib/api-client";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

interface KnowledgeBaseItem {
  id: number;
  name: string;
  document_count: number;
  chunk_count: number;
  status: string;
}

interface KnowledgeDocumentItem {
  id: number;
  kb_id: number;
  filename: string;
  parse_status: string;
  chunk_count: number;
}

interface CitationItem {
  document: string;
  content: string;
  score: number;
  lexical_score?: number;
  vector_score?: number;
  rerank_score?: number;
  strategy?: string;
}

interface EvidenceItem extends CitationItem {
  index: number;
}

interface KnowledgeAnswer {
  answer: string;
  summary?: string;
  evidence?: EvidenceItem[];
  citations: CitationItem[];
  debug?: {
    kb_id?: number;
    top_k?: number;
    strategy?: string;
    rerank?: boolean;
    min_relevance_score?: number;
  };
}

function formatScore(value?: number) {
  if (typeof value !== "number" || Number.isNaN(value)) return "-";
  return value.toFixed(3).replace(/0+$/, "").replace(/\.$/, "");
}

function compactText(value: string, maxLength = 420) {
  const text = value.trim();
  return text.length > maxLength ? `${text.slice(0, maxLength).trim()}…` : text;
}

export function KnowledgeConsole() {
  const [items, setItems] = useState<KnowledgeBaseItem[]>([]);
  const [documents, setDocuments] = useState<KnowledgeDocumentItem[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [question, setQuestion] = useState("");
  const [statusMessage, setStatusMessage] = useState("请选择知识库并上传真实文档后再查询");
  const [result, setResult] = useState<KnowledgeAnswer | null>(null);
  const [uploading, setUploading] = useState(false);
  const [querying, setQuerying] = useState(false);
  const [removingId, setRemovingId] = useState<number | null>(null);
  const [newBaseName, setNewBaseName] = useState("");

  async function loadBases(preferredId = selectedId) {
    const data = await apiGet<KnowledgeBaseItem[]>("/api/knowledge-bases");
    setItems(data);
    const nextSelected = data.some((item) => item.id === preferredId) ? preferredId : data[0]?.id ?? null;
    setSelectedId(nextSelected);
    return nextSelected;
  }

  async function loadDocuments(kbId = selectedId) {
    if (!kbId) {
      setDocuments([]);
      return;
    }
    const data = await apiGet<KnowledgeDocumentItem[]>(`/api/knowledge-bases/${kbId}/documents`);
    setDocuments(data);
  }

  async function reload(preferredId = selectedId) {
    const nextSelected = await loadBases(preferredId);
    await loadDocuments(nextSelected);
  }

  useEffect(() => {
    reload().catch((error) => setStatusMessage(error.message));
  }, []);

  useEffect(() => {
    loadDocuments(selectedId).catch((error) => setStatusMessage(error.message));
  }, [selectedId]);

  async function createBase() {
    const name = newBaseName.trim();
    if (!name) {
      setStatusMessage("请先填写知识库名称");
      return;
    }
    const created = await apiJson<KnowledgeBaseItem>("/api/knowledge-bases", { name });
    setNewBaseName("");
    await reload(created.id);
    setResult(null);
    setStatusMessage(`已创建知识库：${created.name}`);
  }

  async function query() {
    if (!selectedId) {
      setStatusMessage("请先创建或选择知识库");
      return;
    }
    if (!question.trim()) {
      setStatusMessage("请输入要查询的问题");
      return;
    }
    setQuerying(true);
    setStatusMessage("正在检索知识库...");
    try {
      const data = await apiJson<KnowledgeAnswer>(`/api/knowledge-bases/${selectedId}/query`, { question, top_k: 5 });
      setResult(data);
      setStatusMessage(data.citations.length ? "已基于知识库生成回答" : "未找到直接相关的知识库片段");
    } catch (error) {
      setResult(null);
      setStatusMessage(error instanceof Error ? error.message : "知识库查询失败");
    } finally {
      setQuerying(false);
    }
  }

  async function upload(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    if (!selectedId) {
      setStatusMessage("请先创建或选择知识库");
      event.target.value = "";
      return;
    }
    setUploading(true);
    setResult(null);
    setStatusMessage(`正在解析文档：${file.name}`);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const response = await fetch(`${API_BASE_URL}/api/knowledge-bases/${selectedId}/documents`, { method: "POST", body: formData });
      if (!response.ok) {
        const errorBody = await response.json().catch(() => null);
        throw new Error(errorBody?.detail || "上传失败，请检查文档格式");
      }
      await reload(selectedId);
      setStatusMessage(`文档已解析并切片：${file.name}`);
    } catch (error) {
      setStatusMessage(error instanceof Error ? error.message : "上传失败，请检查文档格式");
    } finally {
      setUploading(false);
      event.target.value = "";
    }
  }

  async function removeDocument(documentId: number) {
    if (!selectedId) return;
    setRemovingId(documentId);
    try {
      const response = await fetch(`${API_BASE_URL}/api/knowledge-bases/${selectedId}/documents/${documentId}/remove`, { method: "POST" });
      if (!response.ok) {
        const errorBody = await response.json().catch(() => null);
        throw new Error(errorBody?.detail || "删除失败");
      }
      await reload(selectedId);
      setResult(null);
      setStatusMessage(`已删除文档 #${documentId}。该文档已从知识库列表和后续检索中移除。`);
    } catch (error) {
      setStatusMessage(error instanceof Error ? error.message : "删除失败");
    } finally {
      setRemovingId(null);
    }
  }

  const evidence = result?.evidence?.length ? result.evidence : result?.citations.map((item, index) => ({ ...item, index: index + 1 })) ?? [];

  return (
    <div className="space-y-4">
      <Card className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-xl font-semibold">知识库 RAG · 持久化检索</h2>
          <p className="mt-1 text-sm text-slate-400">从接口读取知识库列表，不固定知识库 ID。请选择或创建知识库后上传真实文档。</p>
        </div>
        <label className="rounded-xl border border-white/10 bg-white/10 px-4 py-3 text-sm text-slate-200 hover:bg-white/15">
          {uploading ? "解析中..." : "上传文档"}
          <input type="file" accept=".txt,.md,.markdown,.pdf,text/plain,text/markdown,application/pdf" onChange={upload} className="hidden" disabled={uploading || !selectedId} />
        </label>
      </Card>

      <Card>
        <div className="flex flex-col gap-3 md:flex-row">
          <input className="flex-1 rounded-xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm" value={newBaseName} onChange={(event) => setNewBaseName(event.target.value)} placeholder="新知识库名称" />
          <Button onClick={createBase}>创建知识库</Button>
          <Button onClick={() => void reload(selectedId)}>刷新</Button>
        </div>
      </Card>

      <div className="grid gap-4 lg:grid-cols-3">
        {items.length === 0 ? (
          <Card className="text-sm text-slate-400">暂无知识库，请先创建。</Card>
        ) : (
          items.map((row) => (
            <button key={row.id} onClick={() => setSelectedId(row.id)} className="text-left">
              <Card className={selectedId === row.id ? "border-blue-400/60" : ""}>
                <div className="flex items-center justify-between">
                  <h3 className="font-semibold">{row.name}</h3>
                  <Badge>{row.status}</Badge>
                </div>
                <div className="mt-4 grid grid-cols-2 gap-3 text-sm text-slate-300">
                  <div className="rounded-xl bg-white/10 p-3">文档 {row.document_count}</div>
                  <div className="rounded-xl bg-white/10 p-3">切片 {row.chunk_count}</div>
                </div>
              </Card>
            </button>
          ))
        )}
      </div>

      <Card>
        <div className="flex items-center justify-between gap-3">
          <div>
            <h3 className="font-semibold">文档列表</h3>
            <p className="mt-1 text-xs text-slate-500">当前知识库：{selectedId ?? "未选择"}</p>
          </div>
          <Button onClick={() => void reload(selectedId)} disabled={!selectedId}>刷新</Button>
        </div>
        <div className="mt-4 space-y-2">
          {documents.length === 0 ? (
            <div className="rounded-xl border border-dashed border-white/10 p-4 text-sm text-slate-400">暂无文档，请先上传。</div>
          ) : (
            documents.map((document) => (
              <div key={document.id} className="flex flex-col gap-3 rounded-xl bg-white/10 p-4 text-sm md:flex-row md:items-center md:justify-between">
                <div>
                  <div className="font-medium">{document.filename}</div>
                  <div className="mt-1 text-slate-400">#{document.id} · {document.parse_status} · 切片 {document.chunk_count}</div>
                </div>
                <Button onClick={() => void removeDocument(document.id)} disabled={removingId === document.id}>
                  {removingId === document.id ? "删除中" : "删除"}
                </Button>
              </div>
            ))
          )}
        </div>
      </Card>

      <Card>
        <div className="flex flex-col gap-3 md:flex-row">
          <input className="flex-1 rounded-xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm" value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="输入要从当前知识库检索的问题" />
          <Button onClick={query} disabled={!selectedId || !question.trim() || querying}>{querying ? "检索中" : "知识库问答"}</Button>
        </div>
        <div className="mt-4 rounded-xl border border-white/10 bg-white/5 p-3 text-sm text-slate-300">{statusMessage}</div>

        {result ? (
          <div className="mt-4 space-y-4">
            <section className="rounded-2xl border border-emerald-400/30 bg-emerald-400/10 p-5">
              <div className="text-xs font-medium uppercase tracking-[0.2em] text-emerald-200">Answer</div>
              <h3 className="mt-2 text-lg font-semibold text-white">直接答案</h3>
              <p className="mt-3 text-base leading-8 text-slate-100">{result.summary || result.answer}</p>
            </section>

            <section className="rounded-2xl border border-white/10 bg-slate-950/40 p-5">
              <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
                <div>
                  <div className="text-xs font-medium uppercase tracking-[0.2em] text-blue-200">Evidence</div>
                  <h3 className="mt-2 text-lg font-semibold text-white">命中依据</h3>
                </div>
                <Badge>{evidence.length ? `${evidence.length} 条引用` : "无引用"}</Badge>
              </div>
              <div className="mt-4 space-y-3">
                {evidence.length === 0 ? (
                  <div className="rounded-xl border border-dashed border-white/10 p-4 text-sm text-slate-400">没有可展示的引用片段。</div>
                ) : (
                  evidence.map((item) => (
                    <article key={`${item.document}-${item.index}`} className="rounded-xl border border-white/10 bg-white/5 p-4">
                      <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
                        <div className="font-medium text-slate-100">来源 {item.index} · {item.document}</div>
                        <div className="flex flex-wrap gap-2 text-xs text-slate-300">
                          <span className="rounded-full bg-white/10 px-2 py-1">score {formatScore(item.score)}</span>
                          <span className="rounded-full bg-white/10 px-2 py-1">lexical {formatScore(item.lexical_score)}</span>
                          <span className="rounded-full bg-white/10 px-2 py-1">vector {formatScore(item.vector_score)}</span>
                          {typeof item.rerank_score === "number" ? <span className="rounded-full bg-white/10 px-2 py-1">rerank {formatScore(item.rerank_score)}</span> : null}
                        </div>
                      </div>
                      <p className="mt-3 whitespace-pre-wrap text-sm leading-7 text-slate-300">{compactText(item.content)}</p>
                    </article>
                  ))
                )}
              </div>
            </section>

            <section className="rounded-2xl border border-white/10 bg-slate-950/40 p-5 text-sm text-slate-300">
              <div className="text-xs font-medium uppercase tracking-[0.2em] text-slate-400">Debug</div>
              <div className="mt-3 grid gap-2 md:grid-cols-4">
                <div className="rounded-xl bg-white/5 p-3">KB：{result.debug?.kb_id ?? selectedId ?? "-"}</div>
                <div className="rounded-xl bg-white/5 p-3">策略：{result.debug?.strategy ?? "-"}</div>
                <div className="rounded-xl bg-white/5 p-3">TopK：{result.debug?.top_k ?? "-"}</div>
                <div className="rounded-xl bg-white/5 p-3">Rerank：{result.debug?.rerank ? "开启" : "-"}</div>
              </div>
            </section>
          </div>
        ) : null}
      </Card>
    </div>
  );
}
