from dataclasses import dataclass, field
from itertools import count

from app.services.chunk_service import chunk_service
from app.services.document_parser import document_parser
from app.services.text_cleaner import clean_extracted_text, make_snippet
from app.services.vector_service import vector_service


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
        demo = KnowledgeBaseRecord(id=1, name="本地回退知识库", description="仅在数据库不可用时使用的内存回退数据")
        demo_text = "报销流程：员工提交发票和报销单，直属负责人审批，财务复核后付款。"
        demo_doc = KnowledgeDocumentRecord(
            id=next(self._doc_ids),
            kb_id=1,
            filename="memory-fallback-policy.md",
            content=demo_text,
            chunks=[self._build_chunk("memory-fallback-policy.md", demo_text, 0, 32)],
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
        return [self._serialize_document(doc) for doc in item.documents if doc.parse_status != "removed"]

    def add_document(self, kb_id: int, filename: str, raw_content: bytes) -> dict[str, object] | None:
        item = self._items.get(kb_id)
        if item is None:
            return None
        parsed = document_parser.parse_upload(filename, raw_content)
        parsed_content = clean_extracted_text(str(parsed["content"]))
        chunks = chunk_service.split_text(parsed_content, chunk_size=800, overlap=150)
        enriched_chunks = [
            self._build_chunk(filename, str(chunk["content"]), int(chunk["chunk_index"]), int(chunk["token_count"]))
            for chunk in chunks
        ]
        doc = KnowledgeDocumentRecord(
            id=next(self._doc_ids),
            kb_id=kb_id,
            filename=filename,
            content=parsed_content,
            chunks=enriched_chunks,
        )
        item.documents.append(doc)
        return self._serialize_document(doc)

    def remove_document(self, kb_id: int, document_id: int) -> bool:
        item = self._items.get(kb_id)
        if item is None:
            return False
        for doc in item.documents:
            if doc.id == document_id and doc.parse_status != "removed":
                doc.parse_status = "removed"
                doc.chunks = []
                return True
        return False

    def search(self, kb_id: int, question: str, top_k: int = 5) -> list[dict[str, object]]:
        item = self._items.get(kb_id)
        if item is None:
            return []
        query_vector = vector_service.embed(question)
        keywords = [part for part in clean_extracted_text(question).lower().split() if part]
        results: list[dict[str, object]] = []
        for doc in item.documents:
            if doc.parse_status == "removed":
                continue
            for chunk in doc.chunks:
                content = clean_extracted_text(str(chunk["content"]))
                keyword_score = sum(1 for keyword in keywords if keyword in content.lower()) * 0.03
                vector_score = vector_service.cosine(query_vector, chunk.get("embedding", []))
                score = round(max(0.0, vector_score) + keyword_score + 0.6, 4)
                result = {**chunk, "content": make_snippet(content, 500), "document": doc.filename, "score": score}
                results.append({k: v for k, v in result.items() if k != "embedding"})
        return sorted(results, key=lambda row: float(row["score"]), reverse=True)[:top_k]

    def answer(self, kb_id: int, question: str, top_k: int = 5) -> dict[str, object]:
        chunks = self.search(kb_id, question, top_k)
        if not chunks:
            return {"answer": "知识库中没有找到相关信息。", "citations": [], "debug": {"kb_id": kb_id, "top_k": top_k, "strategy": "memory_fallback_vector"}}
        evidence = "\n".join(f"- {make_snippet(str(chunk['content']), 220)}" for chunk in chunks)
        answer = f"根据知识库命中片段，可回答：{clean_extracted_text(question)}\n\n依据：\n{evidence}"
        return {
            "answer": answer,
            "citations": chunks,
            "debug": {"kb_id": kb_id, "top_k": top_k, "strategy": "memory_fallback_vector"},
        }

    def _build_chunk(self, filename: str, content: str, chunk_index: int, token_count: int) -> dict[str, object]:
        cleaned_content = clean_extracted_text(content)
        return {
            "chunk_index": chunk_index,
            "content": cleaned_content,
            "token_count": token_count,
            "document": filename,
            "embedding": vector_service.embed(cleaned_content),
            "score": 0.0,
        }

    def _serialize_base(self, item: KnowledgeBaseRecord) -> dict[str, object]:
        active_docs = [doc for doc in item.documents if doc.parse_status != "removed"]
        chunk_count = sum(len(doc.chunks) for doc in active_docs)
        return {"id": item.id, "name": item.name, "description": item.description, "document_count": len(active_docs), "chunk_count": chunk_count, "status": "ready"}

    def _serialize_document(self, doc: KnowledgeDocumentRecord) -> dict[str, object]:
        return {"id": doc.id, "kb_id": doc.kb_id, "filename": doc.filename, "parse_status": doc.parse_status, "chunk_count": len(doc.chunks)}


knowledge_service = KnowledgeService()
