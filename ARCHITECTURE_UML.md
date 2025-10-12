# NeuroAgent Architecture - UML Class Diagrams

## Overview
This document provides comprehensive PlantUML diagrams for the NeuroAgent system architecture, following the structure defined in CLAUDE.md.

---

## 1. Core System Class Diagram

```plantuml
@startuml NeuroAgent_Core_Architecture

!define ENTITY class
!define SERVICE class
!define MODEL class

skinparam backgroundColor #FFFFFF
skinparam classBorderColor #2C3E50
skinparam classBackgroundColor #ECF0F1
skinparam arrowColor #3498DB

package "Models Layer" <<Rectangle>> {
    MODEL PatientInfo {
        - age: int [0-120]
        - gender: GenderEnum
        - weight: Optional<float>
        - height: Optional<float>
        - medical_history: List<str>
        - current_medications: List<str>
        - allergies: List<str>
        __
        + validate(): bool
    }

    MODEL Symptom {
        - name: str
        - severity: SeverityEnum
        - duration_days: int
        - description: Optional<str>
        __
        + to_text(): str
    }

    MODEL DiagnosisRequest {
        - patient_info: PatientInfo
        - symptoms: List<Symptom>
        - vital_signs: Dict<str, float>
        - lab_results: Dict<str, Any>
        - imaging_studies: List<str>
        - chief_complaint: str
        - history_present_illness: str
        __
        + validate(): bool
        + to_context(): Dict
    }

    MODEL DiagnosisResponse {
        - case_id: str
        - diagnosis: List<Dict<str, Any>>
        - confidence: float [0.0-1.0]
        - recommendations: List<str>
        - risk_factors: List<str>
        - next_steps: List<str>
        - timestamp: datetime
        __
        + to_json(): str
    }

    MODEL PatientCase {
        - case_id: str
        - patient_info: PatientInfo
        - request: DiagnosisRequest
        - response: Optional<DiagnosisResponse>
        - created_at: datetime
        - updated_at: datetime
        - status: str
        __
        + save(): bool
        + update_status(status: str): void
    }

    enum GenderEnum {
        MALE
        FEMALE
        OTHER
    }

    enum SeverityEnum {
        MILD
        MODERATE
        SEVERE
    }
}

package "Services Layer" <<Rectangle>> {
    SERVICE BedrockService {
        - region: str
        - agent_id: str
        - model_id: str
        - bedrock_runtime: BotoClient
        - bedrock_agent_runtime: BotoClient
        __
        + __init__()
        + invoke_agent(agent_id: str, session_id: str, input_text: str): Dict<str, Any>
        + invoke_model_direct(prompt: str): Dict<str, Any>
        + analyze_image(image_data: bytes, image_type: str): Dict<str, Any>
        - _invoke_agent_sync(agent_id: str, session_id: str, input_text: str): Dict<str, Any>
        - _invoke_model_sync(prompt: str): Dict<str, Any>
    }
}

package "Knowledge Base Layer" <<Rectangle>> {
    SERVICE NeuroMedicalKnowledge {
        - treatment_guidelines: Dict<str, List<str>>
        - drug_interactions: Dict<Tuple, str>
        __
        + __init__()
        + get_treatment_guidelines(condition: str): List<str>
        + check_drug_interactions(medications: List<str>): List<str>
        + get_condition_protocols(condition: str): Dict
    }
}

package "Agent Layer" <<Rectangle>> {
    ENTITY NeuroAgent {
        - bedrock_service: BedrockService
        - knowledge_base: NeuroMedicalKnowledge
        __
        + __init__(bedrock_service: BedrockService)
        + analyze_case(request: DiagnosisRequest): Dict<str, Any>
        + analyze_image(image_file): Dict<str, Any>
        + get_case(case_id: str): Dict<str, Any>
        - _prepare_medical_context(request: DiagnosisRequest): Dict<str, Any>
        - _generate_diagnosis(context: Dict<str, Any>): Dict<str, Any>
        - _build_diagnostic_prompt(context: Dict<str, Any>): str
        - _parse_agent_response(response: Dict<str, Any>): Dict<str, Any>
        - _calculate_overall_confidence(diagnosis_data: Dict<str, Any>): float
        - _enhance_with_knowledge(result: Dict<str, Any>, request: DiagnosisRequest): Dict<str, Any>
        - _fallback_diagnosis(context: Dict<str, Any>): Dict<str, Any>
    }
}

' Relationships
PatientCase "1" *-- "1" PatientInfo : contains
PatientCase "1" *-- "1" DiagnosisRequest : contains
PatientCase "1" *-- "0..1" DiagnosisResponse : contains

DiagnosisRequest "1" *-- "1" PatientInfo : requires
DiagnosisRequest "1" *-- "1..*" Symptom : has

PatientInfo "1" -- "1" GenderEnum : uses
Symptom "1" -- "1" SeverityEnum : has

NeuroAgent "1" -- "1" BedrockService : uses
NeuroAgent "1" -- "1" NeuroMedicalKnowledge : uses
NeuroAgent ..> DiagnosisRequest : processes
NeuroAgent ..> DiagnosisResponse : generates
NeuroAgent ..> PatientCase : manages

BedrockService ..> NeuroAgent : provides AI inference
NeuroMedicalKnowledge ..> NeuroAgent : provides medical knowledge

note right of NeuroAgent
  Core orchestrator that:
  1. Receives DiagnosisRequest
  2. Prepares medical context
  3. Invokes BedrockService
  4. Enhances with medical knowledge
  5. Returns DiagnosisResponse
end note

note right of BedrockService
  AWS Bedrock integration:
  - AgentCore runtime
  - Fallback to direct model
  - Streaming responses
  - Error recovery
end note

note right of NeuroMedicalKnowledge
  Evidence-based knowledge:
  - Treatment guidelines
  - Drug interactions
  - Neurological protocols
  - Taiwan healthcare context
end note

@enduml
```

---

## 2. Sequence Diagram: Diagnosis Workflow

```plantuml
@startuml Diagnosis_Sequence

actor User
participant "FastAPI\nEndpoint" as API
participant NeuroAgent
participant BedrockService
participant NeuroMedicalKnowledge
participant DynamoDB
participant "AWS Bedrock\nAgentCore" as Bedrock

User -> API: POST /diagnose
activate API

API -> API: Validate DiagnosisRequest
API -> NeuroAgent: analyze_case(request)
activate NeuroAgent

NeuroAgent -> NeuroAgent: generate case_id = UUID
NeuroAgent -> NeuroAgent: _prepare_medical_context()

note right of NeuroAgent
  Extract and structure:
  - Patient demographics
  - Symptoms timeline
  - Clinical data
  - Medical history
end note

NeuroAgent -> NeuroAgent: _build_diagnostic_prompt()
NeuroAgent -> BedrockService: invoke_agent(agent_id, session_id, prompt)
activate BedrockService

BedrockService -> Bedrock: invoke_agent()
activate Bedrock

alt Successful AgentCore Invocation
    Bedrock --> BedrockService: streaming response
    BedrockService -> BedrockService: process event stream
    BedrockService --> NeuroAgent: {"output": {"text": "..."}}
else AgentCore Failure
    Bedrock --> BedrockService: ClientError
    BedrockService -> Bedrock: invoke_model_direct()
    Bedrock --> BedrockService: model response
end

deactivate Bedrock
deactivate BedrockService

NeuroAgent -> NeuroAgent: _parse_agent_response()
NeuroAgent -> NeuroAgent: _calculate_overall_confidence()

NeuroAgent -> NeuroMedicalKnowledge: get_treatment_guidelines(condition)
activate NeuroMedicalKnowledge
NeuroMedicalKnowledge --> NeuroAgent: List[str] recommendations
deactivate NeuroMedicalKnowledge

NeuroAgent -> NeuroMedicalKnowledge: check_drug_interactions(medications)
activate NeuroMedicalKnowledge
NeuroMedicalKnowledge --> NeuroAgent: List[str] interactions
deactivate NeuroMedicalKnowledge

NeuroAgent -> NeuroAgent: _enhance_with_knowledge()

NeuroAgent -> DynamoDB: save_case(PatientCase)
activate DynamoDB
DynamoDB --> NeuroAgent: success
deactivate DynamoDB

NeuroAgent --> API: DiagnosisResponse
deactivate NeuroAgent

API --> User: JSON response (200 OK)
deactivate API

note over User, Bedrock
  Total workflow: <5 seconds
  - API validation: <100ms
  - Bedrock inference: <3s
  - Knowledge enhancement: <500ms
  - Database write: <500ms
end note

@enduml
```

---

## 3. Component Diagram: AWS Architecture

```plantuml
@startuml AWS_Architecture

!include <awslib/AWSCommon>
!include <awslib/Compute/Lambda>
!include <awslib/ApplicationIntegration/APIGateway>
!include <awslib/Database/DynamoDB>
!include <awslib/Storage/S3Bucket>
!include <awslib/MachineLearning/SageMaker>
!include <awslib/ManagementGovernance/CloudWatch>

skinparam backgroundColor #FFFFFF

cloud "Frontend" {
    component [React 18 SPA] as Frontend
    component [Material-UI] as MUI
}

package "AWS Infrastructure" {
    APIGateway(gateway, "API Gateway", "REST API")
    Lambda(lambda, "Lambda Functions", "Python 3.11")
    DynamoDB(dynamodb, "DynamoDB", "Cases Storage")
    S3Bucket(s3, "S3 Bucket", "Medical Images")
    SageMaker(bedrock, "Amazon Bedrock", "Claude 3 Sonnet")
    CloudWatch(cloudwatch, "CloudWatch", "Logs & Metrics")

    component "NeuroAgent\nCore" as Agent
    component "BedrockService" as Bedrock
    component "KnowledgeBase" as KB
}

Frontend --> gateway : HTTPS requests
MUI --> Frontend : UI components

gateway --> lambda : invoke
lambda --> Agent : orchestrate
Agent --> Bedrock : AI inference
Agent --> KB : medical knowledge
Bedrock --> bedrock : API calls

lambda --> dynamodb : read/write cases
lambda --> s3 : store/retrieve images
lambda --> cloudwatch : logs

note right of gateway
  Endpoints:
  - POST /diagnose
  - GET /cases/{id}
  - POST /upload-image
  - GET /health
end note

note right of dynamodb
  Tables:
  - PatientCases
  - DiagnosisHistory
  - AuditLog
end note

note right of s3
  Buckets:
  - medical-images/
  - reports/
  Lifecycle: 90 days
end note

@enduml
```

---

## 4. Detailed Class Relationships

```plantuml
@startuml Detailed_Class_Relationships

skinparam classAttributeIconSize 0

class PatientCase {
    - case_id: str
    - patient_info: PatientInfo
    - request: DiagnosisRequest
    - response: DiagnosisResponse
    - created_at: datetime
    - updated_at: datetime
    - status: str
}

class NeuroAgent {
    - bedrock_service: BedrockService
    - knowledge_base: NeuroMedicalKnowledge
}

class BedrockService {
    - region: str
    - agent_id: str
    - model_id: str
    - bedrock_runtime: BotoClient
    - bedrock_agent_runtime: BotoClient
}

class NeuroMedicalKnowledge {
    - treatment_guidelines: Dict
    - drug_interactions: Dict
}

' Composition (strong ownership)
PatientCase *-- PatientInfo
PatientCase *-- DiagnosisRequest
PatientCase *-- DiagnosisResponse

' Aggregation (has-a relationship)
NeuroAgent o-- BedrockService
NeuroAgent o-- NeuroMedicalKnowledge

' Dependency (uses)
NeuroAgent ..> PatientCase : creates/manages
NeuroAgent ..> DiagnosisRequest : processes
NeuroAgent ..> DiagnosisResponse : generates

' Association with multiplicity
NeuroAgent "1" -- "1" BedrockService : uses >
NeuroAgent "1" -- "1" NeuroMedicalKnowledge : consults >
PatientCase "1" -- "1..*" Symptom : describes symptoms >

note as N1
<b>Composition (*--)</b>
PatientCase owns its components.
If PatientCase is deleted,
components are also deleted.
end note

note as N2
<b>Aggregation (o--)</b>
NeuroAgent uses services
but doesn't own them.
Services can exist independently.
end note

note as N3
<b>Dependency (..>)</b>
NeuroAgent depends on models
for input/output but doesn't
store them as attributes.
end note

@enduml
```

---

## 5. State Diagram: PatientCase Lifecycle

```plantuml
@startuml PatientCase_States

skinparam backgroundColor #FFFFFF
skinparam stateBorderColor #2C3E50

[*] --> Created : new case

Created --> Analyzing : analyze_case()
Analyzing --> Diagnosed : AI response received
Analyzing --> Failed : error occurred

Diagnosed --> Enhanced : add medical knowledge
Enhanced --> Persisted : save to DynamoDB

Persisted --> Completed : success
Failed --> Completed : logged error

Completed --> [*]

note right of Created
  - Generate case_id
  - Validate request
  - Initialize timestamp
end note

note right of Analyzing
  - Prepare context
  - Invoke Bedrock
  - Parse response
  - Calculate confidence
end note

note right of Enhanced
  - Add treatment guidelines
  - Check drug interactions
  - Validate safety
end note

note right of Persisted
  - Store in DynamoDB
  - Generate audit log
  - Return case_id
end note

@enduml
```

---

## 6. ER Diagram: Database Schema

```plantuml
@startuml Database_ER_Diagram

!define TABLE entity
!define PK_COLUMN <b><u>

skinparam backgroundColor #FFFFFF

TABLE PatientCases {
    PK_COLUMN case_id : UUID >>
    --
    patient_age : int
    patient_gender : enum
    chief_complaint : text
    symptoms_json : json
    vital_signs_json : json
    lab_results_json : json
    imaging_studies : list
    medical_history : list
    current_medications : list
    allergies : list
    --
    diagnosis_results : json
    confidence_score : decimal
    recommendations : list
    risk_factors : list
    next_steps : list
    --
    status : enum
    created_at : timestamp
    updated_at : timestamp
    ttl : timestamp (90 days)
}

TABLE DiagnosisHistory {
    PK_COLUMN history_id : UUID >>
    --
    case_id : UUID <<FK>>
    diagnosis_version : int
    differential_diagnoses : json
    ai_model_version : string
    confidence_score : decimal
    created_at : timestamp
}

TABLE DrugInteractions {
    PK_COLUMN interaction_id : UUID >>
    --
    drug1_name : string
    drug2_name : string
    severity : enum
    description : text
    evidence_level : string
    last_updated : timestamp
}

TABLE TreatmentGuidelines {
    PK_COLUMN guideline_id : UUID >>
    --
    condition_name : string
    recommendation_text : text
    evidence_level : string
    taiwan_specific : boolean
    last_reviewed : timestamp
}

TABLE AuditLog {
    PK_COLUMN log_id : UUID >>
    --
    case_id : UUID <<FK>>
    action : enum
    user_id : string
    timestamp : timestamp
    ip_address : string
    details : json
}

' Relationships
PatientCases ||--o{ DiagnosisHistory : "has history"
PatientCases ||--o{ AuditLog : "logged in"
DrugInteractions }o--|| PatientCases : "checked for"
TreatmentGuidelines }o--|| PatientCases : "applied to"

note right of PatientCases
  Primary table for case storage
  GSI: status-created_at-index
  GSI: patient_age-index
  TTL: 90 days (HIPAA compliance)
end note

note right of DiagnosisHistory
  Version history of diagnoses
  Tracks AI model evolution
  GSI: case_id-version-index
end note

note right of DrugInteractions
  Reference table (read-heavy)
  Cached in application layer
  Updated monthly from FDA data
end note

@enduml
```

---

## 7. Activity Diagram: Multi-Modal Diagnosis Flow

```plantuml
@startuml MultiModal_Diagnosis_Activity

skinparam backgroundColor #FFFFFF

start

:User submits diagnosis request;

partition "Input Validation" {
    :Validate patient demographics;
    :Validate symptoms (1-20);
    :Validate vital signs ranges;

    if (Valid input?) then (yes)
        :Continue;
    else (no)
        :Return 400 Bad Request;
        stop
    endif
}

partition "Case Preparation" {
    :Generate unique case_id;
    :Create PatientCase object;
    :Extract medical history;
    :Parse symptom timeline;
}

partition "AI Analysis" {
    fork
        :Prepare text context;
    fork again
        if (Has imaging?) then (yes)
            :Upload to S3;
            :Queue image analysis;
        else (no)
            :Skip imaging;
        endif
    end fork

    :Build diagnostic prompt;
    :Invoke Bedrock AgentCore;

    if (AgentCore success?) then (yes)
        :Parse streaming response;
    else (no)
        :Fallback to direct model;
    endif

    :Extract differential diagnoses;
    :Calculate confidence scores;
}

partition "Knowledge Enhancement" {
    fork
        :Query treatment guidelines;
    fork again
        :Check drug interactions;
    fork again
        :Identify risk factors;
    end fork

    :Merge all recommendations;
}

partition "Persistence" {
    :Create DiagnosisResponse;
    :Update PatientCase;
    :Save to DynamoDB;
    :Log audit trail;
}

:Return response to user;

stop

note right
  Performance targets:
  - Input validation: <100ms
  - AI analysis: <3s
  - Knowledge query: <500ms
  - Database write: <500ms

  Total: <5s end-to-end
end note

@enduml
```

---

## 8. Deployment Diagram

```plantuml
@startuml Deployment_Architecture

node "User's Browser" {
    component [React SPA] as Frontend
    component [Service Worker] as SW
}

node "AWS CloudFront" {
    component [CDN] as CDN
    component [WAF] as WAF
}

node "AWS API Gateway" {
    component [REST API] as API
    component [Authorizer] as Auth
}

node "AWS Lambda (Python 3.11)" {
    component [NeuroAgent Handler] as Lambda
    component [NeuroAgent Core] as Agent
    component [BedrockService] as Bedrock
    component [NeuroMedicalKnowledge] as KB
}

database "AWS DynamoDB" {
    component [PatientCases Table] as Cases
    component [DiagnosisHistory Table] as History
}

database "AWS S3" {
    component [Images Bucket] as Images
    component [Reports Bucket] as Reports
}

cloud "AWS Bedrock" {
    component [Claude 3 Sonnet] as Claude
    component [AgentCore Runtime] as AgentCore
}

node "AWS CloudWatch" {
    component [Logs] as Logs
    component [Metrics] as Metrics
    component [Alarms] as Alarms
}

Frontend --> CDN : HTTPS
CDN --> WAF : filter
WAF --> API : forward
API --> Auth : validate JWT
API --> Lambda : invoke

Lambda --> Agent : orchestrate
Agent --> Bedrock : AI inference
Agent --> KB : medical knowledge

Bedrock --> AgentCore : invoke agent
Bedrock --> Claude : direct invocation

Lambda --> Cases : read/write
Lambda --> History : append
Lambda --> Images : upload/retrieve
Lambda --> Reports : generate

Lambda --> Logs : write logs
Lambda --> Metrics : publish metrics
Metrics --> Alarms : trigger alerts

note right of Lambda
  Configuration:
  - Memory: 1024 MB
  - Timeout: 30 seconds
  - Concurrency: 100
  - Python: 3.11
  - VPC: None (public)
end note

note right of Cases
  Provisioned capacity:
  - Read: 5 RCU
  - Write: 5 WCU
  - Auto-scaling enabled
  - Point-in-time recovery
end note

@enduml
```

---

## Summary of Key Relationships

### 1. **PatientCase ↔ Models** (Composition)
- PatientCase **owns** PatientInfo, DiagnosisRequest, DiagnosisResponse
- Lifecycle: Created together, destroyed together
- File: `backend/models/patient.py:49-56`

### 2. **NeuroAgent ↔ BedrockService** (Aggregation)
- NeuroAgent **uses** BedrockService for AI inference
- BedrockService can exist independently
- Relationship: 1-to-1
- File: `backend/agents/neuro_agent.py:11-13`

### 3. **NeuroAgent ↔ NeuroMedicalKnowledge** (Aggregation)
- NeuroAgent **consults** knowledge base for medical guidelines
- Knowledge base is shared across multiple agents
- Relationship: 1-to-1
- File: `backend/agents/neuro_agent.py:11-13`

### 4. **BedrockService ↔ AWS Bedrock** (Dependency)
- BedrockService **depends on** AWS Bedrock API
- Two modes: AgentCore or direct model invocation
- Fallback mechanism for resilience
- File: `backend/services/bedrock_service.py:18-35`

### 5. **NeuroAgent → PatientCase** (Dependency)
- NeuroAgent **creates and manages** PatientCase instances
- Processes DiagnosisRequest → generates DiagnosisResponse
- Stateless processing (no persistent storage in agent)
- File: `backend/agents/neuro_agent.py:15-36`

---

## Architecture Principles

### 1. **Separation of Concerns**
- Models: Data structures only
- Services: External integrations (AWS, APIs)
- Agents: Business logic orchestration
- Utils: Reusable knowledge bases

### 2. **Dependency Injection**
- NeuroAgent receives BedrockService via constructor
- Enables testing with mock services
- Follows SOLID principles

### 3. **Fail-Safe Design**
- Bedrock AgentCore → fallback to direct model
- Direct model → fallback to rule-based diagnosis
- Multiple layers of error handling

### 4. **Stateless Processing**
- Lambda functions are stateless
- All state stored in DynamoDB
- Enables horizontal scaling

### 5. **Multi-Modal Support**
- Text: Symptoms, history, complaints
- Structured: Vital signs, lab results
- Images: CT/MRI scans (future: AI analysis)

---

## Code References

| Component | File Path | Lines |
|-----------|-----------|-------|
| PatientCase | `backend/models/patient.py` | 49-56 |
| NeuroAgent | `backend/agents/neuro_agent.py` | 10-231 |
| BedrockService | `backend/services/bedrock_service.py` | 8-135 |
| NeuroMedicalKnowledge | `backend/utils/medical_knowledge.py` | 3-62 |
| DiagnosisRequest | `backend/models/patient.py` | 31-38 |
| DiagnosisResponse | `backend/models/patient.py` | 40-47 |

---

**Document Version**: 1.0
**Last Updated**: October 12, 2025
**Author**: Claude Code with NeuroAgent Team
**Purpose**: AWS AI Agent Global Hackathon - Architecture Documentation
