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

interface KnowledgeAnswer {
  answer: string;
  citations: Array<{ document: string; content: string; score: number; lexical_score?: number; vector_score?: number }>;
}

export function KnowledgeConsole() {
  const [items, setItems] = useState<KnowledgeBaseItem[]>([]);
  const [documents, setDocuments] = useState<KnowledgeDocumentItem[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("请选择知识库并上传真实文档后再查询");
  const [uploading, setUploading] = useState(false);
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
    reload().catch((error) => setAnswer(error.message));
  }, []);

  useEffect(() => {
    loadDocuments(selectedId).catch((error) => setAnswer(error.message));
  }, [selectedId]);

  async function createBase() {
    const name = newBaseName.trim();
    if (!name) {
      setAnswer("请先填写知识库名称");
      return;
    }
    const created = await apiJson<KnowledgeBaseItem>("/api/knowledge-bases", { name });
    setNewBaseName("");
    await reload(created.id);
    setAnswer(`已创建知识库：${created.name}`);
  }

  async function query() {
    if (!selectedId) {
      setAnswer("请先创建或选择知识库");
      return;
    }
    if (!question.trim()) {
      setAnswer("请输入要查询的问题");
      return;
    }
    const data = await apiJson<KnowledgeAnswer>(`/api/knowledge-bases/${selectedId}/query`, { question, top_k: 5 });
    const citations = data.citations.length
      ? data.citations.map((item) => `- ${item.document} · score=${item.score} · lexical=${item.lexical_score ?? "-"}: ${item.content}`).join("\n")
      : "无引用来源";
    setAnswer(`${data.answer}\n\n引用来源：\n${citations}`);
  }

  async function upload(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    if (!selectedId) {
      setAnswer("请先创建或选择知识库");
      event.target.value = "";
      return;
    }
    setUploading(true);
    setAnswer(`正在解析文档：${file.name}`);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const response = await fetch(`${API_BASE_URL}/api/knowledge-bases/${selectedId}/documents`, { method: "POST", body: formData });
      if (!response.ok) {
        const errorBody = await response.json().catch(() => null);
        throw new Error(errorBody?.detail || "上传失败，请检查文档格式");
      }
      await reload(selectedId);
      setAnswer(`文档已解析并切片：${file.name}`);
    } catch (error) {
      setAnswer(error instanceof Error ? error.message : "上传失败，请检查文档格式");
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
      setAnswer(`已删除文档 #${documentId}。该文档已从知识库列表和后续检索中移除。`);
    } catch (error) {
      setAnswer(error instanceof Error ? error.message : "删除失败");
    } finally {
      setRemovingId(null);
    }
  }

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
        <div className="flex gap-3">
          <input className="flex-1 rounded-xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm" value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="输入要从当前知识库检索的问题" />
          <Button onClick={query} disabled={!selectedId || !question.trim()}>知识库问答</Button>
        </div>
        <pre className="mt-4 whitespace-pre-wrap rounded-xl bg-slate-950/70 p-4 text-sm text-slate-200">{answer}</pre>
      </Card>
    </div>
  );
}
