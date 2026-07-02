import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

const rows = [
  { name: "企业制度知识库", docs: 12, chunks: 368, status: "ready" },
  { name: "售后客服知识库", docs: 8, chunks: 192, status: "embedding" },
  { name: "项目文档知识库", docs: 5, chunks: 88, status: "parsing" }
];

export default function KnowledgePage() {
  return (
    <div className="space-y-4">
      <Card className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-xl font-semibold">知识库 RAG</h2>
          <p className="mt-1 text-sm text-slate-400">文档上传、解析、切片、向量化、引用来源展示。</p>
        </div>
        <Button>创建知识库</Button>
      </Card>
      <div className="grid gap-4 lg:grid-cols-3">
        {rows.map((row) => (
          <Card key={row.name}>
            <div className="flex items-center justify-between">
              <h3 className="font-semibold">{row.name}</h3>
              <Badge>{row.status}</Badge>
            </div>
            <div className="mt-4 grid grid-cols-2 gap-3 text-sm text-slate-300">
              <div className="rounded-xl bg-white/10 p-3">文档 {row.docs}</div>
              <div className="rounded-xl bg-white/10 p-3">切片 {row.chunks}</div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
