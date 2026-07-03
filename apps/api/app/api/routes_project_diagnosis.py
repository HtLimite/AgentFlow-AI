from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.project_diagnosis_service import project_diagnosis_service

router = APIRouter()


class ProjectFile(BaseModel):
    path: str = Field(min_length=1, max_length=240)
    content: str = Field(default="", max_length=20000)


class ServiceStatus(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    status: str = Field(min_length=1, max_length=80)
    detail: str | None = Field(default=None, max_length=1000)


class ProjectDiagnosisRequest(BaseModel):
    project_name: str = Field(default="未命名项目", min_length=1, max_length=120)
    repository_url: str | None = Field(default=None, max_length=300)
    runtime: str | None = Field(default=None, max_length=300)
    question: str | None = Field(default=None, max_length=1000)
    logs: str = Field(default="", max_length=40000)
    files: list[ProjectFile] = Field(default_factory=list, max_length=12)
    services: list[ServiceStatus] = Field(default_factory=list, max_length=30)


@router.get("/demo")
async def demo_project_diagnosis() -> dict[str, object]:
    return project_diagnosis_service.analyze(project_diagnosis_service.demo_payload())


@router.post("/analyze")
async def analyze_project(payload: ProjectDiagnosisRequest) -> dict[str, object]:
    return project_diagnosis_service.analyze(payload.model_dump())
