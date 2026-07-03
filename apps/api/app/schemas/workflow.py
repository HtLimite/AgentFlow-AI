from typing import Any, Literal

from pydantic import BaseModel, Field

WorkflowNodeType = Literal["start", "knowledge", "llm", "condition", "http", "end"]


class WorkflowNode(BaseModel):
    id: str
    type: WorkflowNodeType
    data: dict[str, Any] = Field(default_factory=dict)


class WorkflowEdge(BaseModel):
    source: str
    target: str
    condition: str | None = None


class WorkflowDefinition(BaseModel):
    nodes: list[WorkflowNode]
    edges: list[WorkflowEdge]


class WorkflowRunRequest(BaseModel):
    input: dict[str, Any]
    definition: WorkflowDefinition | None = None
