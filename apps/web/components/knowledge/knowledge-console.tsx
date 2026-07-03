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

export function KnowledgeConsole() {
  const [items, setItems] = useState<KnowledgeBaseItem[]>([]);
  const [selectedId, setSelectedId] = useState(1);
  const [question, setQuestion] = useState("报销流程是什么？");
  const [answer, setAnswer] = useState("等待查询");
  const [uploading, setUploading] = useState(false);

  async function load() {
    const data = await apiGet<KnowledgeBaseItem[]>("/api/knowledge-bases");
    setItems(data);
    if (data[0]) setSelectedId(data[0].id);
  }

  useEffect(() => {
    load().catch((error) => setAnswer(error.message));
  }, []);

  async function query() {
    const data = await apiJson<{ answer: string; citations: Array<{ document: string; content: string; score: number }> }>(`/api/knowledge-bases/${selectedId}/query`, { question, top_k: 5 });
    const citations = data.citations.map((item) => `- ${item.document} · ${item.score}: ${item.content}`).join("\n");
    setAnswer(`${data.answer}\n\n引用来源：\n${citations}`);
  }

  async function upload(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
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
      await load();
      setAnswer(`文档已解析并切片：${file.name}`);
    } catch (error) {
      setAnswer(error instanceof Error ? error.message : "上传失败，请检查文档格式");
    } finally {
      setUploading(false);
      event.target.value = "";
    }
  }

  return (
    <div className="space-y-4">
      <Card className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-xl font-semibold">知识库 RAG</h2>
          <p className="mt-1 text-sm text-slate-400">已接入后端：创建、上传、切片、问答、引用来源。支持 txt / md / pdf，扫描版 PDF 需先 OCR。</p>
        </div>
        <label className="rounded-xl border border-white/10 bg-white/10 px-4 py-3 text-sm text-slate-200 hover:bg-white/15">
          {uploading ? "解析中..." : "上传文档"}
          <input type="file" accept=".txt,.md,.markdown,.pdf,text/plain,text/markdown,application/pdf" onChange={upload} className="hidden" disabled={uploading} />
        </label>
      </Card>
      <div className="grid gap-4 lg:grid-cols-3">
        {items.map((row) => (
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
        ))}
      </div>
      <Card>
        <div className="flex gap-3">
          <input className="flex-1 rounded-xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm" value={question} onChange={(event) => setQuestion(event.target.value)} />
          <Button onClick={query}>知识库问答</Button>
        </div>
        <pre className="mt-4 whitespace-pre-wrap rounded-xl bg-slate-950/70 p-4 text-sm text-slate-200">{answer}</pre>
      </Card>
    </div>
  );
}
