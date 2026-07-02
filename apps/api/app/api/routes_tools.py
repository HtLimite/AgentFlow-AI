from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def list_tools() -> list[dict[str, object]]:
    return [
        {"name": "knowledge_search", "type": "retrieval", "enabled": True},
        {"name": "sql_query", "type": "database", "enabled": True},
        {"name": "http_request", "type": "http", "enabled": True},
        {"name": "calculator", "type": "utility", "enabled": True},
    ]
