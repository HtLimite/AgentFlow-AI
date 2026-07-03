from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_project_diagnosis_detects_port_and_database_issues() -> None:
    response = client.post(
        "/api/project-diagnosis/analyze",
        json={
            "project_name": "AgentFlow-AI",
            "runtime": "Windows 本地 uv + Docker",
            "source": "demo_sample",
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
    assert payload["source"] == "demo_sample"
    assert payload["severity"] == "critical"
    assert payload["readiness_score"] < 100
    assert payload["actions"]
    assert payload["artifacts"][0]["name"] == "diagnosis-report.md"


def test_project_diagnosis_demo_endpoint_returns_useful_result() -> None:
    response = client.get("/api/project-diagnosis/demo")

    assert response.status_code == 200
    payload = response.json()
    assert payload["project_name"] == "AgentFlow-AI"
    assert payload["source"] == "demo_sample"
    assert payload["mode"] == "local_rules_devops_diagnosis"
    assert payload["next_verification"]


def test_project_diagnosis_ignores_placeholder_descriptions() -> None:
    response = client.post(
        "/api/project-diagnosis/analyze",
        json={
            "project_name": "AgentFlow-AI",
            "runtime": "Windows 本地 uv + Docker",
            "logs": "后端启动报错\nDocker 容器状态\n前端 build 报错\nNginx 502 报错\n数据库连接失败日志",
            "files": [{"path": "diagnosis-notes.txt", "content": "后端启动报错\nDocker 容器状态\n数据库连接失败日志"}],
            "services": [],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    signal_ids = {item["id"] for item in payload["signals"]}
    assert "database_connection" not in signal_ids
    assert "nginx_upstream" not in signal_ids
    assert payload["severity"] == "warning"
    assert payload["source"] == "manual_input"
    assert "真实诊断输入" in payload["summary"]
}
