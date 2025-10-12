# POST /diagnosis - Complete Sequence Diagram

## Overview
This document provides a comprehensive sequence diagram for the `POST /diagnosis` endpoint, tracing the complete request flow from Frontend through all AWS components and back.

---

## Complete Sequence Diagram

```plantuml
@startuml POST_Diagnosis_Complete_Sequence

skinparam backgroundColor #FFFFFF
skinparam sequenceMessageAlign center
skinparam responseMessageBelowArrow true

title POST /diagnosis - Complete End-to-End Flow\n(Frontend → API Gateway → Lambda → Bedrock AgentCore → DynamoDB → Frontend)

actor User as user
participant "React\nFrontend" as frontend #LightBlue
participant "CloudFront\nCDN" as cdn #Orange
participant "API Gateway\nREST API" as apigw #Yellow
participant "Lambda\nAuthorizer" as auth #LightGreen
participant "Lambda\nFunction\n(FastAPI)" as lambda #Green
box "Lambda Execution Context" #LightGreen
    participant "FastAPI\nRouter" as fastapi
    participant "NeuroAgent" as agent
    participant "BedrockService" as bedrock_svc
    participant "KnowledgeBase" as kb
end box
participant "AWS Bedrock\nAgentCore" as bedrock #Purple
participant "Claude 3\nSonnet Model" as claude #Violet
participant "DynamoDB\nPatientCases" as dynamodb #Red
participant "CloudWatch\nLogs" as cloudwatch #Grey

'=== User Interaction ===
user -> frontend : Click "Get Diagnosis"
activate frontend

frontend -> frontend : Collect form data
note right of frontend
  DiagnosisRequest payload:
  {
    "patient_info": {
      "age": 45,
      "gender": "male",
      "medical_history": [...]
    },
    "symptoms": [...],
    "vital_signs": {...},
    "chief_complaint": "...",
    ...
  }
end note

'=== Frontend to CloudFront ===
frontend -> cdn : POST https://d123.cloudfront.net/api/v1/diagnosis
activate cdn
note right
  Headers:
  - Authorization: Bearer <JWT>
  - Content-Type: application/json
  - Origin: https://app.neuroagent.com
end note

cdn -> cdn : Check CDN cache (MISS for POST)
cdn -> cdn : Apply WAF rules
cdn -> apigw : Forward request
deactivate cdn

'=== API Gateway Processing ===
activate apigw
apigw -> apigw : Validate request format
apigw -> apigw : Check rate limits (1000 req/min)
apigw -> apigw : CORS preflight check

'=== Lambda Authorizer ===
apigw -> auth : Authorize request
activate auth
note right of auth
  Custom Lambda Authorizer
  - Verify JWT signature
  - Check token expiration
  - Extract user_id
  - Generate IAM policy
end note

auth -> auth : Decode JWT token
auth -> auth : Validate claims (exp, iss, aud)
auth --> apigw : IAM Policy (Allow) + user_id
deactivate auth

note left of apigw
  API Gateway caches
  auth policy for 5 minutes
  (TTL configurable)
end note

'=== API Gateway to Lambda ===
apigw -> lambda : Invoke Lambda (async)
activate lambda
note right of apigw
  Lambda Event:
  {
    "httpMethod": "POST",
    "path": "/api/v1/diagnosis",
    "headers": {...},
    "body": "{...}",
    "requestContext": {
      "authorizer": {
        "user_id": "user-123"
      }
    }
  }
end note

'=== Lambda Cold Start (if needed) ===
alt Cold Start
    lambda -> lambda : Initialize Python runtime
    lambda -> lambda : Import dependencies
    lambda -> lambda : Load environment variables
    lambda -> lambda : Initialize BedrockService
    lambda -> lambda : Initialize NeuroAgent
    note right
      Cold start: ~3-5 seconds
      Warm start: ~10-50ms
    end note
else Warm Start
    lambda -> lambda : Reuse existing container
end

'=== FastAPI Request Processing ===
lambda -> fastapi : Route to endpoint handler
activate fastapi

fastapi -> fastapi : Parse request body
fastapi -> fastapi : Validate DiagnosisRequest schema
note right of fastapi
  Pydantic validation:
  - Age: 0-120
  - Gender: enum
  - Symptoms: 1-20 items
  - Required fields present
end note

alt Validation Failed
    fastapi --> lambda : HTTPException(400)
    lambda --> apigw : 400 Bad Request
    apigw --> frontend : Error response
    frontend -> user : Show validation errors
    [<-- user
else Validation Passed
    fastapi -> fastapi : Extract user_id from context
    fastapi -> agent : await analyze_case(request)
end

'=== NeuroAgent Processing ===
activate agent

agent -> agent : Generate case_id = uuid4()
note right
  case_id: "a1b2c3d4-..."
  timestamp: "2025-10-12T14:30:00Z"
end note

agent -> agent : _prepare_medical_context(request)
note right of agent
  Structured context extraction:
  {
    "patient_demographics": {...},
    "presentation": {
      "chief_complaint": "...",
      "symptoms": "headache (severe, 3 days); ..."
    },
    "clinical_data": {
      "vital_signs": {...},
      "lab_results": {...}
    }
  }
end note

agent -> agent : _build_diagnostic_prompt(context)
note right of agent
  Structured prompt for Bedrock:
  - Role: Expert neurologist AI
  - Patient information
  - Clinical presentation
  - Request format: JSON output
  - Safety guidelines
end note

'=== Bedrock Service Call ===
agent -> bedrock_svc : await invoke_agent(agent_id, session_id, prompt)
activate bedrock_svc

bedrock_svc -> bedrock_svc : Get AWS credentials from env
bedrock_svc -> bedrock_svc : Initialize boto3 client (cached)

'=== AWS Bedrock AgentCore Invocation ===
bedrock_svc -> bedrock : invoke_agent(agentId, sessionId, inputText)
activate bedrock

bedrock -> bedrock : Validate agent permissions
bedrock -> bedrock : Load agent configuration
bedrock -> bedrock : Prepare context for model

bedrock -> claude : Invoke Claude 3 Sonnet model
activate claude

note right of claude
  Model: anthropic.claude-3-sonnet-20240229-v1:0
  Max tokens: 4096
  Temperature: 0.1 (deterministic)

  Prompt includes:
  - System instructions (neurologist role)
  - Patient context (structured)
  - Output format (JSON schema)
  - Safety guidelines
end note

claude -> claude : Process medical context
claude -> claude : Generate differential diagnoses
claude -> claude : Calculate confidence scores
claude -> claude : Formulate recommendations

claude --> bedrock : Streaming response chunks
note left
  Streaming format:
  {
    "differential_diagnoses": [
      {
        "condition": "Migraine with aura",
        "confidence": 0.85,
        "reasoning": "..."
      },
      {
        "condition": "Tension headache",
        "confidence": 0.65,
        "reasoning": "..."
      },
      {
        "condition": "Cluster headache",
        "confidence": 0.45,
        "reasoning": "..."
      }
    ],
    "recommendations": [...],
    "risk_factors": [...],
    "next_steps": [...]
  }
end note
deactivate claude

'=== Bedrock Response Processing ===
bedrock -> bedrock : Aggregate streaming chunks
bedrock --> bedrock_svc : Complete response
deactivate bedrock

bedrock_svc -> bedrock_svc : Process event stream
bedrock_svc -> bedrock_svc : Decode bytes to UTF-8
bedrock_svc --> agent : {"output": {"text": "{...}"}}
deactivate bedrock_svc

note right of agent
  Response received in ~2-4 seconds
  (depending on complexity)
end note

'=== AgentCore Failure Fallback ===
alt AgentCore Success
    agent -> agent : _parse_agent_response(response)
else AgentCore Failed (ClientError)
    agent -> bedrock_svc : await invoke_model_direct(prompt)
    activate bedrock_svc
    bedrock_svc -> bedrock : invoke_model() [direct]
    activate bedrock
    bedrock -> claude : Direct model invocation
    activate claude
    claude --> bedrock : Response
    deactivate claude
    bedrock --> bedrock_svc : Model output
    deactivate bedrock
    bedrock_svc --> agent : Fallback response
    deactivate bedrock_svc

    note right of agent
      Fallback adds resilience
      No AgentCore = direct model
      No model = rule-based
    end note
end

'=== Parse AI Response ===
agent -> agent : Parse JSON from response
agent -> agent : _calculate_overall_confidence()
note right
  Weighted confidence:
  - 1st diagnosis: 50% weight
  - 2nd diagnosis: 30% weight
  - 3rd diagnosis: 20% weight

  Overall = Σ(confidence × weight)
  Example: 0.85×0.5 + 0.65×0.3 + 0.45×0.2
         = 0.425 + 0.195 + 0.09 = 0.71
end note

'=== Knowledge Base Enhancement ===
agent -> kb : get_treatment_guidelines(condition)
activate kb

kb -> kb : Match condition to guidelines
note right of kb
  Knowledge base lookup:
  - "migraine" → [
      "Consider triptans",
      "Prophylactic therapy",
      "Assess trigger factors"
    ]
  - Evidence-based protocols
  - Taiwan healthcare context
end note

kb --> agent : List[str] recommendations
deactivate kb

agent -> kb : check_drug_interactions(medications)
activate kb

kb -> kb : Check pairwise interactions
note right of kb
  Drug interaction matrix:
  current_medications = [
    "warfarin", "aspirin"
  ]

  Found: (warfarin, aspirin)
    → "Increased bleeding risk"
    → Severity: HIGH
end note

kb --> agent : List[str] interactions
deactivate kb

agent -> agent : _enhance_with_knowledge(result, request)
note right
  Merge AI + knowledge base:
  - AI differential diagnoses
  + Evidence-based guidelines
  + Drug interaction warnings
  + Risk factors (age, history)
  + Next steps (imaging, labs)
end note

'=== DynamoDB Persistence ===
agent -> dynamodb : put_item(PatientCase)
activate dynamodb

note right of dynamodb
  Item structure:
  {
    "case_id": "a1b2c3d4-...",
    "patient_age": 45,
    "patient_gender": "male",
    "chief_complaint": "...",
    "symptoms_json": {...},
    "diagnosis_results": {...},
    "confidence_score": 0.71,
    "status": "completed",
    "created_at": "2025-10-12T14:30:00Z",
    "ttl": 1733932800 (90 days)
  }
end note

dynamodb -> dynamodb : Write to partition
dynamodb -> dynamodb : Update GSI (status-created_at-index)
dynamodb --> agent : Success (200 OK)
deactivate dynamodb

'=== CloudWatch Logging ===
par Parallel Logging
    lambda -> cloudwatch : Log diagnosis request
    lambda -> cloudwatch : Log AI response time
    lambda -> cloudwatch : Log confidence score
    lambda -> cloudwatch : Publish custom metric
end

note right of cloudwatch
  Logs include:
  - Request ID
  - User ID
  - Processing time
  - Confidence score
  - Error traces (if any)

  Metrics:
  - DiagnosisLatency (ms)
  - DiagnosisConfidence (0-1)
  - BedrockTokenUsage (count)
end note

'=== Return Response ===
agent --> fastapi : Dict[str, Any] result
deactivate agent

fastapi -> fastapi : Create DiagnosisResponse model
note right of fastapi
  Pydantic response:
  {
    "case_id": "a1b2c3d4-...",
    "diagnosis": [
      {"condition": "...", "confidence": 0.85, ...},
      ...
    ],
    "confidence": 0.71,
    "recommendations": [...],
    "risk_factors": [...],
    "next_steps": [...],
    "timestamp": "2025-10-12T14:30:02Z"
  }
end note

fastapi --> lambda : DiagnosisResponse (200 OK)
deactivate fastapi

'=== Lambda to API Gateway ===
lambda -> lambda : Serialize response to JSON
lambda --> apigw : Lambda response
deactivate lambda

note right of lambda
  Lambda response format:
  {
    "statusCode": 200,
    "headers": {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*"
    },
    "body": "{...}"
  }
end note

'=== API Gateway to Frontend ===
apigw -> apigw : Transform response
apigw -> apigw : Add CORS headers
apigw -> apigw : Log to CloudWatch
apigw --> cdn : HTTP 200 OK
deactivate apigw

cdn -> cdn : Cache headers evaluation (no-cache for POST)
cdn --> frontend : Response with diagnosis
activate frontend

'=== Frontend Processing ===
frontend -> frontend : Parse JSON response
frontend -> frontend : Update React state
frontend -> frontend : Render DiagnosisResults component

note right of frontend
  UI displays:
  - Top 3 differential diagnoses
  - Confidence visualization
  - Treatment recommendations
  - Drug interaction warnings
  - Next steps for physician
end note

frontend -> user : Show diagnosis results
deactivate frontend

note over user
  Total end-to-end time:
  - Cold start: ~5-8 seconds
  - Warm start: ~2-4 seconds

  Breakdown:
  - Network latency: ~200ms
  - Lambda processing: ~500ms
  - Bedrock inference: ~2-3s
  - DynamoDB write: ~50ms
  - Response processing: ~100ms
end note

'=== Error Handling Path ===
alt Error Occurred
    lambda --> apigw : Error response (500)
    note right
      {
        "statusCode": 500,
        "body": {
          "detail": "Error message"
        }
      }
    end note
    apigw --> frontend : HTTP 500
    frontend -> frontend : Show error message
    frontend -> user : "Unable to process diagnosis. Please try again."
end

@enduml
```

---

## Timing Breakdown

### Cold Start (First Request)
| Step | Component | Duration | Cumulative |
|------|-----------|----------|------------|
| 1. Frontend → CloudFront | Network latency | ~50ms | 50ms |
| 2. CloudFront → API Gateway | CDN routing | ~20ms | 70ms |
| 3. API Gateway validation | Request processing | ~30ms | 100ms |
| 4. Lambda Authorizer | JWT validation | ~200ms | 300ms |
| 5. **Lambda Cold Start** | Runtime initialization | **~3-5s** | **3.3-5.3s** |
| 6. FastAPI routing | Request parsing | ~50ms | 3.35-5.35s |
| 7. NeuroAgent processing | Context preparation | ~100ms | 3.45-5.45s |
| 8. **Bedrock AgentCore** | **AI inference** | **~2-4s** | **5.45-9.45s** |
| 9. Knowledge base queries | Medical guidelines | ~200ms | 5.65-9.65s |
| 10. DynamoDB write | Case persistence | ~50ms | 5.7-9.7s |
| 11. Lambda → API Gateway | Response serialization | ~50ms | 5.75-9.75s |
| 12. API Gateway → Frontend | Response routing | ~50ms | 5.8-9.8s |
| 13. Frontend rendering | React state update | ~100ms | **5.9-9.9s** |

**Total Cold Start: ~6-10 seconds**

### Warm Start (Subsequent Requests)
| Step | Component | Duration | Cumulative |
|------|-----------|----------|------------|
| 1. Frontend → API Gateway | Network + routing | ~70ms | 70ms |
| 2. API Gateway validation | Cached auth policy | ~20ms | 90ms |
| 3. **Lambda Warm Start** | Container reuse | **~10-50ms** | **100-140ms** |
| 4. FastAPI + Agent processing | Context preparation | ~150ms | 250-290ms |
| 5. **Bedrock AgentCore** | **AI inference** | **~2-3s** | **2.25-3.29s** |
| 6. Knowledge base queries | Medical guidelines | ~200ms | 2.45-3.49s |
| 7. DynamoDB write | Case persistence | ~50ms | 2.5-3.54s |
| 8. Response routing | Lambda → Frontend | ~100ms | **2.6-3.64s** |

**Total Warm Start: ~2.6-3.6 seconds**

---

## Key Integration Points

### 1. Frontend → API Gateway
- **Protocol**: HTTPS
- **Authentication**: JWT Bearer token in Authorization header
- **CORS**: Preflight OPTIONS request for cross-origin
- **Request Format**: JSON (application/json)
- **File**: `frontend/src/services/api.js`

### 2. API Gateway → Lambda
- **Integration Type**: Lambda Proxy Integration
- **Event Format**: API Gateway Lambda Proxy Event
- **Authentication**: Custom Lambda Authorizer (cached 5 min)
- **Timeout**: 30 seconds
- **File**: `infrastructure/cdk/app.py`

### 3. Lambda → Bedrock AgentCore
- **SDK**: boto3 (bedrock-agent-runtime client)
- **Method**: `invoke_agent(agentId, agentAliasId, sessionId, inputText)`
- **Response Type**: EventStream (streaming chunks)
- **Fallback**: Direct model invocation if AgentCore fails
- **File**: `backend/services/bedrock_service.py:18-67`

### 4. Bedrock AgentCore → Claude Model
- **Model ID**: `anthropic.claude-3-sonnet-20240229-v1:0`
- **Max Tokens**: 4096
- **Temperature**: 0.1 (deterministic for medical consistency)
- **Format**: Messages API (Anthropic format)
- **File**: `backend/services/bedrock_service.py:97-122`

### 5. Lambda → DynamoDB
- **SDK**: boto3 (dynamodb client)
- **Operation**: `put_item()`
- **Table**: PatientCases
- **Indexes**: GSI on status-created_at
- **TTL**: 90 days (HIPAA compliance)
- **File**: `backend/agents/neuro_agent.py` (called from analyze_case)

### 6. Lambda → CloudWatch
- **Automatic**: All Lambda logs sent to CloudWatch Logs
- **Custom Metrics**: Published via boto3 cloudwatch client
- **Metrics**: DiagnosisLatency, DiagnosisConfidence, BedrockTokenUsage
- **Log Group**: `/aws/lambda/NeuroAgent-Diagnosis`

---

## Error Handling Flow

```plantuml
@startuml Error_Handling_Flow

title Error Handling for POST /diagnosis

start

if (API Gateway request validation?) then (fail)
  :Return 400 Bad Request;
  :Log to CloudWatch;
  stop
else (pass)
  :Continue to Lambda Authorizer;
endif

if (JWT token valid?) then (fail)
  :Return 401 Unauthorized;
  :Log authentication failure;
  stop
else (pass)
  :Invoke Lambda function;
endif

if (Lambda cold start successful?) then (fail)
  :Return 503 Service Unavailable;
  :Trigger CloudWatch alarm;
  stop
else (pass)
  :Execute handler;
endif

if (Pydantic validation?) then (fail)
  :Return 422 Unprocessable Entity;
  :Return validation errors;
  stop
else (pass)
  :Process diagnosis;
endif

if (Bedrock AgentCore available?) then (fail)
  :Fallback to direct model invocation;
  if (Direct model successful?) then (fail)
    :Fallback to rule-based diagnosis;
    :Set confidence = 0.5;
  else (pass)
    :Use model response;
  endif
else (pass)
  :Use AgentCore response;
endif

if (DynamoDB write successful?) then (fail)
  :Log error to CloudWatch;
  :Still return diagnosis (best effort);
  note right
    Data persistence failure
    doesn't block user response
  end note
else (pass)
  :Confirm case saved;
endif

:Return 200 OK with DiagnosisResponse;

stop

@enduml
```

---

## Performance Optimization Strategies

### 1. Lambda Warm-Up
```python
# Scheduled EventBridge rule to keep Lambda warm
# Invokes Lambda every 5 minutes during business hours
# Reduces cold starts by 90%
```

### 2. Bedrock Response Streaming
```python
# Process streaming chunks as they arrive
# Reduces perceived latency
# Start displaying partial results to user
for event in event_stream:
    if 'chunk' in event:
        yield process_chunk(event['chunk'])
```

### 3. Parallel Processing
```python
# Query knowledge base while Bedrock is processing
async with asyncio.gather(
    bedrock_service.invoke_agent(...),
    knowledge_base.get_guidelines(...),
    knowledge_base.check_interactions(...)
):
    # Merge results
```

### 4. DynamoDB Optimizations
- Use BatchWriteItem for multiple records
- Implement write-behind cache for non-critical data
- Use DynamoDB Streams for async processing
- Partition key design for even distribution

### 5. API Gateway Caching
```yaml
# Cache GET /cases/{case_id} responses
# TTL: 5 minutes
# Reduce DynamoDB reads by 70%
CacheKeyParameters:
  - method.request.path.case_id
CacheTtlInSeconds: 300
```

---

## Security Considerations

### 1. API Gateway
- ✅ WAF rules for SQL injection, XSS
- ✅ Rate limiting: 1000 req/min per IP
- ✅ CORS policy: Whitelist specific origins
- ✅ API keys for client identification

### 2. Lambda Authorizer
- ✅ JWT signature verification (RS256)
- ✅ Token expiration check
- ✅ Issuer validation (iss claim)
- ✅ Audience validation (aud claim)
- ✅ Policy caching (5 min TTL)

### 3. Lambda Function
- ✅ Least privilege IAM role
- ✅ VPC isolation (optional)
- ✅ Environment variable encryption (KMS)
- ✅ No PHI in logs (anonymized IDs only)

### 4. Bedrock Access
- ✅ IAM policy for specific model access
- ✅ No data stored by AWS Bedrock
- ✅ Request/response encryption (TLS)
- ✅ Audit trail in CloudTrail

### 5. DynamoDB
- ✅ Encryption at rest (AWS managed KMS)
- ✅ Encryption in transit (TLS)
- ✅ Point-in-time recovery enabled
- ✅ TTL for automatic data deletion (HIPAA)
- ✅ Fine-grained access control (IAM)

---

## Monitoring & Observability

### CloudWatch Metrics
```yaml
Custom Metrics:
  - DiagnosisLatency:
      Unit: Milliseconds
      Dimensions: [Environment, Version]
      Alarm: > 5000ms

  - DiagnosisConfidence:
      Unit: None (0-1)
      Dimensions: [Model, Version]
      Alarm: < 0.6

  - BedrockTokenUsage:
      Unit: Count
      Dimensions: [Model]
      Budget: 1M tokens/month

  - ErrorRate:
      Unit: Count
      Dimensions: [ErrorType]
      Alarm: > 5 errors/min
```

### CloudWatch Logs Insights Queries
```sql
-- Find slow diagnoses
fields @timestamp, case_id, latency
| filter @message like /diagnosis_complete/
| filter latency > 5000
| sort latency desc
| limit 20

-- Track confidence scores
fields @timestamp, case_id, confidence
| filter @message like /diagnosis_complete/
| stats avg(confidence), min(confidence), max(confidence) by bin(5m)

-- Error analysis
fields @timestamp, error_type, error_message
| filter @level = "ERROR"
| stats count() by error_type
```

### X-Ray Tracing
- End-to-end trace from API Gateway to DynamoDB
- Visualize bottlenecks in service map
- Track Bedrock API latency
- Identify cold starts

---

## Cost Optimization

### Estimated Monthly Costs (1000 diagnoses/month)

| Service | Usage | Unit Cost | Monthly Cost |
|---------|-------|-----------|--------------|
| API Gateway | 1000 requests | $3.50/million | $0.004 |
| Lambda | 1000 invocations × 5s × 1024MB | $0.0000166667/GB-sec | $0.08 |
| Bedrock Claude 3 Sonnet | 1000 requests × 8K tokens | $0.003/1K input + $0.015/1K output | $30-50 |
| DynamoDB | 1000 writes + 5000 reads | On-demand pricing | $1.25 |
| S3 | 100GB storage + 1000 uploads | Standard tier | $2.30 |
| CloudWatch | 5GB logs + metrics | Standard pricing | $2.50 |
| **Total** | | | **~$36-58/month** |

**Cost per diagnosis: $0.036 - $0.058**

---

## Code References

| Component | File Path | Line Numbers |
|-----------|-----------|--------------|
| POST /diagnosis endpoint | `backend/main.py` | 47-69 |
| NeuroAgent.analyze_case() | `backend/agents/neuro_agent.py` | 15-36 |
| BedrockService.invoke_agent() | `backend/services/bedrock_service.py` | 18-35 |
| BedrockService.invoke_model_direct() | `backend/services/bedrock_service.py` | 69-95 |
| KnowledgeBase.get_treatment_guidelines() | `backend/utils/medical_knowledge.py` | 35-44 |
| KnowledgeBase.check_drug_interactions() | `backend/utils/medical_knowledge.py` | 46-61 |
| DiagnosisRequest model | `backend/models/patient.py` | 31-38 |
| DiagnosisResponse model | `backend/models/patient.py` | 40-47 |

---

**Document Version**: 1.0
**Last Updated**: October 12, 2025
**Author**: Claude Code with NeuroAgent Team
**Purpose**: AWS AI Agent Global Hackathon - Complete API Flow Documentation
