# NeuroAgent design review guide

Use [implementation evidence](IMPLEMENTATION_EVIDENCE.md) to distinguish local execution from offline SDK contracts and unknown cloud behavior.

## Trace the added behavior

1. Environment configuration is loaded before JWT settings, then FastAPI verifies the token and request model.
2. NeuroAgent formats the input and calls a configured text model. The response must contain structured assessments with finite non-boolean confidence values between0 and1.
3. The endpoint saves its validated response and owner ID using parameterized SQLite SQL locally or conditional DynamoDB writes in cloud mode.
4. Retrieval checks both case ID and owner; missing and other-owner cases share404. Storage failures503 do not look like absent cases or successful saves.
5. Image upload checks size/signature, sends actual base64 bytes to a supported Claude adapter, validates JSON observations, and optionally saves bytes to S3.

## Questions to prepare

- What is the difference between a SQLite context manager committing and explicitly closing a connection?
- Why does INSERT or conditional PutItem prevent another owner replacing a case?
- Why send synchronous SDK/database work to a thread from an async endpoint?
- Why is SQLite not shared persistence for Lambda replicas?
- How does a naive local-time versus UTC comparison reject valid JWTs?
- Why are provider failures reported as errors rather than invented fallback assessments?
- What do botocore stubs establish, and what does only a live deployment establish?
- Which upstream acceptance tests were only specifications, and what now exercises the real API?

No clinical accuracy, cloud deployment, or production certification follows from these local checks. The original authors remain credited.
