from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def list_prompts() -> list[dict[str, object]]:
    return [
        {
            "id": 1,
            "name": "RAG 问答模板",
            "current_version": 1,
            "variables": ["question", "context"],
        }
    ]
