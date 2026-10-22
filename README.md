# NeuroAgent — Technical Setup and Verification

A Python/FastAPI assessment application extending [thc1006/neuro-agent](https://github.com/thc1006/neuro-agent). Original source history and attribution are retained. This copy adds persistent case responses, authenticated retrieval, provider error handling, real image-model requests, frontend session configuration, and automated delivery checks.

**Current status:** local automated verification is recorded in [technical evidence](docs/IMPLEMENTATION_EVIDENCE.md). The application has not been deployed or tested against live AWS services in this adaptation. Recruiter-oriented documentation is deferred until deployment is verified. No AWS requests were made during the automated checks described here.

Use synthetic inputs only. This is an educational application, not a clinically validated diagnosis system.

## Architecture and endpoint contracts

```text
React → REST API / FastAPI → JWT + input validation → NeuroAgent → AWS Bedrock
                                     ↓
                       SQLite (local) / DynamoDB (cloud)

Image upload → signature and size checks → Claude image request → optional S3 storage
```

The preserved cloud architecture is API Gateway → Lambda → Bedrock, DynamoDB, and S3. The canonical [CDK project](infrastructure/cdk-clean/) defines cloud infrastructure. SQLite is the local alternative; Lambda replicas use DynamoDB.

| Method | Endpoint | Behavior |
|---|---|---|
| GET | `/` | Application information |
| GET | `/health` | Liveness only; Bedrock connectivity is explicitly not checked |
| POST | `/api/v1/diagnosis` | Validate, invoke model, validate response, persist response for authenticated owner |
| GET | `/api/v1/cases/{case_id}` | Retrieve the owner's saved response; other-owner and absent IDs both return 404 |
| POST | `/api/v1/drug-interactions` | Existing local medication-knowledge lookup |
| POST | `/api/v1/upload-image` | Real multimodal request for supported Claude models; optional S3 upload |

The image adapter accepts JPEG/PNG signatures up to 3.75 MB. It does not implement DICOM or clinical image validation. Unsupported model families return 501; provider failures return 503; image findings are never fabricated. Text-model failure returns 503 and malformed assessment JSON returns 502. A successful assessment is not returned if saving its response fails.

## Quick start

Install Python 3.11, Node 22.22.2+ (supported release) and Make. From the cloned
repository, `make install` creates the environment and installs backend/frontend
dependencies. Configure `.env` as below, then run `make api` and `make web` in
separate terminals. Open `http://localhost:3000`. Run `make test` for both suites.
Model-backed assessment requires your own enabled AWS Bedrock account and can
incur charges; setup and offline tests do not invoke it.

## Local configuration

Use Python 3.11 and run from the repository root:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Set a generated private `JWT_SECRET_KEY`, AWS region, and model ID in `.env`. Prefer the AWS credential provider chain over copying credentials into files. Configuration is loaded before authentication settings. `CASE_STORE_BACKEND=sqlite` uses `CASE_DB_PATH` (default `data/cases.sqlite3`); cloud mode requires `CASE_STORE_BACKEND=dynamodb` and `DYNAMODB_TABLE_NAME`. `S3_BUCKET_NAME` enables encrypted image upload after analysis.

For a private local demonstration, generate a signing secret with `python -c 'import secrets; print(secrets.token_urlsafe(48))'` and save it only in the backend `.env`. Start the API:

```bash
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

The API starts without initializing AWS clients. Actual model requests require valid AWS permissions/model access and can incur charges; they were not executed for this adaptation. Local API docs are at `http://127.0.0.1:8000/docs`.

Generate a short-lived local demonstration token in a second activated terminal:

```bash
python -c 'from dotenv import load_dotenv; load_dotenv(); from backend.utils.auth import create_access_token; print(create_access_token("local-demo", "local-demo"))'
```

This is a local operator helper, not a user registration/login service. Use the bearer token in Swagger or the frontend session panel. Never paste the signing secret or AWS keys into the frontend.

## Frontend

Create `frontend/.env.local` containing `REACT_APP_API_URL=http://localhost:8000`, then run:

```bash
cd frontend
npm ci
npm start
```

The API client honors `REACT_APP_API_URL` in every build mode. There is no inherited hosted API or hardcoded token fallback. The session panel stores a bearer token in this tab's `sessionStorage`; clear it when finished. The case page retrieves an actual saved case by ID rather than displaying hardcoded records.

## Automated checks

Install acceptance-test dependencies with `python -m pip install 'pytest-bdd>=6.1.1,<9' pytest-cov pytest-timeout requests-mock`, then run:

```bash
python -m pytest backend/tests tests/test_*.py -q
```

Verified on Python 3.11: **121 tests passed**, including live local SQLite operations, HTTP endpoint contracts, three executable BDD scenarios, and offline Bedrock/DynamoDB/S3 SDK stubs. This does not measure medical accuracy or confirm AWS deployment. Frontend, container, and infrastructure verification is tracked in the [CI/CD guide](docs/CI_CD.md) and [infrastructure evidence](docs/INFRASTRUCTURE_EVIDENCE.md).

## Browser routes and hosting

`/` is the overview, `/diagnosis` opens the assessment form, and `/history`
looks up a saved case. `/cases` redirects to `/history`; unknown URLs show a
page-not-found message with a home link. Optional vital signs can be left blank.
The form and service errors use English guidance. The API URL is configured
through `frontend/.env.local` locally or `REACT_APP_API_URL` during a cloud build.

The AWS CDK stack now also defines a private S3 frontend origin and HTTPS
CloudFront distribution. Its viewer-request function rewrites extensionless
SPA routes to `index.html`, so direct links and refreshes work; asset paths
retain normal file lookup. The generated frontend HTTPS origin is allowed by
the API's CORS configuration. No cloud resources are created by local synthesis.
See [release checklist](docs/DEPLOYMENT_READINESS.md) for the remaining account
configuration and manual deployment steps.

## Changes and remaining boundaries

See [implementation evidence](docs/IMPLEMENTATION_EVIDENCE.md) and the [contribution record](PORTFOLIO.md). Upstream non-executable BDD specifications are preserved in [archive/upstream_acceptance](archive/upstream_acceptance/); they were replaced by actual source-application acceptance contracts, not reported as passing clinical or SLA tests.

Remaining boundaries include live cloud verification, clinical validation, shared token revocation, production identity management, and data retention policy. SQLite files and S3 images in this demo are not an approved patient-record system. Runtime Python and frontend audits are currently clean; see [dependency review](docs/DEPENDENCY_REVIEW.md).

## Attribution and licensing

Original project: [thc1006/neuro-agent](https://github.com/thc1006/neuro-agent), created for the AWS AI Agent Global Hackathon 2025. Original awards, deployments, benchmarks, and participation belong to their authors.

Upstream licensing metadata is inconsistent: `pyproject.toml` says MIT, the original README described educational use, and this clone has no root LICENSE. This adaptation does not assign a new license.
