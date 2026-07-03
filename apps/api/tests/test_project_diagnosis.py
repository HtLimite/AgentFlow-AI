from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_project_diagnosis_detects_port_and_database_issues() -> None:
    response = client.post(
        "/api/project-diagnosis/analyze",
        json={
            "project_name": "AgentFlow-AI",
            "runtime": "Windows 本地 uv + Docker",
            "logs": "port is already allocated\npsycopg OperationalError connection refused",
            "files": [{"path": "deploy/docker-compose.yml", "content": "services:\n  postgres:\n    image: pgvector/pgvector:pg16"}],
            "services": [{"name": "agentflow-api", "status": "exited", "detail": "connection refused"}],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    signal_ids = {item["id"] for item in payload["signals"]}
    assert "port_conflict" in signal_ids
    assert "database_connection" in signal_ids
    assert payload["severity"] == "critical"
    assert payload["readiness_score"] < 100
    assert payload["actions"]
    assert payload["artifacts"][0]["name"] == "diagnosis-report.md"


def test_project_diagnosis_demo_endpoint_returns_useful_result() -> None:
    response = client.get("/api/project-diagnosis/demo")

    assert response.status_code == 200
    payload = response.json()
    assert payload["project_name"] == "AgentFlow-AI"
    assert payload["mode"] == "local_rules_devops_diagnosis"
    assert payload["next_verification"]
