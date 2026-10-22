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

The complete active backend suite passed 121 tests locally on Python 3.11. Original mock-only acceptance specifications are preserved in `archive/upstream_acceptance/`. Provider stubs do not establish live cloud behavior. CI/CD and infrastructure details are maintained in their technical guides.

These changes were developed with AI assistance. Understand and explain the implementation before presenting it as experience; inherited code and upstream deployments remain credited to their authors. Recruiter-oriented documentation is deferred until a deployed application is verified. No personal identity, degree, or employment details are invented here.
