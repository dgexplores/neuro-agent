#!/usr/bin/env python3
import boto3

apigateway = boto3.client('apigateway', region_name='us-east-1')

REST_API_ID = '1w80v6fnw1'
RESOURCES = {
    'root': 'hmz32fziqd',
    'proxy': 'mo1lqr'
}

def fix_options_integration(resource_id, resource_name):
    """Fix OPTIONS integration with proper request template and response"""

    # Step 1: Put integration with request template
    print(f"Updating OPTIONS integration for {resource_name}...")
    apigateway.put_integration(
        restApiId=REST_API_ID,
        resourceId=resource_id,
        httpMethod='OPTIONS',
        type='MOCK',
        requestTemplates={
            'application/json': '{"statusCode": 200}'
        }
    )

    # Step 2: Put integration response with CORS headers
    print(f"Updating OPTIONS integration response for {resource_name}...")
    apigateway.put_integration_response(
        restApiId=REST_API_ID,
        resourceId=resource_id,
        httpMethod='OPTIONS',
        statusCode='200',
        responseParameters={
            'method.response.header.Access-Control-Allow-Headers': "'Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token'",
            'method.response.header.Access-Control-Allow-Methods': "'GET,POST,PUT,DELETE,OPTIONS'",
            'method.response.header.Access-Control-Allow-Origin': "'*'"
        },
        responseTemplates={
            'application/json': ''
        }
    )
    print(f"OK: Fixed {resource_name} OPTIONS integration\n")

if __name__ == '__main__':
    print("Fixing OPTIONS MOCK integrations...")
    print("=" * 60)

    for name, resource_id in RESOURCES.items():
        fix_options_integration(resource_id, name)

    # Deploy
    print("Creating deployment...")
    response = apigateway.create_deployment(
        restApiId=REST_API_ID,
        stageName='prod',
        description='Fix OPTIONS MOCK integration'
    )

    print(f"Deployment created: {response['id']}")
    print("\n" + "=" * 60)
    print("SUCCESS! Test with:")
    print("curl -X OPTIONS https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod/ -i")
