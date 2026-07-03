# API 设计

## System

- `GET /health`

## Dashboard

- `GET /api/dashboard/summary`
- `GET /api/dashboard/recent-errors`

## Model Providers

- `GET /api/model-providers`
- `POST /api/model-providers`
- `GET /api/model-providers/{provider_id}`
- `PUT /api/model-providers/{provider_id}`
- `DELETE /api/model-providers/{provider_id}`
- `POST /api/model-providers/{provider_id}/test`

API Key 仅在创建/更新时传入，后端使用 Fernet 加密保存，查询接口只返回 `api_key_masked`。

## Models

- `GET /api/model-providers/models/list`
- `POST /api/model-providers/models`

## Chat

- `POST /api/chat/completions`
- `POST /api/chat/completions/stream`

## Knowledge Base

- `GET /api/knowledge-bases`
- `POST /api/knowledge-bases`
- `POST /api/knowledge-bases/{kb_id}/documents`
- `POST /api/knowledge-bases/{kb_id}/query`

## Agent

- `GET /api/agents`
- `POST /api/agents/{agent_id}/chat`

## Workflow

- `GET /api/workflows`
- `POST /api/workflows/{workflow_id}/run`
