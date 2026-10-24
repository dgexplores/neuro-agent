# Deployment readiness and route guide

The Oracle + Gemini fictional demonstration is live at
https://neuro-161-118-164-31.sslip.io/. Actual model, storage, ownership, quota
and restart checks are recorded in [Oracle verification](ORACLE_VERIFICATION.md).
The preserved AWS deployment remains unexecuted; its prerequisites follow below.
Hosted backend runner sign-off is tracked separately from the manual live release.

## Local use

1. Install Python 3.11 and a supported Node release (22.22.2+).
2. Run `make install`; copy `.env.example` to `.env` and set a new private signing secret.
3. Run `make api` and `make web` in separate terminals.
4. Open `http://localhost:3000`. Create a local development bearer token using the helper in the README and save it in the session panel.
5. Open Assessment, enter synthetic information, and submit. Model-backed results require the selected provider and actual access. Use the fictional demo with Gemini or configure Bedrock explicitly; provider failures remain actual errors.
6. Save the returned case ID and use Saved cases to retrieve it with the same account token.

`make test` runs backend and frontend checks without AWS calls. No mock success
mode is substituted for a failed model invocation.

## AWS bootstrap (manual, potentially billable)

The deployment workflow updates an existing stack. Provisioning requires an
AWS account, region, Bedrock model entitlement and explicit spending authorization.
This session has a zero-spend limit, so no bootstrap or deployment was performed.

Build the Linux layer with `bash infrastructure/cdk-clean/build_layer.sh`, install
the CDK requirements, and run `python infrastructure/cdk-clean/verify_stack.py`.
The canonical CDK app defines Lambda, API Gateway, DynamoDB, image S3, private
frontend S3 and CloudFront. Supply `JwtSecretKey` as a secure CloudFormation
parameter, never a committed file. Use the original CDK app entry point for your
approved deployment. Review retained data and regional model availability first.

Use the stack outputs to configure the GitHub `production` environment:

| Variable | Source |
|---|---|
| `AWS_REGION`, `AWS_DEPLOY_ROLE_ARN` | Your region and repository-scoped OIDC deployment role |
| `LAMBDA_FUNCTION_NAME` | Deployed `NeuroAgentAPI` function |
| `LAMBDA_ARTIFACT_BUCKET` | Existing private release-artifact bucket you control |
| `PUBLIC_API_URL` | `APIGatewayURL` output, including its API stage |
| `FRONTEND_BUCKET` | `FrontendBucketName` output |
| `FRONTEND_DISTRIBUTION_ID` | `FrontendDistributionId` output |
| `CLOUD_DEPLOYMENT_ENABLED` | Keep absent/false until spending is explicitly authorized |

The role needs code-update rights for that function, upload/list rights for the
two release buckets and invalidation rights for that distribution. The runtime
role separately accesses its own DynamoDB/S3/model resources. Reviewers and
protected release branches are recommended for the production environment.

## Routing and post-deployment verification

Browser paths: `/`, `/diagnosis`, `/history`, `/cases` (redirect), and a useful
unknown-page screen. CloudFront rewrites only extensionless frontend paths to
`index.html`. API Gateway retains its stage prefix; the build-time API URL must
include it. API requests go to the configured API origin, not the frontend bucket.
The CDN origin is included in runtime CORS. An asset such as `/assets/index.js`
is never rewritten to the SPA.

After an approved release, verify HTTPS `/health`, `/openapi.json`, missing-token
401, a synthetic successful assessment, same-owner case retrieval, other-owner
404, frontend nested-route refreshes, missing assets, CORS and service-error
messages. Save the actual URL and evidence before adding recruiter deployment
claims. Local successful synthesis does not establish any of these cloud checks.

The real Mangum entry point is covered by API Gateway REST proxy-event tests for health, OpenAPI, missing credentials and unknown API paths. CORS preflight is handled by middleware; an inherited catchall OPTIONS route was removed so unknown GET paths correctly return 404. Allowed and rejected preflight origins are covered by regression tests.
