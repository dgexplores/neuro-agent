# NeuroAgent 專案結構深度分析報告
*Generated with Ultrathink Mode - 2025-10-12*
*Based on Claude Code Workflow - Phase 2.1: 專案架構掃描*

---

## 【第一步：專案結構分析】

### 1. 主要程式碼目錄結構 📁

#### 1.1 Backend (Python/FastAPI) - 後端核心系統
```
backend/                                    # 後端根目錄
├── __init__.py                            # Python 套件初始化
├── main.py                                # FastAPI 應用程式入口點
│                                           # - CORS 配置
│                                           # - API 路由定義
│                                           # - 健康檢查端點
│
├── agents/                                # AI Agent 模組
│   ├── __init__.py
│   └── neuro_agent.py                     # 神經診斷 AI Agent
│                                           # - Bedrock AgentCore 整合
│                                           # - 多模態資料處理
│                                           # - 差異診斷生成
│                                           # - 信心分數計算
│
├── models/                                # 資料模型層
│   ├── __init__.py
│   └── patient.py                         # 病患資料模型
│                                           # - Pydantic 模型定義
│                                           # - 症狀資料結構
│                                           # - 病史模型
│                                           # - 生命徵象模型
│
├── services/                              # 服務層 (Business Logic)
│   ├── __init__.py
│   └── bedrock_service.py                 # AWS Bedrock 整合服務
│                                           # - Bedrock Runtime 客戶端
│                                           # - AgentCore 調用
│                                           # - 串流回應處理
│                                           # - 錯誤恢復與備援
│                                           # - Model: anthropic.claude-3-sonnet-20240229-v1:0
│
├── utils/                                 # 工具函式庫
│   ├── __init__.py
│   ├── auth.py                            # 認證工具
│   │                                       # - JWT Token 處理
│   │                                       # - API Key 驗證
│   │                                       # - 安全性工具
│   │
│   └── medical_knowledge.py               # 醫學知識庫
│                                           # - 實證治療指引
│                                           # - 藥物交互作用資料庫
│                                           # - 神經疾病診療規範
│                                           # - 台灣健保體系相容性
│
└── tests/                                 # 測試套件
    ├── __init__.py
    └── test_neuro_agent.py                # AI Agent 單元測試
                                            # - 功能測試
                                            # - 邊界條件測試
                                            # - 錯誤處理測試
```

**關鍵特徵**:
- **架構模式**: 分層架構 (Layered Architecture)
  - Presentation Layer: FastAPI Routes (main.py)
  - Business Logic Layer: Services + Agents
  - Data Layer: Models
  - Utility Layer: Utils

- **設計模式**:
  - Service Pattern (services/)
  - Repository Pattern (隱含於 models/)
  - Agent Pattern (agents/neuro_agent.py)

#### 1.2 Frontend (React 18) - 前端使用者介面
```
frontend/                                  # 前端根目錄
├── public/
│   └── index.html                         # HTML 入口點
│
├── src/                                   # React 原始碼
│   ├── index.js                           # React 應用程式入口
│   │                                       # - React DOM 渲染
│   │                                       # - Provider 設置
│   │
│   ├── App.js                             # 主應用程式元件
│   │   └── App.css                        # 全域樣式
│   │                                       # - React Router 配置
│   │                                       # - 應用程式狀態管理
│   │                                       # - Material-UI 主題配置
│   │
│   ├── components/                        # React 元件
│   │   ├── HomePage.js                    # 首頁元件
│   │   │                                   # - 歡迎畫面
│   │   │                                   # - 功能導覽
│   │   │
│   │   ├── DiagnosisPage.js               # 診斷介面元件
│   │   │                                   # - 病患資料輸入表單
│   │   │                                   # - 症狀收集介面
│   │   │                                   # - 病史採集
│   │   │                                   # - 即時診斷請求
│   │   │
│   │   ├── DiagnosisResults.js            # 診斷結果展示元件
│   │   │                                   # - 差異診斷視覺化
│   │   │                                   # - 信心分數顯示
│   │   │                                   # - 治療建議展示
│   │   │                                   # - 風險因子標示
│   │   │
│   │   ├── CaseHistoryPage.js             # 病例歷史元件
│   │   │                                   # - 病例清單檢視
│   │   │                                   # - 歷史查詢
│   │   │                                   # - 病例詳細資訊
│   │   │
│   │   └── Navigation.js                  # 導覽列元件
│   │                                       # - 頁面導覽
│   │                                       # - 使用者狀態顯示
│   │
│   └── services/
│       └── api.js                         # API 客戶端服務
│                                           # - Axios 配置
│                                           # - API 端點定義
│                                           # - 請求/回應處理
│                                           # - 錯誤管理
│
└── package.json                           # Node.js 專案定義
```

**關鍵特徵**:
- **架構模式**: Component-Based Architecture
- **狀態管理**: React Hooks (useState, useEffect)
- **路由**: React Router v6
- **UI 框架**: Material-UI v5
- **HTTP 客戶端**: Axios

#### 1.3 Infrastructure (AWS CDK) - 雲端基礎設施即程式碼
```
infrastructure/
└── cdk/                                   # AWS CDK 專案
    ├── app.py                             # CDK 應用程式定義
    │                                       # - Lambda Functions
    │                                       # - API Gateway 配置
    │                                       # - DynamoDB Tables
    │                                       # - S3 Buckets
    │                                       # - IAM Roles & Policies
    │
    ├── cdk.json                           # CDK 配置檔
    │                                       # - CDK 功能開關
    │                                       # - AWS 最佳實踐配置
    │
    └── requirements.txt                   # CDK Python 依賴
                                            # - aws-cdk-lib
                                            # - constructs
```

**Infrastructure Components**:
- **Compute**: AWS Lambda (Serverless Functions)
- **API**: Amazon API Gateway (REST API)
- **Database**: Amazon DynamoDB (NoSQL)
- **Storage**: Amazon S3 (Object Storage)
- **AI/ML**: Amazon Bedrock (Claude 3 Sonnet)
- **Identity**: AWS IAM (Access Control)

#### 1.4 MCP Integration - Model Context Protocol 擴展
```
mcp-servers/                               # MCP 伺服器集合
├── github/                                # GitHub 操作 MCP
│   ├── index.js                           # 主程式
│   ├── start.sh                           # 啟動腳本
│   └── package.json
│
├── aws-bedrock/                           # AWS Bedrock MCP
│   ├── .venv/                             # Python 虛擬環境
│   ├── src/
│   │   ├── ui/app.py                      # Chainlit UI
│   │   └── mcp/server.py                  # MCP 伺服器
│   ├── pyproject.toml
│   └── uv.lock
│
├── mcp-servers-official/                  # 官方 Filesystem MCP
│   └── src/filesystem/
│       ├── dist/index.js                  # 編譯後主程式
│       ├── index.ts                       # TypeScript 原始碼
│       └── package.json
│
├── claude-context/                        # 語義搜索 MCP
│   ├── packages/
│   ├── dist/index.js
│   └── package.json
│
└── semgrep-mcp/                           # 安全掃描 MCP
    ├── venv/                              # Python 虛擬環境
    ├── src/semgrep_mcp/server.py
    └── pyproject.toml
```

**MCP Protocol**:
- **通訊協定**: stdio (Standard Input/Output)
- **配置位置**: `~/.config/claude-desktop/claude_desktop_config.json`
- **功能**: 擴展 Claude Code 能力
  - GitHub 操作
  - 檔案系統存取
  - AWS Bedrock 模型呼叫
  - 語義程式碼搜尋
  - 安全漏洞掃描

---

### 2. 設定檔案位置與內容 ⚙️

#### 2.1 環境變數設定
```
📄 .env                                    # 環境變數 (566 bytes)
   Location: /home/thc1006/dev/neuro-agent/.env
   Status: ✅ 已建立並配置

   Key Variables:
   ├── AWS_REGION=us-east-1
   ├── AWS_ACCESS_KEY_ID=***
   ├── AWS_SECRET_ACCESS_KEY=***
   ├── BEDROCK_AGENTCORE_AGENT_ID=***
   ├── BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
   ├── API_HOST=localhost
   ├── API_PORT=8000
   ├── DEBUG=true
   ├── DYNAMODB_TABLE_NAME=neuroagent-cases
   ├── S3_BUCKET_NAME=neuroagent-data
   ├── JWT_SECRET_KEY=*** (自動生成 64 字元)
   ├── API_KEY=*** (自動生成 32 字元)
   └── REACT_APP_API_URL=http://localhost:8000

📄 .env.example                            # 環境變數範本 (507 bytes)
   Location: /home/thc1006/dev/neuro-agent/.env.example
   Purpose: 新開發者環境設置參考
```

#### 2.2 Python 專案設定
```
📄 pyproject.toml                          # Python 專案配置 (PEP 518/621)
   Location: /home/thc1006/dev/neuro-agent/pyproject.toml

   Configuration:
   ├── [build-system]
   │   ├── requires: setuptools>=61.0, wheel
   │   └── build-backend: setuptools.build_meta
   │
   ├── [project]
   │   ├── name: neuroagent
   │   ├── version: 1.0.0
   │   ├── description: AI-Driven Neurological Diagnosis Assistant
   │   └── license: MIT
   │
   ├── [tool.pytest.ini_options]              # Pytest 配置
   │   ├── testpaths: ["backend/tests"]
   │   ├── python_files: ["test_*.py", "*_test.py"]
   │   └── addopts: -v --tb=short
   │
   ├── [tool.black]                            # Code Formatter
   │   ├── line-length: 88
   │   └── target-version: py311
   │
   └── [tool.isort]                            # Import Sorter
       ├── profile: black
       └── line_length: 88

📄 requirements.txt                        # Python 依賴清單 (19 packages)
   Location: /home/thc1006/dev/neuro-agent/requirements.txt

   Core Dependencies:
   ├── Web Framework: fastapi==0.104.1, uvicorn==0.24.0
   ├── AWS Integration: boto3==1.34.0
   ├── Data Validation: pydantic==2.5.0
   ├── Authentication: python-jose==3.3.0, passlib==1.7.4
   ├── HTTP Client: httpx==0.25.2
   ├── Data Science: pandas==2.1.4, numpy==1.24.3, scikit-learn==1.3.2
   ├── Image Processing: Pillow==10.1.0, opencv-python==4.8.1.78
   └── Testing: pytest==7.4.3, pytest-asyncio==0.21.1
```

#### 2.3 Frontend 專案設定
```
📄 package.json                            # Node.js 專案配置
   Location: /home/thc1006/dev/neuro-agent/package.json

   Configuration:
   ├── name: neuroagent-frontend
   ├── version: 1.0.0
   ├── main: src/index.js
   │
   ├── scripts:
   │   ├── start: react-scripts start         # 開發伺服器
   │   ├── build: react-scripts build         # 生產建置
   │   ├── test: react-scripts test           # 測試執行
   │   └── eject: react-scripts eject
   │
   ├── dependencies:
   │   ├── UI Framework: @mui/material@^5.14.0, @emotion/react@^11.11.0
   │   ├── React Core: react@^18.2.0, react-dom@^18.2.0
   │   ├── Routing: react-router-dom@^6.8.0
   │   ├── HTTP Client: axios@^1.6.0
   │   ├── Charts: recharts@^2.8.0
   │   └── File Upload: react-dropzone@^14.2.0
   │
   └── devDependencies:
       └── react-scripts@5.0.1                # Create React App 工具鏈
```

#### 2.4 Docker & Kubernetes 設定
```
📄 docker-compose.yml                      # Docker Compose 多容器編排
   Location: /home/thc1006/dev/neuro-agent/docker-compose.yml

   Services:
   ├── backend:
   │   ├── build: . (使用 Dockerfile)
   │   ├── ports: 8000:8000
   │   ├── command: uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
   │   └── volumes: ./backend, ./data
   │
   ├── frontend:
   │   ├── image: node:18-alpine
   │   ├── ports: 3000:3000
   │   ├── command: npm install && npm start
   │   └── env: REACT_APP_API_URL=http://localhost:8000
   │
   └── localstack:                            # AWS 本地模擬環境
       ├── image: localstack/localstack:latest
       ├── ports: 4566:4566
       └── services: s3, dynamodb, lambda

📄 Dockerfile                              # Docker 映像建置定義
   Location: /home/thc1006/dev/neuro-agent/Dockerfile
   Purpose: Backend API 容器化
```

#### 2.5 AWS CDK 設定
```
📄 infrastructure/cdk/cdk.json             # CDK 配置與功能開關
   Location: /home/thc1006/dev/neuro-agent/infrastructure/cdk/cdk.json

   Configuration:
   ├── app: python app.py                     # CDK 應用程式入口
   ├── watch: 監控檔案變更
   └── context: 58+ AWS CDK 功能開關
       ├── @aws-cdk/core:checkSecretUsage: true
       ├── @aws-cdk/aws-iam:minimizePolicies: true
       ├── @aws-cdk/aws-s3:createDefaultLoggingPolicy: true
       └── ... (詳見 cdk.json 第 17-58 行)

📄 infrastructure/cdk/requirements.txt     # CDK Python 依賴
   Location: /home/thc1006/dev/neuro-agent/infrastructure/cdk/requirements.txt
```

#### 2.6 Version Control & CI/CD 設定
```
📄 .gitignore                              # Git 忽略規則
   Location: /home/thc1006/dev/neuro-agent/.gitignore

   Ignored Patterns:
   ├── Python: __pycache__/, *.pyc, venv/, .env
   ├── Node.js: node_modules/, npm-debug.log
   ├── IDE: .vscode/, .idea/, *.swp
   ├── AWS: .aws/, *.pem
   ├── Data: *.db, *.sqlite3, /data/models/
   ├── MCP: mcp-servers/                     # MCP 伺服器 (第三方)
   └── Chainlit: .chainlit/                  # Chainlit 配置

📄 .github/workflows/claude-guard.yml      # GitHub Actions 工作流程
   Location: /home/thc1006/dev/neuro-agent/.github/workflows/claude-guard.yml
   Purpose: CLAUDE.md 檔案完整性保護
   Trigger: push, pull_request
```

#### 2.7 Claude Code 設定
```
📄 .claude/settings.json                   # Claude Code 專案設定
   Location: /home/thc1006/dev/neuro-agent/.claude/settings.json

   Configuration:
   └── Claude Code 行為自定義 (如存在)

📄 CLAUDE.md                               # Claude Code 專案指南
   Location: /home/thc1006/dev/neuro-agent/CLAUDE.md
   Size: 6.3 KB (203 行)
   Status: 🔒 Protected by SHA256 checksum

   Content Structure:
   ├── 專案概述 (Project Overview)
   ├── 架構說明 (Architecture)
   ├── 核心元件 (Core Components)
   ├── 開發指南 (Development Guidelines)
   ├── AI 整合最佳實踐 (AI Integration Best Practices)
   ├── 醫療安全要求 (Medical Safety Requirements)
   ├── AWS 部署標準 (AWS Deployment Standards)
   ├── 開發工作流程 (Development Workflow)
   ├── 資料模型 (Data Models)
   ├── Claude Code 整合 (Claude Code Integration)
   ├── Hackathon 成功標準 (Hackathon Success Criteria)
   ├── 安全與合規 (Security & Compliance)
   └── 效能目標 (Performance Targets)

📄 CLAUDE.md.sha256                        # CLAUDE.md 校驗和
   Location: /home/thc1006/dev/neuro-agent/CLAUDE.md.sha256
   Purpose: 檔案完整性驗證
   Usage: make verify-claude
```

#### 2.8 Makefile 建置自動化
```
📄 Makefile                                # GNU Make 建置腳本
   Location: /home/thc1006/dev/neuro-agent/Makefile

   Targets:
   ├── lock-claude: 鎖定 CLAUDE.md (產生 SHA256)
   ├── unlock-claude: 解鎖 CLAUDE.md (刪除 SHA256)
   └── verify-claude: 驗證 CLAUDE.md 完整性
```

---

### 3. 測試目錄組織 🧪

#### 3.1 Backend 測試結構
```
backend/tests/                             # Backend 測試套件
├── __init__.py                            # Pytest 套件初始化
│
└── test_neuro_agent.py                    # AI Agent 單元測試
    Location: /home/thc1006/dev/neuro-agent/backend/tests/test_neuro_agent.py

    Test Coverage:
    ├── 功能測試 (Functional Tests)
    │   ├── 診斷流程測試
    │   ├── Bedrock 整合測試
    │   └── 回應格式驗證
    │
    ├── 邊界條件測試 (Boundary Tests)
    │   ├── 空輸入處理
    │   ├── 超大資料集
    │   └── 特殊字元處理
    │
    └── 錯誤處理測試 (Error Handling Tests)
        ├── API 錯誤回應
        ├── 網路逾時
        └── 無效資料格式
```

#### 3.2 Frontend 測試結構
```
frontend/src/                              # Frontend 測試 (隱含於 src/)
└── *.test.js                              # React 元件測試 (如存在)

    Framework: React Testing Library
    Runner: Jest (透過 react-scripts)
    Command: npm test
```

#### 3.3 測試配置
```
📄 pyproject.toml (測試配置)
   [tool.pytest.ini_options]
   ├── testpaths: ["backend/tests"]           # 測試檔案搜尋路徑
   ├── python_files: ["test_*.py", "*_test.py"] # 測試檔案命名模式
   └── addopts: "-v --tb=short"               # Pytest 參數
       ├── -v: Verbose 輸出
       └── --tb=short: 簡短的 traceback

📄 package.json (測試腳本)
   scripts:
   └── test: "react-scripts test"             # Jest 測試執行器
       └── 配置: Create React App 預設
```

#### 3.4 測試策略 (依據 CLAUDE.md)
```
測試金字塔 (Test Pyramid):
├── Unit Tests (單元測試) ████████████████████ 80%
│   ├── backend/tests/test_neuro_agent.py
│   ├── 函式層級測試
│   └── Mock 外部依賴
│
├── Integration Tests (整合測試) ██████ 15%
│   ├── API 端點測試
│   ├── Bedrock 服務整合
│   └── 資料庫操作測試
│
└── E2E Tests (端到端測試) ██ 5%
    ├── 完整診斷流程
    ├── 使用者介面互動
    └── 系統級行為驗證

測試覆蓋率目標:
├── 程式碼覆蓋率: > 80%
├── 分支覆蓋率: > 70%
└── 功能覆蓋率: 100%
```

#### 3.5 測試執行指令
```bash
# Backend 測試
pytest backend/tests/ -v                   # 執行所有後端測試
pytest backend/tests/test_neuro_agent.py   # 執行特定測試檔案
pytest --cov=backend --cov-report=html     # 生成覆蓋率報告

# Frontend 測試
cd frontend
npm test                                   # 互動式測試模式
npm test -- --coverage                     # 生成覆蓋率報告

# Docker 環境測試
docker-compose up -d                       # 啟動測試環境
docker-compose exec backend pytest         # 容器內測試執行
```

---

### 4. 文檔結構 📚

#### 4.1 核心文檔檔案
```
📚 Documentation Root: /home/thc1006/dev/neuro-agent/

├── README.md                              # 專案主要說明文件
│   Purpose: 專案概述、快速開始、功能介紹
│   Audience: 開發者、使用者、貢獻者
│
├── CLAUDE.md                              # Claude Code 專案指南
│   Location: /home/thc1006/dev/neuro-agent/CLAUDE.md
│   Size: 6.3 KB (203 行)
│   Purpose: AI 輔助開發專案規範
│   Content:
│   ├── 專案概述與架構
│   ├── 核心元件說明
│   ├── 開發指南與最佳實踐
│   ├── AI 整合規範
│   ├── 醫療安全要求
│   ├── AWS 部署標準
│   ├── 資料模型定義
│   ├── Hackathon 成功標準
│   └── 效能與合規目標
│   Protection: 🔒 SHA256 校驗和保護
│
├── MCP_INTEGRATION_GUIDE.md               # MCP 整合指南
│   Location: /home/thc1006/dev/neuro-agent/MCP_INTEGRATION_GUIDE.md
│   Size: 6.7 KB (295 行)
│   Purpose: Model Context Protocol 伺服器整合文檔
│   Content:
│   ├── MCP 概念介紹
│   ├── 安裝與配置步驟
│   ├── 5 個 MCP 伺服器說明
│   ├── API Keys 設置指南
│   ├── 故障排除指南
│   └── 使用範例
│
├── CODEBASE_INDEX.md                      # 程式碼庫索引
│   Location: /home/thc1006/dev/neuro-agent/CODEBASE_INDEX.md
│   Generated: 2025-10-12
│   Purpose: 程式碼結構快速參考
│   Content:
│   ├── 目錄結構總覽
│   ├── 關鍵檔案說明
│   ├── 依賴關係
│   ├── 入口點定義
│   └── 開發統計資料
│
├── RESOURCE_SUMMARY.md                    # 資源總覽文件
│   Location: /home/thc1006/dev/neuro-agent/RESOURCE_SUMMARY.md
│   Purpose: 專案資源與參考連結彙整
│
├── claude-code-workflow-zh.md             # Claude Code 工作流程 (中文)
│   Location: /home/thc1006/dev/neuro-agent/claude-code-workflow-zh.md
│   Size: 10 KB (470 行)
│   Purpose: 開源專案 Issue 修復完整工作流程
│   Content:
│   ├── 階段 1: 專案設置與環境準備
│   ├── 階段 2: 深度分析與理解
│   ├── 階段 3: 設計階段 (UML/ER)
│   ├── 階段 4: PRD 需求文檔
│   ├── 階段 5: BDD 行為驅動開發
│   ├── 階段 6: TDD 測試驅動開發
│   ├── 階段 7: 實作階段
│   ├── 階段 8: 驗證與部署測試
│   └── 階段 9: 文檔與提交
│
└── PROJECT_STRUCTURE_ANALYSIS.md          # 本文件
    Location: /home/thc1006/dev/neuro-agent/PROJECT_STRUCTURE_ANALYSIS.md
    Generated: 2025-10-12
    Purpose: 深度專案結構分析報告
```

#### 4.2 技術文檔目錄
```
docs/                                      # 技術文檔目錄
└── development.md                         # 開發指南
    Location: /home/thc1006/dev/neuro-agent/docs/development.md
    Purpose: 開發環境設置、開發流程、最佳實踐
```

#### 4.3 API 文檔 (自動生成)
```
FastAPI 自動文檔:
├── Swagger UI: http://localhost:8000/docs
│   └── 互動式 API 測試介面
│
└── ReDoc: http://localhost:8000/redoc
    └── 精美的 API 文檔展示

Generated from:
└── backend/main.py                        # FastAPI 路由定義
    └── Pydantic Models (backend/models/)  # 自動生成 Schema
```

#### 4.4 程式碼內文檔
```
Python Docstrings:
├── backend/agents/neuro_agent.py
├── backend/services/bedrock_service.py
├── backend/utils/medical_knowledge.py
└── backend/models/patient.py

Format: Google Style or NumPy Style
Tool: Sphinx (可選)

JSDoc Comments:
├── frontend/src/components/*.js
└── frontend/src/services/api.js

Format: JSDoc 3
Tool: JSDoc Generator (可選)
```

#### 4.5 變更日誌與版本控制
```
Git Commit History:
└── git log --oneline --graph              # 視覺化提交歷史

Recent Commits:
├── ac9ea2c - add a develop way files
├── f940f4c - chore: Add MCP servers and Chainlit directories to gitignore
├── 8c94e19 - feat: Update MCP servers setup script with virtualenv support
├── 198dcb9 - chore: add CLAUDE.md protection system
└── 606a04f - chore: lock CLAUDE.md with SHA256
```

#### 4.6 文檔更新工作流程
```
Documentation Update Workflow:
1. 程式碼變更 → 同步更新相關文檔
2. API 變更 → 更新 FastAPI Docstrings
3. 架構變更 → 更新 CLAUDE.md 和 CODEBASE_INDEX.md
4. 新功能 → 更新 README.md 和使用指南
5. Bug 修復 → 更新故障排除文檔
```

---

### 5. 建置與部署相關檔案 🚀

#### 5.1 本地開發建置
```
📄 Makefile                                # GNU Make 自動化腳本
   Location: /home/thc1006/dev/neuro-agent/Makefile

   Targets:
   ├── lock-claude                            # 鎖定 CLAUDE.md
   ├── unlock-claude                          # 解鎖 CLAUDE.md
   └── verify-claude                          # 驗證 CLAUDE.md

📄 setup_mcp_servers.sh                    # MCP 伺服器安裝腳本
   Location: /home/thc1006/dev/neuro-agent/setup_mcp_servers.sh
   Permissions: -rwxr-xr-x (可執行)

   Functions:
   ├── 檢查環境需求 (Node.js, Python3, AWS CLI)
   ├── 建立 MCP 配置目錄
   ├── 安裝 5 個 MCP 伺服器:
   │   ├── GitHub MCP (Node.js)
   │   ├── AWS Bedrock MCP (Python + uv)
   │   ├── Filesystem MCP (Node.js)
   │   ├── Claude Context MCP (Node.js)
   │   └── Semgrep MCP (Python + venv)
   ├── 生成 Claude Desktop 配置檔
   └── 產生設置指引文件

📂 scripts/                                # 建置與部署腳本
   ├── local-setup.sh                         # 本地開發環境設置
   │   └── 安裝依賴、初始化資料庫、配置環境
   │
   └── deploy.sh                              # 部署腳本
       └── 建置、測試、部署流程自動化
```

#### 5.2 容器化建置
```
📄 Dockerfile                              # Docker 映像建置定義
   Location: /home/thc1006/dev/neuro-agent/Dockerfile

   Build Stages:
   ├── Base Image: python:3.11-slim
   ├── Dependencies Installation
   ├── Application Copy
   └── Entrypoint: uvicorn backend.main:app

📄 docker-compose.yml                      # 多容器編排配置
   Location: /home/thc1006/dev/neuro-agent/docker-compose.yml

   Services:
   ├── backend:                               # FastAPI 後端
   │   ├── Build Context: .
   │   ├── Port Mapping: 8000:8000
   │   ├── Volumes: ./backend, ./data
   │   └── Command: uvicorn --reload
   │
   ├── frontend:                              # React 前端
   │   ├── Image: node:18-alpine
   │   ├── Port Mapping: 3000:3000
   │   ├── Volumes: ./frontend
   │   └── Command: npm install && npm start
   │
   └── localstack:                            # AWS 本地模擬
       ├── Image: localstack/localstack:latest
       ├── Port Mapping: 4566:4566
       ├── Services: s3, dynamodb, lambda
       └── Volumes: ./localstack_data

Build Commands:
$ docker-compose build                     # 建置所有服務
$ docker-compose up -d                     # 啟動所有服務
$ docker-compose logs -f backend           # 查看後端日誌
$ docker-compose down                      # 停止所有服務
```

#### 5.3 AWS CDK 基礎設施部署
```
📂 infrastructure/cdk/                     # AWS CDK 專案
   ├── app.py                                 # CDK 應用程式定義
   │   Location: /home/thc1006/dev/neuro-agent/infrastructure/cdk/app.py
   │
   │   Resources Defined:
   │   ├── Lambda Functions                   # 無伺服器運算
   │   │   ├── API Handler Lambda
   │   │   ├── Diagnosis Lambda
   │   │   └── Case Management Lambda
   │   │
   │   ├── API Gateway                        # REST API 端點
   │   │   ├── Routes: /health, /diagnose, /cases
   │   │   ├── CORS Configuration
   │   │   └── API Keys & Usage Plans
   │   │
   │   ├── DynamoDB Tables                    # NoSQL 資料庫
   │   │   ├── neuroagent-cases (案例儲存)
   │   │   ├── Partition Key: case_id
   │   │   ├── Sort Key: timestamp
   │   │   └── GSI: user_id-index
   │   │
   │   ├── S3 Buckets                         # 物件儲存
   │   │   ├── neuroagent-data (醫學影像)
   │   │   ├── Versioning: Enabled
   │   │   ├── Encryption: AES-256
   │   │   └── Lifecycle: 90 days
   │   │
   │   ├── IAM Roles                          # 存取控制
   │   │   ├── LambdaExecutionRole
   │   │   ├── BedrockAccessRole
   │   │   └── DynamoDBAccessRole
   │   │
   │   └── Bedrock Integration                # AI 模型存取
   │       ├── Model: anthropic.claude-3-sonnet-20240229-v1:0
   │       └── AgentCore Configuration
   │
   ├── cdk.json                               # CDK 配置
   │   └── 58+ Feature Flags
   │
   └── requirements.txt                       # CDK 依賴
       ├── aws-cdk-lib
       └── constructs

CDK Deployment Commands:
$ cd infrastructure/cdk
$ cdk bootstrap                            # 初始化 CDK 環境
$ cdk synth                                # 合成 CloudFormation 模板
$ cdk diff                                 # 顯示變更差異
$ cdk deploy                               # 部署到 AWS
$ cdk destroy                              # 刪除所有資源
```

#### 5.4 Frontend 建置
```
📦 Frontend Build Process
   Location: /home/thc1006/dev/neuro-agent/frontend/

   Development Build:
   $ npm start                                # 開發伺服器 (localhost:3000)

   Production Build:
   $ npm run build                            # 生產建置
   └── Output: frontend/build/
       ├── index.html                         # HTML 入口
       ├── static/
       │   ├── js/                            # 壓縮 JavaScript
       │   ├── css/                           # 壓縮 CSS
       │   └── media/                         # 圖片與字型
       └── asset-manifest.json                # 資源清單

   Optimization:
   ├── Code Splitting                         # 程式碼分割
   ├── Tree Shaking                           # 移除未使用程式碼
   ├── Minification                           # 程式碼壓縮
   └── Asset Optimization                     # 資源優化

   Deployment Target:
   └── AWS S3 + CloudFront                    # 靜態網站託管
```

#### 5.5 CI/CD 管線
```
📄 .github/workflows/claude-guard.yml      # GitHub Actions 工作流程
   Location: /home/thc1006/dev/neuro-agent/.github/workflows/claude-guard.yml

   Workflow: CLAUDE.md 保護
   Trigger: push, pull_request

   Jobs:
   └── validate-claude-md:
       ├── Checkout code
       ├── Verify CLAUDE.md checksum
       └── Fail if modified without updating SHA256

未來 CI/CD 建議:
├── .github/workflows/test.yml             # 自動化測試
│   ├── Backend: pytest
│   ├── Frontend: npm test
│   └── Coverage Report
│
├── .github/workflows/build.yml            # 建置驗證
│   ├── Docker Build Test
│   └── CDK Synth Test
│
└── .github/workflows/deploy.yml           # 自動部署
    ├── Staging Deployment
    └── Production Deployment (manual approval)
```

#### 5.6 部署環境
```
🌍 Deployment Environments

Development Environment:
├── Local Machine
│   ├── Backend: http://localhost:8000
│   ├── Frontend: http://localhost:3000
│   └── LocalStack: http://localhost:4566
│
└── Docker Compose
    ├── Multi-container setup
    └── AWS Service Mocking

Staging Environment:
├── AWS Account: Staging
├── API Gateway: https://api-staging.neuroagent.example.com
├── Frontend: https://staging.neuroagent.example.com
└── Database: DynamoDB (test data)

Production Environment:
├── AWS Account: Production
├── API Gateway: https://api.neuroagent.example.com
├── Frontend: https://neuroagent.example.com
├── Database: DynamoDB (production data)
├── Monitoring: CloudWatch
└── Logging: CloudWatch Logs
```

---

### 6. 依賴管理檔案 📦

#### 6.1 Python 依賴管理
```
📄 requirements.txt                        # Python 套件依賴清單
   Location: /home/thc1006/dev/neuro-agent/requirements.txt
   Format: pip requirements file
   Total Packages: 19

   ┌─────────────────────────────────────────────────────────────┐
   │ Core Dependencies (Production)                              │
   ├─────────────────────────────────────────────────────────────┤
   │ Web Framework                                               │
   │ ├── fastapi==0.104.1              # Modern web framework    │
   │ └── uvicorn[standard]==0.24.0     # ASGI server            │
   │                                                             │
   │ AWS Integration                                             │
   │ └── boto3==1.34.0                 # AWS SDK for Python     │
   │                                                             │
   │ Data Validation & Serialization                             │
   │ └── pydantic==2.5.0               # Data validation        │
   │                                                             │
   │ HTTP & File Processing                                      │
   │ ├── python-multipart==0.0.6       # Form data parsing      │
   │ └── httpx==0.25.2                 # HTTP client            │
   │                                                             │
   │ Authentication & Security                                   │
   │ ├── python-jose[cryptography]==3.3.0  # JWT handling       │
   │ └── passlib[bcrypt]==1.7.4        # Password hashing       │
   │                                                             │
   │ Environment & Configuration                                 │
   │ └── python-dotenv==1.0.0          # .env file loading      │
   └─────────────────────────────────────────────────────────────┘

   ┌─────────────────────────────────────────────────────────────┐
   │ Data Science & ML Dependencies                              │
   ├─────────────────────────────────────────────────────────────┤
   │ ├── pandas==2.1.4                 # Data manipulation       │
   │ ├── numpy==1.24.3                 # Numerical computing    │
   │ └── scikit-learn==1.3.2           # Machine learning       │
   └─────────────────────────────────────────────────────────────┘

   ┌─────────────────────────────────────────────────────────────┐
   │ Image Processing                                            │
   ├─────────────────────────────────────────────────────────────┤
   │ ├── Pillow==10.1.0                # Image processing       │
   │ └── opencv-python==4.8.1.78       # Computer vision        │
   └─────────────────────────────────────────────────────────────┘

   ┌─────────────────────────────────────────────────────────────┐
   │ Async & File I/O                                            │
   ├─────────────────────────────────────────────────────────────┤
   │ ├── asyncio==3.4.3                # Async programming      │
   │ └── aiofiles==23.2.1              # Async file operations  │
   └─────────────────────────────────────────────────────────────┘

   ┌─────────────────────────────────────────────────────────────┐
   │ Testing Dependencies                                        │
   ├─────────────────────────────────────────────────────────────┤
   │ ├── pytest==7.4.3                 # Testing framework      │
   │ └── pytest-asyncio==0.21.1        # Async testing support  │
   └─────────────────────────────────────────────────────────────┘

📄 pyproject.toml                          # PEP 518 專案配置
   Location: /home/thc1006/dev/neuro-agent/pyproject.toml

   [project]
   dependencies = [
       "fastapi>=0.104.1",
       "uvicorn[standard]>=0.24.0",
       "boto3>=1.34.0",
       "pydantic>=2.5.0"
   ]

   Purpose: 專案元資料 + 工具配置
   Tools Configured:
   ├── pytest: 測試框架配置
   ├── black: 程式碼格式化工具
   └── isort: Import 排序工具

📄 infrastructure/cdk/requirements.txt     # CDK Python 依賴
   Location: /home/thc1006/dev/neuro-agent/infrastructure/cdk/requirements.txt

   Dependencies:
   ├── aws-cdk-lib                           # AWS CDK 核心函式庫
   └── constructs                            # CDK Constructs
```

#### 6.2 Node.js 依賴管理
```
📄 package.json                            # Node.js 專案定義
   Location: /home/thc1006/dev/neuro-agent/package.json (Frontend)
   Package Manager: npm
   Total Dependencies: 8
   Total DevDependencies: 1

   ┌─────────────────────────────────────────────────────────────┐
   │ Production Dependencies                                     │
   ├─────────────────────────────────────────────────────────────┤
   │ UI Framework (Material-UI)                                  │
   │ ├── @mui/material@^5.14.0         # Core components        │
   │ ├── @mui/icons-material@^5.14.0   # Icon library          │
   │ ├── @emotion/react@^11.11.0       # CSS-in-JS (required)  │
   │ └── @emotion/styled@^11.11.0      # Styled components     │
   │                                                             │
   │ React Core                                                  │
   │ ├── react@^18.2.0                 # React library          │
   │ └── react-dom@^18.2.0             # React DOM rendering    │
   │                                                             │
   │ Routing                                                     │
   │ └── react-router-dom@^6.8.0       # Client-side routing    │
   │                                                             │
   │ HTTP Client                                                 │
   │ └── axios@^1.6.0                  # Promise-based HTTP     │
   │                                                             │
   │ Data Visualization                                          │
   │ └── recharts@^2.8.0               # React charts library   │
   │                                                             │
   │ File Upload                                                 │
   │ └── react-dropzone@^14.2.0        # Drag & drop uploads    │
   └─────────────────────────────────────────────────────────────┘

   ┌─────────────────────────────────────────────────────────────┐
   │ Development Dependencies                                    │
   ├─────────────────────────────────────────────────────────────┤
   │ └── react-scripts@5.0.1           # Create React App       │
   │     ├── Webpack configuration                              │
   │     ├── Babel transpiler                                   │
   │     ├── Jest testing                                       │
   │     └── Development server                                 │
   └─────────────────────────────────────────────────────────────┘

📄 package-lock.json                       # npm 鎖定檔案
   Location: /home/thc1006/dev/neuro-agent/package-lock.json (如存在)
   Purpose: 確保依賴版本一致性
   Generated: npm install

No Yarn Lock File Found
No pnpm Lock File Found
```

#### 6.3 MCP Servers 依賴
```
MCP Servers Dependencies:

┌─────────────────────────────────────────────────────────────┐
│ 1. GitHub MCP Server (Node.js)                              │
├─────────────────────────────────────────────────────────────┤
│ Location: mcp-servers/github/                              │
│ Manager: npm                                                │
│ Dependencies: 88 packages                                   │
│ Key Packages:                                               │
│ ├── express                           # Web framework       │
│ ├── octokit                           # GitHub API client   │
│ └── zod                               # Schema validation   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 2. AWS Bedrock MCP Server (Python)                          │
├─────────────────────────────────────────────────────────────┤
│ Location: mcp-servers/aws-bedrock/                         │
│ Manager: uv (modern Python package manager)                │
│ Environment: .venv/ (virtual environment)                  │
│ Dependencies: 177 packages                                  │
│ Key Packages:                                               │
│ ├── chainlit==2.5.5                   # UI framework        │
│ ├── boto3                             # AWS SDK             │
│ ├── langchain==0.3.24                 # LLM framework       │
│ ├── langgraph==0.3.34                 # Agent orchestration │
│ └── mcp==1.6.0                        # MCP protocol        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 3. Filesystem MCP Server (Node.js/TypeScript)               │
├─────────────────────────────────────────────────────────────┤
│ Location: mcp-servers/mcp-servers-official/src/filesystem/ │
│ Manager: npm                                                │
│ Dependencies: 461 packages                                  │
│ Source: TypeScript (compiled to dist/index.js)             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 4. Claude Context MCP Server (Node.js)                      │
├─────────────────────────────────────────────────────────────┤
│ Location: mcp-servers/claude-context/                      │
│ Manager: pnpm (workspace)                                   │
│ Dependencies: 173+ packages                                 │
│ Lockfile: pnpm-lock.yaml (289 KB)                          │
│ Workspace: Monorepo structure                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 5. Semgrep MCP Server (Python)                              │
├─────────────────────────────────────────────────────────────┤
│ Location: mcp-servers/semgrep-mcp/                         │
│ Manager: pip                                                │
│ Environment: venv/ (virtual environment)                   │
│ Key Packages:                                               │
│ ├── semgrep==1.135.0                  # Security scanner    │
│ ├── mcp==1.12.2                       # MCP protocol        │
│ └── opentelemetry-*                   # Observability       │
└─────────────────────────────────────────────────────────────┘
```

#### 6.4 依賴安裝指令總覽
```bash
# ==========================================
# Backend Python Dependencies
# ==========================================
cd /home/thc1006/dev/neuro-agent
pip install -r requirements.txt           # 安裝後端依賴

# Or using virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# ==========================================
# Frontend Node.js Dependencies
# ==========================================
cd frontend
npm install                               # 安裝前端依賴
# or: npm ci (使用 package-lock.json)

# ==========================================
# AWS CDK Dependencies
# ==========================================
cd infrastructure/cdk
pip install -r requirements.txt           # 安裝 CDK 依賴

# ==========================================
# MCP Servers Dependencies
# ==========================================
./setup_mcp_servers.sh                    # 一鍵安裝所有 MCP servers

# Manual installation:
# 1. GitHub MCP
cd mcp-servers/github && npm install

# 2. AWS Bedrock MCP
cd mcp-servers/aws-bedrock
./venv/bin/pip install uv
./venv/bin/uv sync --all-groups

# 3. Filesystem MCP
cd mcp-servers/mcp-servers-official/src/filesystem
npm install

# 4. Claude Context MCP
cd mcp-servers/claude-context
npm install

# 5. Semgrep MCP
cd mcp-servers/semgrep-mcp
./venv/bin/pip install -e .
```

#### 6.5 依賴版本鎖定策略
```
Version Locking Strategy:

Python (requirements.txt):
├── Strategy: Exact versions (==)
├── Example: fastapi==0.104.1
└── Rationale: 確保生產環境一致性

Node.js (package.json):
├── Strategy: Caret ranges (^)
├── Example: "react": "^18.2.0"
└── Rationale: 允許安全的補丁更新

Lock Files:
├── Python: 無標準 lock file (考慮使用 Poetry 或 pip-tools)
├── Node.js: package-lock.json (npm)
├── AWS Bedrock MCP: uv.lock (uv package manager)
└── Claude Context MCP: pnpm-lock.yaml (pnpm)

Dependency Update Policy:
├── Security patches: 立即更新
├── Minor versions: 每月檢查
├── Major versions: 評估後更新
└── Testing: 所有更新需通過完整測試套件
```

#### 6.6 依賴健康度檢查
```bash
# Python 依賴安全性檢查
pip install safety
safety check -r requirements.txt

# Node.js 依賴漏洞掃描
cd frontend
npm audit                                 # 檢查已知漏洞
npm audit fix                             # 自動修復

# 過時套件檢查
pip list --outdated                       # Python
npm outdated                              # Node.js

# 未使用依賴檢測
pip install pip-autoremove                # Python
npx depcheck                              # Node.js
```

---

## 總結與建議 💡

### 專案健康度評估

#### ✅ 優勢 (Strengths)
1. **清晰的架構分層**: Backend (MVC), Frontend (Component-Based), Infrastructure (IaC)
2. **完整的文檔系統**: CLAUDE.md, MCP_INTEGRATION_GUIDE.md, 工作流程文檔
3. **現代化技術棧**: FastAPI, React 18, AWS Bedrock, MCP Protocol
4. **容器化支援**: Docker + Docker Compose
5. **基礎設施即程式碼**: AWS CDK
6. **擴展性設計**: MCP Servers 整合
7. **安全性考量**: JWT 認證, 環境變數管理, HIPAA 指引

#### ⚠️ 改進建議 (Recommendations)

**1. 測試覆蓋率提升**
```
Current: 基礎單元測試
Needed:
├── 增加整合測試 (API endpoints)
├── E2E 測試 (Playwright/Cypress)
├── 效能測試 (Locust/k6)
└── 安全測試 (OWASP ZAP)
```

**2. CI/CD 管線完善**
```
Current: Claude Guard workflow only
Needed:
├── Automated testing on PR
├── Code quality checks (SonarQube)
├── Security scanning (Semgrep, Snyk)
├── Automated deployment (Staging → Production)
└── Rollback mechanisms
```

**3. 監控與可觀測性**
```
Missing:
├── Application Performance Monitoring (APM)
├── Error tracking (Sentry)
├── Log aggregation (CloudWatch Logs Insights)
├── Metrics dashboard (CloudWatch Dashboard)
└── Alerting system (CloudWatch Alarms)
```

**4. 資料庫遷移管理**
```
Current: DynamoDB (schema-less)
Needed:
├── Data migration scripts
├── Backup & restore procedures
├── Data validation
└── Audit logging
```

**5. API 版本控制**
```
Current: Single version
Needed:
├── /api/v1/ versioned endpoints
├── Deprecation policy
├── Backward compatibility
└── Version migration guides
```

**6. 依賴管理優化**
```
Python:
├── Consider: Poetry or Pipenv for better dependency resolution
└── Add: requirements-dev.txt, requirements-test.txt

Node.js:
├── Use: package-lock.json consistently
└── Consider: Renovate Bot for automated updates
```

---

## 後續行動計畫 📅

### Phase 1: 測試與品質 (Week 1-2)
- [ ] 提升測試覆蓋率至 80%+
- [ ] 設置 CI/CD 測試管線
- [ ] 整合程式碼品質工具

### Phase 2: 部署與維運 (Week 3-4)
- [ ] 完善 AWS CDK 部署腳本
- [ ] 設置 Staging 環境
- [ ] 建立監控與告警系統

### Phase 3: 功能擴展 (Week 5-6)
- [ ] 完成 MCP Servers 整合
- [ ] 實作進階 AI 功能
- [ ] 優化使用者體驗

### Phase 4: 文檔與合規 (Week 7-8)
- [ ] API 文檔完善
- [ ] HIPAA 合規檢查
- [ ] 使用者手冊撰寫
- [ ] Demo 準備

---

*本分析報告由 Claude Code (Ultrathink Mode) 產生*
*分析時間: 2025-10-12*
*專案版本: 1.0.0*
*AWS AI Agent Global Hackathon 2025*
