#!/usr/bin/env python3
"""
Fix API Gateway CORS by updating method responses
"""
import boto3
import json

# Initialize AWS clients
apigateway = boto3.client('apigateway', region_name='us-east-1')

REST_API_ID = '1w80v6fnw1'
RESOURCE_ID_ROOT = 'hmz32fziqd'
RESOURCE_ID_PROXY = 'mo1lqr'

def update_method_response(resource_id, http_method):
    """Update method response to include CORS headers"""
    try:
        # Update method response to include CORS headers
        apigateway.update_method_response(
            restApiId=REST_API_ID,
            resourceId=resource_id,
            httpMethod=http_method,
            statusCode='200',
            patchOperations=[
                {'op': 'add', 'path': '/responseParameters/method.response.header.Access-Control-Allow-Headers', 'value': 'true'},
                {'op': 'add', 'path': '/responseParameters/method.response.header.Access-Control-Allow-Methods', 'value': 'true'},
                {'op': 'add', 'path': '/responseParameters/method.response.header.Access-Control-Allow-Origin', 'value': 'true'}
            ]
        )
        print(f"OK: Updated {http_method} method response for resource {resource_id}")
    except Exception as e:
        print(f"ERROR updating {http_method} method response: {e}")

def update_integration_response(resource_id, http_method):
    """Update integration response to set CORS header values"""
    try:
        apigateway.update_integration_response(
            restApiId=REST_API_ID,
            resourceId=resource_id,
            httpMethod=http_method,
            statusCode='200',
            patchOperations=[
                {'op': 'replace', 'path': '/responseParameters/method.response.header.Access-Control-Allow-Headers', 'value': "'Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token'"},
                {'op': 'replace', 'path': '/responseParameters/method.response.header.Access-Control-Allow-Methods', 'value': "'GET,POST,PUT,DELETE,OPTIONS'"},
                {'op': 'replace', 'path': '/responseParameters/method.response.header.Access-Control-Allow-Origin', 'value': "'*'"}
            ]
        )
        print(f"OK: Updated {http_method} integration response for resource {resource_id}")
    except Exception as e:
        print(f"ERROR updating {http_method} integration response: {e}")

def create_deployment():
    """Create new deployment to prod stage"""
    try:
        response = apigateway.create_deployment(
            restApiId=REST_API_ID,
            stageName='prod',
            description='CORS fix deployment via Python script'
        )
        print(f"OK: Created deployment: {response['id']}")
        return response['id']
    except Exception as e:
        print(f"ERROR creating deployment: {e}")
        return None

if __name__ == '__main__':
    print("Fixing API Gateway CORS configuration...")
    print("=" * 60)

    # Update OPTIONS method for both resources
    for resource_id in [RESOURCE_ID_ROOT, RESOURCE_ID_PROXY]:
        update_method_response(resource_id, 'OPTIONS')
        update_integration_response(resource_id, 'OPTIONS')

    # Deploy changes
    print("\nDeploying changes...")
    deployment_id = create_deployment()

    if deployment_id:
        print("\n" + "=" * 60)
        print("SUCCESS: CORS configuration updated!")
        print(f"Deployment ID: {deployment_id}")
        print("\nTest with:")
        print(f"curl -X OPTIONS https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod/api/v1/diagnosis -i")
    else:
        print("\nERROR: Deployment failed")
