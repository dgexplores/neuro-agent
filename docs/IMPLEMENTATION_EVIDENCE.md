# NeuroAgent implementation evidence

## Scope and baseline

Source baseline: upstream commit `e03dee6b0ad5ce711aaeb970b2f4523c1a81b418`. Analysis used the complete local source repository, following the invoked reverse-engineer-anything skill's source-analysis route. No binary reverse engineering or live provider probing was required. Source observations, local execution, offline provider stubs, and unknown remote behavior are kept distinct below.

## Source-to-contract map

| Question | Source and change | Verification | Boundary |
|---|---|---|---|
| Are completed responses durable? | `backend/services/case_store.py`, diagnosis endpoint in `backend/main.py` | SQLite reopen test and real HTTP create/retrieve roundtrip | Local SQLite only exercised as a real database |
| Can one user retrieve another user's response? | Owner filter in SQLite query; owner check after DynamoDB GetItem | HTTP other-owner 404 test, SQLite injection-shaped lookup, DDB SDK stub | Shared JWT issuer/key remains demo identity |
| Can duplicate case IDs overwrite owners? | SQLite primary key INSERT; DynamoDB `attribute_not_exists(case_id)` | Duplicate SQLite test and asserted DDB PutItem request | Real AWS conditional failure not exercised |
| Does image upload actually send image bytes? | `NeuroAgent.analyze_image`, `BedrockService.analyze_image` | HTTP plus botocore stub validates base64 bytes/media type; optional S3 PutObject stub | No live inference or clinical validation |
| Are model failures fabricated as success? | Direct model failures503; malformed assessment502; image failures503 | BDD503 scenario, SDK failure stub, invalid confidence tests | Model output quality unknown |
| Do credentials and input affect real app behavior? | `.env` loaded before local imports; JWT UTC-aware check | HTTP authentication/validation and source inspection | Production identity/refresh service not implemented |
| Does UI target your own backend? | `frontend/src/services/api.js`, `App.jsx` | API URL source path, session token panel, frontend component checks | Hosted frontend not deployed |

## Observed execution

Command from the repository root:

```bash
AWS_ACCESS_KEY_ID=testing AWS_SECRET_ACCESS_KEY=testing AWS_EC2_METADATA_DISABLED=true \
  .venv/bin/python -m pytest backend/tests tests/test_*.py -q
```

Result on Python 3.11.15: **115 passed**, with one inherited HTTPX raw-upload deprecation warning. Provider clients use botocore stubs; dummy credentials are test-only. No cloud resources, requests, or charges were created by these tests.

The provider tests cover Claude and Mistral text payload formats, image data and media type, unsupported models, image byte/signature limits, malformed provider responses, and provider failures. The case tests exercise real SQLite and assert DynamoDB serialization/conditional insert/owner scope with the AWS SDK. SDK stubs verify request contracts, not AWS availability or deployed IAM.

## Why inherited acceptance tests changed

The original BDD module's request step had `TODO: Make actual API request`, then assigned response status200 and an empty response body. Its feature used a mismatched language declaration and asserted unimplemented clinical confidence/SLA/localization behavior. The complete original files are retained under `archive/upstream_acceptance/` for provenance. They are not claimed as application verification.

The active feature now has three executable scenarios against `backend.main.app`: successful assessment/persistence/owner retrieval; empty-symptom rejection before invoking a model; and honest provider failure with no saved response. Only the external model response is stubbed; request validation, application parsing, route logic, token verification, and SQLite storage execute.

Inherited image tests asserted success fields from a hardcoded placeholder. They were replaced with the real adapter contracts rather than preserving invented clinical findings. Existing get-case tests now use actual repository storage instead of patching the removed placeholder `NeuroAgent.get_case` method.

## Unknown or not executed

- Live AWS model invocation, deployed API Gateway/Lambda integration, real DynamoDB/S3 persistence, real IAM, hosted frontend, and post-deployment smoke tests.
- Clinical accuracy, fraud/medical model benchmarks, throughput, latency SLAs, security certification, and production data policy.
- Live cloud and identity-flow verification. Runtime dependency remediation is complete with clean Python/npm audits; the frontend has fourteen passing tests.

The preserved cloud architecture and infrastructure can be synthesized locally, but synthesis alone is not deployment. No recruiter README or claim of verified cloud operation is supplied by this document.
