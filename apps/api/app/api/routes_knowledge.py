from fastapi import APIRouter, UploadFile
from pydantic import BaseModel

from app.services.rag_service import rag_service

router = APIRouter()


class KnowledgeQueryRequest(BaseModel):
    question: str
    top_k: int = 5


@router.get("")
async def list_knowledge_bases() -> list[dict[str, object]]:
    return [
        {"id": 1, "name": "企业制度知识库", "document_count": 12, "chunk_count": 368, "status": "ready"}
    ]


@router.post("")
async def create_knowledge_base(name: str, description: str | None = None) -> dict[str, object]:
    return {"id": 1, "name": name, "description": description, "status": "created"}


@router.post("/{kb_id}/documents")
async def upload_document(kb_id: int, file: UploadFile) -> dict[str, object]:
    return {"kb_id": kb_id, "filename": file.filename, "parse_status": "pending"}


@router.post("/{kb_id}/query")
async def query_knowledge_base(kb_id: int, payload: KnowledgeQueryRequest) -> dict[str, object]:
    return await rag_service.answer(kb_id=kb_id, question=payload.question, top_k=payload.top_k)
