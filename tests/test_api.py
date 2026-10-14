"""Tests for the FastAPI backend adapter (api/main.py)."""

import os
from fastapi.testclient import TestClient
import pytest

from api.main import app

client = TestClient(app)


def test_health_endpoint_safe_response():
    """Verify health endpoint returns safe fields without exposing secrets."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["workbook_loaded"] is True
    assert data["workflow_count"] >= 10
    assert "llm_configured" in data
    assert data["offline_router_available"] is True

    # Assert no secret material in response
    serialized = response.text.lower()
    assert "api_key" not in serialized
    assert "token" not in serialized
    assert "secret" not in serialized


def test_health_endpoint_never_leaks_synthetic_secret(monkeypatch):
    """Set a synthetic secret in environment and verify it never leaks."""
    synthetic_key = "SYNTHETIC_TEST_SECRET_DO_NOT_LEAK_12345"
    monkeypatch.setenv("GEMINI_API_KEY", synthetic_key)
    monkeypatch.setenv("OPENAI_API_KEY", synthetic_key)

    response = client.get("/api/health")
    assert response.status_code == 200
    assert synthetic_key not in response.text
    assert synthetic_key[:8] not in response.text


def test_workflows_catalog():
    """Verify workflow list includes all 10 core Excel workflows plus WF011 extension."""
    response = client.get("/api/workflows")
    assert response.status_code == 200
    workflows = response.json()
    assert len(workflows) >= 11
    ids = [w["workflow_id"] for w in workflows]
    for i in range(1, 11):
        assert f"WF{i:03d}" in ids
    assert "WF011" in ids

    # Check structure of a workflow
    wf1 = next(w for w in workflows if w["workflow_id"] == "WF001")
    assert wf1["workflow_name"] == "Inventory Restock Check"
    assert len(wf1["parsed_steps"]) == 5
    assert len(wf1["parsed_tools"]) >= 1


def test_examples_endpoint():
    """Verify examples endpoint returns benchmark queries."""
    response = client.get("/api/examples")
    assert response.status_code == 200
    examples = response.json()
    assert len(examples) >= 20
    slugs = [e["slug"] for e in examples]
    assert "wf001_restock_check" in slugs
    assert "unrelated_weather" in slugs


def test_static_runs_endpoint():
    """Verify static demonstration runs can be listed and retrieved."""
    response = client.get("/api/static-runs")
    assert response.status_code == 200
    runs = response.json()
    assert len(runs) >= 20

    # Retrieve specific run
    detail_res = client.get("/api/static-runs/wf001_restock_check")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["selected_workflow_id"] == "WF001"
    assert detail["status"] == "success"

    # 404 on nonexistent slug
    not_found = client.get("/api/static-runs/nonexistent_workflow_xyz")
    assert not_found.status_code == 404


def test_run_empty_request_rejected():
    """Verify empty or whitespace-only requests return HTTP 422."""
    res1 = client.post("/api/run", json={"request": ""})
    assert res1.status_code == 422

    res2 = client.post("/api/run", json={"request": "   \n\t  "})
    assert res2.status_code == 422


def test_run_prohibited_path_inputs_rejected():
    """Verify inputs containing path/file/csv keys or path traversal are rejected with HTTP 422."""
    # Prohibited key containing path
    res1 = client.post("/api/run", json={
        "request": "Process vendor file",
        "inputs": {"csv_path": "/etc/passwd"}
    })
    assert res1.status_code == 422
    assert "Prohibited input key" in res1.json()["detail"]

    # Prohibited key containing file
    res2 = client.post("/api/run", json={
        "request": "Process vendor file",
        "inputs": {"file_name": "data.csv"}
    })
    assert res2.status_code == 422

    # Path traversal in allowed value
    res3 = client.post("/api/run", json={
        "request": "Describe product",
        "inputs": {"product_name": "../../bad_path"}
    })
    assert res3.status_code == 422
    assert "Invalid characters" in res3.json()["detail"]


def test_run_recruiter_request_routes_to_wf001_offline(monkeypatch):
    """Verify recruiter demo query routes offline to WF001 with exit code 0."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    payload = {"request": "Check today's inventory and identify products that need restocking."}
    response = client.post("/api/run", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["selected_workflow_id"] == "WF001"
    assert data["selected_workflow_name"] == "Inventory Restock Check"
    assert data["status"] == "success"
    assert data["routing_mode"] == "offline"
    assert data["exit_code"] == 0
    assert len(data["steps"]) == 5
    assert data["final_output"]["restock_required_count"] == 4


def test_run_forced_route():
    """Verify forced workflow routing is labelled as forced."""
    payload = {
        "request": "Audit vendor catalog",
        "forced_workflow_id": "WF003",
    }
    response = client.post("/api/run", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["selected_workflow_id"] == "WF003"
    assert data["routing_mode"] == "forced"
    assert data["status"] == "success"
    assert data["exit_code"] == 0


def test_run_forced_route_warning_on_mismatch():
    """Verify forced routing emits an advisory warning when query matches a different workflow."""
    payload = {
        "request": "Check today's inventory and identify products that need restocking.",
        "forced_workflow_id": "WF003",
    }
    response = client.post("/api/run", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["selected_workflow_id"] == "WF003"
    assert data["routing_mode"] == "forced"
    assert any("appears to match WF001" in w for w in data["warnings"])


def test_run_unknown_forced_workflow_id_rejected():
    """Verify unknown forced workflow IDs return HTTP 422."""
    payload = {
        "request": "Check inventory",
        "forced_workflow_id": "WF999",
    }
    response = client.post("/api/run", json=payload)
    assert response.status_code == 422
    assert "Unknown workflow ID" in response.json()["detail"]


def test_run_off_topic_query_requires_clarification():
    """Verify unrelated query returns status needs_clarification and exit code 4."""
    payload = {"request": "What is the weather in Paris?"}
    response = client.post("/api/run", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "needs_clarification"
    assert data["clarification_required"] is True
    assert data["selected_workflow_id"] is None
    assert data["exit_code"] == 4
    assert len(data["steps"]) == 0
