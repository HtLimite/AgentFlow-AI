from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "agentflow-api"}


def test_full_health_accepts_empty_tool_audit_records() -> None:
    response = client.get("/api/system/health/full")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["modules"]["tool_audit"] is True
    assert payload["counts"]["audit_records"] >= 0
    assert payload["failed_modules"] == []


def test_tools_are_registered() -> None:
    response = client.get("/api/tools")

    assert response.status_code == 200
    payload = response.json()
    tool_names = {item["name"] for item in payload}
    assert {"knowledge_search", "calculator", "sql_query", "http_request"}.issubset(tool_names)
