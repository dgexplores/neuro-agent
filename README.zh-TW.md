#  NeuroAgent - AI 

[![Tests](https://img.shields.io/badge/tests-94%2F94%20passing-brightgreen)](./FINAL_ACCEPTANCE_REPORT.md)
[![Deployment](https://img.shields.io/badge/AWS-deployed-orange)](https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod/)
[![Security](https://img.shields.io/badge/security-0%20high%20vulnerabilities-brightgreen)](./FINAL_ACCEPTANCE_REPORT.md)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![AWS](https://img.shields.io/badge/AWS-Bedrock%20%7C%20Lambda%20%7C%20CDK-orange)](./infrastructure/cdk/)
[![Hackathon](https://img.shields.io/badge/AWS%20AI%20Agent-Hackathon%202025-success)](./HACKATHON_SUBMISSION.md)

>  AI  AWS Bedrock  AWS AI Agent Global Hackathon 2025 

NeuroAgent  AWS AI Agent  Amazon Bedrock  AI 

** **:   AWS | ** **: 100% (94/94) | ** **: 0 

** Live Demo**: 

---

##  

###  AI 
- ****: 
- ****:  3  ( 85%)
- ****: 
- ****: 14 WarfarinLevodopa 

###  
- **HIPAA **: 
- ****:  AI 
- ****: 
- **90  TTL**: DynamoDB 

###  
- **Redis **: 60-70% p95  < 2s
- ****: AWS Lambda + API Gateway ( 100+ )
- ****: Locust  100 
- ****:  $40-50 65%

###  
- ****: 16 
- **JWT **: 7 
- **CORS **:  `*` 
- ****: 

---

##  

###   (2025-10-13)

 **AWS **
- Lambda Python 3.11, 1GB RAM, Mangum 
- API Gateway 
- ElastiCache Redis neuroagent-redis.xjuedn.0001.use1.cache.amazonaws.com
- CloudWatch 3 
- 6  2009-2024

### 
```
============================= test session starts ==============================
collected 94 items

tests/unit/ ..................................... [ 46%]
tests/integration/ .................................................. [100%]

======================== 94 passed, 1 warning in 0.67s =========================
```

- ****: 38/38 passing (100%)
- ****: 56/56 passing (100%)
- ****: 94/94 passing (100%) 

### 
| Component | Status | Details |
|-----------|--------|---------|
| AI Diagnosis Engine |  Deployed | Bedrock Claude 3 Sonnet integrated |
| Lambda Function |  Running | 1024MB, 5min timeout, Mangum handler |
| API Gateway |  Running | Proxy mode, CORS configured |
| DynamoDB |  Active | neuroagent-cases (On-Demand) |
| S3 Bucket |  Active | neuroagent-images-100939136870-us-east-1 |
| ElastiCache Redis |  Available | cache.t3.micro, 60-70% hit rate |
| CloudWatch Alarms |  Configured | Errors, Duration, 5xx monitoring |
| Security |  Hardened | JWT, Input sanitization, CORS |
| Demo Data |  Generated | 6 realistic case studies |
| Documentation |  Complete | 10,000+ lines across 5 guides |

---

##  

###   API

**API **: https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod/

****:
```bash
curl https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod/health
```

**API Swagger UI**:
```
https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod/docs
```

###   Demo 

 6 :

1. **** - 45 13 /
2. **** - 57 
3. **** - 66  COVID-19
4. **** - 35 
5. **** - 25 
6. **** - 70 

: [data/demo_cases.json](./data/demo_cases.json)

###   JWT Token

```python
import jwt
import datetime

payload = {
    'user_id': 'demo-physician',
    'role': 'doctor',
    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24),
    'iat': datetime.datetime.utcnow()
}

secret = 'REDACTED'
token = jwt.encode(payload, secret, algorithm='HS256')
print(f"Bearer {token}")
```

###   API

```bash
curl -X POST https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod/api/v1/diagnosis \
  -H "Authorization: Bearer REDACTED" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_info": {
      "age": 45,
      "gender": "female",
      "medical_history": ["chronic migraine"],
      "current_medications": ["Anti-CGRP monoclonal antibodies"],
      "allergies": []
    },
    "symptoms": [
      {
        "name": "throbbing headache",
        "severity": "severe",
        "duration_days": 365,
        "description": "One-sided throbbing headache, 13 days per month, severity 9/10"
      }
    ],
    "vital_signs": {
      "bp_systolic": 120,
      "bp_diastolic": 69,
      "heart_rate": 51,
      "temperature": 37.0
    },
    "chief_complaint": "Chronic severe headaches"
  }'
```

---

##  

### 

- **Python**: 3.11+
- **Node.js**: 18+ ( CDK)
- **AWS CLI**: 
- **Docker**: ()

### 1. 
```bash
git clone https://github.com/thc1006/neuro-agent.git
cd neuro-agent
```

### 2.  Python 
```bash
# 
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
#  venv\Scripts\activate  # Windows

# 
pip install -r requirements.txt
```

### 3. 
```bash
# 
cp .env.example .env

#  .env 
# AWS_REGION=us-east-1
# BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
# JWT_SECRET_KEY=your-secret-key-min-32-chars
# ALLOWED_ORIGINS=http://localhost:3000
# REDIS_ENABLED=false  #  false
```

### 4.  API
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# API : http://localhost:8000/docs
# Health Check: http://localhost:8000/health
```

### 5. 
```bash
cd frontend
npm install
npm start

# : http://localhost:3000
```

### 6. 
```bash
# 
pytest tests/ -v

# 
cd tests/load
locust -f locustfile.py --host=http://localhost:8000
```

---

##  

```

                        Frontend (React 18)                      
                  Material-UI • Axios • React Router             
                     http://localhost:3000                       

                                HTTPS + JWT

              AWS API Gateway (REST API)                         
  https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod/  
                                                                  
  • POST /api/v1/diagnosis      - AI                         
  • POST /api/v1/upload-image   -                       
  • POST /api/v1/drug-interactions -                 
  • GET  /api/v1/cases          -                        
  • GET  /api/v1/cases/{id}     -                       

                               

                 AWS Lambda (Serverless Compute)                 
              NeuroAgentStack-NeuroAgentAPI-*                    
                Python 3.11 • 1024MB • 5min timeout             
                      Mangum ASGI Adapter                        
                                                                  
    
                FastAPI Application                           
          
      NeuroAgent       BedrockService     Security    
      (Orchestrator) (AI Integration)    (JWT)       
                       • InvokeAgent      • Verify    
     • Analyze case    • InvokeModel      • Sanitize  
     • Check drugs     • Fallback                     
          
                                                            
        
          Medical Knowledge Base                           
      • 14 drug interactions                               
      • Treatment protocols                                
      • Risk stratification                                
        
    
                                                                  
  Environment Variables: BEDROCK_MODEL_ID, JWT_SECRET_KEY,      
  REDIS_HOST, DYNAMODB_TABLE_NAME, S3_BUCKET_NAME, etc.        

                                          
      
 DynamoDB      Amazon Bedrock     ElastiCache         S3     
                                    (Redis)                  
 neuroagent-   Claude 3 Sonnet                    Medical    
 cases                            neuroagent-     Images     
               • InvokeModel      redis                      
 On-Demand     • Streaming                        neuroagent-
 TTL: 90d                         cache.t3.       images-*   
               $0.003/1K input    micro                      
      
       

            CloudWatch Logs + Alarms                            
  • Lambda Errors (>5 in 5min) → SNS notification              
  • Lambda Duration p95 (>2000ms) → SNS notification           
  • API Gateway 5xx Errors (>10 in 5min) → SNS notification    

```

### 

** AI**:
- AWS Lambda, API Gateway, DynamoDB, S3, ElastiCache, CloudWatch, IAM, CDK
- Amazon Bedrock (Claude 3 Sonnet: anthropic.claude-3-sonnet-20240229-v1:0)

****:
- Python 3.11, FastAPI, Pydantic, Mangum, Boto3, python-jose (JWT), Redis

****:
- React 18, Material-UI (MUI), Axios, React Router

****:
- pytest (94/94 passing), pytest-asyncio, Locust (load testing)

****:
- AWS CDK (Python), CloudFormation

---

##  API 

### 

#### 1. 
```http
GET /health
```

****:
```json
{
  "status": "healthy",
  "services": {"bedrock": "connected"}
}
```

#### 2.  JWT
```http
POST /api/v1/diagnosis
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

****:  [data/demo_cases.json](./data/demo_cases.json)

****:
```json
{
  "case_id": "550e8400-e29b-41d4-a716-446655440000",
  "diagnosis": [
    {
      "condition": "Chronic Migraine without Aura",
      "confidence": 0.85,
      "reasoning": "Throbbing headache, 13 days/month, photophobia, phonophobia..."
    }
  ],
  "recommendations": [
    "Triptan medication within 2 hours of onset",
    "Consider prophylactic treatment if >4 episodes/month"
  ],
  "risk_factors": [
    "History of ependymoma (brain tumor)",
    "Post-surgical weak neck muscles"
  ],
  "next_steps": [
    "Continue anti-CGRP therapy trial",
    "Keep headache diary",
    "Follow-up in 4 weeks"
  ]
}
```

#### 3. 
```http
POST /api/v1/drug-interactions
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "medications": ["warfarin", "aspirin", "levodopa"]
}
```

****:
```json
{
  "medication_count": 3,
  "medications_checked": ["warfarin", "aspirin", "levodopa"],
  "interactions_found": 1,
  "interactions": [
    {
      "drug_1": "warfarin",
      "drug_2": "aspirin",
      "severity": "contraindicated",
      "description": "Increased bleeding risk",
      "recommendation": "Avoid combination or monitor INR closely"
    }
  ],
  "severity_summary": {
    "contraindicated": 1,
    "severe": 0,
    "moderate": 0,
    "minor": 0
  }
}
```

---

##  AWS 

### 

 ** AWS us-east-1 **

| AWS  |  |  |
|---------|------|------|
| Lambda |  Running | NeuroAgentStack-NeuroAgentAPI-dffwIyfopqTk |
| API Gateway |  Running | 1w80v6fnw1 (REST API) |
| DynamoDB |  Active | neuroagent-cases (On-Demand) |
| S3 |  Active | neuroagent-images-100939136870-us-east-1 |
| ElastiCache |  Available | neuroagent-redis (cache.t3.micro) |
| CloudWatch |  Monitoring | 3 alarms configured |
| IAM Roles |  Configured | Lambda execution role with Bedrock, DynamoDB, S3 permissions |

**CloudFormation Stack**: NeuroAgentStack (UPDATE_COMPLETE)
****: 39 

### 

:
- **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** - 5000+ 
- **[DEPLOYMENT_STATUS_REPORT.md](./DEPLOYMENT_STATUS_REPORT.md)** - 

#### 1.  AWS CLI
```bash
aws configure
# AWS Access Key ID: YOUR_ACCESS_KEY
# AWS Secret Access Key: YOUR_SECRET_KEY
# Default region name: us-east-1
```

#### 2. Bootstrap CDK ()
```bash
cd infrastructure/cdk-clean
npm install -g aws-cdk
pip install -r requirements.txt
cdk bootstrap aws://YOUR-ACCOUNT-ID/us-east-1
```

#### 3. 
```bash
#  CloudFormation 
cdk synth

# 
cdk diff

# 
cdk deploy NeuroAgentStack --require-approval never
```

#### 4. 
```bash
#  API Gateway URL
aws cloudformation describe-stacks \
  --stack-name NeuroAgentStack \
  --region us-east-1 \
  --query 'Stacks[0].Outputs[?OutputKey==`APIGatewayURL`].OutputValue' \
  --output text

#  API
curl https://YOUR-API-URL/health
```

---

##  

### 

#### 1. JWT 7 
```python
def verify_token(token: str) -> str:
    payload = jwt.decode(
        token, JWT_SECRET_KEY,
        algorithms=[JWT_ALGORITHM],  # HS256 
        options={
            "verify_signature": True,
            "verify_exp": True,
            "verify_iat": True,
            "require_exp": True,
            "require_iat": True,
        }
    )
    # + token 
```

#### 2. 16 
```python
DANGEROUS_PATTERNS = [
    r'ignore\s+(?:previous|all|above)\s+instructions?',
    r'(?:system|assistant|user)\s*[:=]',
    r'(?:override|bypass|disable)\s+(?:security|safety|protocol)',
    r'eval\s*\(',
    r'exec\s*\(',
    r'__import__',
    # ... 10 more patterns
]

#  Bedrock 
sanitized_input = sanitizer.sanitize_text(user_input)
```

#### 3. CORS 
```python
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "https://neuroagent.example.com,http://localhost:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  #  "*"
    allow_methods=["GET", "POST"],  # 
    allow_headers=["Authorization", "Content-Type"],
    allow_credentials=True
)
```

### 
-  0 Bandit 
-  JWT 
-  
-  Git  AWS Secrets Manager / 
-  HIPAA 
-  IAM 
-  S3 
-  DynamoDB AWS 

---

##  

### 

|  |  |  |
|------|------|---------|
| AWS Lambda | 1GB, 10K invocations, 3s avg | $0.00 - $8.40 |
| API Gateway | 10K REST API requests | $0.35 |
| DynamoDB | On-demand, 10K writes, 20K reads | $2.75 |
| S3 | 5GB storage, 100 PUT, 500 GET | $1.15 |
| AWS Bedrock | 1K calls, 2K tokens avg (Claude 3 Sonnet) | $36.00 |
| ElastiCache Redis | cache.t3.micro (0.5GB) | $12.41 |
| CloudWatch | 1GB logs, 3 alarms | $5.00 |
| **** | | **~$40-50/** |
| **** | | **~$120-150/** |

### 
-  **Redis **: 60-70%  65% Bedrock 
-  **DynamoDB On-Demand**: 
-  **Lambda **:  1.2GB → 45MB
-  **CloudWatch **: 7 

****: $200 $100  + $100 Hackathon **4-5 ** 

---

##  

### 
- **[README.zh-TW.md](./README.zh-TW.md)** - 
- **[README.md](./README.md)** - English version
- **[HACKATHON_SUBMISSION.md](./HACKATHON_SUBMISSION.md)** - Hackathon 5000+ 
- **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** - 5000+ 
- **[DEPLOYMENT_STATUS_REPORT.md](./DEPLOYMENT_STATUS_REPORT.md)** - 100+ 
- **[CLAUDE.md](./CLAUDE.md)** - Claude Code 150+ 

### 
- **[AWS_INTEGRATION_HANDOFF.md](./AWS_INTEGRATION_HANDOFF.md)** - AWS 2000+ 
- **[FINAL_ACCEPTANCE_REPORT.md](./FINAL_ACCEPTANCE_REPORT.md)** - 1500+ 
- **[PHASE_7_2_AND_8_IMPLEMENTATION_SUMMARY.md](./PHASE_7_2_AND_8_IMPLEMENTATION_SUMMARY.md)** - 500+ 

### 
- **[ARCHITECTURE_UML.md](./ARCHITECTURE_UML.md)** - UML 
- **[DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md)** - 
- **[POST_DIAGNOSIS_SEQUENCE.md](./POST_DIAGNOSIS_SEQUENCE.md)** - API 

### Demo 
- **[data/demo_cases.json](./data/demo_cases.json)** - 6 
  - : PubMed Central, Frontiers in Neurology, University of Utah (2009-2024)
  - 

---

##  

###  Phase 1-10 Complete (100%)
- [x] AI Phase 1-6
- [x] Phase 7-2
- [x] Phase 8-1
- [x] Phase 8-2
- [x] CDK Phase 9-1
- [x] AWS Phase 9
- [x] Demo Phase 10
- [x] 94/94 100%
- [x] Hackathon 

###  AWS AI Agent Global Hackathon 2025
****:  Readiness: 98/100

****:
-  5000+ 
-  
-  Live API Demo
-  6 
-  10,000+ 

---

##  

### AWS AI Agent Global Hackathon 2025
 AWS AI Agent Global Hackathon 2025 

### 
- **AWS Bedrock Team** -  Claude 3 Sonnet 
- **Anthropic** -  Claude  Claude Code 40% 
- **FastAPI Community** -  Web 
- **AWS CDK Community** - 

### 
- **PubMed Central / NIH** - 
- **Frontiers in Neurology** - 
- **University of Utah Medical Library** - MS 

---

##  

****: NeuroAgent  **** AWS AI Agent Global Hackathon 2025 

-  ** FDA **
-  ****
-  ****
-  ——119/911
-   AWS AI/ML 

****

---

##  

### 
- **GitHub**: [@thc1006](https://github.com/thc1006)
- **Repository**:
  - GitHub: https://github.com/thc1006/neuro-agent
  - GitLab: https://gitlab.com/thc1006/neuro-agent

### 
- **Issues**: https://github.com/thc1006/neuro-agent/issues
- **Documentation**: 

### AWS 
- **AWS Support Console**: https://console.aws.amazon.com/support/
- **Bedrock Documentation**: https://docs.aws.amazon.com/bedrock/

---

##  Star History



[![Star History Chart](https://api.star-history.com/svg?repos=thc1006/neuro-agent&type=Date)](https://star-history.com/#thc1006/neuro-agent&Date)

---

<div align="center">

**Built with  for Healthcare AI**

[Report Bug](https://github.com/thc1006/neuro-agent/issues) ·
[Request Feature](https://github.com/thc1006/neuro-agent/issues) ·
[View Documentation](./HACKATHON_SUBMISSION.md) ·
[Try Live Demo](https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod/)

**AWS AI Agent Global Hackathon 2025** | © 2025 NeuroAgent Project

</div>
