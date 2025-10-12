# AWS Integration Handoff Document
## NeuroAgent - AI-Driven Neurological Diagnosis Assistant

**Document Version**: 1.0
**Last Updated**: 2025-10-12
**Target Deployment**: AWS EC2 + Lambda + Bedrock + DynamoDB + S3
**Handoff Date**: [To be determined]

---

## 📋 Executive Summary

This document provides a comprehensive handoff guide for integrating NeuroAgent with AWS services. The project has completed **Phases 1-10** with a solid foundation including:

✅ **Completed Components**:
- Backend API with FastAPI (92/92 tests passing)
- AI agent framework with Bedrock service layer
- Security hardening (CORS, input sanitization, JWT validation)
- Redis caching architecture
- Blue/Green deployment infrastructure (CDK)
- Load testing framework (Locust)
- Automated demo script (Playwright)
- Comprehensive documentation

🔧 **Requires AWS Integration**:
- AWS Bedrock AgentCore (AI model invocation)
- DynamoDB (case storage)
- S3 (medical image storage)
- ElastiCache Redis (performance caching)
- CloudWatch (monitoring and logging)
- SageMaker (medical image analysis - future)

---

## 🎯 Project Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React)                         │
│                    localhost:3000 / CloudFront                  │
└──────────────────────────────┬──────────────────────────────────┘
                               │ HTTPS
┌──────────────────────────────▼──────────────────────────────────┐
│                   API Gateway (REST API)                        │
│            /api/v1/diagnosis, /api/v1/upload-image             │
└──────────────────────────────┬──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│                    Lambda Function (FastAPI)                    │
│               Python 3.11 | 1024MB RAM | 5min timeout          │
│                                                                 │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐ │
│  │  NeuroAgent      │  │ BedrockService   │  │ Auth/Cache   │ │
│  │  (Diagnosis)     │──│ (AI Integration) │  │ (Security)   │ │
│  └──────────────────┘  └──────────────────┘  └──────────────┘ │
└─────────┬──────────────────────┬──────────────────┬────────────┘
          │                      │                  │
          │                      │                  │
  ┌───────▼───────┐     ┌───────▼────────┐  ┌──────▼──────┐
  │   DynamoDB    │     │ AWS Bedrock    │  │ ElastiCache │
  │ (Case Storage)│     │ AgentCore/AI   │  │  (Redis)    │
  └───────────────┘     └────────────────┘  └─────────────┘
          │
  ┌───────▼───────┐     ┌─────────────────┐
  │      S3       │     │   CloudWatch    │
  │ (Med Images)  │     │ (Logs/Metrics)  │
  └───────────────┘     └─────────────────┘
```

---

## 📂 Project Structure Analysis

### Current File Structure

```
neuro-agent/
├── backend/
│   ├── agents/
│   │   └── neuro_agent.py          ✅ COMPLETE (AI orchestration logic)
│   ├── cache/
│   │   └── redis_cache.py          ✅ COMPLETE (needs Redis endpoint)
│   ├── models/
│   │   └── patient.py              ✅ COMPLETE (Pydantic models)
│   ├── services/
│   │   ├── bedrock_service.py      🔧 NEEDS AWS CREDENTIALS
│   │   ├── dynamodb_service.py     ❌ MISSING (to implement)
│   │   └── s3_service.py           ❌ MISSING (to implement)
│   ├── utils/
│   │   ├── auth.py                 ✅ COMPLETE (JWT validation)
│   │   ├── input_sanitizer.py      ✅ COMPLETE (security)
│   │   └── medical_knowledge.py    ✅ COMPLETE (knowledge base)
│   ├── tests/                      ✅ 92/92 PASSING
│   └── main.py                     ✅ COMPLETE (FastAPI app)
├── frontend/
│   └── src/                        ✅ COMPLETE (needs backend URL)
├── infrastructure/
│   └── cdk/
│       ├── app.py                  ✅ COMPLETE (needs env vars)
│       ├── cdk-bluegreen.ts        ✅ COMPLETE (Blue/Green deploy)
│       └── cdk.json                🔧 NEEDS CONFIGURATION
└── tests/
    ├── e2e/demo.spec.ts            ✅ COMPLETE (Playwright)
    └── load/locustfile.py          ✅ COMPLETE (load testing)
```

### Component Completion Status

| Component | Status | Tests | AWS Integration Required |
|-----------|--------|-------|--------------------------|
| FastAPI Backend | ✅ Complete | 92/92 passing | Bedrock, DynamoDB, S3 |
| AI Agent Logic | ✅ Complete | ✅ Tested | Bedrock AgentCore |
| Security Layer | ✅ Complete | ✅ Tested | None (ready) |
| Caching Layer | ✅ Complete | ✅ Tested | ElastiCache Redis |
| DynamoDB Service | ❌ Missing | ❌ No tests | DynamoDB Table |
| S3 Service | ❌ Missing | ❌ No tests | S3 Bucket |
| Bedrock Integration | 🔧 Partial | ⚠️ Mock | Bedrock Agent ID |
| CDK Infrastructure | ✅ Complete | N/A | AWS Account |
| Frontend | ✅ Complete | ✅ Manual | API Gateway URL |

---

## 🔧 Missing Components (To Implement with TDD)

### 1. DynamoDB Service Layer

**Purpose**: Store and retrieve patient cases in DynamoDB

**File to Create**: `backend/services/dynamodb_service.py`

**Required Operations**:
- `create_case(case_data: Dict)` - Store new diagnosis case
- `get_case(case_id: str)` - Retrieve case by ID
- `list_cases(user_id: str, limit: int)` - List user's cases
- `update_case(case_id: str, updates: Dict)` - Update case status
- `delete_case(case_id: str)` - Soft delete (mark as inactive)

**DynamoDB Table Schema**:
```python
Table Name: neuroagent-cases (from CDK)
Partition Key: case_id (String)
Sort Key: created_at (String, ISO 8601 timestamp)

Attributes:
- case_id: str (UUID)
- user_id: str (from JWT token)
- patient_info: Map (age, gender, medical_history, etc.)
- symptoms: List<Map>
- diagnosis_result: Map
- status: str (pending | analyzed | completed | failed)
- created_at: str (ISO timestamp)
- updated_at: str (ISO timestamp)
- ttl: number (Unix timestamp for auto-expiration after 90 days)

Global Secondary Index (GSI):
- GSI Name: user-index
- Partition Key: user_id
- Sort Key: created_at
```

**Test Requirements** (`backend/tests/unit/test_dynamodb_service.py`):
1. Test case creation with valid data
2. Test case retrieval by ID
3. Test list cases by user_id with pagination
4. Test case update operations
5. Test error handling (non-existent case, network errors)
6. Test TTL calculation (90 days expiration)
7. Mock boto3 DynamoDB client

**AWS Dependencies**:
- DynamoDB table: `neuroagent-cases` (created by CDK)
- IAM permissions: `dynamodb:PutItem`, `dynamodb:GetItem`, `dynamodb:Query`, `dynamodb:UpdateItem`

---

### 2. S3 Service Layer

**Purpose**: Upload and retrieve medical images from S3

**File to Create**: `backend/services/s3_service.py`

**Required Operations**:
- `upload_image(image_file, image_id: str, user_id: str)` - Upload to S3
- `generate_presigned_url(image_id: str, expiration: int)` - Get signed URL
- `get_image_metadata(image_id: str)` - Retrieve image info
- `delete_image(image_id: str)` - Remove image from S3

**S3 Bucket Structure**:
```
Bucket: neuroagent-images-{account-id}-{region} (from CDK)

Key Format:
medical-images/{user_id}/{case_id}/{image_id}.{ext}

Example:
medical-images/user-123/case-456/img-789.jpg

Metadata (stored as S3 object tags):
- case_id: Associated diagnosis case
- user_id: Owner
- modality: MRI | CT | X-ray
- upload_date: ISO timestamp
- content_type: image/jpeg | image/png | application/dicom
```

**Test Requirements** (`backend/tests/unit/test_s3_service.py`):
1. Test image upload with valid JPEG/PNG
2. Test presigned URL generation
3. Test metadata retrieval
4. Test image deletion
5. Test error handling (invalid file type, size limits)
6. Test DICOM format support (future)
7. Mock boto3 S3 client

**AWS Dependencies**:
- S3 bucket: `neuroagent-images-{account}-{region}` (created by CDK)
- IAM permissions: `s3:PutObject`, `s3:GetObject`, `s3:DeleteObject`, `s3:GetObjectMetadata`

---

### 3. Integration Tests for AWS Services

**File to Create**: `backend/tests/integration/test_aws_integration.py`

**Test Scenarios**:
1. **End-to-End Diagnosis Flow**:
   - Submit diagnosis request
   - Verify case stored in DynamoDB
   - Check Bedrock invocation
   - Validate response format

2. **Image Upload Flow**:
   - Upload medical image
   - Verify S3 storage
   - Check image metadata
   - Generate presigned URL

3. **Cache Integration**:
   - Test Redis cache hits
   - Test cache misses fall back to Bedrock
   - Verify cache TTL

4. **Error Recovery**:
   - Test Bedrock timeout handling
   - Test DynamoDB throttling
   - Test S3 upload failures

**Test Setup Requirements**:
- LocalStack (for local AWS service mocking)
- Moto (Python AWS mock library)
- Test fixtures for DynamoDB tables and S3 buckets

---

## 🔐 AWS Credentials & Configuration

### Environment Variables Required

**File**: `.env` (DO NOT COMMIT TO GIT)

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_SESSION_TOKEN=...  # If using temporary credentials

# Bedrock Configuration
BEDROCK_AGENTCORE_AGENT_ID=AGENT123456
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0

# DynamoDB Configuration
DYNAMODB_TABLE_NAME=neuroagent-cases
DYNAMODB_ENDPOINT_URL=  # Leave empty for prod, use http://localhost:8000 for LocalStack

# S3 Configuration
S3_BUCKET_NAME=neuroagent-images-{account-id}-us-east-1
S3_ENDPOINT_URL=  # Leave empty for prod

# ElastiCache Redis Configuration
REDIS_ENABLED=true
REDIS_HOST=neuroagent-cache.abc123.0001.use1.cache.amazonaws.com
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=  # If AUTH enabled

# Authentication & Security
JWT_SECRET_KEY=your-super-secret-jwt-key-min-32-characters
ALLOWED_ORIGINS=https://neuroagent.example.com,https://staging.neuroagent.example.com

# Application Configuration
ENV=production  # development | staging | production
LOG_LEVEL=INFO  # DEBUG | INFO | WARNING | ERROR
```

### CDK Context Configuration

**File**: `infrastructure/cdk/cdk.json`

```json
{
  "context": {
    "bedrock_agent_id": "AGENT123456",
    "jwt_secret_key": "your-super-secret-jwt-key-min-32-characters",
    "allowed_origins": "https://neuroagent.example.com",
    "redis_enabled": "true",
    "redis_host": "neuroagent-cache.abc123.0001.use1.cache.amazonaws.com"
  }
}
```

**⚠️ SECURITY WARNING**: Never commit actual secrets to Git. Use AWS Secrets Manager or Systems Manager Parameter Store for production.

---

## 🚀 Deployment Steps (Step-by-Step)

### Phase 1: AWS Account Setup & IAM Configuration

**Prerequisites**:
- AWS Account with admin access
- AWS CLI installed and configured
- AWS CDK CLI installed (`npm install -g aws-cdk`)

**Steps**:

1. **Configure AWS CLI**:
```bash
aws configure
# AWS Access Key ID: AKIA...
# AWS Secret Access Key: ...
# Default region name: us-east-1
# Default output format: json
```

2. **Verify AWS Access**:
```bash
aws sts get-caller-identity
# Should return: UserId, Account, Arn
```

3. **Bootstrap CDK** (one-time per account/region):
```bash
cd infrastructure/cdk
cdk bootstrap aws://ACCOUNT-ID/us-east-1
```

4. **Create IAM Role for Lambda**:
   - CDK will automatically create the role
   - Verify permissions include:
     - Bedrock: `bedrock:InvokeAgent`, `bedrock:InvokeModel`
     - DynamoDB: `dynamodb:*` on `neuroagent-cases` table
     - S3: `s3:*` on `neuroagent-images-*` bucket
     - CloudWatch: `logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents`
     - ElastiCache: `elasticache:DescribeCacheClusters`

---

### Phase 2: Deploy Infrastructure with CDK

**Steps**:

1. **Review CDK Stack**:
```bash
cd infrastructure/cdk
cdk synth
# Review generated CloudFormation template
```

2. **Deploy DynamoDB + S3 + Lambda**:
```bash
cdk deploy NeuroAgentStack
# Confirm changes: yes
```

**Expected Outputs**:
```
Outputs:
NeuroAgentStack.APIGatewayURL = https://abc123.execute-api.us-east-1.amazonaws.com/prod/
NeuroAgentStack.DynamoDBTableName = neuroagent-cases
NeuroAgentStack.S3BucketName = neuroagent-images-123456-us-east-1
```

3. **Verify Resources Created**:
```bash
# DynamoDB Table
aws dynamodb describe-table --table-name neuroagent-cases

# S3 Bucket
aws s3 ls | grep neuroagent-images

# Lambda Function
aws lambda get-function --function-name NeuroAgentStack-NeuroAgentAPI

# API Gateway
aws apigateway get-rest-apis | grep NeuroAgent
```

---

### Phase 3: Deploy ElastiCache Redis

**Steps**:

1. **Create Redis Cluster**:
```bash
aws elasticache create-cache-cluster \
  --cache-cluster-id neuroagent-cache \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --engine-version 7.0 \
  --num-cache-nodes 1 \
  --preferred-availability-zone us-east-1a \
  --tags Key=Project,Value=NeuroAgent Key=Environment,Value=production
```

2. **Wait for Cluster to be Available** (5-10 minutes):
```bash
aws elasticache describe-cache-clusters \
  --cache-cluster-id neuroagent-cache \
  --show-cache-node-info
```

3. **Get Redis Endpoint**:
```bash
aws elasticache describe-cache-clusters \
  --cache-cluster-id neuroagent-cache \
  --show-cache-node-info \
  --query 'CacheClusters[0].CacheNodes[0].Endpoint.Address' \
  --output text
```

**Output Example**: `neuroagent-cache.abc123.0001.use1.cache.amazonaws.com`

4. **Update CDK Context** with Redis endpoint and redeploy:
```bash
# Edit infrastructure/cdk/cdk.json
# "redis_host": "neuroagent-cache.abc123.0001.use1.cache.amazonaws.com"

cdk deploy NeuroAgentStack
```

---

### Phase 4: Configure AWS Bedrock AgentCore

**Steps**:

1. **Enable Bedrock Model Access**:
```bash
# Go to AWS Console → Bedrock → Model Access
# Request access to: Anthropic Claude 3 Sonnet
# Wait for approval (usually immediate)
```

2. **Create Bedrock Agent** (Option A: Console):
   - Navigate to AWS Console → Bedrock → Agents
   - Click "Create Agent"
   - Agent Name: `neuro-diagnosis-agent`
   - Model: `anthropic.claude-3-sonnet-20240229-v1:0`
   - Instructions: Use neurological diagnosis prompt from `backend/agents/neuro_agent.py:173-209`
   - Create Agent Alias: `production`
   - Note the Agent ID: `AGENT123456`

3. **Create Bedrock Agent** (Option B: CLI):
```bash
# Create agent configuration file
cat > agent-config.json <<EOF
{
  "agentName": "neuro-diagnosis-agent",
  "foundationModel": "anthropic.claude-3-sonnet-20240229-v1:0",
  "instruction": "You are an expert neurologist AI assistant. Analyze patient cases and provide comprehensive neurological assessments...",
  "description": "AI agent for neurological diagnosis assistance",
  "idleSessionTTLInSeconds": 1800
}
EOF

# Create agent
aws bedrock-agent create-agent --cli-input-json file://agent-config.json

# Get Agent ID from output
# "agentId": "AGENT123456"
```

4. **Update Lambda Environment Variables**:
```bash
aws lambda update-function-configuration \
  --function-name NeuroAgentStack-NeuroAgentAPI \
  --environment Variables="{
    BEDROCK_AGENTCORE_AGENT_ID=AGENT123456,
    BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
  }"
```

5. **Test Bedrock Integration**:
```bash
# From local machine with AWS credentials
python3 -c "
import boto3
import json

bedrock_runtime = boto3.client('bedrock-agent-runtime', region_name='us-east-1')

response = bedrock_runtime.invoke_agent(
    agentId='AGENT123456',
    agentAliasId='TSTALIASID',
    sessionId='test-session-001',
    inputText='Analyze a 45-year-old with headache and dizziness'
)

print('Bedrock agent invoked successfully!')
"
```

---

### Phase 5: Implement Missing Services (TDD Approach)

#### 5.1 DynamoDB Service

**Create Tests First** (`backend/tests/unit/test_dynamodb_service.py`):

```python
import pytest
from moto import mock_dynamodb
import boto3
from backend.services.dynamodb_service import DynamoDBService

@mock_dynamodb
def test_create_case_success():
    # Setup mock DynamoDB
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.create_table(
        TableName='neuroagent-cases',
        KeySchema=[{'AttributeName': 'case_id', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'case_id', 'AttributeType': 'S'}],
        BillingMode='PAY_PER_REQUEST'
    )

    # Create service
    service = DynamoDBService(table_name='neuroagent-cases')

    # Test data
    case_data = {
        'user_id': 'user-123',
        'patient_info': {'age': 45, 'gender': 'male'},
        'symptoms': [{'name': 'headache', 'severity': 'moderate'}],
        'status': 'pending'
    }

    # Execute
    result = service.create_case(case_data)

    # Assert
    assert 'case_id' in result
    assert result['status'] == 'pending'
    assert len(result['case_id']) == 36  # UUID length
```

**Implement Service** (`backend/services/dynamodb_service.py`):

```python
import boto3
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid
import os

class DynamoDBService:
    def __init__(self, table_name: Optional[str] = None):
        self.table_name = table_name or os.getenv('DYNAMODB_TABLE_NAME', 'neuroagent-cases')
        self.dynamodb = boto3.resource('dynamodb', region_name=os.getenv('AWS_REGION', 'us-east-1'))
        self.table = self.dynamodb.Table(self.table_name)

    def create_case(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new case in DynamoDB"""
        case_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        ttl = int((datetime.utcnow() + timedelta(days=90)).timestamp())

        item = {
            'case_id': case_id,
            'created_at': timestamp,
            'updated_at': timestamp,
            'ttl': ttl,
            **case_data
        }

        self.table.put_item(Item=item)
        return item

    def get_case(self, case_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve case by ID"""
        response = self.table.get_item(Key={'case_id': case_id})
        return response.get('Item')

    def list_cases(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """List cases for a user"""
        response = self.table.query(
            IndexName='user-index',
            KeyConditionExpression='user_id = :uid',
            ExpressionAttributeValues={':uid': user_id},
            Limit=limit,
            ScanIndexForward=False  # Sort descending (newest first)
        )
        return response.get('Items', [])

    def update_case(self, case_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update case with new data"""
        updates['updated_at'] = datetime.utcnow().isoformat()

        update_expression = 'SET ' + ', '.join(f'{k} = :{k}' for k in updates.keys())
        expression_values = {f':{k}': v for k, v in updates.items()}

        response = self.table.update_item(
            Key={'case_id': case_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values,
            ReturnValues='ALL_NEW'
        )
        return response.get('Attributes')

    def delete_case(self, case_id: str) -> bool:
        """Soft delete case (mark as inactive)"""
        self.update_case(case_id, {'status': 'deleted', 'deleted_at': datetime.utcnow().isoformat()})
        return True
```

**Run Tests**:
```bash
pytest backend/tests/unit/test_dynamodb_service.py -v
```

#### 5.2 S3 Service (Similar TDD Approach)

**Create Tests First** (`backend/tests/unit/test_s3_service.py`)
**Implement Service** (`backend/services/s3_service.py`)
**Run Tests**: `pytest backend/tests/unit/test_s3_service.py -v`

(Full implementation provided in handoff materials)

---

### Phase 6: Integration Testing

**Setup LocalStack** (for local AWS testing):

```bash
# Install LocalStack
pip install localstack awscli-local

# Start LocalStack
localstack start -d

# Create local DynamoDB table
awslocal dynamodb create-table \
  --table-name neuroagent-cases \
  --attribute-definitions AttributeName=case_id,AttributeType=S \
  --key-schema AttributeName=case_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

# Create local S3 bucket
awslocal s3 mb s3://neuroagent-images-test
```

**Run Integration Tests**:
```bash
# Set LocalStack endpoints
export DYNAMODB_ENDPOINT_URL=http://localhost:4566
export S3_ENDPOINT_URL=http://localhost:4566

# Run tests
pytest backend/tests/integration/test_aws_integration.py -v
```

---

### Phase 7: Frontend Configuration

**Update API Base URL** (`frontend/src/services/api.js`):

```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://abc123.execute-api.us-east-1.amazonaws.com/prod';

export const submitDiagnosis = async (diagnosisRequest) => {
  const response = await fetch(`${API_BASE_URL}/api/v1/diagnosis`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getAuthToken()}`
    },
    body: JSON.stringify(diagnosisRequest)
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return response.json();
};
```

**Build and Deploy Frontend**:
```bash
cd frontend
npm install
REACT_APP_API_URL=https://your-api-gateway-url.amazonaws.com/prod npm run build

# Deploy to S3 + CloudFront (optional)
aws s3 sync build/ s3://neuroagent-frontend-bucket --delete
```

---

### Phase 8: Blue/Green Deployment (Zero-Downtime)

**Initial Deployment** (10% traffic to new version):

```bash
cd infrastructure/cdk
npm install
npm run deploy:bluegreen -- --traffic-percent 10
```

**Monitor CloudWatch Metrics** (5-10 minutes):
- Error rate < 5 errors/min ✅
- p95 latency < 2000ms ✅
- No alarms triggered ✅

**Shift Traffic Gradually**:
```bash
npm run shift -- --traffic-percent 50
# Wait 5 minutes, monitor metrics
npm run shift -- --traffic-percent 100
# Wait 5 minutes, monitor metrics
```

**Complete Deployment**:
```bash
npm run complete
```

**Emergency Rollback** (if issues detected):
```bash
npm run rollback
```

---

## 📊 Testing & Validation

### Local Testing (Before AWS Deployment)

```bash
# 1. Install dependencies
cd backend
pip install -r requirements.txt

# 2. Start LocalStack (for AWS mocking)
localstack start -d

# 3. Run all tests
pytest backend/tests/ -v

# Expected: 92+ tests passing (including new DynamoDB/S3 tests)

# 4. Start local server
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# 5. Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/docs  # Swagger UI
```

### AWS Integration Testing (After Deployment)

```bash
# 1. Health Check
curl https://YOUR-API-URL/health

# 2. Test Diagnosis Endpoint (requires JWT token)
curl -X POST https://YOUR-API-URL/api/v1/diagnosis \
  -H "Authorization: Bearer REDACTED" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_info": {
      "age": 45,
      "gender": "male",
      "medical_history": ["hypertension"],
      "current_medications": ["amlodipine"],
      "allergies": []
    },
    "symptoms": [
      {"name": "headache", "severity": "moderate", "duration_days": 3}
    ],
    "vital_signs": {"bp_systolic": 140, "bp_diastolic": 90},
    "chief_complaint": "Persistent headache for 3 days",
    "history_present_illness": "Patient reports throbbing headache..."
  }'

# 3. Test Image Upload
curl -X POST https://YOUR-API-URL/api/v1/upload-image \
  -H "Authorization: Bearer REDACTED" \
  -F "file=@test-brain-mri.jpg"

# 4. Test Case Retrieval
curl https://YOUR-API-URL/api/v1/cases/CASE-ID \
  -H "Authorization: Bearer REDACTED"
```

### Load Testing (Locust)

```bash
cd backend
locust -f tests/load/locustfile.py \
  --host=https://YOUR-API-URL \
  --users=100 \
  --spawn-rate=10 \
  --run-time=10m

# Open browser: http://localhost:8089
# Monitor: p95 < 2000ms, error rate < 1%
```

---

## 🔍 Monitoring & Observability

### CloudWatch Dashboards

**1. Create Custom Dashboard**:
```bash
aws cloudwatch put-dashboard --dashboard-name NeuroAgent-Production --dashboard-body file://dashboard-config.json
```

**Dashboard Widgets** (`dashboard-config.json`):
```json
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "title": "Lambda Invocations",
        "metrics": [
          ["AWS/Lambda", "Invocations", {"stat": "Sum"}]
        ]
      }
    },
    {
      "type": "metric",
      "properties": {
        "title": "Lambda Duration (p95)",
        "metrics": [
          ["AWS/Lambda", "Duration", {"stat": "p95"}]
        ],
        "yAxis": {"left": {"min": 0, "max": 5000}}
      }
    },
    {
      "type": "metric",
      "properties": {
        "title": "Lambda Errors",
        "metrics": [
          ["AWS/Lambda", "Errors", {"stat": "Sum"}]
        ]
      }
    },
    {
      "type": "metric",
      "properties": {
        "title": "API Gateway 4xx/5xx",
        "metrics": [
          ["AWS/ApiGateway", "4XXError", {"stat": "Sum"}],
          ["...", "5XXError", {"stat": "Sum"}]
        ]
      }
    }
  ]
}
```

### CloudWatch Alarms

**1. Lambda Error Rate Alarm**:
```bash
aws cloudwatch put-metric-alarm \
  --alarm-name NeuroAgent-Lambda-Errors \
  --alarm-description "Alert when Lambda error rate exceeds 5%" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold \
  --alarm-actions arn:aws:sns:us-east-1:ACCOUNT-ID:neuroagent-alerts
```

**2. Lambda Duration (p95) Alarm**:
```bash
aws cloudwatch put-metric-alarm \
  --alarm-name NeuroAgent-Lambda-Duration \
  --alarm-description "Alert when p95 latency exceeds 2 seconds" \
  --metric-name Duration \
  --namespace AWS/Lambda \
  --extended-statistic p95 \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 2000 \
  --comparison-operator GreaterThanThreshold \
  --alarm-actions arn:aws:sns:us-east-1:ACCOUNT-ID:neuroagent-alerts
```

**3. DynamoDB Throttling Alarm**:
```bash
aws cloudwatch put-metric-alarm \
  --alarm-name NeuroAgent-DynamoDB-Throttles \
  --metric-name UserErrors \
  --namespace AWS/DynamoDB \
  --dimensions Name=TableName,Value=neuroagent-cases \
  --statistic Sum \
  --period 300 \
  --evaluation-periods 1 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold
```

### CloudWatch Logs Insights Queries

**1. Top 10 Slowest Requests**:
```
fields @timestamp, @message, @duration
| filter @type = "REPORT"
| sort @duration desc
| limit 10
```

**2. Error Analysis**:
```
fields @timestamp, @message
| filter @message like /ERROR|Exception/
| stats count() by bin(5m)
```

**3. Bedrock API Call Analysis**:
```
fields @timestamp, bedrock_agent_id, duration_ms, status
| filter @message like /bedrock/
| stats avg(duration_ms), max(duration_ms), count() by bin(1h)
```

---

## 🛠️ Troubleshooting Guide

### Common Issues & Solutions

#### Issue 1: Lambda Timeout (5 minutes exceeded)

**Symptoms**:
- 504 Gateway Timeout errors
- CloudWatch logs show: "Task timed out after 300.00 seconds"

**Root Causes**:
- Bedrock API taking too long (> 10 seconds)
- Redis unavailable, falling back to Bedrock
- Network latency to DynamoDB/S3

**Solutions**:
1. Enable Redis caching (60-70% hit rate reduces Bedrock calls)
2. Increase Lambda timeout in CDK: `timeout=Duration.minutes(10)`
3. Use Bedrock streaming for faster initial responses
4. Check VPC configuration if Lambda in VPC

**Diagnostic Commands**:
```bash
# Check Lambda timeout configuration
aws lambda get-function-configuration \
  --function-name NeuroAgentStack-NeuroAgentAPI \
  --query 'Timeout'

# Check CloudWatch Logs for timeouts
aws logs tail /aws/lambda/NeuroAgentStack-NeuroAgentAPI \
  --since 1h --filter-pattern "Task timed out"
```

#### Issue 2: DynamoDB ProvisionedThroughputExceededException

**Symptoms**:
- 400 errors with "Rate exceeded"
- CloudWatch metrics show throttled requests

**Root Causes**:
- Insufficient on-demand capacity
- Hot partition key (not distributed)

**Solutions**:
1. Verify table is in PAY_PER_REQUEST mode (on-demand)
2. Check partition key distribution (should be UUID, not sequential)
3. Consider enabling DynamoDB auto-scaling if using provisioned

**Diagnostic Commands**:
```bash
# Check table billing mode
aws dynamodb describe-table \
  --table-name neuroagent-cases \
  --query 'Table.BillingModeSummary'

# Check throttled requests
aws cloudwatch get-metric-statistics \
  --namespace AWS/DynamoDB \
  --metric-name UserErrors \
  --dimensions Name=TableName,Value=neuroagent-cases \
  --start-time 2025-10-12T00:00:00Z \
  --end-time 2025-10-12T23:59:59Z \
  --period 3600 \
  --statistics Sum
```

#### Issue 3: Bedrock AccessDeniedException

**Symptoms**:
- 403 errors when calling Bedrock
- Error message: "User is not authorized to perform: bedrock:InvokeAgent"

**Root Causes**:
- Lambda execution role missing Bedrock permissions
- Bedrock model access not enabled
- Incorrect agent ID

**Solutions**:
1. Verify Lambda IAM role has Bedrock permissions
2. Enable model access in Bedrock console
3. Check agent ID matches environment variable

**Diagnostic Commands**:
```bash
# Check Lambda execution role permissions
aws lambda get-function \
  --function-name NeuroAgentStack-NeuroAgentAPI \
  --query 'Configuration.Role'

# Check IAM role policy
aws iam get-role-policy \
  --role-name NeuroAgentStack-LambdaExecutionRole \
  --policy-name BedrockPolicy

# Test Bedrock access manually
aws bedrock list-foundation-models --region us-east-1
```

#### Issue 4: Redis Connection Timeout

**Symptoms**:
- Slow response times (> 5 seconds)
- Logs show: "Redis connection failed, falling back to direct API"

**Root Causes**:
- Redis endpoint incorrect
- Lambda not in same VPC as ElastiCache
- Security group blocking port 6379

**Solutions**:
1. Verify Redis endpoint in environment variables
2. Move Lambda to same VPC as ElastiCache (or use VPC peering)
3. Update security group to allow inbound 6379 from Lambda security group

**Diagnostic Commands**:
```bash
# Check Redis cluster status
aws elasticache describe-cache-clusters \
  --cache-cluster-id neuroagent-cache \
  --show-cache-node-info \
  --query 'CacheClusters[0].CacheClusterStatus'

# Test Redis connectivity from EC2 in same VPC
redis-cli -h neuroagent-cache.abc123.0001.use1.cache.amazonaws.com -p 6379 PING
```

---

## 💰 Cost Estimation & Optimization

### Monthly Cost Breakdown (100,000 requests/month)

| Service | Usage | Monthly Cost |
|---------|-------|--------------|
| **AWS Lambda** | 100K invocations, 1GB RAM, 5s avg | $8.40 |
| **API Gateway** | 100K REST API requests | $0.35 |
| **DynamoDB** | On-demand, 100K writes, 200K reads, 10GB storage | $2.75 |
| **S3** | 50GB storage, 1000 PUT, 5000 GET | $1.15 |
| **AWS Bedrock** | 10K invocations, 2K tokens avg (Claude 3 Sonnet) | $120.00 |
| **ElastiCache Redis** | cache.t3.micro (0.5GB) | $12.41 |
| **CloudWatch** | 10GB logs, 100 alarms | $5.00 |
| **Data Transfer** | 50GB outbound | $4.50 |
| **Total** | | **~$154.56/month** |

### Cost Optimization Strategies

**1. Enable Redis Caching** (60-70% cache hit rate):
- **Savings**: ~$72/month in Bedrock costs
- **New Monthly Cost**: ~$82/month
- **ROI**: Redis cost ($12.41) saves 6x in Bedrock charges

**2. Reserved ElastiCache** (1-year commitment):
- **Savings**: 40% off on-demand ($4.96/month saved)
- **Cost**: $7.45/month vs $12.41/month

**3. S3 Intelligent-Tiering**:
- Automatically move infrequently accessed images to cheaper storage
- **Savings**: ~$0.30/month (30% reduction)

**4. DynamoDB On-Demand** (already implemented):
- Pay only for actual reads/writes
- No wasted provisioned capacity

**5. Lambda Provisioned Concurrency** (only if needed):
- For critical endpoints with <100ms latency requirement
- **Cost**: +$30-50/month
- **Benefit**: Eliminates cold starts

**6. CloudWatch Logs Retention**:
- Default: 7 days retention
- Reduce to 3 days for non-production: $2.50/month saved

**Total Optimized Cost**: **~$75/month** (with Redis caching + reserved ElastiCache)

---

## 📚 Additional Resources & Documentation

### Project Documentation

- **Architecture Overview**: `/docs/ARCHITECTURE.md`
- **API Documentation**: `https://YOUR-API-URL/docs` (Swagger UI)
- **Security Best Practices**: `PHASE_7_2_AND_8_IMPLEMENTATION_SUMMARY.md`
- **Performance Optimization**: `PHASE_8_IMPLEMENTATION_PLAN.md`
- **Deployment Guide**: `infrastructure/cdk/README.md`
- **Demo Video Script**: `tests/e2e/demo.spec.ts`

### AWS Documentation

- [AWS Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [DynamoDB Best Practices](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html)
- [API Gateway Documentation](https://docs.aws.amazon.com/apigateway/)
- [ElastiCache for Redis](https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/)

### Medical Compliance

- **HIPAA Compliance**: AWS provides HIPAA-eligible services (Lambda, DynamoDB, S3)
- **Medical Device Software**: FDA guidance for clinical decision support software
- **Data Retention**: Implement 90-day TTL in DynamoDB for GDPR/HIPAA compliance
- **Audit Logging**: Enable CloudTrail for all API calls

---

## ✅ Handoff Checklist

### Pre-Handoff Verification

- [ ] All 92+ tests passing locally (including new DynamoDB/S3 tests)
- [ ] AWS account access verified
- [ ] IAM roles and permissions configured
- [ ] CDK bootstrap completed
- [ ] Environment variables documented in `.env.example`
- [ ] Security review completed (no secrets in Git)

### Infrastructure Deployment

- [ ] DynamoDB table created via CDK
- [ ] S3 bucket created via CDK
- [ ] Lambda function deployed
- [ ] API Gateway configured
- [ ] ElastiCache Redis cluster provisioned
- [ ] CloudWatch logging enabled
- [ ] CloudWatch alarms configured

### AWS Service Integration

- [ ] Bedrock model access enabled
- [ ] Bedrock agent created and configured
- [ ] DynamoDB service layer implemented and tested
- [ ] S3 service layer implemented and tested
- [ ] Redis caching tested (hit/miss scenarios)
- [ ] End-to-end integration tests passing

### Frontend Deployment

- [ ] Frontend built with production API URL
- [ ] CORS configured correctly in API Gateway
- [ ] JWT authentication working
- [ ] Image upload tested
- [ ] Case history retrieval tested

### Monitoring & Alerting

- [ ] CloudWatch dashboard created
- [ ] Error rate alarms configured
- [ ] Latency alarms configured
- [ ] SNS topic for alerts configured
- [ ] Log retention configured (7 days)

### Documentation

- [ ] README updated with AWS setup instructions
- [ ] API documentation accessible (Swagger UI)
- [ ] Troubleshooting guide reviewed
- [ ] Cost estimation documented
- [ ] Handoff document reviewed and signed off

### Performance Validation

- [ ] Load testing completed (100 concurrent users)
- [ ] p95 latency < 2000ms verified
- [ ] Cache hit rate > 60% verified
- [ ] Error rate < 1% verified

### Security Validation

- [ ] No secrets in Git repository
- [ ] JWT validation working
- [ ] Input sanitization tested
- [ ] CORS restricted to specific origins
- [ ] IAM least-privilege verified
- [ ] Security scan completed (0 high-severity vulnerabilities)

---

## 🔄 Next Steps After Handoff

### Immediate Actions (Week 1)

1. **Deploy Infrastructure**: Run CDK deploy for all stacks
2. **Configure Bedrock**: Create agent and update environment variables
3. **Implement Missing Services**: DynamoDB and S3 service layers (TDD approach)
4. **Integration Testing**: Verify all AWS services working together
5. **Deploy Frontend**: Build and host frontend with production API URL

### Short-term (Week 2-4)

1. **Blue/Green Deployment**: Test zero-downtime deployment workflow
2. **Load Testing**: Validate performance under 100+ concurrent users
3. **Monitoring Setup**: Configure CloudWatch dashboards and alarms
4. **Cost Optimization**: Enable Redis caching, monitor Bedrock usage
5. **Documentation**: Record demo video with Playwright script

### Long-term (Month 2+)

1. **SageMaker Integration**: Implement real medical image analysis (Phase 7-2 TODOs)
2. **Advanced Features**: Add real-time streaming diagnosis updates
3. **Multi-region**: Deploy to additional AWS regions for redundancy
4. **Advanced Caching**: Implement multi-layer caching (Redis + Lambda)
5. **Machine Learning**: Train custom models for neurological diagnosis

---

## 📞 Support & Contact

### Technical Support

**Claude Code on AWS EC2**:
- SSH into EC2 instance
- Navigate to project directory: `cd /home/ubuntu/neuro-agent`
- Run Claude Code: `claude-code`
- Reference this document: `AWS_INTEGRATION_HANDOFF.md`

**AWS Support**:
- AWS Support Console: https://console.aws.amazon.com/support/
- Bedrock Support: bedrock-support@amazon.com
- Technical Account Manager (if Enterprise Support)

### Project Maintainer

**Handoff Prepared By**: Claude Code Assistant
**Handoff Date**: 2025-10-12
**Project Repository**: [GitHub URL]
**AWS Account ID**: [To be filled]
**Project Contact**: [To be filled]

---

## 🎓 Learning Resources

### For New Team Members

1. **FastAPI Tutorial**: https://fastapi.tiangolo.com/tutorial/
2. **AWS Lambda with Python**: https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html
3. **AWS Bedrock Workshop**: https://catalog.workshops.aws/bedrock/
4. **DynamoDB Data Modeling**: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/data-modeling.html
5. **AWS CDK Workshop**: https://cdkworkshop.com/

### Medical AI Resources

1. **FDA Guidance on Clinical Decision Support**: https://www.fda.gov/regulatory-information/search-fda-guidance-documents/clinical-decision-support-software
2. **HIPAA Security Rule**: https://www.hhs.gov/hipaa/for-professionals/security/index.html
3. **Medical Terminology (RadLex)**: https://radlex.org/
4. **HL7 FHIR Standards**: https://www.hl7.org/fhir/

---

**End of AWS Integration Handoff Document**

This comprehensive guide ensures smooth transition of NeuroAgent development to AWS environment. All missing components are documented with TDD approach, AWS integration steps are detailed, and troubleshooting guides are provided.

**Next Action**: Begin implementation following Phase 1 (AWS Account Setup) → Phase 5 (TDD Implementation) → Phase 8 (Blue/Green Deployment).

Good luck with the AWS integration! 🚀
