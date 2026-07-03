from sqlalchemy import delete, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import KnowledgeBase, KnowledgeChunk, KnowledgeDocument
from app.services.chunk_service import chunk_service
from app.services.document_parser import document_parser
from app.services.embedding_service import embedding_service
from app.services.text_cleaner import clean_extracted_text, make_snippet
from app.services.vector_service import vector_service

_STOP_WORDS = {
    "什么",
    "怎么",
    "如何",
    "是否",
    "可以",
    "一下",
    "请问",
    "这个",
    "那个",
    "的是",
    "有吗",
}


class PersistentKnowledgeService:
    """Database-backed knowledge service with the same response shape as the demo service."""

    async def list_bases(self, session: AsyncSession) -> list[dict[str, object]]:
        await self._ensure_default_base(session)
        result = await session.execute(
            select(
                KnowledgeBase,
                func.count(func.distinct(KnowledgeDocument.id)).label("document_count"),
                func.count(KnowledgeChunk.id).label("chunk_count"),
            )
            .outerjoin(KnowledgeDocument, KnowledgeDocument.kb_id == KnowledgeBase.id)
            .outerjoin(KnowledgeChunk, KnowledgeChunk.kb_id == KnowledgeBase.id)
            .group_by(KnowledgeBase.id)
            .order_by(KnowledgeBase.id.desc())
        )
        return [self._serialize_base(item, document_count, chunk_count) for item, document_count, chunk_count in result.all()]

    async def create_base(self, session: AsyncSession, name: str, description: str | None = None) -> dict[str, object]:
        item = KnowledgeBase(name=name, description=description, visibility="private")
        session.add(item)
        await session.commit()
        await session.refresh(item)
        return self._serialize_base(item, 0, 0)

    async def list_documents(self, session: AsyncSession, kb_id: int) -> list[dict[str, object]]:
        result = await session.scalars(
            select(KnowledgeDocument).where(KnowledgeDocument.kb_id == kb_id).order_by(KnowledgeDocument.id.desc())
        )
        return [self._serialize_document(item) for item in result.all()]

    async def add_document(self, session: AsyncSession, kb_id: int, filename: str, raw_content: bytes) -> dict[str, object] | None:
        knowledge_base = await session.get(KnowledgeBase, kb_id)
        if knowledge_base is None:
            return None

        parsed = document_parser.parse_upload(filename, raw_content)
        parsed_content = clean_extracted_text(str(parsed["content"]))
        chunks = chunk_service.split_text(parsed_content, chunk_size=800, overlap=150)
        file_type = str(parsed.get("file_type") or (filename.rsplit(".", 1)[-1] if "." in filename else "text"))
        document = KnowledgeDocument(
            kb_id=kb_id,
            filename=filename,
            file_type=file_type,
            file_size=len(raw_content),
            parse_status="ready",
            chunk_count=len(chunks),
        )
        session.add(document)
        await session.flush()

        for chunk in chunks:
            content = clean_extracted_text(str(chunk["content"]))
            embedding = await embedding_service.embed(content)
            session.add(
                KnowledgeChunk(
                    kb_id=kb_id,
                    document_id=document.id,
                    content=content,
                    chunk_index=int(chunk["chunk_index"]),
                    token_count=int(chunk["token_count"]),
                    metadata_json={"document": filename, "embedding": embedding, "source": "database"},
                )
            )

        await session.commit()
        await session.refresh(document)
        return self._serialize_document(document)

    async def delete_document(self, session: AsyncSession, kb_id: int, document_id: int) -> bool:
        document = await session.get(KnowledgeDocument, document_id)
        if document is None or document.kb_id != kb_id:
            return False
        await session.execute(delete(KnowledgeChunk).where(KnowledgeChunk.document_id == document_id))
        await session.delete(document)
        await session.commit()
        return True

    async def search(self, session: AsyncSession, kb_id: int, question: str, top_k: int = 5) -> list[dict[str, object]]:
        query_vector = await embedding_service.embed(question)
        query_terms = self._extract_query_terms(question)
        result = await session.execute(
            select(KnowledgeChunk, KnowledgeDocument.filename)
            .join(KnowledgeDocument, KnowledgeDocument.id == KnowledgeChunk.document_id)
            .where(KnowledgeChunk.kb_id == kb_id)
            .order_by(KnowledgeChunk.id.desc())
            .limit(200)
        )
        rows: list[dict[str, object]] = []
        for chunk, filename in result.all():
            metadata = chunk.metadata_json or {}
            embedding = metadata.get("embedding", []) if isinstance(metadata, dict) else []
            content = clean_extracted_text(chunk.content)
            content_lower = content.lower()
            keyword_hits = sum(1 for term in query_terms if term in content_lower)
            keyword_score = keyword_hits / max(1, min(len(query_terms), 8))
            vector_score = max(0.0, vector_service.cosine(query_vector, embedding))
            score = round(keyword_score * 0.85 + vector_score * 0.15, 4)
            if keyword_hits <= 0 and score < 0.72:
                continue
            rows.append(
                {
                    "chunk_index": chunk.chunk_index,
                    "content": make_snippet(content, 500),
                    "token_count": chunk.token_count,
                    "document": filename,
                    "score": score,
                    "keyword_hits": keyword_hits,
                }
            )
        return sorted(rows, key=lambda row: float(row["score"]), reverse=True)[:top_k]

    async def answer(self, session: AsyncSession, kb_id: int, question: str, top_k: int = 5) -> dict[str, object]:
        chunks = await self.search(session, kb_id, question, top_k)
        if not chunks:
            return {
                "answer": f"知识库中没有找到与“{clean_extracted_text(question)}”直接相关的信息。请确认选择的知识库或上传包含该问题的文档。",
                "citations": [],
                "debug": {"kb_id": kb_id, "top_k": top_k, "strategy": "database_keyword_vector", "rejected_low_relevance": True},
            }
        evidence = "\n".join(f"- {make_snippet(str(chunk['content']), 220)}" for chunk in chunks)
        return {
            "answer": f"命中 {len(chunks)} 条相关知识片段，请结合引用来源核对。\n\n摘要：\n{evidence}",
            "citations": chunks,
            "debug": {"kb_id": kb_id, "top_k": top_k, "strategy": "database_keyword_vector"},
        }

    async def _ensure_default_base(self, session: AsyncSession) -> None:
        existing = await session.scalar(select(KnowledgeBase.id).limit(1))
        if existing:
            return
        default = KnowledgeBase(id=1, name="企业制度知识库", description="默认演示知识库", visibility="private")
        session.add(default)
        await session.flush()
        document = KnowledgeDocument(kb_id=1, filename="demo-policy.md", file_type="md", parse_status="ready", chunk_count=1)
        session.add(document)
        await session.flush()
        content = "报销流程：员工提交发票和报销单，直属负责人审批，财务复核后付款。"
        session.add(
            KnowledgeChunk(
                kb_id=1,
                document_id=document.id,
                content=content,
                chunk_index=0,
                token_count=32,
                metadata_json={"document": "demo-policy.md", "embedding": await embedding_service.embed(content), "source": "seed"},
            )
        )
        await session.commit()

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

    def _serialize_base(self, item: KnowledgeBase, document_count: int, chunk_count: int) -> dict[str, object]:
        return {
            "id": item.id,
            "name": item.name,
            "description": item.description,
            "document_count": int(document_count or 0),
            "chunk_count": int(chunk_count or 0),
            "status": "ready",
        }

    def _serialize_document(self, item: KnowledgeDocument) -> dict[str, object]:
        return {
            "id": item.id,
            "kb_id": item.kb_id,
            "filename": item.filename,
            "parse_status": item.parse_status,
            "chunk_count": item.chunk_count,
        }


persistent_knowledge_service = PersistentKnowledgeService()


def is_database_error(exc: Exception) -> bool:
    return isinstance(exc, SQLAlchemyError)
