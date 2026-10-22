# Verification and deployment

`.github/workflows/ci.yml` verifies Python 3.11 backend tests, builds the React
frontend with Node 22 using `npm ci`, and builds the backend container. Every
job is blocking; backend failures are not converted into successful releases.
JUnit results are uploaded even when tests fail. AWS credentials in the test
job are dummy values; real Bedrock calls are not part of offline validation.

Run locally from the repository root:

```sh
python -m pip install -r requirements.txt 'pytest-bdd>=6.1.1,<9' pytest-cov pytest-timeout requests-mock
AWS_EC2_METADATA_DISABLED=true AWS_DEFAULT_REGION=us-east-1 AWS_ACCESS_KEY_ID=testing AWS_SECRET_ACCESS_KEY=testing python -m pytest backend/tests tests/test_*.py --junitxml=reports/backend.xml
cd frontend
npm ci
npm run build
```

The active acceptance tests call the real FastAPI application with deterministic
provider fixtures. The original placeholder acceptance specifications are retained
under `archive/upstream_acceptance/` and are excluded from executable evidence.

## AWS delivery

`deploy.yml` is manual and runs full CI first. It packages the original
FastAPI/Mangum handler for the existing Python 3.11 x86_64 AWS Lambda function,
uploads the revision artifact to a private S3 bucket, updates Lambda code, and
waits for the update. Existing API Gateway, Cognito, Bedrock runtime IAM role,
environment settings, and databases remain configured through infrastructure.
It then builds React for the configured API URL and uploads to a dedicated
frontend S3 bucket. Provisioning is separate in the original CDK directories.

Create a GitHub `production` environment with required reviewers and a
protected-branch restriction. Configure these environment variables:

- `AWS_DEPLOY_ROLE_ARN`, `AWS_REGION`, `LAMBDA_FUNCTION_NAME`
- `LAMBDA_ARTIFACT_BUCKET`, `FRONTEND_BUCKET`, `PUBLIC_API_URL`
- `CLOUD_DEPLOYMENT_ENABLED=true` only after account/credits configuration is approved.

The deployment gate defaults to disabled. No workflow can guarantee zero cloud
charges; do not enable it until billing and credits meet the account owner's
requirements. OIDC trust must bind the role to your repository and production
environment. Limit permissions to the specific function and buckets: Lambda
configuration read/update code/publish version and S3 list/upload. Runtime
Bedrock access belongs to the Lambda execution role.

The package installs `requirements-lambda.txt` wheels for Lambda's actual Linux
runtime, rather than copying the checked-in third-party layer directory. Ensure
all runtime imports remain represented there. The function must use
`backend.main.handler`. An alias-pinned API Gateway needs a separate approved
alias promotion: updating code alone does not move an alias.

Persist case data in the configured DynamoDB store or an appropriate persistent
mount. `/tmp` SQLite on Lambda is temporary and not shared across instances.
Serve frontend assets through HTTPS (for example an existing CloudFront origin)
and configure SPA fallback to `index.html`. Configure CDN invalidation/cache
rules separately. Runtime CORS must allow the actual frontend origin.

No public endpoint is assumed. Verify the API and frontend externally before
recording deployed links. Rollback by promoting the previous Lambda version
and restoring its matching frontend artifact. Backend/frontend rollout is not
atomic; endpoint contracts should remain compatible.

## Infrastructure verification

The infrastructure job builds a fresh Linux x86_64 Python 3.11 Lambda layer
using `infrastructure/cdk-clean/build_layer.sh`, then installs the canonical
CDK dependencies and runs `verify_stack.py`. Assertions verify runtime/handler,
DynamoDB keys, private retained storage, authentication parameter handling,
API-compatible timeout, and optional cache behavior. Synthesis runs locally on
the CI runner and does not create AWS resources. Account bootstrap, CDK
provisioning, secrets, credits approval, and API/domain setup remain explicit
manual prerequisites; the deployment workflow only updates existing resources.

## Local verification, 22 October 2026

The frontend now uses Vite 8.3.5, Vitest 5.0.5, React 18.3.1 and React Router
7.18.4. Use Node 22.22.2 or newer within a supported Node release, as specified
in `frontend/package.json`. Create React App and its inherited build dependency
tree were removed. JSX sources use `.jsx`; the Vite configuration preserves
`REACT_APP_API_URL` and the deployment output directory `build/`.

A clean `npm ci` installed 199 packages. `npm run test:ci` passed four suites
and fourteen tests, covering saved-case lookup, errors, educational attribution,
session configuration and actual router integration. `npm run build` passed.
A separate build confirmed that an explicit `REACT_APP_API_URL` is embedded,
and local preview requests for `/`, `/cases`, and `/diagnosis` returned the SPA.
The default local build was restored after that check. These checks do not
establish public hosting or browser end-to-end authentication.

Both full and production-only npm audits reported zero vulnerabilities on
22 October 2026. This is an advisory snapshot, not a guarantee against future
findings. CI runs the complete npm audit at the low severity threshold.

The Python backend verification reported 121 active tests passing in a clean environment. Canonical
CDK synthesis and contract assertions passed with DynamoDB selected. The Linux
ARM64 backend image built and its Uvicorn health and OpenAPI endpoints returned
200; unauthenticated case lookup returned 403. `.dockerignore` excludes local
virtual environments, frontend dependencies, environment files and generated
assets from the backend build context.

Python dependency security review is separate from these behavioral checks.
See `docs/DEPENDENCY_REVIEW.md` for the clean runtime audit and release limits.
Actual Bedrock inference, GitHub-hosted CI, and public AWS deployment remain
unverified. Cloud spending is not enabled.

## HTTPS frontend delivery

The canonical stack includes a retained private S3 frontend bucket and CloudFront distribution with SPA rewriting. Configure `FRONTEND_DISTRIBUTION_ID` to invalidate its cache after upload. CORS includes the generated HTTPS frontend origin. See `DEPLOYMENT_READINESS.md` for stack outputs, routing and the manual account bootstrap boundary.
