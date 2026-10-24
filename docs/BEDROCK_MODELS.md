# Bedrock model configuration

The default is `amazon.nova-lite-v1:0`, an Amazon multimodal model. AWS lists it
as Active and supports direct inference in `us-east-1` as of 24 October 2026.
This replaces the inherited Claude 3 Sonnet default, which reached end of life
in that region. Model access, quotas and credit coverage still require account
verification; choosing an Amazon model does not make inference permanently free.

The adapter uses Bedrock Converse for Nova and current Claude Haiku, Sonnet and
Opus models. It passes an explicit output-token limit and sends image bytes
through Converse's image content block. Nova Micro is text-only and returns 501
for images. Older Claude 3 and Mistral request formats remain compatible with
their existing offline tests; regional lifecycle rules can prevent live use.
Failed, refused, truncated or malformed responses are never replaced with
successful synthetic findings.

`BEDROCK_MODEL_ID` accepts the selected model or inference profile ID locally.
The canonical stack's `BedrockModelId` parameter configures the same value for
Lambda. For example, `us.amazon.nova-2-lite-v1:0` or
`us.anthropic.claude-haiku-4-5-20251001-v1:0` uses a US geographic profile.
Current availability and account entitlements must be checked before selecting
a model. Anthropic access can require a usage form and a Marketplace subscription.

The runtime IAM policy grants only `bedrock:InvokeModel`. A direct model is
scoped to its exact foundation-model ARN in the deployment region. A geographic
or global profile additionally grants its exact profile ARN and the matching
foundation model across destination regions. The latter permission is conditioned
on that same profile ARN. It does not grant arbitrary model invocation or
Marketplace subscription permissions to Lambda.

`verify_stack.py` evaluates both policy branches for a direct Nova model and
Nova/Claude profiles. SDK Stubber tests verify actual text/image request
contracts and rejection behavior without contacting AWS. These checks establish
software behavior, not inference quality or deployed model access.

Primary references: [Nova Lite model card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-amazon-nova-lite.html),
[regional model availability](https://docs.aws.amazon.com/bedrock/latest/userguide/models-region-compatibility.html),
[inference profile permissions](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles-prereq.html),
[model access](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html).
