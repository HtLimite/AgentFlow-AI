from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl

ProviderType = Literal["openai-compatible", "ollama", "azure-openai"]
ModelType = Literal["chat", "embedding", "rerank"]


class ModelProviderCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    provider_type: ProviderType = "openai-compatible"
    base_url: HttpUrl
    api_key: str = Field(min_length=1)
    enabled: bool = True


class ModelProviderUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    provider_type: ProviderType | None = None
    base_url: HttpUrl | None = None
    api_key: str | None = Field(default=None, min_length=1)
    enabled: bool | None = None


class ModelProviderRead(BaseModel):
    id: int
    name: str
    provider_type: str
    base_url: str
    api_key_masked: str
    enabled: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None


class AIModelCreate(BaseModel):
    provider_id: int
    model_name: str = Field(min_length=1, max_length=128)
    model_type: ModelType = "chat"
    context_window: int | None = None
    input_price: Decimal | None = None
    output_price: Decimal | None = None
    enabled: bool = True


class AIModelUpdate(BaseModel):
    provider_id: int | None = None
    model_name: str | None = Field(default=None, min_length=1, max_length=128)
    model_type: ModelType | None = None
    context_window: int | None = None
    input_price: Decimal | None = None
    output_price: Decimal | None = None
    enabled: bool | None = None


class AIModelRead(BaseModel):
    id: int
    provider_id: int
    model_name: str
    model_type: str
    context_window: int | None
    input_price: Decimal | None
    output_price: Decimal | None
    enabled: bool
    created_at: datetime | None = None
