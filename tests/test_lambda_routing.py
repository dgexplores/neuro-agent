"""Exercise the actual Mangum entry point with API Gateway REST proxy events."""
import json
from types import SimpleNamespace
import pytest
from backend.main import handler

@pytest.mark.parametrize('path,expected', [
    ('/health', 200),
    ('/openapi.json', 200),
    ('/api/v1/cases/absent', 401),
    ('/unknown-api-route', 404),
])
def test_api_gateway_proxy_preserves_application_routes(path, expected):
    event = {
        'resource': '/{proxy+}', 'path': path, 'httpMethod': 'GET',
        'headers': {'Host': 'example.execute-api.us-east-1.amazonaws.com'},
        'multiValueHeaders': {}, 'queryStringParameters': None,
        'multiValueQueryStringParameters': None,
        'pathParameters': {'proxy': path.lstrip('/')}, 'stageVariables': None,
        'requestContext': {
            'stage': 'prod', 'httpMethod': 'GET', 'path': '/prod' + path,
            'identity': {'sourceIp': '127.0.0.1'},
        },
        'body': None, 'isBase64Encoded': False,
    }
    response = handler(event, SimpleNamespace(aws_request_id='offline-routing-check'))
    assert response['statusCode'] == expected
    if path == '/health':
        assert json.loads(response['body'])['services']['bedrock'] == 'not_checked'

@pytest.mark.parametrize('origin,expected', [
    ('http://localhost:3000', 200), ('https://unapproved.example', 400),
])
def test_preflight_uses_cors_policy_without_a_catchall_application_route(origin, expected):
    from backend.tests.http_client import api_client
    from backend.main import app
    with api_client(app) as client:
        response = client.options('/api/v1/diagnosis', headers={
            'Origin': origin, 'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'authorization,content-type',
        })
    assert response.status_code == expected
    if expected == 200:
        assert response.headers['access-control-allow-origin'] == origin
    else:
        assert 'access-control-allow-origin' not in response.headers
