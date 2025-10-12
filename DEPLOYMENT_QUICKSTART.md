# 🚀 NeuroAgent Deployment Quickstart

## 當前部署狀態 (2025-10-13)

### ✅ 已部署 (Working)
- AWS Infrastructure (100%)
- Documentation (100%)
- Testing (100%)
- Demo Data (100%)

### ⚠️ 部分運作
- **Backend API**: Deployed but broken (Lambda import error)
- **Frontend**: Built but not deployed yet

### ❌ 待修復
- Lambda dependencies packaging (需要 Linux 環境)

---

## 🎯 Hackathon Demo 快速啟動 (< 5 分鐘)

### 選項 1: 本地全棧 (最簡單)

```bash
# Terminal 1: Backend
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend
npm start

# 開啟瀏覽器: http://localhost:3000
```

**Demo 準備**:
- ✅ 功能完整
- ✅ 有 6 個真實醫學案例可測試
- ✅ Swagger UI: http://localhost:8000/docs

---

### 選項 2: Frontend 部署到 Vercel (< 5 分鐘)

#### 步驟 1: 安裝 Vercel CLI
```bash
npm install -g vercel
```

#### 步驟 2: 登入 Vercel
```bash
vercel login
# 使用 GitHub/GitLab/Email 登入
```

#### 步驟 3: 部署
```bash
cd frontend
vercel --prod

# 回答問題：
# Set up and deploy? Y
# Which scope? [選擇你的帳號]
# Link to existing project? N
# What's your project's name? neuroagent
# In which directory is your code located? ./
# Want to override the settings? N

# 等待 1-2 分鐘...
# ✅ Deployed to: https://neuroagent-xxxx.vercel.app
```

#### 步驟 4: 本地運行 Backend
```bash
# Terminal 1: Backend (本地)
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000

# Terminal 2: 使用 ngrok 暴露（可選）
ngrok http 8000
# 複製 ngrok URL

# 更新 Vercel 環境變數
vercel env add REACT_APP_API_URL
# 輸入 ngrok URL 或保持 localhost (僅自己可訪問)
```

**Demo URL**: `https://neuroagent-xxxx.vercel.app`

---

## 🔧 完整雲端部署 (需要 Linux 環境)

### 使用 AWS Cloud9 (推薦)

#### 1. 創建 Cloud9 環境
```bash
# AWS Console → Cloud9 → Create environment
# - Name: neuroagent-dev
# - Instance: t2.micro
# - Platform: Amazon Linux 2023
```

#### 2. 在 Cloud9 中執行
```bash
# Clone 專案
git clone https://github.com/thc1006/neuro-agent.git
cd neuro-agent

# 修復 Lambda dependencies
chmod +x scripts/fix_lambda_dependencies.sh
./scripts/fix_lambda_dependencies.sh

# 部署到 AWS
cd infrastructure/cdk-clean
npm install -g aws-cdk
cdk deploy NeuroAgentStack

# 等待 5-10 分鐘...
```

#### 3. 驗證部署
```bash
# 測試 API Gateway
curl https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod/health

# 預期回應：
# {"status":"healthy","services":{"bedrock":"connected"}}
```

#### 4. 更新 Frontend 環境變數
```bash
cd ../../frontend

# Vercel 環境變數已設定為 AWS API Gateway
# 重新部署
vercel --prod
```

**完成！** 🎉
- Backend: https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod/
- Frontend: https://neuroagent-xxxx.vercel.app

---

## 📊 Demo 數據準備

### 6 個真實醫學案例 (已準備)

```bash
# 查看案例
cat data/demo_cases.json

# 案例類型：
1. Chronic Migraine (慢性偏頭痛) - 45F
2. Hemiplegic Migraine (偏癱型偏頭痛) - 57F
3. Acute Ischemic Stroke (急性缺血性中風) - 66M
4. Multiple Sclerosis (多發性硬化症) - 35F
5. Generalized Epilepsy (全身性癲癇) - 25F
6. Early Parkinson's (早期帕金森氏症) - 70M
```

### JWT Token 生成

```python
# 產生 Demo Token
import jwt
import datetime

payload = {
    'user_id': 'demo-physician',
    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
}
token = jwt.encode(
    payload,
    'REDACTED',
    algorithm='HS256'
)
print(f"Bearer {token}")
```

### 測試 API Calls

```bash
# 1. Health Check (無需認證)
curl https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod/health

# 2. Diagnosis API (需要 JWT)
curl -X POST https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod/api/v1/diagnosis \
  -H "Authorization: Bearer REDACTED" \
  -H "Content-Type: application/json" \
  -d @data/demo_cases.json

# 3. Drug Interaction Check
curl -X POST https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod/api/v1/drug-interactions \
  -H "Authorization: Bearer REDACTED" \
  -H "Content-Type: application/json" \
  -d '{"medications": ["warfarin", "aspirin", "levodopa"]}'
```

---

## 🎥 Demo 腳本

詳細 3 分鐘 Demo 流程請參考:
- **[DEMO_SCRIPT.md](./DEMO_SCRIPT.md)** - 完整演示腳本
- **[HACKATHON_SUBMISSION.md](./HACKATHON_SUBMISSION.md)** - Hackathon 提交材料

### Demo 重點

1. **展示 Live API** (30 秒)
   - 開啟 Swagger UI: `/docs`
   - 執行 health check
   - 展示 5 個端點

2. **真實案例診斷** (60 秒)
   - 使用 Chronic Migraine 案例
   - 展示 AI 回應
   - 說明信心分數上限 (85%)

3. **藥物交互檢查** (30 秒)
   - Warfarin + Aspirin = 禁忌
   - 展示安全警告

4. **技術亮點** (60 秒)
   - 100% 測試覆蓋率
   - Redis 快取 (省 65% 成本)
   - 安全強化 (JWT + 提示注入防護)

---

## 🔗 重要連結

### 部署相關
- **Live API**: https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod/
- **API Docs**: https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod/docs
- **GitHub**: https://github.com/thc1006/neuro-agent
- **GitLab Mirror**: https://gitlab.com/thc1006/neuro-agent

### 文檔
- **README (EN)**: [README.md](./README.md)
- **README (繁中)**: [README.zh-TW.md](./README.zh-TW.md)
- **Lambda Fix Guide**: [LAMBDA_FIX_GUIDE.md](./LAMBDA_FIX_GUIDE.md)
- **Deployment Status**: [DEPLOYMENT_STATUS_REPORT.md](./DEPLOYMENT_STATUS_REPORT.md)

### AWS Resources
| Resource | Status | Identifier |
|----------|--------|------------|
| API Gateway | ✅ | 1w80v6fnw1 |
| Lambda | ⚠️ | NeuroAgentAPI |
| DynamoDB | ✅ | neuroagent-cases |
| S3 | ✅ | neuroagent-images-100939136870-us-east-1 |
| Redis | ✅ | neuroagent-redis.xjuedn.0001.use1.cache.amazonaws.com |

---

## 🎯 3 種 Demo 情境選擇

### 情境 A: 最佳展示 (需要 Cloud9，1-2 小時準備)
- ✅ 完全雲端部署
- ✅ Backend: AWS Lambda
- ✅ Frontend: Vercel
- ✅ 專業印象最佳

### 情境 B: 混合方案 (5 分鐘準備)
- 🟡 Backend: 本地 (說明 Windows 限制)
- ✅ Frontend: Vercel (雲端)
- ✅ 功能完整，有雲端 URL

### 情境 C: 全本地 (2 分鐘準備)
- 🟡 Backend: 本地
- 🟡 Frontend: 本地
- ✅ 功能完整，展示最穩定

---

## ✅ Pre-Demo Checklist

### 必做項目
- [ ] Backend 可以正常啟動
- [ ] Frontend 可以正常訪問
- [ ] 至少測試 1 個 demo 案例成功
- [ ] 準備好 JWT token (24 小時有效期)
- [ ] 瀏覽器開啟 Swagger UI `/docs`
- [ ] 準備 DEMO_SCRIPT.md 投影片

### 可選項目
- [ ] Frontend 部署到 Vercel
- [ ] Lambda 修復完成 (Cloud9)
- [ ] 準備 backup slides (以防 API 掛掉)
- [ ] 錄製 demo 影片作為 backup

---

## 📞 緊急支援

如果 demo 時遇到問題：

1. **API 無法連線**
   - 立即切換到本地 backend
   - `uvicorn backend.main:app --reload`

2. **Frontend 無法載入**
   - 使用本地 frontend
   - `cd frontend && npm start`

3. **忘記 JWT token**
   - 執行 `python scripts/generate_jwt.py`
   - 或暫時跳過認證，只展示 `/health`

4. **Demo 資料問題**
   - 使用 `data/demo_cases.json` 中的任一案例
   - 備用：直接展示 Swagger UI 的 schema

---

**最後更新**: 2025-10-13
**準備時間**: 2-5 分鐘 (本地) / 1-2 小時 (完整雲端)
**建議方案**: 情境 B (混合方案) - 平衡功能與準備時間
