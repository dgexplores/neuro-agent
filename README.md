# NeuroAgent - AI-Driven Neurological Diagnosis Assistant

## 專案概述
NeuroAgent 是一個基於 AWS AI Agent 的企業級神經疾病診療輔助系統，整合多模態分析能力，為醫療專業人員提供智能診斷建議。

## 快速開始

### 環境需求
- Python 3.11+
- Node.js 18+
- AWS CLI 已配置
- Docker & Docker Compose

### 本地開發設置
```bash
# 1. 複製環境變數
cp .env.example .env

# 2. 啟動開發環境
docker-compose up -d

# 3. 安裝依賴
pip install -r requirements.txt
cd frontend && npm install

# 4. 啟動服務
python backend/main.py  # 後端 API (8000)
cd frontend && npm start  # 前端 (3000)
```

### AWS 部署
```bash
cd infrastructure/cdk
cdk bootstrap
cdk deploy --all
```

## 架構說明
- **後端**: FastAPI + Amazon Bedrock AgentCore
- **前端**: React + Material-UI
- **AI服務**: Amazon Bedrock, SageMaker AI
- **資料庫**: DynamoDB
- **部署**: AWS Lambda + API Gateway

## 開發指南
詳見 `docs/development.md`

## API 文檔
啟動後端後訪問: http://localhost:8000/docs
