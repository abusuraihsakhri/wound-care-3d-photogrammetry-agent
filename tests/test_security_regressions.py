"""Regression tests for audit integrity, validation, and API error boundaries."""
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from agents.base import AuditTrail, SecurityException
from agents.models import SystemTaskPayload
from agents.api import app


def test_hmac_signature_detects_modified_entry():
    trail = AuditTrail(secret_key="isolated-test-key")
    trail.log("test", "worker", "evaluate", {"task_id": "DEMO-001"})
    assert trail.verify_integrity() is True
    trail.logs[0]["event_type"] = "changed-after-signature"
    assert trail.verify_integrity() is False


def test_hmac_signature_detects_forged_tail():
    trail = AuditTrail(secret_key="isolated-test-key")
    trail.log("test", "worker", "evaluate", {"task_id": "DEMO-001"})
    trail.logs[0]["current_hash"] = "0" * 64
    assert trail.verify_integrity() is False


def test_get_trail_is_copy():
    trail = AuditTrail(secret_key="isolated-test-key")
    trail.log("test", "worker", "evaluate", {"task_id": "DEMO-001"})
    observed = trail.get_trail()
    observed[0]["event_type"] = "injected"
    assert trail.verify_integrity() is True
    assert trail.get_trail()[0]["event_type"] == "evaluate"


@pytest.mark.parametrize("kwargs", [
    {"task_id": "  "},
    {"target_identifier": ""},
    {"status_descriptor": "\r\nheader"},
    {"primary_metric": float("nan")},
    {"secondary_metric": float("inf")},
])
def test_invalid_payload_rejected(kwargs):
    data = {"task_id": "T1", "target_identifier": "SAMPLE-1", "primary_metric": 12.0,
            "secondary_metric": 3.0, "status_descriptor": "NOMINAL"}
    data.update(kwargs)
    with pytest.raises(ValidationError):
        SystemTaskPayload(**data)


def test_http_rejects_phi_without_server_error():
    client = TestClient(app)
    response = client.post("/api/audit", json={
        "task_id": "T1", "target_identifier": "MRN-123456", "primary_metric": 10.0
    })
    assert response.status_code == 422
    assert "MRN-123456" not in response.text


def test_http_rejects_phi_inside_attributes():
    client = TestClient(app)
    response = client.post("/api/audit", json={
        "task_id": "T1", "target_identifier": "SAMPLE-1",
        "primary_metric": 10.0, "attributes": {"contact": "alice@example.com"}
    })
    assert response.status_code == 422


def test_static_console_serves_relative_asset():
    client = TestClient(app)
    html = client.get("/")
    script = client.get("/app.js")
    assert html.status_code == 200 and 'src="./app.js"' in html.text
    assert script.status_code == 200 and "function evaluateRule" in script.text
