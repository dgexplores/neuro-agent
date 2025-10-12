# CLAUDE.md - NeuroAgent Project Guide

## Project Overview
NeuroAgent is an AI-driven neurological diagnosis assistant built for the AWS AI Agent Global Hackathon. This system combines advanced AI capabilities with medical expertise to provide intelligent diagnostic support for healthcare professionals.

## Architecture
- **Backend**: FastAPI + Amazon Bedrock AgentCore
- **Frontend**: React 18 + Material-UI 
- **AI Services**: Amazon Bedrock, SageMaker AI
- **Database**: DynamoDB (cases storage)
- **Storage**: S3 (medical images)
- **Deployment**: AWS Lambda + API Gateway via CDK

## Core Components

### 1. AI Agent System (`backend/agents/neuro_agent.py`)
- Multi-modal neurological diagnosis engine
- Integrates patient symptoms, medical history, and imaging data
- Provides differential diagnoses with confidence scores
- Drug interaction checking and safety recommendations

### 2. Bedrock Integration (`backend/services/bedrock_service.py`) 
- Amazon Bedrock AgentCore runtime integration
- Fallback to direct model invocation
- Handles streaming responses and error recovery
- Model: anthropic.claude-3-sonnet-20240229-v1:0

### 3. Medical Knowledge Base (`backend/utils/medical_knowledge.py`)
- Evidence-based treatment guidelines
- Drug interaction database
- Neurological condition protocols
- Taiwan healthcare system compatibility

### 4. Frontend Application (`frontend/src/`)
- Patient data input forms
- Real-time diagnosis visualization
- Case history management
- Multi-language support (繁體中文)

## Development Guidelines

### Code Quality Standards
- Follow PEP 8 for Python code
- Use TypeScript strict mode for frontend
- Implement comprehensive error handling
- Write unit tests for core functions
- Maintain HIPAA-compliant data handling

### AI Integration Best Practices
- Use structured prompts for consistent AI responses
- Implement confidence thresholds for safety
- Provide fallback mechanisms when AI fails
- Log all AI interactions for debugging
- Validate AI outputs against medical standards

### Medical Safety Requirements
- Never provide definitive diagnoses without human oversight
- Include appropriate medical disclaimers
- Validate all drug interaction warnings
- Ensure patient data anonymization
- Follow medical device software guidelines

### AWS Deployment Standards
- Use least-privilege IAM policies
- Enable CloudWatch logging for all services
- Implement proper error handling and retries
- Use environment variables for configuration
- Follow AWS Well-Architected principles

## Development Workflow

### 1. Setup Phase
```bash
# Environment setup
cp .env.example .env
docker-compose up -d
pip install -r requirements.txt
cd frontend && npm install
```

### 2. Development Phase
- Use TDD approach for backend functions
- Test AI agent responses with sample cases
- Validate frontend UI/UX with medical workflows
- Implement proper error handling and logging

### 3. Testing Phase
```bash
# Backend testing
pytest backend/tests/ -v
# Frontend testing  
cd frontend && npm test
# Integration testing
python backend/main.py & curl localhost:8000/health
```

### 4. Deployment Phase
```bash
# AWS infrastructure
cd infrastructure/cdk
cdk bootstrap && cdk deploy --all
# Verify deployment
curl https://api-gateway-url/health
```

## Data Models

### Patient Input Schema
- age: integer (0-120)
- gender: enum (male, female, other) 
- symptoms: array of symptom objects
- medical_history: array of strings
- vital_signs: object with numeric values
- imaging_studies: array of strings

### AI Response Schema
- case_id: unique identifier
- diagnosis: array of diagnosis objects with confidence
- recommendations: array of treatment suggestions
- risk_factors: array of identified risks
- next_steps: array of follow-up actions

## Claude Code Integration

### Preferred Commands
- `/explore backend/agents/neuro_agent.py` - Analyze core AI logic
- `/plan "Implement medical image analysis"` - Strategic planning
- `/code "Add drug interaction checking"` - Feature implementation  
- `/test "Verify AI agent responses"` - Quality assurance
- `/commit "Add neurological diagnosis engine"` - Version control

### Sub-agent Usage
- Use sub-agents for complex medical logic verification
- Separate agents for frontend vs backend development
- Dedicated agent for AWS infrastructure management
- Specialized agent for medical compliance checking

### Thinking Modes
- `think` - For routine development decisions
- `think hard` - For medical algorithm design
- `ultrathink` - For system architecture planning

## Hackathon Success Criteria

### Technical Excellence (50%)
- Functional AWS Bedrock AgentCore integration
- Multi-modal AI processing capabilities
- Scalable serverless architecture
- Comprehensive error handling
- Production-ready code quality

### Medical Value (20%)
- Clinically relevant diagnostic suggestions
- Evidence-based recommendations
- Drug safety checking
- Taiwan healthcare context awareness
- User-friendly medical interface

### Innovation (20%)
- Novel AI agent orchestration
- Advanced prompt engineering
- Real-time diagnostic visualization
- Multi-language medical support
- Integration of multiple AI models  

### Implementation Quality (10%)
- Clean, maintainable codebase
- Comprehensive documentation
- Proper testing coverage
- Security best practices
- Demo-ready presentation

## Security & Compliance
- All patient data must be anonymized
- Use JWT tokens for API authentication
- Implement CORS policies properly  
- Follow HIPAA guidelines for data handling
- Encrypt sensitive data in transit and at rest

## Performance Targets
- API response time: <2 seconds for diagnosis
- Bedrock integration: <5 seconds per call
- Frontend load time: <3 seconds
- 99.9% uptime for critical services
- Handle 100+ concurrent users

## Medical Disclaimers
⚠️ This system is for educational and demonstration purposes only
⚠️ All diagnostic suggestions require professional medical review
⚠️ Not intended for direct patient care without physician oversight
⚠️ Complies with AWS AI/ML responsible use guidelines

## Contact & Support
For development questions during hackathon:
- AWS Bedrock issues: Check CloudWatch logs
- Frontend bugs: Use browser dev tools
- Medical questions: Refer to knowledge base
- Deployment issues: Review CDK outputs

---
*Generated for AWS AI Agent Global Hackathon 2025*
*Last updated: October 12, 2025*
# Test
