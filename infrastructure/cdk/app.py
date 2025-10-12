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
    RemovalPolicy
)

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

        # Add Bedrock permissions
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "bedrock:InvokeModel",
                    "bedrock:InvokeAgent",
                    "bedrock-agent-runtime:InvokeAgent"
                ],
                resources=["*"]
            )
        )

        # Grant DynamoDB permissions
        cases_table.grant_read_write_data(lambda_role)

        # Grant S3 permissions
        images_bucket.grant_read_write(lambda_role)

        # Lambda function
        api_lambda = _lambda.Function(
            self, "NeuroAgentAPI",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="main.handler",
            code=_lambda.Code.from_asset("../backend"),
            timeout=Duration.minutes(5),
            memory_size=1024,
            role=lambda_role,
            environment={
                "DYNAMODB_TABLE_NAME": cases_table.table_name,
                "S3_BUCKET_NAME": images_bucket.bucket_name,
                "AWS_REGION": self.region
            }
        )

        # API Gateway
        api = apigw.LambdaRestApi(
            self, "NeuroAgentAPI",
            handler=api_lambda,
            proxy=False,
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=apigw.Cors.ALL_METHODS,
                allow_headers=["*"]
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
