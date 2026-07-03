import json
import re
from typing import Any

from sqlalchemy import func, select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import KnowledgeBase, KnowledgeChunk, KnowledgeDocument
from app.services.chunk_service import chunk_service
from app.services.document_parser import document_parser
from app.services.embedding_service import embedding_service
from app.services.text_cleaner import clean_extracted_text, make_snippet
from app.services.vector_service import vector_service

CJK_RE = re.compile(r"[\u4e00-\u9fff]{2,}")
WORD_RE = re.compile(r"[a-zA-Z0-9_]{2,}")
MIN_RELEVANCE_SCORE = 0.18
STOP_TERMS = {"什么", "怎么", "如何", "是否", "the", "and"}


def _query_terms(text_value: str) -> set[str]:
    cleaned = clean_extracted_text(text_value).lower()
    terms = set(WORD_RE.findall(cleaned))
    terms.update(CJK_RE.findall(cleaned))
    return {term for term in terms if term not in STOP_TERMS}


def _lexical_score(question: str, content: str) -> float:
    terms = _query_terms(question)
    if not terms:
        return 0.0
    lower_content = clean_extracted_text(content).lower()
    hits = sum(1 for term in terms if term in lower_content)
    return hits / len(terms)


def _vector_literal(values: list[float]) -> str:
    return "[" + ",".join(f"{float(value):.6f}" for value in values) + "]"


class PersistentKnowledgeService:
    """Database-backed knowledge service with pgvector-first retrieval and memory fallback compatibility."""

    async def list_bases(self, session: AsyncSession) -> list[dict[str, object]]:
        await self._ensure_default_base(session)
        result = await session.execute(
            select(
                KnowledgeBase,
                func.count(func.distinct(KnowledgeDocument.id)).label("document_count"),
                func.count(KnowledgeChunk.id).label("chunk_count"),
            )
            .outerjoin(KnowledgeDocument, (KnowledgeDocument.kb_id == KnowledgeBase.id) & (KnowledgeDocument.parse_status != "removed"))
            .outerjoin(KnowledgeChunk, KnowledgeChunk.document_id == KnowledgeDocument.id)
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
            select(KnowledgeDocument)
            .where(KnowledgeDocument.kb_id == kb_id, KnowledgeDocument.parse_status != "removed")
            .order_by(KnowledgeDocument.id.desc())
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
            await self._insert_chunk(
                session,
                kb_id=kb_id,
                document_id=int(document.id),
                content=content,
                chunk_index=int(chunk["chunk_index"]),
                token_count=int(chunk["token_count"]),
                embedding=embedding,
                metadata={"document": filename, "source": "database"},
            )

        await session.commit()
        await session.refresh(document)
        return self._serialize_document(document)

    async def remove_document(self, session: AsyncSession, kb_id: int, document_id: int) -> bool:
        document = await session.get(KnowledgeDocument, document_id)
        if document is None or document.kb_id != kb_id or document.parse_status == "removed":
            return False
        document.parse_status = "removed"
        document.chunk_count = 0
        await session.commit()
        return True

    async def search(self, session: AsyncSession, kb_id: int, question: str, top_k: int = 5) -> list[dict[str, object]]:
        query_vector = await embedding_service.embed(question)
        pgvector_rows = await self._search_pgvector(session, kb_id, question, query_vector, top_k)
        if pgvector_rows:
            return pgvector_rows
        return await self._search_metadata_hybrid(session, kb_id, question, query_vector, top_k)

    async def answer(self, session: AsyncSession, kb_id: int, question: str, top_k: int = 5) -> dict[str, object]:
        chunks = await self.search(session, kb_id, question, top_k)
        if not chunks:
            return {
                "answer": f"知识库中没有找到与“{clean_extracted_text(question)}”直接相关的内容。请确认已上传对应文档，或换一个知识库后再问。",
                "citations": [],
                "debug": {"kb_id": kb_id, "top_k": top_k, "strategy": "pgvector_sql_hybrid", "min_relevance_score": MIN_RELEVANCE_SCORE},
            }
        evidence = "\n".join(f"- {make_snippet(str(chunk['content']), 220)}" for chunk in chunks)
        strategy = str(chunks[0].get("strategy") or "pgvector_sql_hybrid")
        return {
            "answer": f"根据知识库命中片段回答：{clean_extracted_text(question)}\n\n依据：\n{evidence}",
            "citations": chunks,
            "debug": {"kb_id": kb_id, "top_k": top_k, "strategy": strategy, "min_relevance_score": MIN_RELEVANCE_SCORE},
        }

    async def _insert_chunk(
        self,
        session: AsyncSession,
        kb_id: int,
        document_id: int,
        content: str,
        chunk_index: int,
        token_count: int,
        embedding: list[float],
        metadata: dict[str, Any],
    ) -> None:
        await session.execute(
            text(
                """
                INSERT INTO knowledge_chunk (kb_id, document_id, content, chunk_index, token_count, embedding, metadata)
                VALUES (:kb_id, :document_id, :content, :chunk_index, :token_count, CAST(:embedding AS vector), CAST(:metadata AS jsonb))
                """
            ),
            {
                "kb_id": kb_id,
                "document_id": document_id,
                "content": content,
                "chunk_index": chunk_index,
                "token_count": token_count,
                "embedding": _vector_literal(embedding),
                "metadata": json.dumps(metadata, ensure_ascii=False),
            },
        )

    async def _search_pgvector(
        self,
        session: AsyncSession,
        kb_id: int,
        question: str,
        query_vector: list[float],
        top_k: int,
    ) -> list[dict[str, object]]:
        result = await session.execute(
            text(
                """
                SELECT
                  kc.chunk_index,
                  kc.content,
                  kc.token_count,
                  kd.filename AS document,
                  1 - (kc.embedding <=> CAST(:query_embedding AS vector)) AS vector_score
                FROM knowledge_chunk kc
                JOIN knowledge_document kd ON kd.id = kc.document_id
                WHERE kc.kb_id = :kb_id
                  AND kd.parse_status = 'ready'
                  AND kc.embedding IS NOT NULL
                ORDER BY kc.embedding <=> CAST(:query_embedding AS vector)
                LIMIT :limit
                """
            ),
            {"kb_id": kb_id, "query_embedding": _vector_literal(query_vector), "limit": max(top_k * 5, 20)},
        )
        rows: list[dict[str, object]] = []
        for row in result.mappings().all():
            content = clean_extracted_text(str(row["content"]))
            lexical_score = _lexical_score(question, content)
            vector_score = max(0.0, float(row["vector_score"] or 0))
            score = round(lexical_score * 0.35 + vector_score * 0.65, 4)
            if score < MIN_RELEVANCE_SCORE:
                continue
            rows.append(
                {
                    "chunk_index": int(row["chunk_index"]),
                    "content": make_snippet(content, 500),
                    "token_count": int(row["token_count"] or 0),
                    "document": row["document"],
                    "score": score,
                    "lexical_score": round(lexical_score, 4),
                    "vector_score": round(vector_score, 4),
                    "strategy": "pgvector_sql_hybrid",
                }
            )
        return sorted(rows, key=lambda row: float(row["score"]), reverse=True)[:top_k]

    async def _search_metadata_hybrid(self, session: AsyncSession, kb_id: int, question: str, query_vector: list[float], top_k: int) -> list[dict[str, object]]:
        result = await session.execute(
            select(KnowledgeChunk, KnowledgeDocument.filename)
            .join(KnowledgeDocument, KnowledgeDocument.id == KnowledgeChunk.document_id)
            .where(KnowledgeChunk.kb_id == kb_id, KnowledgeDocument.parse_status == "ready")
            .order_by(KnowledgeChunk.id.desc())
            .limit(200)
        )
        rows: list[dict[str, object]] = []
        for chunk, filename in result.all():
            metadata = chunk.metadata_json or {}
            embedding = metadata.get("embedding", []) if isinstance(metadata, dict) else []
            content = clean_extracted_text(chunk.content)
            lexical_score = _lexical_score(question, content)
            vector_score = max(0.0, vector_service.cosine(query_vector, embedding))
            score = round(lexical_score * 0.75 + vector_score * 0.25, 4)
            if score < MIN_RELEVANCE_SCORE:
                continue
            rows.append(
                {
                    "chunk_index": chunk.chunk_index,
                    "content": make_snippet(content, 500),
                    "token_count": chunk.token_count,
                    "document": filename,
                    "score": score,
                    "lexical_score": round(lexical_score, 4),
                    "vector_score": round(vector_score, 4),
                    "strategy": "metadata_vector_hybrid",
                }
            )
        return sorted(rows, key=lambda row: float(row["score"]), reverse=True)[:top_k]

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
        embedding = await embedding_service.embed(content)
        await self._insert_chunk(
            session,
            kb_id=1,
            document_id=int(document.id),
            content=content,
            chunk_index=0,
            token_count=32,
            embedding=embedding,
            metadata={"document": "demo-policy.md", "source": "seed"},
        )
        await session.commit()

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
