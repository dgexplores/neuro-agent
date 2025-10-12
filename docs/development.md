# NeuroAgent 開發指南

## 專案架構

### 後端 (Backend)
- **框架**: FastAPI
- **AI服務**: Amazon Bedrock AgentCore
- **資料庫**: DynamoDB
- **檔案儲存**: S3
- **部署**: AWS Lambda + API Gateway

### 前端 (Frontend)
- **框架**: React 18
- **UI庫**: Material-UI (MUI)
- **狀態管理**: React Hooks
- **HTTP客戶端**: Axios

### 基礎設施 (Infrastructure)
- **IaC**: AWS CDK (Python)
- **容器化**: Docker
- **開發環境**: Docker Compose

## 開發工作流程

### 1. 環境設置
```bash
# 複製環境變數
cp .env.example .env

# 啟動開發環境
./scripts/local-setup.sh
```

### 2. 本地開發
```bash
# 後端開發
python backend/main.py

# 前端開發
cd frontend && npm start
```

### 3. 測試
```bash
# 執行後端測試
pytest backend/tests/

# 執行前端測試
cd frontend && npm test
```

### 4. 部署
```bash
# 部署到AWS
./scripts/deploy.sh
```

## Claude Code MAX 開發建議

### 最佳實踐
1. **探索階段**: 使用 `/explore` 指令分析現有代碼結構
2. **規劃階段**: 使用 `/plan` 指令制定開發計畫
3. **編程階段**: 使用 `/code` 指令實現功能
4. **提交階段**: 使用 `/commit` 指令提交變更

### 工作流程範例
```
/explore backend/agents/neuro_agent.py
/plan "Add image analysis functionality to NeuroAgent"
/code "Implement analyze_image method with SageMaker integration"
/commit "Add medical image analysis capability"
```

### 模型選擇建議
- **日常編程**: Sonnet 4 (高效且平衡)
- **複雜架構設計**: Opus 4 (深度思考能力)
- **快速原型**: Haiku 4 (快速回應)

## API 文檔

### 核心端點
- `POST /api/v1/diagnosis` - 提交診斷請求
- `POST /api/v1/upload-image` - 上傳醫學影像
- `GET /api/v1/cases/{case_id}` - 取得病例詳情

### 認證
- 使用 Bearer Token 認證
- 開發環境可使用 demo token

## 部署指南

### AWS 服務需求
- Amazon Bedrock (AI模型)
- Lambda (API執行)
- API Gateway (API管理)
- DynamoDB (資料存儲)
- S3 (檔案存儲)

### 環境變數
確保設置以下環境變數：
- `AWS_REGION`
- `BEDROCK_AGENTCORE_AGENT_ID`
- `BEDROCK_MODEL_ID`
- `DYNAMODB_TABLE_NAME`
- `S3_BUCKET_NAME`

## 故障排除

### 常見問題
1. **Bedrock 權限錯誤**: 確認 IAM 角色有正確權限
2. **CORS 錯誤**: 檢查 API Gateway CORS 設定
3. **模型調用失敗**: 驗證 Bedrock 模型 ID 和可用性

### 調試技巧
- 使用 FastAPI 自動生成的 `/docs` 頁面測試 API
- 查看 CloudWatch 日誌排查 Lambda 錯誤
- 使用瀏覽器開發者工具檢查前端請求
