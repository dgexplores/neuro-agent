# AWS architecture and infrastructure evidence

## Canonical source

`infrastructure/cdk-clean/app.py` is the canonical Python CDK stack. The previous `infrastructure/cdk/app.py` now delegates to it so the two entry points cannot drift. Original architecture is retained: API Gateway REST API → Python 3.11 Lambda (`backend.main.handler`) → Bedrock, DynamoDB, and private S3. Redis is disabled and no ElastiCache resource is created. Direct Bedrock model invocation is the implemented path; the stack does not claim to provision an AgentCore runtime.

## Reconstruction repairs

- Removed a literal JWT signing secret and a previously configured Redis endpoint from checked-in CDK context. New deployments require a `JwtSecretKey` CloudFormation parameter with `NoEcho`, a minimum length of 32 characters, and no default.
- Removed the duplicate construct name and reserved `AWS_REGION` override from the old stack variant. Lambda provides its own region environment variable.
- Packaged the correct `backend.main.handler` entry point with a fresh Linux x86_64 Python 3.11 dependency layer. The legacy checked-in `lambda_layer/` is no longer the CDK asset source.
- Scoped `bedrock:InvokeModel` to the selected foundation-model ARN, rather than granting model and unrelated agent operations on all resources. The `BedrockModelId` parameter must select a model the application supports and that the AWS account can invoke in its chosen region.
- Retained DynamoDB and S3 data on stack removal, enabled DynamoDB managed encryption, blocked S3 public access, required TLS, and used S3 server-side encryption.
- Configured proxy integration for the application's actual FastAPI routes and binary multipart payload handling for uploads.
- Replaced wildcard CORS with an explicit origin list, defaulting to the local development frontend. Supply the actual frontend origin through `allowed_origins` CDK context; no hosted frontend domain is invented.
- Set a 28-second Lambda timeout to fit the REST API integration deadline, one week of Lambda log retention, and low API request throttles. These are limits, not a guarantee of zero cost.

## Build and local verification

From the repository root, install the CDK Python requirements into an isolated Python environment and run:

```bash
bash infrastructure/cdk-clean/build_layer.sh
python infrastructure/cdk-clean/verify_stack.py
```

The layer build uses `uv` when available or `python -m pip`, explicitly targeting Linux manylinux2014 x86_64 CPython 3.11 binary wheels. It refuses to overwrite an existing generated layer. Remove only `infrastructure/cdk-clean/build/` before a deliberate rebuild after dependency changes. Generated packages are ignored by Git.

Verification synthesizes CloudFormation locally and asserts the Lambda entry point/runtime/architecture, storage key schema, production configuration, private S3 access, retained data, no-default secret parameter, absence of ElastiCache, and API-compatible timeout. The locally prepared layer includes Linux CPython 3.11 native extensions. The rebuilt layer was also imported successfully in an actual Linux x86_64 Python 3.11 container, with HTTP health passing. This checks packaged dependencies, not AWS Lambda service integration.

## Deployment status and limits

No AWS resources have been created. No bootstrap, deployment, account lookup, Bedrock invocation, or real patient upload was performed. There is no verified deployed URL.

A zero-spend requirement does not authorize provisioning these services. Free-tier or trial eligibility varies; API requests, Bedrock inference, storage, logs, and retained resources can incur charges. Cloud deployment remains gated on account access, model availability, a real secret and frontend origin, and explicit approval for the applicable costs. Low throttling does not prevent all charges.

Application JWT authentication protects the diagnosis and case endpoints. DynamoDB owner isolation is enforced by application queries; Lambda's IAM role has access to its case table as a whole. This is a portfolio prototype, and this synthesis does not establish clinical validation or production suitability.

The stack now includes a private S3 frontend origin and HTTPS CloudFront distribution. A viewer-request function rewrites extensionless SPA paths while preserving asset paths. The generated origin is included in application CORS. These resources passed local synthesis and infrastructure assertions; they have not been provisioned.
