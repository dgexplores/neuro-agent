# NeuroAgent local change record

This copy extends [thc1006/neuro-agent](https://github.com/thc1006/neuro-agent). Original architecture, authorship, and Git history are retained.

## Added implementation

- Persistent case-response repositories: SQLite for local development and DynamoDB for the preserved AWS deployment architecture.
- Owner-scoped authenticated retrieval, duplicate-insert protection, and sanitized storage errors.
- Real Claude image-model requests with actual uploaded bytes, structured response validation, optional encrypted S3 upload, and honest errors for unsupported/failing services.
- Lazy AWS clients, UTC-aware JWT validation, dotenv initialization order, and validated model output without manufactured failure success.
- Frontend API URL/session-token configuration and retrieval of real cases.
- Source-application BDD, HTTP, database, and AWS SDK contracts. See [evidence](docs/IMPLEMENTATION_EVIDENCE.md).

## Verification and provenance

The current complete backend suite passed 181 tests locally and in an offline Linux container; the frontend has 25 passing tests. Original mock-only acceptance specifications are preserved in `archive/upstream_acceptance/`. Provider stubs do not establish live cloud behavior. CI/CD and infrastructure details are maintained in their technical guides.

These changes were developed with AI assistance. Understand and explain the implementation before presenting it as experience; inherited code and upstream deployments remain credited to their authors. The recruiter README now links the verified Oracle + Gemini demonstration; AWS deployment is not claimed. No personal identity, degree, or employment details are invented here.

## Oracle and public demo extension — 24 October 2026

- Provider selection keeps Bedrock as the AWS default and adds a bounded Gemini REST adapter.
- Public sessions have random owners, 15-minute JWTs and fictional-only scope.
- SQLite/DynamoDB atomic reservations enforce one attempt per session and ten per UTC day.
- Nonroot ARM packaging retains SQLite data; Caddy routes static pages and API requests on one HTTPS origin.
- Actual Gemini inference, owner isolation, browser lookup, and case/quota persistence after restart passed.
- The first release was manual. Full hosted backend CI sign-off remains separately tracked; see [cloud evidence](docs/ORACLE_VERIFICATION.md).
