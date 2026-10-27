"""Synthetic local persistence and HTTP authorization tests. No AWS calls."""

import importlib
import sqlite3
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from backend.services.case_store import SQLiteCaseStore, get_case_store


@pytest.fixture
def store(tmp_path):
    return SQLiteCaseStore(str(tmp_path / "cases.sqlite3"))


def test_persists_after_reopen(store):
    response = {"case_id": "case-1", "diagnosis": [{"condition": "synthetic"}]}
    store.save("alice", response)
    reopened = SQLiteCaseStore(store.path)
    assert reopened.get("alice", "case-1") == response
    assert reopened.get("bob", "case-1") is None
    assert reopened.get("alice", "missing") is None


def test_duplicate_cannot_replace_original_owner(store):
    store.save("alice", {"case_id": "case-1", "value": "original"})
    with pytest.raises(sqlite3.IntegrityError):
        store.save("bob", {"case_id": "case-1", "value": "replacement"})
    assert store.get("alice", "case-1")["value"] == "original"
    assert store.get("bob", "case-1") is None


def test_lookup_uses_parameters(store):
    store.save("alice", {"case_id": "case-1"})
    assert store.get("alice", "case-1' OR 1=1 --") is None
    assert store.get("alice' OR 1=1 --", "case-1") is None


@pytest.fixture
def api(store, monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "synthetic-test-secret-only")
    # Patch construction before importing the application: no credentials or AWS.
    with patch("backend.services.bedrock_service.BedrockService"):
        main = importlib.import_module("backend.main")
    result = {
        "case_id": "synthetic-case-1",
        "diagnosis": [{"condition": "Synthetic example", "confidence": 0.5}],
        "confidence": 0.5,
        "recommendations": ["Synthetic response"],
        "risk_factors": [],
        "next_steps": [],
    }
    monkeypatch.setattr(main.neuro_agent, "analyze_case", AsyncMock(return_value=result))
    main.app.dependency_overrides[get_case_store] = lambda: store
    from backend.utils.auth import create_access_token
    headers = {
        owner: {"Authorization": "Bearer " + create_access_token(owner, owner)}
        for owner in ("alice", "bob")
    }
    with TestClient(main.app) as client:
        yield client, headers, main
    main.app.dependency_overrides.clear()


PAYLOAD = {
    "patient_info": {"age": 30, "gender": "other"},
    "symptoms": [{"name": "synthetic symptom", "severity": "mild", "duration_days": 1}],
    "chief_complaint": "Synthetic local test",
    "history_present_illness": "Synthetic data only",
}


def test_create_then_retrieve_exact_response_and_isolate_owners(api):
    client, headers, _ = api
    created = client.post("/api/v1/diagnosis", json=PAYLOAD, headers=headers["alice"])
    assert created.status_code == 200
    case_id = created.json()["case_id"]
    retrieved = client.get(f"/api/v1/cases/{case_id}", headers=headers["alice"])
    assert retrieved.status_code == 200
    assert retrieved.json() == created.json()
    hidden = client.get(f"/api/v1/cases/{case_id}", headers=headers["bob"])
    missing = client.get("/api/v1/cases/missing", headers=headers["bob"])
    assert hidden.status_code == missing.status_code == 404
    assert hidden.json() == missing.json()


def test_invalid_auth_remains_401(api):
    client, _, _ = api
    response = client.get("/api/v1/cases/anything", headers={"Authorization": "Bearer invalid"})
    assert response.status_code == 401


def test_missing_auth_is_rejected(api):
    client, _, _ = api
    assert client.get("/api/v1/cases/anything").status_code == 401


def test_storage_failure_is_not_reported_as_missing_case(api, store, monkeypatch):
    client, headers, _ = api
    def unavailable(*args):
        raise sqlite3.OperationalError("private database path")
    monkeypatch.setattr(store, "get", unavailable)
    response = client.get("/api/v1/cases/anything", headers=headers["alice"])
    assert response.status_code == 503
    assert "private database path" not in response.text


def test_create_storage_failure_does_not_return_unsaved_success(api, store, monkeypatch):
    client, headers, _ = api
    def unavailable(*args):
        raise sqlite3.OperationalError("private database path")
    monkeypatch.setattr(store, "save", unavailable)
    response = client.post("/api/v1/diagnosis", json=PAYLOAD, headers=headers["alice"])
    assert response.status_code == 503
    assert "private database path" not in response.text


def test_storage_initialization_failure_is_sanitized(tmp_path, monkeypatch):
    monkeypatch.setenv("CASE_DB_PATH", str(tmp_path))  # A directory cannot be a database.
    with pytest.raises(HTTPException) as error:
        get_case_store()
    assert error.value.status_code == 503
    assert error.value.detail == "Case storage unavailable"


def test_dynamodb_owner_scope_and_conditional_insert():
    from unittest.mock import Mock
    from backend.services.case_store import DynamoDBCaseStore
    table = Mock()
    store = DynamoDBCaseStore('cases', table=table)
    response = {'case_id': 'case-1', 'confidence': 0.5}
    store.save('alice', response)
    request = table.put_item.call_args.kwargs
    assert request['ConditionExpression'] == 'attribute_not_exists(case_id)'
    assert request['Item']['owner_id'] == 'alice'
    table.get_item.return_value = {'Item': request['Item']}
    assert store.get('alice', 'case-1') == response
    assert store.get('bob', 'case-1') is None
    table.get_item.assert_called_with(Key={'case_id': 'case-1'}, ConsistentRead=True)
    table.get_item.return_value = {}
    assert store.get('alice', 'missing') is None


def test_cloud_backend_requires_table_name(monkeypatch):
    monkeypatch.setenv('CASE_STORE_BACKEND', 'dynamodb')
    monkeypatch.delenv('DYNAMODB_TABLE_NAME', raising=False)
    with pytest.raises(HTTPException) as error:
        get_case_store()
    assert error.value.status_code == 503
