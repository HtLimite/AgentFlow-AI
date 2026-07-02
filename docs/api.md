# API 设计

## System

- `GET /health`

## Dashboard

- `GET /api/dashboard/summary`
- `GET /api/dashboard/recent-errors`

## Model Providers

- `GET /api/model-providers`
- `POST /api/model-providers`
- `POST /api/model-providers/{provider_id}/test`

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
