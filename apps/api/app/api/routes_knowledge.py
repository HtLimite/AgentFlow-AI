from fastapi import APIRouter, HTTPException, UploadFile, status
from pydantic import BaseModel, Field

from app.services.knowledge_service import knowledge_service
from app.services.rag_service import rag_service

router = APIRouter()


class KnowledgeBaseCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None


class KnowledgeQueryRequest(BaseModel):
    question: str = Field(min_length=1)
    top_k: int = Field(default=5, gt=0, le=20)


@router.get("")
async def list_knowledge_bases() -> list[dict[str, object]]:
    return knowledge_service.list_bases()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_knowledge_base(payload: KnowledgeBaseCreateRequest) -> dict[str, object]:
    return knowledge_service.create_base(payload.name, payload.description)


@router.get("/{kb_id}/documents")
async def list_documents(kb_id: int) -> list[dict[str, object]]:
    return knowledge_service.list_documents(kb_id)


@router.post("/{kb_id}/documents")
async def upload_document(kb_id: int, file: UploadFile) -> dict[str, object]:
    content = await file.read()
    document = knowledge_service.add_document(kb_id, file.filename or "untitled.txt", content)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge base not found")
    return document


@router.post("/{kb_id}/query")
async def query_knowledge_base(kb_id: int, payload: KnowledgeQueryRequest) -> dict[str, object]:
    return await rag_service.answer(kb_id=kb_id, question=payload.question, top_k=payload.top_k)
