# Model providers

`MODEL_PROVIDER` defaults to `bedrock`, preserving the AWS Lambda architecture.
The canonical AWS stack selects `BEDROCK_MODEL_ID` and stores cases in DynamoDB.
See [Bedrock configuration](BEDROCK_MODELS.md) for model and IAM details.

The optional Oracle demonstration uses the same assessment and image interfaces
with Gemini. Configure these only in the private backend environment:

```dotenv
MODEL_PROVIDER=gemini
GEMINI_MODEL=gemini-3.5-flash-lite
CASE_STORE_BACKEND=sqlite
CASE_DB_PATH=/app/data/cases.sqlite3
```

Set `GEMINI_API_KEY` separately as a runtime secret. Mount `/app/data` persistently
and leave `S3_BUCKET_NAME` unset when AWS image storage is not configured. The
Gemini adapter does not initialize AWS clients or require AWS credentials.
Provider selection does not change token ownership, saved-case validation or
the synthetic demo's durable inference limits.

The adapter uses Google's REST `generateContent` endpoint through the existing
HTTPX dependency. Text and images request JSON with explicit output limits.
Only a completed response is accepted; provider failures and invalid findings
return service errors. No canned success response substitutes for live inference.
Model access and free-tier quotas still depend on the configured Google project.

`tests/test_gemini_provider.py` uses an offline HTTP transport to verify text and
image payloads, credential handling, timeouts, rejected output and a full
synthetic assessment-to-saved-case application flow. These are contract tests;
they do not establish clinical accuracy or live provider availability.

Primary references: [Google content generation API](https://ai.google.dev/api/generate-content),
[image input](https://ai.google.dev/gemini-api/docs/image-understanding).
