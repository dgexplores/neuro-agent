"""Synthesize the stack and assert infrastructure contracts without AWS access."""
import tempfile
import aws_cdk as cdk
from aws_cdk.assertions import Template, Match
from app import NeuroAgentStack

with tempfile.TemporaryDirectory(prefix='neuroagent-cdk-') as output:
    app = cdk.App(outdir=output)
    stack = NeuroAgentStack(app, 'NeuroAgentStack')
    template = Template.from_stack(stack)
    template.has_resource_properties('AWS::DynamoDB::Table', {
        'BillingMode': 'PAY_PER_REQUEST',
        'KeySchema': [{'AttributeName': 'case_id', 'KeyType': 'HASH'}],
    })
    template.has_resource_properties('AWS::Lambda::Function', {
        'Handler': 'backend.main.handler', 'Runtime': 'python3.11',
        'Architectures': ['x86_64'],
        'Environment': {'Variables': Match.object_like({
            'ENV': 'production', 'JWT_SECRET_KEY': {'Ref': 'JwtSecretKey'},
            'REDIS_ENABLED': 'false', 'CASE_STORE_BACKEND': 'dynamodb',
        })},
    })
    template.has_resource_properties('AWS::S3::Bucket', {
        'PublicAccessBlockConfiguration': {
            'BlockPublicAcls': True, 'BlockPublicPolicy': True,
            'IgnorePublicAcls': True, 'RestrictPublicBuckets': True,
        },
    })
    template.resource_count_is('AWS::CloudFront::Distribution', 1)
    template.has_resource_properties('AWS::CloudFront::Distribution', {
        'DistributionConfig': Match.object_like({
            'DefaultRootObject': 'index.html',
            'DefaultCacheBehavior': Match.object_like({
                'ViewerProtocolPolicy': 'redirect-to-https',
                'FunctionAssociations': Match.array_with([Match.object_like({'EventType': 'viewer-request'})]),
            }),
        }),
    })
    template.resource_count_is('AWS::CloudFront::Function', 1)
    document = template.to_json()
    secret = document['Parameters']['JwtSecretKey']
    assert secret['NoEcho'] and 'Default' not in secret
    assert not any(resource['Type'].startswith('AWS::ElastiCache') for resource in document['Resources'].values())
    for resource in document['Resources'].values():
        if resource['Type'] == 'AWS::Lambda::Function' and resource['Properties'].get('Handler') == 'backend.main.handler':
            assert 'AWS_REGION' not in resource['Properties']['Environment']['Variables']
            assert resource['Properties']['Timeout'] <= 29
        if resource['Type'] in {'AWS::DynamoDB::Table', 'AWS::S3::Bucket'}:
            assert resource['DeletionPolicy'] == 'Retain'
    app.synth()
    print('PASS: CDK synthesis; handler, runtime, storage keys, retained private storage, JWT parameter, timeout, and optional-cache contracts')
