"""Offline Bedrock and DynamoDB SDK contract tests."""
import json
from io import BytesIO
from unittest.mock import Mock

import boto3
import pytest
from botocore.response import StreamingBody
from botocore.stub import ANY, Stubber
from fastapi import HTTPException

from backend.services.bedrock_service import BedrockService
from backend.services.case_store import DynamoDBCaseStore
from backend.agents.neuro_agent import NeuroAgent


def runtime(name):
    return boto3.client(name, region_name="us-east-1", aws_access_key_id="testing", aws_secret_access_key="testing")


@pytest.mark.asyncio
@pytest.mark.parametrize("family", ["claude", "mistral"])
async def test_text_provider_request_and_response_contract(family):
    client = runtime("bedrock-runtime")
    service = BedrockService()
    service.bedrock_runtime = client
    if family == "claude":
        service.model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
        body = {"anthropic_version": "bedrock-2023-05-31", "messages": [{"role": "user", "content": "synthetic"}], "max_tokens": 4096, "temperature": 0.1}
        output = {"content": [{"text": "synthetic-output"}]}
    else:
        service.model_id = "mistral.mistral-large-2402-v1:0"
        body = {"prompt": "<s>[INST] synthetic [/INST]", "max_tokens": 2048, "temperature": 0.1}
        output = {"outputs": [{"text": "synthetic-output"}]}
    payload = json.dumps(output).encode()
    with Stubber(client) as stub:
        stub.add_response("invoke_model", {"body": StreamingBody(BytesIO(payload), len(payload)), "contentType": "application/json"},
                          {"modelId": service.model_id, "body": json.dumps(body), "accept": "application/json", "contentType": "application/json"})
        assert await service.invoke_model_direct("synthetic") == {"output": {"text": "synthetic-output"}}
        stub.assert_no_pending_responses()


@pytest.mark.asyncio
async def test_model_failure_is_not_a_successful_assessment():
    service = BedrockService()
    service.model_id = "amazon.nova-lite-v1:0"
    service.bedrock_runtime = runtime("bedrock-runtime")
    with Stubber(service.bedrock_runtime) as stub:
        stub.add_client_error("converse", service_error_code="AccessDeniedException")
        with pytest.raises(HTTPException) as error:
            await service.invoke_model_direct("synthetic")
        assert error.value.status_code == 503


def converse_response(text, stop="end_turn"):
    return {"output": {"message": {"role": "assistant", "content": [{"text": text}]}},
            "stopReason": stop, "usage": {"inputTokens": 10, "outputTokens": 10, "totalTokens": 20},
            "metrics": {"latencyMs": 1}}


@pytest.mark.asyncio
@pytest.mark.parametrize("model", ["amazon.nova-lite-v1:0", "us.amazon.nova-2-lite-v1:0",
                                  "us.anthropic.claude-haiku-4-5-20251001-v1:0",
                                  "us.anthropic.claude-sonnet-4-6"])
async def test_current_models_use_converse_with_explicit_output_limit(model):
    service = BedrockService()
    service.model_id = model
    service.bedrock_runtime = runtime("bedrock-runtime")
    with Stubber(service.bedrock_runtime) as stub:
        stub.add_response("converse", converse_response("synthetic-output"), {
            "modelId": model, "messages": [{"role": "user", "content": [{"text": "synthetic"}]}],
            "inferenceConfig": {"maxTokens": 4096},
        })
        assert await service.invoke_model_direct("synthetic") == {"output": {"text": "synthetic-output"}}
        stub.assert_no_pending_responses()


@pytest.mark.asyncio
@pytest.mark.parametrize("stop", ["max_tokens", "content_filtered", "guardrail_intervened"])
async def test_truncated_or_refused_converse_output_is_not_a_success(stop):
    service = BedrockService()
    service.model_id = "amazon.nova-lite-v1:0"
    service.bedrock_runtime = runtime("bedrock-runtime")
    with Stubber(service.bedrock_runtime) as stub:
        stub.add_response("converse", converse_response("incomplete", stop), {
            "modelId": service.model_id, "messages": ANY, "inferenceConfig": {"maxTokens": 4096},
        })
        with pytest.raises(HTTPException) as error:
            await service.invoke_model_direct("synthetic")
        assert error.value.status_code == 503


@pytest.mark.asyncio
@pytest.mark.parametrize("model", ["amazon.nova-lite-v1:0", "us.amazon.nova-2-lite-v1:0",
                                  "us.anthropic.claude-haiku-4-5-20251001-v1:0"])
@pytest.mark.parametrize("media_type", ["image/png", "image/jpeg"])
async def test_current_multimodal_models_receive_actual_image_bytes(model, media_type):
    service = BedrockService()
    service.model_id = model
    service.bedrock_runtime = runtime("bedrock-runtime")
    image = b"synthetic-image-bytes"
    analysis = {"findings": ["Synthetic observation"], "limitations": ["Not clinical"], "impression": "Synthetic"}
    with Stubber(service.bedrock_runtime) as stub:
        stub.add_response("converse", converse_response(json.dumps(analysis)), {
            "modelId": model, "messages": [{"role": "user", "content": [
                {"image": {"format": media_type.split("/")[1], "source": {"bytes": image}}},
                {"text": ANY},
            ]}], "inferenceConfig": {"maxTokens": 2048},
        })
        assert await service.analyze_image(image, media_type) == analysis
        stub.assert_no_pending_responses()


@pytest.mark.asyncio
async def test_text_only_nova_micro_rejects_image_without_provider_call():
    service = BedrockService()
    service.model_id = "us.amazon.nova-micro-v1:0"
    service.bedrock_runtime = Mock()
    with pytest.raises(HTTPException) as error:
        await service.analyze_image(b"synthetic", "image/png")
    assert error.value.status_code == 501
    service.bedrock_runtime.converse.assert_not_called()


@pytest.mark.parametrize("score", [True, False, float("nan"), float("inf"), -0.1, 1.1])
def test_invalid_model_confidence_is_rejected(score):
    agent = NeuroAgent(Mock())
    response = {"output": {"text": json.dumps({"differential_diagnoses": [{"condition": "Synthetic", "confidence": score}]})}}
    with pytest.raises(HTTPException) as error:
        agent._parse_agent_response(response)
    assert error.value.status_code == 502


def test_dynamodb_sdk_roundtrip_and_other_owner_rejection():
    resource = boto3.resource("dynamodb", region_name="us-east-1", aws_access_key_id="testing", aws_secret_access_key="testing")
    table = resource.Table("synthetic-cases")
    store = DynamoDBCaseStore("synthetic-cases", table=table)
    response = {"case_id": "case-1", "confidence": 0.5}
    serialized = json.dumps(response)
    with Stubber(table.meta.client) as stub:
        stub.add_response("put_item", {}, {"TableName": "synthetic-cases", "Item": {"case_id": "case-1", "owner_id": "alice", "response_json": serialized}, "ConditionExpression": "attribute_not_exists(case_id)"})
        store.save("alice", response)
        stub.add_response("get_item", {"Item": {"case_id": {"S": "case-1"}, "owner_id": {"S": "alice"}, "response_json": {"S": serialized}}}, {"TableName": "synthetic-cases", "Key": {"case_id": "case-1"}, "ConsistentRead": True})
        assert store.get("alice", "case-1") == response
        stub.add_response("get_item", {"Item": {"case_id": {"S": "case-1"}, "owner_id": {"S": "alice"}, "response_json": {"S": serialized}}}, {"TableName": "synthetic-cases", "Key": {"case_id": "case-1"}, "ConsistentRead": True})
        assert store.get("bob", "case-1") is None
        stub.assert_no_pending_responses()
