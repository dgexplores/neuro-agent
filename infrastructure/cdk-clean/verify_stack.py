"""Synthesize the stack and assert infrastructure contracts without AWS access."""
import tempfile
import aws_cdk as cdk
from aws_cdk.assertions import Template, Match
from app import NeuroAgentStack


def resolve(value, refs, conditions):
    """Evaluate the small intrinsic subset used by the model IAM policy."""
    if isinstance(value, list):
        return [item for item in (resolve(v, refs, conditions) for v in value) if item is not None]
    if not isinstance(value, dict):
        return value
    if 'Ref' in value:
        return refs[value['Ref']]
    if 'Fn::If' in value:
        condition, yes, no = value['Fn::If']
        return resolve(yes if resolve(conditions[condition], refs, conditions) else no, refs, conditions)
    if 'Fn::Equals' in value:
        left, right = value['Fn::Equals']
        return resolve(left, refs, conditions) == resolve(right, refs, conditions)
    if 'Fn::Or' in value:
        return any(resolve(v, refs, conditions) for v in value['Fn::Or'])
    if 'Fn::Not' in value:
        return not resolve(value['Fn::Not'][0], refs, conditions)
    if 'Fn::Join' in value:
        delimiter, items = value['Fn::Join']
        return delimiter.join(resolve(items, refs, conditions))
    if 'Fn::Split' in value:
        delimiter, text = value['Fn::Split']
        return resolve(text, refs, conditions).split(delimiter)
    if 'Fn::Select' in value:
        index, values = value['Fn::Select']
        return resolve(values, refs, conditions)[int(index)]
    return {key: resolve(v, refs, conditions) for key, v in value.items()}


with tempfile.TemporaryDirectory(prefix='neuroagent-cdk-') as output:
    app = cdk.App(outdir=output)
    stack = NeuroAgentStack(app, 'NeuroAgentStack')
    template = Template.from_stack(stack)
    template.has_resource_properties('AWS::DynamoDB::Table', {
        'BillingMode': 'PAY_PER_REQUEST',
        'KeySchema': [{'AttributeName': 'case_id', 'KeyType': 'HASH'}],
        'TimeToLiveSpecification': {'AttributeName': 'expires_at', 'Enabled': True},
    })
    template.has_resource_properties('AWS::Lambda::Function', {
        'Handler': 'backend.main.handler', 'Runtime': 'python3.11',
        'Architectures': ['x86_64'],
        'Environment': {'Variables': Match.object_like({
            'ENV': 'production', 'JWT_SECRET_KEY': {'Ref': 'JwtSecretKey'},
            'REDIS_ENABLED': 'false', 'CASE_STORE_BACKEND': 'dynamodb',
            'MODEL_PROVIDER': 'bedrock',
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
    assert document['Parameters']['DemoAccessEnabled']['Default'] == 'false'
    template.has_resource_properties('AWS::Lambda::Function', {
        'Handler': 'backend.main.handler',
        'Environment': {'Variables': Match.object_like({'DEMO_ACCESS_ENABLED': {'Ref': 'DemoAccessEnabled'}})},
    })
    template.has_resource_properties('AWS::IAM::Policy', {
        'PolicyDocument': {'Statement': Match.array_with([Match.object_like({
            'Action': Match.array_with(['dynamodb:ConditionCheckItem', 'dynamodb:PutItem', 'dynamodb:UpdateItem']),
            'Resource': Match.any_value(),
        })])},
    })
    assert not any(resource['Type'].startswith('AWS::ElastiCache') for resource in document['Resources'].values())
    policy = document['Resources']['ModelInvocationPolicy']['Properties']['PolicyDocument']
    references = {'AWS::Partition': 'aws', 'AWS::Region': 'us-east-1',
                  'AWS::AccountId': '111122223333', 'AWS::NoValue': None}
    for model in ('amazon.nova-lite-v1:0', 'us.amazon.nova-2-lite-v1:0',
                  'us.anthropic.claude-haiku-4-5-20251001-v1:0'):
        references['BedrockModelId'] = model
        evaluated = resolve(policy, references, document['Conditions'])['Statement']
        assert all(s['Action'] == 'bedrock:InvokeModel' and s['Effect'] == 'Allow' for s in evaluated)
        if model.startswith('us.'):
            profile_arn = 'arn:aws:bedrock:us-east-1:111122223333:inference-profile/' + model
            assert len(evaluated) == 2
            assert evaluated[0]['Resource'] == profile_arn
            assert evaluated[1]['Resource'] == 'arn:aws:bedrock:*::foundation-model/' + model[3:]
            assert evaluated[1]['Condition'] == {'StringEquals': {'bedrock:InferenceProfileArn': profile_arn}}
        else:
            assert evaluated == [{'Effect': 'Allow', 'Action': 'bedrock:InvokeModel',
                                  'Resource': 'arn:aws:bedrock:us-east-1::foundation-model/' + model}]
    for resource in document['Resources'].values():
        if resource['Type'] == 'AWS::Lambda::Function' and resource['Properties'].get('Handler') == 'backend.main.handler':
            assert 'AWS_REGION' not in resource['Properties']['Environment']['Variables']
            assert resource['Properties']['Timeout'] <= 29
        if resource['Type'] in {'AWS::DynamoDB::Table', 'AWS::S3::Bucket'}:
            assert resource['DeletionPolicy'] == 'Retain'
    app.synth()
    print('PASS: CDK synthesis; handler, runtime, retained storage, JWT, timeout, optional cache, and scoped direct/profile Bedrock IAM')
