# 🔧 Lambda Dependencies Fix Guide

## 問題描述

**Current Issue**: Lambda 函數無法導入 Python 模組
```json
{"errorMessage": "Unable to import module 'backend.main': No module named 'fastapi'"}
```

**Root Cause**: AWS Lambda 需要將 dependencies 與應用程式碼一起打包，但目前只上傳了源代碼。

**Why Windows Can't Fix It**:
- pandas、numpy、cryptography 等套件需要編譯 C/Rust 擴充
- Windows 環境缺少 GCC/Rust 編譯器
- AWS CDK Docker bundling 需要 Docker Desktop（Windows Git Bash 不支援）

---

## ✅ Solution 1: AWS Cloud9 (推薦)

### 優點
- ✅ 原生 Linux 環境
- ✅ 已預裝 Python 3.11、pip、AWS CLI
- ✅ 直接連接 AWS 帳戶
- ✅ 免費層級可用（t2.micro）

### 步驟

#### 1. 創建 Cloud9 環境
```bash
# 在 AWS Console
1. 前往 AWS Cloud9
2. Create environment
   - Name: neuroagent-dev
   - Instance type: t2.micro (免費層級)
   - Platform: Amazon Linux 2023
3. 等待 2-3 分鐘創建完成
```

#### 2. Clone 專案
```bash
# 在 Cloud9 Terminal
git clone https://github.com/thc1006/neuro-agent.git
cd neuro-agent
```

#### 3. 執行修復腳本
```bash
chmod +x scripts/fix_lambda_dependencies.sh
./scripts/fix_lambda_dependencies.sh
```

#### 4. 部署到 AWS
```bash
cd infrastructure/cdk-clean

# 安裝 CDK（如果還沒安裝）
npm install -g aws-cdk

# 部署
cdk deploy NeuroAgentStack
```

#### 5. 測試 Lambda
```bash
# 回到專案根目錄
cd ../..

# 測試 health endpoint
curl https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod/health

# 應該回傳：
# {"status":"healthy","services":{"bedrock":"connected"}}
```

---

## ✅ Solution 2: Linux VM / WSL2

### 使用 WSL2 (Windows Subsystem for Linux)

#### 1. 啟用 WSL2
```powershell
# 在 PowerShell (管理員權限)
wsl --install
wsl --set-default-version 2
```

#### 2. 安裝 Ubuntu
```powershell
wsl --install -d Ubuntu-22.04
```

#### 3. 在 WSL2 中執行
```bash
# 進入 WSL2
wsl

# 安裝必要工具
sudo apt update
sudo apt install -y python3.11 python3-pip git

# Clone 專案
git clone https://github.com/thc1006/neuro-agent.git
cd neuro-agent

# 執行修復腳本
chmod +x scripts/fix_lambda_dependencies.sh
./scripts/fix_lambda_dependencies.sh
```

---

## ✅ Solution 3: Docker 打包（需要 Docker Desktop）

### 前置條件
- Docker Desktop 已安裝並執行

### 步驟

#### 1. 創建 Dockerfile for Lambda
```dockerfile
# infrastructure/lambda-builder.Dockerfile
FROM public.ecr.aws/lambda/python:3.11

COPY requirements.txt .
RUN pip install -r requirements.txt -t /asset-output/python/

CMD ["echo", "Dependencies packaged"]
```

#### 2. 建置 Docker image
```bash
cd infrastructure
docker build -f lambda-builder.Dockerfile -t neuro-lambda-builder ..
```

#### 3. 提取 dependencies
```bash
# 創建容器並複製檔案
docker create --name temp-container neuro-lambda-builder
docker cp temp-container:/asset-output ../lambda_layer
docker rm temp-container
```

#### 4. 部署
```bash
cd cdk-clean
cdk deploy NeuroAgentStack
```

---

## 🚀 Solution 4: 預編譯 Lambda Layer (最快)

如果時間緊迫，可以使用預編譯的 Lambda Layer：

### 使用 AWS Serverless Application Repository

```bash
# 搜尋現有的 Python 3.11 Lambda Layer
aws serverlessrepo list-applications \
  --query 'Applications[?contains(Name, `python`) && contains(Name, `layer`)]'

# 或使用社群維護的 Layer
# https://github.com/keithrozario/Klayers
```

### 手動添加 Layer ARN 到 CDK

編輯 `infrastructure/cdk-clean/app.py`:

```python
# 使用公開的 Lambda Layer
requirements_layer = _lambda.LayerVersion.from_layer_version_arn(
    self, "PythonDepsLayer",
    layer_version_arn="arn:aws:lambda:us-east-1:770693421928:layer:Klayers-p311-fastapi:1"
)
```

---

## 📊 驗證步驟

### 1. 測試 Lambda 本地執行
```bash
# 測試 imports
python3 << EOF
import sys
sys.path.insert(0, 'lambda_layer/python')

import fastapi
import boto3
import pydantic
import mangum

print("✅ All imports successful")
EOF
```

### 2. 測試 Lambda 在 AWS
```bash
# 健康檢查
curl https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod/health

# 診斷 API（需要 JWT token）
curl -X POST https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod/api/v1/diagnosis \
  -H "Authorization: Bearer REDACTED" \
  -H "Content-Type: application/json" \
  -d @data/demo_cases.json
```

### 3. 檢查 CloudWatch Logs
```bash
# 查看最近的 Lambda logs
aws logs tail /aws/lambda/NeuroAgentAPI --follow

# 應該看到：
# [INFO] Bedrock service initialized
# [INFO] FastAPI application started
```

---

## 🎯 Hackathon Demo 緊急方案

如果 Hackathon 前無法修復 Lambda，使用以下方案：

### 方案 A: 本地 Backend + 雲端 Frontend
```bash
# Terminal 1: 本地執行 backend
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000

# Terminal 2: 使用 ngrok 暴露到公網（可選）
ngrok http 8000
# 將 ngrok URL 更新到 frontend/.env.production

# Frontend 已部署到 Vercel
# 使用者訪問: https://neuroagent.vercel.app
```

### 方案 B: 完全本地運行
```bash
# Terminal 1: Backend
uvicorn backend.main:app --reload

# Terminal 2: Frontend
cd frontend
npm start

# Demo URL: http://localhost:3000
```

### Demo 時的說明話術
> "我們的系統已經完全部署到 AWS，包括 API Gateway、DynamoDB、S3 和 ElastiCache Redis。目前 Lambda 函數因為 Windows 環境的編譯限制暫時使用本地 backend 展示，這是一個常見的跨平台開發挑戰。在生產環境中，我們會使用 Linux 環境打包 Lambda dependencies。"

---

## 📈 部署後性能指標

修復完成後，預期指標：

| Metric | Target | Current |
|--------|--------|---------|
| Lambda Cold Start | < 3s | N/A (broken) |
| Lambda Warm Start | < 500ms | N/A (broken) |
| API Response Time (p95) | < 2s | N/A (broken) |
| Cache Hit Rate | 60-70% | ✅ Redis running |
| Error Rate | < 1% | 100% (import error) |

---

## 🔗 相關資源

- **AWS Cloud9**: https://aws.amazon.com/cloud9/
- **Lambda Layers**: https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html
- **CDK Python**: https://docs.aws.amazon.com/cdk/v2/guide/work-with-cdk-python.html
- **Klayers (Community Layers)**: https://github.com/keithrozario/Klayers
- **WSL2 Installation**: https://learn.microsoft.com/en-us/windows/wsl/install

---

## 📞 需要幫助？

如果在修復過程中遇到問題：

1. 檢查 CloudWatch Logs: `/aws/lambda/NeuroAgentAPI`
2. 查看 CDK deployment output
3. 驗證 IAM permissions
4. 確認 Lambda Layer 大小 < 250 MB (unzipped)

---

**最後更新**: 2025-10-13
**狀態**: Lambda dependencies 需要 Linux 環境打包
**優先級**: High (Hackathon demo 可使用本地 backend workaround)
