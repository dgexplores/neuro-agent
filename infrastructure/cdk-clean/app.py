#!/usr/bin/env python3
"""Canonical NeuroAgent AWS architecture. Synthesis is local; deployment is explicit."""
from pathlib import Path
from urllib.parse import urlsplit

import aws_cdk as cdk
from aws_cdk import (
    Aws, CfnCondition, CfnOutput, CfnParameter, Duration, Fn, RemovalPolicy, Stack, Token,
    aws_apigateway as apigw, aws_dynamodb as dynamodb,
    aws_iam as iam, aws_lambda as lambda_, aws_logs as logs, aws_s3 as s3,
    aws_cloudfront as cloudfront, aws_cloudfront_origins as origins_,
)
from constructs import Construct

ROOT = Path(__file__).resolve().parents[2]


class NeuroAgentStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        # Supply using a local CloudFormation parameter file; never commit a value.
        jwt_secret = CfnParameter(
            self, 'JwtSecretKey', type='String', no_echo=True, min_length=32, max_length=128,
            description='JWT signing secret, at least 32 characters. No default is provided.',
        )
        model = CfnParameter(
            self, 'BedrockModelId', type='String',
            default='amazon.nova-lite-v1:0',
            allowed_pattern=r'(?:(?:us|eu|apac|au|jp|in|ca|us-gov|global)\.)?(?:amazon|anthropic|mistral)\.[a-z0-9:-]+',
            description='An enabled Bedrock model ID or geographic/global inference profile ID; access and credits are account-specific.',
        )
        demo_access = CfnParameter(
            self, 'DemoAccessEnabled', type='String', default='false',
            allowed_values=['true', 'false'],
            description='Opt in to isolated synthetic demonstration sessions with bounded model usage.',
        )
        origins_value = self.node.try_get_context('allowed_origins') or 'http://localhost:3000'
        origins = [origin.strip() for origin in origins_value.split(',') if origin.strip()]
        for origin in origins:
            parsed = urlsplit(origin)
            if ('*' in origin or not parsed.hostname or parsed.username or parsed.password
                    or parsed.path or parsed.query or parsed.fragment
                    or not (parsed.scheme == 'https' or parsed.scheme == 'http' and parsed.hostname == 'localhost')):
                raise ValueError('allowed_origins must contain explicit HTTPS or localhost HTTP origins, without paths or wildcards')
        if not origins:
            raise ValueError('At least one allowed origin is required')

        # Private S3 origin with HTTPS CDN and extensionless SPA routing.
        frontend = s3.Bucket(
            self, 'FrontendBucket', encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            enforce_ssl=True, removal_policy=RemovalPolicy.RETAIN,
        )
        spa_router = cloudfront.Function(
            self, 'SpaRouter', code=cloudfront.FunctionCode.from_inline(
                "function handler(event) { var r = event.request; "
                "if (r.uri === '/' || r.uri.split('/').pop().indexOf('.') === -1) "
                "{ r.uri = '/index.html'; } return r; }"
            ),
        )
        distribution = cloudfront.Distribution(
            self, 'FrontendDistribution', default_root_object='index.html',
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins_.S3Origin(frontend),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                response_headers_policy=cloudfront.ResponseHeadersPolicy.SECURITY_HEADERS,
                function_associations=[cloudfront.FunctionAssociation(
                    function=spa_router, event_type=cloudfront.FunctionEventType.VIEWER_REQUEST,
                )],
            ),
        )
        origins.append('https://' + distribution.distribution_domain_name)
        CfnOutput(self, 'FrontendBucketName', value=frontend.bucket_name)
        CfnOutput(self, 'FrontendURL', value='https://' + distribution.distribution_domain_name)
        CfnOutput(self, 'FrontendDistributionId', value=distribution.distribution_id)

        cases = dynamodb.Table(
            self, 'CasesTable',
            partition_key=dynamodb.Attribute(name='case_id', type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            time_to_live_attribute='expires_at',
            encryption=dynamodb.TableEncryption.AWS_MANAGED,
            removal_policy=RemovalPolicy.RETAIN,
        )
        images = s3.Bucket(
            self, 'ImagesBucket', encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            enforce_ssl=True, removal_policy=RemovalPolicy.RETAIN,
            object_ownership=s3.ObjectOwnership.BUCKET_OWNER_ENFORCED,
        )
        role = iam.Role(
            self, 'LambdaExecutionRole', assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
            managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaBasicExecutionRole')],
        )
        # The inspected application uses direct model invocation; it does not create AgentCore.
        model_parts = Fn.split('.', model.value_as_string)
        profile = CfnCondition(self, 'UsesInferenceProfile', expression=Fn.condition_not(
            Fn.condition_or(*[Fn.condition_equals(Fn.select(0, model_parts), provider)
                              for provider in ('amazon', 'anthropic', 'mistral')]),
        ))
        base_model = Fn.condition_if(profile.logical_id,
            Fn.join('.', [Fn.select(1, model_parts), Fn.select(2, model_parts)]),
            model.value_as_string)
        profile_arn = self.format_arn(service='bedrock', resource='inference-profile',
                                     resource_name=model.value_as_string)
        direct_arn = self.format_arn(service='bedrock', account='', resource='foundation-model',
                                    resource_name=model.value_as_string)
        routed_model_arn = Fn.join('', [
            'arn:', Aws.PARTITION, ':bedrock:*::foundation-model/', Token.as_string(base_model),
        ])
        # Profile invocations require both resources. The wildcard is only the
        # destination region, and the matching model can only run via this profile.
        iam.CfnPolicy(self, 'ModelInvocationPolicy', policy_name='NeuroAgentModelInvocation',
                      roles=[role.role_name], policy_document={
            'Version': '2012-10-17', 'Statement': [
                Fn.condition_if(profile.logical_id,
                    {'Effect': 'Allow', 'Action': 'bedrock:InvokeModel', 'Resource': profile_arn},
                    {'Effect': 'Allow', 'Action': 'bedrock:InvokeModel', 'Resource': direct_arn}),
                Fn.condition_if(profile.logical_id,
                    {'Effect': 'Allow', 'Action': 'bedrock:InvokeModel', 'Resource': routed_model_arn,
                     'Condition': {'StringEquals': {'bedrock:InferenceProfileArn': profile_arn}}},
                    Aws.NO_VALUE),
            ],
        })
        cases.grant_read_write_data(role)
        images.grant_read_write(role)
        dependencies = lambda_.LayerVersion(
            self, 'DependenciesLayer',
            code=lambda_.Code.from_asset(str(ROOT / 'infrastructure' / 'cdk-clean' / 'build' / 'lambda_layer'), exclude=['*.pyc', '__pycache__']),
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_11],
            compatible_architectures=[lambda_.Architecture.X86_64],
            description='Build using infrastructure/cdk-clean/build_layer.sh for Linux x86_64 Python 3.11',
        )
        api_function = lambda_.Function(
            self, 'NeuroAgentAPI', runtime=lambda_.Runtime.PYTHON_3_11,
            architecture=lambda_.Architecture.X86_64, handler='backend.main.handler',
            code=lambda_.Code.from_asset(str(ROOT), exclude=[
                '*.md', '.git', '.github', 'node_modules', 'frontend', 'infrastructure', 'tests',
                'docs', 'data', 'scripts', '*.pyc', '__pycache__', '.pytest_cache', '.env', '.env.*',
                '*.log', '*.spec.ts', 'locustfile.py', '.venv', 'venv', 'cdk.out', 'lambda_layer',
                'archive', 'blog-posts', 'demo_video', 'hackathon_submission',
            ]),
            layers=[dependencies], timeout=Duration.seconds(28), memory_size=512,
            role=role, log_retention=logs.RetentionDays.ONE_WEEK,
            environment={
                'DYNAMODB_TABLE_NAME': cases.table_name,
                'CASE_STORE_BACKEND': 'dynamodb',
                'S3_BUCKET_NAME': images.bucket_name,
                'BEDROCK_MODEL_ID': model.value_as_string,
                'MODEL_PROVIDER': 'bedrock',
                'JWT_SECRET_KEY': jwt_secret.value_as_string,
                'ALLOWED_ORIGINS': ','.join(origins), 'ENV': 'production',
                'REDIS_ENABLED': 'false',
                'DEMO_ACCESS_ENABLED': demo_access.value_as_string,
            },
        )
        api = apigw.LambdaRestApi(
            self, 'NeuroAgentAPIGateway', handler=api_function, proxy=True,
            binary_media_types=['multipart/form-data'],
            deploy_options=apigw.StageOptions(throttling_rate_limit=2, throttling_burst_limit=5),
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=origins, allow_methods=['GET', 'POST', 'OPTIONS'],
                allow_headers=['Authorization', 'Content-Type'], allow_credentials=False,
                max_age=Duration.minutes(10),
            ),
        )
        CfnOutput(self, 'APIGatewayURL', value=api.url)
        CfnOutput(self, 'CasesTableName', value=cases.table_name)
        CfnOutput(self, 'ImagesBucketName', value=images.bucket_name)


if __name__ == '__main__':
    app = cdk.App()
    NeuroAgentStack(app, 'NeuroAgentStack')
    app.synth()
