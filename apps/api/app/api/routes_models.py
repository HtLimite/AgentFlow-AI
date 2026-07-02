from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.core.security import mask_secret

router = APIRouter()


class ModelProviderCreate(BaseModel):
    name: str
    provider_type: str = Field(default="openai-compatible")
    base_url: str
    api_key: str
    enabled: bool = True


@router.get("")
async def list_model_providers() -> list[dict[str, object]]:
    return [
        {
            "id": 1,
            "name": "OpenAI Compatible",
            "provider_type": "openai-compatible",
            "base_url": "https://api.openai.com/v1",
            "api_key_masked": "sk-****demo",
            "enabled": True,
        }
    ]


@router.post("")
async def create_model_provider(payload: ModelProviderCreate) -> dict[str, object]:
    return {
        "id": 1,
        "name": payload.name,
        "provider_type": payload.provider_type,
        "base_url": payload.base_url,
        "api_key_masked": mask_secret(payload.api_key),
        "enabled": payload.enabled,
    }


@router.post("/{provider_id}/test")
async def test_model_provider(provider_id: int) -> dict[str, object]:
    return {"provider_id": provider_id, "ok": True, "latency_ms": 320}
