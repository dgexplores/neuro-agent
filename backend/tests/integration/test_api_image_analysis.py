"""Real HTTP image adapter contracts with botocore's offline provider stub."""
import base64
import json
from io import BytesIO
from unittest.mock import patch

import boto3
import pytest
from botocore.response import StreamingBody
from botocore.stub import ANY, Stubber
from fastapi.testclient import TestClient

from backend.main import app, neuro_agent
from backend.utils.auth import create_access_token

PNG = b'\x89PNG\r\n\x1a\n' + b'synthetic-image-fixture'
JPEG = b'\xff\xd8\xff' + b'synthetic-image-fixture'
ANALYSIS = {'findings': ['Synthetic test observation'], 'limitations': ['Not clinical inference'],
            'impression': 'Synthetic provider result'}


@pytest.fixture
def image_api(monkeypatch):
    client = boto3.client('bedrock-runtime', region_name='us-east-1',
                          aws_access_key_id='testing', aws_secret_access_key='testing')
    service = neuro_agent.bedrock_service
    monkeypatch.setattr(service, '_bedrock_runtime', client)
    monkeypatch.setattr(service, 'model_id', 'anthropic.claude-3-sonnet-20240229-v1:0')
    monkeypatch.delenv('S3_BUCKET_NAME', raising=False)
    with TestClient(app) as api, Stubber(client) as stub:
        headers = {'Authorization': 'Bearer ' + create_access_token('image-owner', 'image-owner')}
        yield api, headers, stub
        stub.assert_no_pending_responses()


def add_response(stub, analysis=ANALYSIS):
    payload = json.dumps({'content': [{'type': 'text', 'text': json.dumps(analysis)}]}).encode()
    stub.add_response('invoke_model', {
        'body': StreamingBody(BytesIO(payload), len(payload)), 'contentType': 'application/json',
    }, {'modelId': 'anthropic.claude-3-sonnet-20240229-v1:0', 'body': ANY,
        'accept': 'application/json', 'contentType': 'application/json'})


def upload(fixture, data=PNG, content_type='image/png'):
    api, headers, _ = fixture
    return api.post('/api/v1/upload-image', headers=headers,
                    files={'file': ('synthetic.png', BytesIO(data), content_type)})


@pytest.mark.parametrize('data,media_type', [(PNG, 'image/png'), (JPEG, 'image/jpeg')],
                         ids=['png', 'jpeg'])
def test_image_model_receives_actual_content_and_returns_provider_observations(image_api, data, media_type):
    _, _, stub = image_api
    add_response(stub)
    with patch.object(stub.client, 'invoke_model', wraps=stub.client.invoke_model) as invoke:
        response = upload(image_api, data, media_type)
    assert response.status_code == 200
    assert response.json()['analysis'] == ANALYSIS
    assert response.json()['image_metadata']['storage_location'] is None
    request = json.loads(invoke.call_args.kwargs['body'])
    source = request['messages'][0]['content'][0]['source']
    assert source['type'] == 'base64'
    assert source['media_type'] == media_type
    assert base64.b64decode(source['data']) == data
    assert 'qualified review' in request['messages'][0]['content'][1]['text']


@pytest.mark.parametrize('data,media_type,status', [
    (b'not an image', 'image/png', 400),
    (PNG, 'image/jpeg', 400),
    (PNG, 'image/gif', 415),
    (b'plain text', 'text/plain', 400),
    (PNG + b'x' * 3_750_000, 'image/png', 413),
], ids=['invalid-signature', 'media-type-mismatch', 'unsupported-image-type',
        'unsupported-text-type', 'oversized-image'])
def test_invalid_or_unsupported_upload_does_not_call_provider(image_api, data, media_type, status):
    assert upload(image_api, data, media_type).status_code == status


def test_upload_requires_authentication(image_api):
    api, _, _ = image_api
    assert api.post('/api/v1/upload-image', files={'file': ('image.png', PNG, 'image/png')}).status_code == 401


def test_unsupported_model_reports_501_without_fake_findings(image_api, monkeypatch):
    monkeypatch.setattr(neuro_agent.bedrock_service, 'model_id', 'mistral.mistral-large-2402-v1:0')
    response = upload(image_api)
    assert response.status_code == 501
    assert 'analysis' not in response.json()


def test_provider_failure_reports_503(image_api):
    image_api[2].add_client_error('invoke_model', service_error_code='AccessDeniedException')
    response = upload(image_api)
    assert response.status_code == 503
    assert 'findings' not in response.text


def test_malformed_provider_output_reports_503(image_api):
    add_response(image_api[2], {'impression': 'missing fields'})
    assert upload(image_api).status_code == 503


def test_configured_s3_persists_actual_image_bytes(image_api, monkeypatch):
    monkeypatch.setenv('S3_BUCKET_NAME', 'synthetic-test-bucket')
    s3 = boto3.client('s3', region_name='us-east-1', aws_access_key_id='testing', aws_secret_access_key='testing')
    add_response(image_api[2])
    with Stubber(s3) as stub:
        stub.add_response('put_object', {}, {'Bucket': 'synthetic-test-bucket', 'Key': ANY, 'Body': PNG,
                          'ContentType': 'image/png', 'ServerSideEncryption': 'AES256'})
        with patch('boto3.client', return_value=s3):
            response = upload(image_api)
        assert response.status_code == 200
        assert response.json()['image_metadata']['storage_location'].startswith('s3://synthetic-test-bucket/')
        stub.assert_no_pending_responses()
