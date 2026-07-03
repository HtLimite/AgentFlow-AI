from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.document_parser import DocumentParseError
from app.services.knowledge_service import knowledge_service
from app.services.persistent_knowledge_service import is_database_error, persistent_knowledge_service
from app.services.rag_service import rag_service

router = APIRouter()


class KnowledgeBaseCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None


class KnowledgeQueryRequest(BaseModel):
    question: str = Field(min_length=1)
    top_k: int = Field(default=5, gt=0, le=20)


@router.get("")
async def list_knowledge_bases(session: AsyncSession = Depends(get_db)) -> list[dict[str, object]]:
    try:
        return await persistent_knowledge_service.list_bases(session)
    except Exception as exc:
        if is_database_error(exc):
            return knowledge_service.list_bases()
        raise


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_knowledge_base(payload: KnowledgeBaseCreateRequest, session: AsyncSession = Depends(get_db)) -> dict[str, object]:
    try:
        return await persistent_knowledge_service.create_base(session, payload.name, payload.description)
    except Exception as exc:
        if is_database_error(exc):
            return knowledge_service.create_base(payload.name, payload.description)
        raise


@router.get("/{kb_id}/documents")
async def list_documents(kb_id: int, session: AsyncSession = Depends(get_db)) -> list[dict[str, object]]:
    try:
        return await persistent_knowledge_service.list_documents(session, kb_id)
    except Exception as exc:
        if is_database_error(exc):
            return knowledge_service.list_documents(kb_id)
        raise


@router.post("/{kb_id}/documents")
async def upload_document(kb_id: int, file: UploadFile, session: AsyncSession = Depends(get_db)) -> dict[str, object]:
    content = await file.read()
    try:
        document = await persistent_knowledge_service.add_document(session, kb_id, file.filename or "untitled.txt", content)
    except DocumentParseError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        if is_database_error(exc):
            try:
                document = knowledge_service.add_document(kb_id, file.filename or "untitled.txt", content)
            except DocumentParseError as parse_exc:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(parse_exc)) from parse_exc
        else:
            raise
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge base not found")
    return document


@router.post("/{kb_id}/query")
async def query_knowledge_base(kb_id: int, payload: KnowledgeQueryRequest, session: AsyncSession = Depends(get_db)) -> dict[str, object]:
    try:
        return await persistent_knowledge_service.answer(session, kb_id=kb_id, question=payload.question, top_k=payload.top_k)
    except Exception as exc:
        if is_database_error(exc):
            return await rag_service.answer(kb_id=kb_id, question=payload.question, top_k=payload.top_k)
        raise
