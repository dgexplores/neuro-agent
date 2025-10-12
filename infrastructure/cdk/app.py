#!/usr/bin/env python3
import aws_cdk as cdk
from constructs import Construct
from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_dynamodb as dynamodb,
    aws_s3 as s3,
    aws_iam as iam,
    Duration,
    RemovalPolicy,
    BundlingOptions
)
import os

class NeuroAgentStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # DynamoDB table for storing cases
        cases_table = dynamodb.Table(
            self, "CasesTable",
            table_name="neuroagent-cases",
            partition_key=dynamodb.Attribute(
                name="case_id",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )

        # S3 bucket for medical images
        images_bucket = s3.Bucket(
            self, "ImagesBucket",
            bucket_name=f"neuroagent-images-{self.account}-{self.region}",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        # IAM role for Lambda
        lambda_role = iam.Role(
            self, "LambdaExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ]
        )

        # Add Bedrock permissions (Phase 9-1: Scoped to specific agent)
        bedrock_agent_id = self.node.try_get_context("bedrock_agent_id")
        bedrock_agent_arn = f"arn:aws:bedrock:{self.region}:{self.account}:agent/*" if bedrock_agent_id else "*"

        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "bedrock:InvokeModel",
                    "bedrock:InvokeAgent",
                    "bedrock-agent-runtime:InvokeAgent",
                    "bedrock:InvokeModelWithResponseStream"  # For streaming responses
                ],
                resources=[bedrock_agent_arn] if bedrock_agent_id else ["*"]
            )
        )

        # Grant DynamoDB permissions
        cases_table.grant_read_write_data(lambda_role)

        # Grant S3 permissions
        images_bucket.grant_read_write(lambda_role)

        # Lambda function
        # Phase 9-1: Enhanced environment variables
        api_lambda = _lambda.Function(
            self, "NeuroAgentAPI",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="backend.main.handler",
            code=_lambda.Code.from_asset(
                "../../",
                exclude=[
                    "*.md", ".git", ".github", "node_modules", "frontend",
                    "infrastructure", "tests", "docs", "data", "scripts",
                    "*.pyc", "__pycache__", ".pytest_cache", ".env",
                    "*.log", "*.spec.ts", "locustfile.py", ".venv", "venv"
                ]
            ),
            timeout=Duration.minutes(5),
            memory_size=1024,
            role=lambda_role,
            environment={
                # Storage
                "DYNAMODB_TABLE_NAME": cases_table.table_name,
                "S3_BUCKET_NAME": images_bucket.bucket_name,
                "AWS_REGION": self.region,

                # Bedrock Configuration (Phase 9-1)
                "BEDROCK_AGENTCORE_AGENT_ID": self.node.try_get_context("bedrock_agent_id") or "",
                "BEDROCK_MODEL_ID": "anthropic.claude-3-sonnet-20240229-v1:0",

                # Authentication & Security (Phase 8-2)
                "JWT_SECRET_KEY": self.node.try_get_context("jwt_secret_key") or "",
                "ALLOWED_ORIGINS": self.node.try_get_context("allowed_origins") or "https://neuroagent.example.com",
                "ENV": "production",

                # Caching Configuration (Phase 8-1)
                "REDIS_ENABLED": self.node.try_get_context("redis_enabled") or "false",
                "REDIS_HOST": self.node.try_get_context("redis_host") or "",
                "REDIS_PORT": "6379",
                "REDIS_DB": "0",
            }
        )

        # API Gateway (Phase 9-1: Secure CORS configuration)
        # Get allowed origins from context (should match ALLOWED_ORIGINS env var)
        allowed_origins = self.node.try_get_context("allowed_origins")
        cors_origins = allowed_origins.split(",") if allowed_origins else ["https://neuroagent.example.com"]

        api = apigw.LambdaRestApi(
            self, "NeuroAgentAPI",
            handler=api_lambda,
            proxy=False,
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=cors_origins,  # ✅ SECURITY: Specific origins only
                allow_methods=["GET", "POST", "OPTIONS"],  # ✅ SECURITY: Only required methods
                allow_headers=["Authorization", "Content-Type"],  # ✅ SECURITY: Specific headers
                allow_credentials=True,
                max_age=Duration.minutes(10)
            )
        )

        # API routes
        api_v1 = api.root.add_resource("api").add_resource("v1")

        diagnosis_resource = api_v1.add_resource("diagnosis")
        diagnosis_resource.add_method("POST")

        upload_resource = api_v1.add_resource("upload-image")
        upload_resource.add_method("POST")

        cases_resource = api_v1.add_resource("cases")
        cases_resource.add_method("GET")

        case_resource = cases_resource.add_resource("{case_id}")
        case_resource.add_method("GET")

        # Outputs
        cdk.CfnOutput(
            self, "APIGatewayURL",
            value=api.url,
            description="API Gateway URL"
        )

app = cdk.App()
NeuroAgentStack(app, "NeuroAgentStack")
app.synth()
