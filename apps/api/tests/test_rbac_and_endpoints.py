from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

VIEWER_HEADERS = {"X-User-Role": "viewer"}
ADMIN_HEADERS = {"X-User-Role": "admin"}


def test_create_provider_forbidden_for_viewer() -> None:
    """RBAC gate runs before any DB access, so the 403 is deterministic without a database."""
    response = client.post("/api/model-providers", headers=VIEWER_HEADERS, json={
        "name": "should-be-blocked",
        "provider_type": "openai-compatible",
        "base_url": "https://example.com/v1",
        "api_key": "sk-test",
        "enabled": True,
    })
    assert response.status_code == 403


def test_create_knowledge_base_forbidden_for_viewer() -> None:
    response = client.post("/api/knowledge-bases", headers=VIEWER_HEADERS, json={"name": "blocked"})
    assert response.status_code == 403


def test_workflow_create_forbidden_for_viewer() -> None:
    response = client.post("/api/workflows", headers=VIEWER_HEADERS, json={
        "name": "blocked",
        "definition": {"nodes": [], "edges": []},
        "enabled": True,
    })
    assert response.status_code == 403


def test_prompt_create_forbidden_for_viewer() -> None:
    response = client.post("/api/prompts", headers=VIEWER_HEADERS, json={
        "name": "blocked",
        "scenario": "general",
        "content": "hello",
    })
    assert response.status_code == 403


def test_eval_run_forbidden_for_viewer() -> None:
    # viewer has eval:read but NOT eval:run, so creating a run must be 403.
    response = client.post("/api/evals/runs", headers=VIEWER_HEADERS, json={"dataset_id": 1, "model": "x"})
    assert response.status_code == 403


def test_invalid_role_defaults_to_viewer_permissions() -> None:
    # An unknown role must not grant manage permissions.
    response = client.post(
        "/api/model-providers",
        headers={"X-User-Role": "superuser-not-defined"},
        json={
            "name": "should-be-blocked",
            "provider_type": "openai-compatible",
            "base_url": "https://example.com/v1",
            "api_key": "sk-test",
            "enabled": True,
        },
    )
    assert response.status_code == 403


def test_audit_export_is_csv() -> None:
    response = client.get("/api/audit/tools/export", headers=ADMIN_HEADERS)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "tool_name" in response.text
