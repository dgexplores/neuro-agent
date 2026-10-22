# NeuroAgent Codebase Index
*Generated: 2025-10-12*

## 📊 Project Overview
- **Project**: NeuroAgent - AI Neurological Diagnosis Assistant
- **Purpose**: AWS AI Agent Global Hackathon 2025
- **Tech Stack**: FastAPI + React + AWS Bedrock + DynamoDB

---

## 📁 Directory Structure

### Backend (Python/FastAPI)
```
backend/
├── agents/
│   ├── __init__.py
│   └── neuro_agent.py              # Core AI agent for neurological diagnosis
├── models/
│   ├── __init__.py
│   └── patient.py                  # Patient data models
├── services/
│   ├── __init__.py
│   └── bedrock_service.py          # AWS Bedrock integration
├── utils/
│   ├── __init__.py
│   ├── auth.py                     # Authentication utilities
│   └── medical_knowledge.py        # Medical knowledge base
├── tests/
│   ├── __init__.py
│   └── test_neuro_agent.py         # Unit tests
├── __init__.py
└── main.py                         # FastAPI application entry point
```

### Frontend (React)
```
frontend/
├── src/
│   ├── components/
│   │   ├── CaseHistoryPage.jsx      # Case history view
│   │   ├── DiagnosisPage.jsx        # Main diagnosis interface
│   │   ├── DiagnosisResults.jsx     # Results display
│   │   ├── HomePage.jsx             # Landing page
│   │   └── Navigation.jsx           # Navigation component
│   ├── services/
│   │   └── api.js                  # API client
│   ├── App.jsx                      # Main application component
│   └── index.jsx                    # Application entry point
└── package.json
```

### Infrastructure (AWS CDK)
```
infrastructure/
└── cdk/
    └── app.py                      # AWS CDK infrastructure definition
```

### MCP Integration
```
mcp-servers/
├── github/                         # GitHub MCP Server
├── aws-bedrock/                    # AWS Bedrock MCP Server
├── mcp-servers-official/           # Filesystem MCP Server
├── claude-context/                 # Semantic search MCP Server
└── semgrep-mcp/                    # Security scanning MCP Server
```

---

## 🔑 Key Files & Components

### Core Backend Files

#### `backend/main.py` - API Entry Point
- FastAPI application setup
- CORS configuration
- API routes definition
- Health check endpoints

#### `backend/agents/neuro_agent.py` - AI Agent Core
- Neurological diagnosis engine
- Bedrock AgentCore integration
- Multi-modal data processing
- Differential diagnosis generation
- Confidence scoring

#### `backend/services/bedrock_service.py` - AWS Bedrock Service
- Bedrock runtime client
- AgentCore invocation
- Streaming response handling
- Error recovery and fallback
- Model: anthropic.claude-3-sonnet-20240229-v1:0

#### `backend/utils/medical_knowledge.py` - Medical Knowledge Base
- Evidence-based treatment guidelines
- Drug interaction database
- Neurological condition protocols
- Taiwan healthcare compatibility

#### `backend/models/patient.py` - Data Models
- Patient information schema
- Symptom data structures
- Medical history models
- Vital signs models

#### `backend/utils/auth.py` - Authentication
- JWT token handling
- API key validation
- Security utilities

### Core Frontend Files

#### `frontend/src/App.jsx` - Main Application
- React Router setup
- Application state management
- Theme configuration

#### `frontend/src/components/DiagnosisPage.jsx` - Diagnosis Interface
- Patient data input forms
- Symptom collection
- Medical history capture
- Real-time diagnosis requests

#### `frontend/src/components/DiagnosisResults.jsx` - Results Display
- Differential diagnosis visualization
- Confidence score display
- Treatment recommendations
- Risk factor highlighting

#### `frontend/src/services/api.js` - API Client
- Axios configuration
- API endpoint definitions
- Request/response handling
- Error management

### Infrastructure

#### `infrastructure/cdk/app.py` - AWS CDK Stack
- Lambda functions
- API Gateway configuration
- DynamoDB tables
- S3 buckets
- IAM roles and policies

---

## 📝 Documentation Files

- `CLAUDE.md` - Project guide for Claude Code (203 lines)
- `MCP_INTEGRATION_GUIDE.md` - MCP server integration guide (295 lines)
- `RESOURCE_SUMMARY.md` - Resource documentation
- `docs/development.md` - Development guidelines
- `claude-code-workflow-zh.md` - Claude Code workflow (Chinese)
- `README.md` - Project README

---

## 🔧 Configuration Files

- `.env` - Environment variables (566 bytes)
- `.env.example` - Environment template
- `.gitignore` - Git ignore rules
- `setup_mcp_servers.sh` - MCP servers installation script
- `backend/requirements.txt` - Python dependencies
- `frontend/package.json` - Node.js dependencies

---

## 🧪 Test Files

- `backend/tests/test_neuro_agent.py` - Neuro agent unit tests

---

## 🔌 MCP Integration

### Installed MCP Servers
1. **GitHub MCP** - GitHub repository operations
2. **Filesystem MCP** - Local filesystem access
3. **AWS Bedrock MCP** - Bedrock model interactions
4. **Claude Context MCP** - Semantic code search
5. **Semgrep MCP** - Security vulnerability scanning

### Configuration
- Location: `~/.config/claude-desktop/claude_desktop_config.json`
- Protocol: stdio (standard input/output)
- Authentication: API keys required

---

## 📦 Dependencies

### Python (Backend)
- fastapi
- uvicorn
- boto3 (AWS SDK)
- pydantic
- python-jose (JWT)
- passlib (password hashing)

### JavaScript (Frontend)
- react
- react-router-dom
- axios
- @mui/material (Material-UI)

### AWS Services
- Amazon Bedrock (AI models)
- DynamoDB (database)
- S3 (storage)
- Lambda (serverless functions)
- API Gateway (REST API)

---

## 🚀 Entry Points

### Development
- **Backend**: `python backend/main.py` (localhost:8000)
- **Frontend**: `npm start` in frontend/ (localhost:3000)

### Production
- **Backend**: AWS Lambda via API Gateway
- **Frontend**: S3 + CloudFront

---

## 🔒 Security Features

- JWT authentication
- API key validation
- CORS configuration
- Environment variable protection (.env in .gitignore)
- HIPAA-compliant data handling guidelines

---

## 📊 Code Statistics

- **Total Files**: 32 code files (excluding node_modules)
- **Python Files**: ~15
- **JavaScript Files**: ~10
- **Documentation**: ~7 markdown files

---

## 🎯 Key Features

1. **Multi-modal Diagnosis**: Combines symptoms, history, and imaging
2. **AI-Powered**: Uses Amazon Bedrock with Claude 3 Sonnet
3. **Drug Safety**: Interaction checking and warnings
4. **Case Management**: Store and retrieve patient cases
5. **Real-time**: Streaming responses from AI
6. **Multilingual**: Support for Traditional Chinese
7. **MCP Integration**: Extended with Model Context Protocol servers

---

*This index provides a comprehensive overview of the NeuroAgent codebase structure and key components for AI-assisted development with Claude Code.*
