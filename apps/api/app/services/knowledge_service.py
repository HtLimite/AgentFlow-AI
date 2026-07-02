from dataclasses import dataclass, field
from itertools import count

from app.services.chunk_service import chunk_service
from app.services.document_parser import document_parser


@dataclass
class KnowledgeDocumentRecord:
    id: int
    kb_id: int
    filename: str
    content: str
    chunks: list[dict[str, object]] = field(default_factory=list)
    parse_status: str = "ready"


@dataclass
class KnowledgeBaseRecord:
    id: int
    name: str
    description: str | None = None
    documents: list[KnowledgeDocumentRecord] = field(default_factory=list)


class KnowledgeService:
    def __init__(self) -> None:
        self._kb_ids = count(2)
        self._doc_ids = count(1)
        demo = KnowledgeBaseRecord(id=1, name="企业制度知识库", description="默认演示知识库")
        demo_doc = KnowledgeDocumentRecord(
            id=next(self._doc_ids),
            kb_id=1,
            filename="demo-policy.md",
            content="报销流程：员工提交发票和报销单，直属负责人审批，财务复核后付款。",
            chunks=[
                {
                    "chunk_index": 0,
                    "content": "报销流程：员工提交发票和报销单，直属负责人审批，财务复核后付款。",
                    "token_count": 32,
                    "document": "demo-policy.md",
                    "score": 0.91,
                }
            ],
        )
        demo.documents.append(demo_doc)
        self._items: dict[int, KnowledgeBaseRecord] = {1: demo}

    def list_bases(self) -> list[dict[str, object]]:
        return [self._serialize_base(item) for item in self._items.values()]

    def create_base(self, name: str, description: str | None = None) -> dict[str, object]:
        kb_id = next(self._kb_ids)
        item = KnowledgeBaseRecord(id=kb_id, name=name, description=description)
        self._items[kb_id] = item
        return self._serialize_base(item)

    def list_documents(self, kb_id: int) -> list[dict[str, object]]:
        item = self._items.get(kb_id)
        if item is None:
            return []
        return [self._serialize_document(doc) for doc in item.documents]

    def add_document(self, kb_id: int, filename: str, raw_content: bytes) -> dict[str, object] | None:
        item = self._items.get(kb_id)
        if item is None:
            return None
        text = raw_content.decode("utf-8", errors="ignore") or filename
        parsed = document_parser.parse_text(filename, text)
        chunks = chunk_service.split_text(str(parsed["content"]), chunk_size=800, overlap=150)
        enriched_chunks = [
            {**chunk, "document": filename, "score": round(0.92 - index * 0.03, 4)}
            for index, chunk in enumerate(chunks)
        ]
        doc = KnowledgeDocumentRecord(
            id=next(self._doc_ids),
            kb_id=kb_id,
            filename=filename,
            content=str(parsed["content"]),
            chunks=enriched_chunks,
        )
        item.documents.append(doc)
        return self._serialize_document(doc)

    def search(self, kb_id: int, question: str, top_k: int = 5) -> list[dict[str, object]]:
        item = self._items.get(kb_id)
        if item is None:
            return []
        all_chunks: list[dict[str, object]] = []
        keywords = [part for part in question.lower().split() if part]
        for doc in item.documents:
            for chunk in doc.chunks:
                content = str(chunk["content"])
                hit_count = sum(1 for keyword in keywords if keyword in content.lower())
                score = float(chunk.get("score", 0.8)) + min(hit_count * 0.02, 0.1)
                all_chunks.append({**chunk, "document": doc.filename, "score": round(score, 4)})
        return sorted(all_chunks, key=lambda row: float(row["score"]), reverse=True)[:top_k]

    def answer(self, kb_id: int, question: str, top_k: int = 5) -> dict[str, object]:
        chunks = self.search(kb_id, question, top_k)
        if not chunks:
            return {"answer": "知识库中没有找到相关信息。", "citations": [], "debug": {"kb_id": kb_id, "top_k": top_k}}
        evidence = "\n".join(f"- {chunk['content']}" for chunk in chunks)
        return {"answer": f"根据知识库命中片段，可回答：{question}\n\n依据：\n{evidence}", "citations": chunks, "debug": {"kb_id": kb_id, "top_k": top_k}}

    def _serialize_base(self, item: KnowledgeBaseRecord) -> dict[str, object]:
        chunk_count = sum(len(doc.chunks) for doc in item.documents)
        return {"id": item.id, "name": item.name, "description": item.description, "document_count": len(item.documents), "chunk_count": chunk_count, "status": "ready"}

    def _serialize_document(self, doc: KnowledgeDocumentRecord) -> dict[str, object]:
        return {"id": doc.id, "kb_id": doc.kb_id, "filename": doc.filename, "parse_status": doc.parse_status, "chunk_count": len(doc.chunks)}


knowledge_service = KnowledgeService()
