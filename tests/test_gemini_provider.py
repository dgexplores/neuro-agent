"""Gemini REST contracts with an offline HTTP transport; no model calls."""
import base64
import json
from unittest.mock import patch

import httpx
import pytest
from fastapi import HTTPException

from backend.services.gemini_service import GeminiService
from backend.services.model_service import create_model_service


def result(text, finish="STOP"):
    return {"candidates": [{"finishReason": finish, "content": {"parts": [{"text": text}]}}]}


@pytest.fixture(autouse=True)
def configuration(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "synthetic-contract-key")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-3.5-flash-lite")


def test_factory_selects_gemini_without_initializing_aws(monkeypatch):
    monkeypatch.setenv("MODEL_PROVIDER", "gemini")
    with patch("boto3.client", side_effect=AssertionError("AWS must stay unused")), \
            patch("boto3.resource", side_effect=AssertionError("AWS must stay unused")):
        assert isinstance(create_model_service(), GeminiService)


def test_factory_preserves_bedrock_default(monkeypatch):
    monkeypatch.delenv("MODEL_PROVIDER", raising=False)
    with patch("backend.services.bedrock_service.BedrockService") as constructor:
        assert create_model_service() is constructor.return_value


def test_factory_rejects_unknown_provider(monkeypatch):
    monkeypatch.setenv("MODEL_PROVIDER", "unsupported")
    with pytest.raises(ValueError, match="MODEL_PROVIDER"):
        create_model_service()


@pytest.mark.asyncio
async def test_text_request_uses_header_credentials_json_mode_and_bounded_output():
    def handler(request):
        assert request.url == "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent"
        assert "synthetic-contract-key" not in str(request.url)
        assert request.headers["x-goog-api-key"] == "synthetic-contract-key"
        assert json.loads(request.content) == {
            "contents": [{"role": "user", "parts": [{"text": "synthetic prompt"}]}],
            "generationConfig": {"maxOutputTokens": 4096, "responseMimeType": "application/json"},
        }
        assert request.extensions["timeout"] == {"connect": 3.0, "read": 30.0, "write": 5.0, "pool": 3.0}
        return httpx.Response(200, json=result('{"differential_diagnoses": []}'))
    service = GeminiService(transport=httpx.MockTransport(handler))
    assert await service.invoke_model_direct("synthetic prompt") == {
        "output": {"text": '{"differential_diagnoses": []}'},
    }


@pytest.mark.asyncio
@pytest.mark.parametrize("media_type", ["image/png", "image/jpeg"])
async def test_image_request_contains_actual_bytes_and_validates_provider_findings(media_type):
    image = b"synthetic-image-content"
    analysis = {"findings": ["Synthetic observation"], "limitations": ["Not clinically validated"],
                "impression": "Synthetic output"}
    def handler(request):
        body = json.loads(request.content)
        content = body["contents"][0]["parts"]
        assert content[0]["inlineData"]["mimeType"] == media_type
        assert base64.b64decode(content[0]["inlineData"]["data"]) == image
        assert "qualified review" in content[1]["text"]
        assert body["generationConfig"]["maxOutputTokens"] == 2048
        return httpx.Response(200, json=result(json.dumps(analysis)))
    service = GeminiService(transport=httpx.MockTransport(handler))
    assert await service.analyze_image(image, media_type) == analysis


@pytest.mark.asyncio
@pytest.mark.parametrize("status", [400, 401, 403, 429, 500, 503])
async def test_provider_errors_hide_response_content_and_credentials(status):
    def handler(request):
        return httpx.Response(status, json={"error": {"message": "synthetic-contract-key sensitive provider detail"}})
    service = GeminiService(transport=httpx.MockTransport(handler))
    with pytest.raises(HTTPException) as error:
        await service.invoke_model_direct("synthetic")
    assert error.value.status_code == 503
    assert error.value.detail == "Assessment model unavailable"
    assert "synthetic-contract-key" not in str(error.value)


@pytest.mark.asyncio
@pytest.mark.parametrize("envelope", [
    {}, [], {"candidates": []}, {"candidates": [None]},
    {"promptFeedback": {"blockReason": "SAFETY"}},
    result("partial", "MAX_TOKENS"), result("refused", "SAFETY"),
    result(""), {"candidates": [{"finishReason": "STOP", "content": {"parts": [{"thought": True, "text": "private reasoning"}]}}]},
])
async def test_incomplete_blocked_or_empty_output_cannot_be_success(envelope):
    service = GeminiService(transport=httpx.MockTransport(lambda request: httpx.Response(200, json=envelope)))
    with pytest.raises(HTTPException) as error:
        await service.invoke_model_direct("synthetic")
    assert error.value.status_code == 503


@pytest.mark.asyncio
async def test_timeout_is_controlled():
    def handler(request):
        raise httpx.ReadTimeout("synthetic timeout", request=request)
    with pytest.raises(HTTPException) as error:
        await GeminiService(transport=httpx.MockTransport(handler)).invoke_model_direct("synthetic")
    assert error.value.status_code == 503


@pytest.mark.asyncio
async def test_missing_key_never_sends_a_request(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY")
    def handler(request):
        raise AssertionError("No request allowed without a key")
    with pytest.raises(HTTPException) as error:
        await GeminiService(transport=httpx.MockTransport(handler)).invoke_model_direct("synthetic")
    assert error.value.status_code == 503


@pytest.mark.asyncio
@pytest.mark.parametrize("text", ["not json", '{}', '{"findings": [1], "limitations": [], "impression": "bad"}'])
async def test_malformed_image_findings_are_not_fabricated(text):
    service = GeminiService(transport=httpx.MockTransport(lambda request: httpx.Response(200, json=result(text))))
    with pytest.raises(HTTPException) as error:
        await service.analyze_image(b"synthetic", "image/png")
    assert error.value.status_code == 503


def test_model_id_cannot_change_api_host_or_path(monkeypatch):
    monkeypatch.setenv("GEMINI_MODEL", "gemini-test/../../other?key=value")
    with pytest.raises(ValueError, match="Invalid Gemini"):
        GeminiService()


def test_demo_http_flow_parses_gemini_output_and_persists_owner_case(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient
    from backend.main import app, neuro_agent
    from backend.services.case_store import SQLiteCaseStore, get_case_store

    monkeypatch.setenv("DEMO_ACCESS_ENABLED", "true")
    output = {"differential_diagnoses": [{"condition": "Synthetic provider assessment", "confidence": .4}],
              "recommendations": [], "risk_factors": [], "next_steps": []}
    requests = []
    def handler(request):
        requests.append(json.loads(request.content))
        return httpx.Response(200, json=result(json.dumps(output)))
    monkeypatch.setattr(neuro_agent, "bedrock_service", GeminiService(transport=httpx.MockTransport(handler)))
    store = SQLiteCaseStore(str(tmp_path / "gemini-cases.sqlite3"))
    app.dependency_overrides[get_case_store] = lambda: store
    try:
        with TestClient(app) as client:
            session = client.post("/api/v1/demo/session").json()["access_token"]
            headers = {"Authorization": "Bearer " + session}
            created = client.post("/api/v1/demo/diagnosis", json={"sample_id": "fictional-headache"}, headers=headers)
            assert created.status_code == 200
            assert created.json()["diagnosis"][0]["condition"] == "Synthetic provider assessment"
            assert "invented" in requests[0]["contents"][0]["parts"][0]["text"].lower()
            path = "/api/v1/cases/" + created.json()["case_id"]
            assert client.get(path, headers=headers).json() == created.json()
            other = client.post("/api/v1/demo/session").json()["access_token"]
            assert client.get(path, headers={"Authorization": "Bearer " + other}).status_code == 404
            assert client.post("/api/v1/demo/diagnosis", json={"sample_id": "fictional-headache"}, headers=headers).status_code == 429
            assert len(requests) == 1
    finally:
        app.dependency_overrides.pop(get_case_store, None)
