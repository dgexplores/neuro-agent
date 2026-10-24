"""Synthetic-only access boundaries and durable inference budgets. No model calls."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import importlib
import sqlite3
import uuid
from unittest.mock import AsyncMock, Mock, patch

import boto3
from botocore.exceptions import ClientError
from botocore.stub import Stubber
from fastapi import HTTPException
from fastapi.testclient import TestClient
import pytest

from backend.services.case_store import SQLiteCaseStore, get_case_store
from backend.services.demo_access import DynamoDBDemoBudget, SQLiteDemoBudget, get_demo_budget
from backend.utils.auth import create_access_token, verify_token


@pytest.fixture
def api(tmp_path, monkeypatch):
    monkeypatch.setenv("DEMO_ACCESS_ENABLED", "true")
    with patch("backend.services.bedrock_service.BedrockService"):
        main = importlib.import_module("backend.main")
    store = SQLiteCaseStore(str(tmp_path / "cases.sqlite3"))
    main.app.dependency_overrides[get_case_store] = lambda: store
    result = {
        "case_id": str(uuid.uuid4()), "diagnosis": [{"condition": "Synthetic output", "confidence": .4}],
        "confidence": .4, "recommendations": [], "risk_factors": [], "next_steps": [],
    }
    analyze = AsyncMock(return_value=result)
    monkeypatch.setattr(main.neuro_agent, "analyze_case", analyze)
    with TestClient(main.app) as client:
        yield client, analyze, store
    main.app.dependency_overrides.pop(get_case_store, None)
    main.app.dependency_overrides.pop(get_demo_budget, None)


def start(client):
    response = client.post("/api/v1/demo/session")
    assert response.status_code == 200
    return response.json(), {"Authorization": "Bearer " + response.json()["access_token"]}


def test_disabled_by_default_cannot_issue_tokens_or_invoke(api, monkeypatch):
    client, analyze, _ = api
    _, headers = start(client)
    monkeypatch.delenv("DEMO_ACCESS_ENABLED", raising=False)
    assert client.get("/api/v1/demo/config").json() == {"enabled": False}
    assert client.post("/api/v1/demo/session").status_code == 404
    assert client.post("/api/v1/demo/diagnosis", json={"sample_id": "fictional-headache"}, headers=headers).status_code == 404
    analyze.assert_not_called()


def test_sessions_are_short_lived_and_have_distinct_owners(api):
    client, _, _ = api
    first, _ = start(client)
    second, _ = start(client)
    assert first["expires_in"] == 900
    assert first["scope"] == "demo"
    assert verify_token(first["access_token"], allow_demo=True) != verify_token(second["access_token"], allow_demo=True)
    expired = create_access_token("demo-" + str(uuid.uuid4()), "synthetic", {
        "scope": "demo", "exp": datetime.now(timezone.utc) - timedelta(seconds=1),
    })
    response = client.post("/api/v1/demo/diagnosis", json={"sample_id": "fictional-headache"},
                           headers={"Authorization": "Bearer " + expired})
    assert response.status_code == 401


def test_server_owned_input_and_private_case_retrieval(api):
    client, analyze, _ = api
    _, first = start(client)
    _, second = start(client)
    created = client.post("/api/v1/demo/diagnosis", json={"sample_id": "fictional-headache"}, headers=first)
    assert created.status_code == 200
    submitted = analyze.call_args.args[0]
    assert submitted.patient_info.age == 32
    assert "invented" in submitted.history_present_illness.lower()
    assert "expected_diagnosis" not in submitted.model_dump()
    case_id = created.json()["case_id"]
    assert client.get("/api/v1/cases/" + case_id, headers=first).json() == created.json()
    hidden = client.get("/api/v1/cases/" + case_id, headers=second)
    missing = client.get("/api/v1/cases/unknown", headers=second)
    assert hidden.status_code == missing.status_code == 404
    assert hidden.json() == missing.json()


def test_demo_token_cannot_access_unrestricted_endpoints(api):
    client, analyze, _ = api
    _, headers = start(client)
    sample = client.get("/api/v1/demo/config").json()["samples"][0]["request"]
    assert client.post("/api/v1/diagnosis", json=sample, headers=headers).status_code == 403
    assert client.post("/api/v1/drug-interactions", json={"medications": ["a", "b"]}, headers=headers).status_code == 403
    assert client.post("/api/v1/upload-image", files={"file": ("test.png", b"fake", "image/png")}, headers=headers).status_code == 403
    analyze.assert_not_called()


def test_demo_route_rejects_extra_user_input_and_normal_tokens(api):
    client, analyze, _ = api
    _, headers = start(client)
    assert client.post("/api/v1/demo/diagnosis", json={"sample_id": "fictional-headache", "chief_complaint": "user input"}, headers=headers).status_code == 422
    assert client.post("/api/v1/demo/diagnosis", json={"sample_id": "unknown"}, headers=headers).status_code == 404
    normal = {"Authorization": "Bearer " + create_access_token("operator", "operator")}
    assert client.post("/api/v1/demo/diagnosis", json={"sample_id": "fictional-headache"}, headers=normal).status_code == 403
    analyze.assert_not_called()


def test_failed_provider_call_is_not_mocked_and_reservation_is_not_refunded(api):
    client, analyze, store = api
    _, headers = start(client)
    analyze.side_effect = HTTPException(status_code=503, detail="Assessment model unavailable")
    first = client.post("/api/v1/demo/diagnosis", json={"sample_id": "fictional-headache"}, headers=headers)
    assert first.status_code == 503
    assert first.json() == {"detail": "Assessment model unavailable"}
    # Reopen the database to prove this is durable, rather than process-local state.
    import backend.main as main
    main.app.dependency_overrides[get_case_store] = lambda: SQLiteCaseStore(store.path)
    second = client.post("/api/v1/demo/diagnosis", json={"sample_id": "fictional-headache"}, headers=headers)
    assert second.status_code == 429
    analyze.assert_awaited_once()


def test_storage_reservation_failure_prevents_model_call(api, monkeypatch):
    client, analyze, _ = api
    _, headers = start(client)
    monkeypatch.setattr(SQLiteDemoBudget, "reserve", Mock(side_effect=sqlite3.OperationalError("private path")))
    response = client.post("/api/v1/demo/diagnosis", json={"sample_id": "fictional-headache"}, headers=headers)
    assert response.status_code == 503
    assert "private path" not in response.text
    analyze.assert_not_called()


def test_sqlite_atomic_global_daily_cap_under_concurrency(tmp_path):
    store = SQLiteCaseStore(str(tmp_path / "budget.sqlite3"))
    budget = SQLiteDemoBudget(store.path)
    now = datetime(2026, 10, 24, 23, 59, tzinfo=timezone.utc)
    def attempt(owner):
        try:
            budget.reserve(owner, now=now)
            return 200
        except HTTPException as failure:
            return failure.status_code
    with ThreadPoolExecutor(max_workers=12) as executor:
        statuses = list(executor.map(attempt, [str(uuid.uuid4()) for _ in range(16)]))
    assert statuses.count(200) == 10
    assert statuses.count(429) == 6
    reopened = SQLiteDemoBudget(store.path)
    with pytest.raises(HTTPException):
        reopened.reserve("new", now=now)
    reopened.reserve("new", now=now + timedelta(minutes=2))


def test_sqlite_atomic_per_session_cap_does_not_consume_global_on_rejection(tmp_path):
    store = SQLiteCaseStore(str(tmp_path / "budget.sqlite3"))
    budget = SQLiteDemoBudget(store.path)
    def attempt(_):
        try:
            budget.reserve("same-owner")
            return True
        except HTTPException:
            return False
    with ThreadPoolExecutor(max_workers=8) as executor:
        assert sum(executor.map(attempt, range(8))) == 1
    for index in range(9):
        budget.reserve("other-" + str(index))
    with pytest.raises(HTTPException):
        budget.reserve("eleventh")


def test_dynamodb_reserves_both_limits_in_one_conditional_transaction():
    client = Mock()
    budget = DynamoDBDemoBudget("cases", client=client)
    budget.reserve("demo-owner", now=datetime(2026, 10, 24, tzinfo=timezone.utc))
    transaction = client.transact_write_items.call_args.kwargs["TransactItems"]
    assert len(transaction) == 2
    assert transaction[0]["Update"]["TableName"] == transaction[1]["Put"]["TableName"] == "cases"
    assert transaction[0]["Update"]["ExpressionAttributeValues"][":limit"] == {"N": "10"}
    assert "#used < :limit" in transaction[0]["Update"]["ConditionExpression"]
    assert transaction[1]["Put"]["ConditionExpression"] == "attribute_not_exists(case_id)"
    assert transaction[1]["Put"]["Item"]["expires_at"]["N"].isdigit()
    # Validate the low-level DynamoDB wire shape against botocore, without AWS.
    wire_client = boto3.client("dynamodb", region_name="us-east-1", aws_access_key_id="synthetic", aws_secret_access_key="synthetic")
    with Stubber(wire_client) as stubber:
        stubber.add_response("transact_write_items", {}, {"TransactItems": transaction})
        DynamoDBDemoBudget("cases", client=wire_client).reserve("demo-owner", now=datetime(2026, 10, 24, tzinfo=timezone.utc))
        stubber.assert_no_pending_responses()


def test_dynamodb_only_conditional_failures_are_reported_as_limit():
    client = Mock()
    budget = DynamoDBDemoBudget("cases", client=client)
    client.transact_write_items.side_effect = ClientError({
        "Error": {"Code": "TransactionCanceledException", "Message": "conditional"},
        "CancellationReasons": [{"Code": "None"}, {"Code": "ConditionalCheckFailed"}],
    }, "TransactWriteItems")
    with pytest.raises(HTTPException) as failure:
        budget.reserve("same")
    assert failure.value.status_code == 429
    client.transact_write_items.side_effect = ClientError({
        "Error": {"Code": "TransactionCanceledException", "Message": "throughput"},
        "CancellationReasons": [{"Code": "ProvisionedThroughputExceeded"}],
    }, "TransactWriteItems")
    with pytest.raises(ClientError):
        budget.reserve("same")
