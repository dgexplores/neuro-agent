"""Executable API acceptance contracts; Bedrock is the only stubbed service."""
import json
from contextlib import ExitStack
from unittest.mock import AsyncMock
import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from fastapi.testclient import TestClient
from fastapi import HTTPException
from backend.main import app, neuro_agent
from backend.utils.auth import create_access_token

scenarios("features/migraine_diagnosis.feature")

PAYLOAD = {
    "patient_info": {"age": 30, "gender": "other"},
    "symptoms": [{"name": "synthetic symptom", "severity": "mild", "duration_days": 1}],
    "chief_complaint": "Synthetic case", "history_present_illness": "Synthetic input only",
}

@pytest.fixture
def context():
    with ExitStack() as clients:
        yield {"clients": clients}

@given("a configured local assessment application")
def configured(context, monkeypatch, case_store):
    response = {"differential_diagnoses": [{"condition": "Synthetic example", "confidence": 0.5}],
                "recommendations": [], "risk_factors": [], "next_steps": []}
    stub = AsyncMock(return_value={"output": {"text": json.dumps(response)}})
    monkeypatch.setattr(neuro_agent.bedrock_service, "invoke_model_direct", stub)
    api = context["clients"].enter_context(TestClient(app))
    context.update(client=api, store=case_store, stub=stub,
                   headers={"Authorization": "Bearer " + create_access_token("owner", "owner")})

@when("an authenticated owner submits a valid synthetic case")
def submit(context):
    context["response"] = context["client"].post("/api/v1/diagnosis", json=PAYLOAD, headers=context["headers"])

@then("the assessment is stored and retrievable by that owner")
def stored(context):
    response = context["response"]
    assert response.status_code == 200
    result = context["client"].get("/api/v1/cases/" + response.json()["case_id"], headers=context["headers"])
    assert result.status_code == 200
    assert result.json() == response.json()
    context["stub"].assert_awaited_once()

@then("a different owner cannot retrieve that case")
def isolated(context):
    headers={"Authorization": "Bearer " + create_access_token("other", "other")}
    response = context["client"].get("/api/v1/cases/" + context["response"].json()["case_id"], headers=headers)
    assert response.status_code == 404

@when("an authenticated owner submits a case without symptoms")
def invalid(context):
    context["response"] = context["client"].post("/api/v1/diagnosis", json={**PAYLOAD, "symptoms": []}, headers=context["headers"])
    context["stub"].assert_not_awaited()

@when("Bedrock fails while assessing a synthetic case")
def provider_failure(context):
    context["stub"].side_effect = HTTPException(status_code=503, detail="Assessment model unavailable")
    submit(context)

@then(parsers.parse("the API rejects the request with status {code:d}"))
def failure(context, code):
    assert context["response"].status_code == code

@then("no case response has been persisted")
def not_saved(context):
    import sqlite3
    from contextlib import closing
    with closing(sqlite3.connect(context["store"].path)) as connection:
        assert connection.execute("SELECT COUNT(*) FROM cases").fetchone()[0] == 0
