from dataclasses import dataclass, field
from itertools import count

from app.services.chunk_service import chunk_service
from app.services.document_parser import document_parser
from app.services.text_cleaner import clean_extracted_text, make_snippet
from app.services.vector_service import vector_service

_STOP_WORDS = {"什么", "怎么", "如何", "是否", "可以", "一下", "请问", "这个", "那个", "的是", "有吗"}


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
        demo_text = "报销流程：员工提交发票和报销单，直属负责人审批，财务复核后付款。"
        demo_doc = KnowledgeDocumentRecord(
            id=next(self._doc_ids),
            kb_id=1,
            filename="demo-policy.md",
            content=demo_text,
            chunks=[self._build_chunk("demo-policy.md", demo_text, 0, 32)],
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

    def delete_document(self, kb_id: int, document_id: int) -> bool:
        item = self._items.get(kb_id)
        if item is None:
            return False
        before = len(item.documents)
        item.documents = [document for document in item.documents if document.id != document_id]
        return len(item.documents) != before

    def search(self, kb_id: int, question: str, top_k: int = 5) -> list[dict[str, object]]:
        item = self._items.get(kb_id)
        if item is None:
            return []
        query_vector = vector_service.embed(question)
        query_terms = self._extract_query_terms(question)
        results: list[dict[str, object]] = []
        for doc in item.documents:
            for chunk in doc.chunks:
                content = clean_extracted_text(str(chunk["content"]))
                content_lower = content.lower()
                keyword_hits = sum(1 for term in query_terms if term in content_lower)
                keyword_score = keyword_hits / max(1, min(len(query_terms), 8))
                vector_score = max(0.0, vector_service.cosine(query_vector, chunk.get("embedding", [])))
                score = round(keyword_score * 0.85 + vector_score * 0.15, 4)
                if keyword_hits <= 0 and score < 0.72:
                    continue
                result = {
                    **chunk,
                    "content": make_snippet(content, 500),
                    "document": doc.filename,
                    "score": score,
                    "keyword_hits": keyword_hits,
                }
                results.append({k: v for k, v in result.items() if k != "embedding"})
        return sorted(results, key=lambda row: float(row["score"]), reverse=True)[:top_k]

    def answer(self, kb_id: int, question: str, top_k: int = 5) -> dict[str, object]:
        chunks = self.search(kb_id, question, top_k)
        if not chunks:
            return {
                "answer": f"知识库中没有找到与“{clean_extracted_text(question)}”直接相关的信息。请确认选择的知识库或上传包含该问题的文档。",
                "citations": [],
                "debug": {"kb_id": kb_id, "top_k": top_k, "strategy": "local_keyword_vector", "rejected_low_relevance": True},
            }
        evidence = "\n".join(f"- {make_snippet(str(chunk['content']), 220)}" for chunk in chunks)
        return {
            "answer": f"命中 {len(chunks)} 条相关知识片段，请结合引用来源核对。\n\n摘要：\n{evidence}",
            "citations": chunks,
            "debug": {"kb_id": kb_id, "top_k": top_k, "strategy": "local_keyword_vector"},
        }

    def _extract_query_terms(self, question: str) -> list[str]:
        text = clean_extracted_text(question).lower()
        terms: list[str] = []
        for part in text.replace("？", " ").replace("?", " ").replace("，", " ").replace("。", " ").split():
            if len(part) >= 2 and part not in _STOP_WORDS:
                terms.append(part)
        cjk_chars = [char for char in text if "\u4e00" <= char <= "\u9fff"]
        for size in (2, 3, 4):
            for index in range(0, max(0, len(cjk_chars) - size + 1)):
                term = "".join(cjk_chars[index : index + size])
                if term and term not in _STOP_WORDS:
                    terms.append(term)
        return list(dict.fromkeys(terms))

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
        chunk_count = sum(len(doc.chunks) for doc in item.documents)
        return {"id": item.id, "name": item.name, "description": item.description, "document_count": len(item.documents), "chunk_count": chunk_count, "status": "ready"}

    def _serialize_document(self, doc: KnowledgeDocumentRecord) -> dict[str, object]:
        return {"id": doc.id, "kb_id": doc.kb_id, "filename": doc.filename, "parse_status": doc.parse_status, "chunk_count": len(doc.chunks)}


knowledge_service = KnowledgeService()
