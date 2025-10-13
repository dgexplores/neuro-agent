# NeuroAgent API 完整教學指南

**適用對象**：後端開發者、系統整合工程師、DevOps 工程師
**技術難度**：中級
**預計閱讀時間**：30 分鐘
**最後更新**：2025年10月13日

---

## 📋 目錄

1. [API 概覽](#api-概覽)
2. [認證機制](#認證機制)
3. [API 端點詳解](#api-端點詳解)
4. [完整範例：診斷流程](#完整範例診斷流程)
5. [錯誤處理](#錯誤處理)
6. [效能優化](#效能優化)
7. [SDK 與工具](#sdk-與工具)
8. [安全性最佳實踐](#安全性最佳實踐)
9. [常見問題](#常見問題)

---

## API 概覽

### 基本資訊

```yaml
API Base URL: https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod/
API Version: v1
Protocol: HTTPS (TLS 1.2+)
Authentication: JWT Bearer Token
Content-Type: application/json
Rate Limit: 100 requests/minute (per user)
Timeout: 30 seconds (diagnosis), 60 seconds (image upload)
```

### API 架構

```
使用者應用程式
      ↓ HTTPS + JWT
AWS API Gateway (REST API)
      ↓ Proxy Integration
AWS Lambda (Python 3.11 + FastAPI)
      ↓
Amazon Bedrock (Claude 3 Sonnet)
      ↓
DynamoDB / S3 / ElastiCache
```

### 可用端點總覽

| HTTP Method | Endpoint | 描述 | 認證需求 |
|-------------|----------|------|----------|
| `GET` | `/health` | 健康檢查 | ❌ 不需要 |
| `GET` | `/` | API 根路徑 | ❌ 不需要 |
| `POST` | `/api/v1/diagnosis` | 建立診斷 | ✅ 需要 JWT |
| `POST` | `/api/v1/drug-interactions` | 藥物交互作用檢查 | ✅ 需要 JWT |
| `POST` | `/api/v1/upload-image` | 醫學影像上傳 | ✅ 需要 JWT |
| `GET` | `/api/v1/cases` | 取得病例清單 | ✅ 需要 JWT |
| `GET` | `/api/v1/cases/{case_id}` | 取得特定病例 | ✅ 需要 JWT |
| `GET` | `/docs` | Swagger UI 文件 | ❌ 不需要 |
| `GET` | `/redoc` | ReDoc 文件 | ❌ 不需要 |

---

## 認證機制

### JWT Token 結構

NeuroAgent 使用 **JWT (JSON Web Token)** 進行認證。

#### Token 格式

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiZGVtby1waHlzaWNpYW4iLCJyb2xlIjoiZG9jdG9yIiwiZXhwIjoxNzI4OTY3MjAwLCJpYXQiOjE3Mjg4ODA4MDB9.XYZ123...
```

#### Token Payload 結構

```json
{
  "user_id": "demo-physician",
  "role": "doctor",
  "exp": 1728967200,
  "iat": 1728880800
}
```

| 欄位 | 說明 | 必填 |
|------|------|------|
| `user_id` | 使用者唯一識別碼 | ✅ 是 |
| `role` | 使用者角色（doctor, nurse, researcher） | ✅ 是 |
| `exp` | Token 到期時間（Unix timestamp） | ✅ 是 |
| `iat` | Token 發行時間（Unix timestamp） | ✅ 是 |

---

### 產生 JWT Token

#### 方法 1：使用 Python（推薦）

```python
import jwt
import datetime

# JWT 設定
JWT_SECRET_KEY = "REDACTED"
JWT_ALGORITHM = "HS256"

def generate_token(user_id: str, role: str = "doctor", hours: int = 24) -> str:
    """
    產生 JWT Token

    Args:
        user_id: 使用者 ID
        role: 使用者角色（doctor, nurse, researcher）
        hours: Token 有效時數

    Returns:
        JWT Token 字串
    """
    payload = {
        'user_id': user_id,
        'role': role,
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=hours)
    }

    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token

# 使用範例
token = generate_token("demo-physician", "doctor", 24)
print(f"Bearer {token}")
```

#### 方法 2：使用 Node.js

```javascript
const jwt = require('jsonwebtoken');

const JWT_SECRET_KEY = "REDACTED";

function generateToken(userId, role = 'doctor', hours = 24) {
    const payload = {
        user_id: userId,
        role: role,
        iat: Math.floor(Date.now() / 1000),
        exp: Math.floor(Date.now() / 1000) + (hours * 60 * 60)
    };

    return jwt.sign(payload, JWT_SECRET_KEY, { algorithm: 'HS256' });
}

// 使用範例
const token = generateToken('demo-physician', 'doctor', 24);
console.log(`Bearer ${token}`);
```

#### 方法 3：使用 cURL（測試用）

```bash
# 使用 jwt.io 網站手動產生 Token
# 或使用 Python/Node.js 腳本產生後複製

export JWT_TOKEN="REDACTED"

curl -X GET \
  https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod/health \
  -H "Authorization: Bearer $JWT_TOKEN"
```

---

### JWT 驗證流程

當您發送請求時，API Gateway 會執行以下 7 層驗證：

```
1. Token 格式檢查
   ↓
2. 簽章驗證（HMAC SHA-256）
   ↓
3. 演算法檢查（僅允許 HS256）
   ↓
4. 到期時間驗證（exp）
   ↓
5. 發行時間驗證（iat）
   ↓
6. 必填欄位檢查（user_id, role）
   ↓
7. 未來時間戳記防護
```

**如果任一層驗證失敗，會回傳 `401 Unauthorized`**。

---

## API 端點詳解

### 1. 健康檢查

#### `GET /health`

檢查 API 服務狀態及 Bedrock 連線。

**請求範例**：

```bash
curl -X GET \
  https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod/health
```

**回應範例**（200 OK）：

```json
{
  "status": "healthy",
  "services": {
    "bedrock": "connected"
  }
}
```

**用途**：
- 監控系統健康狀態
- 驗證 API 可用性
- CloudWatch Alarms 整合

---

### 2. 神經疾病診斷

#### `POST /api/v1/diagnosis`

根據病患資料提供 AI 診斷建議。

**請求標頭**：

```http
POST /api/v1/diagnosis HTTP/1.1
Host: 1w80v6fnw1.execute-api.us-east-1.amazonaws.com
Content-Type: application/json
Authorization: Bearer REDACTED
```

**請求 Body**：

```json
{
  "patient_info": {
    "age": 45,
    "gender": "female",
    "medical_history": [
      "Ependymoma (brain tumor removed at age 30)",
      "Chronic migraine since age 22"
    ],
    "current_medications": [
      "Anti-CGRP monoclonal antibodies (trial)"
    ],
    "allergies": []
  },
  "symptoms": [
    {
      "name": "throbbing headache",
      "severity": "severe",
      "duration_days": 365,
      "description": "One-sided, alternating, throbbing headaches. 13 days per month, severity 9/10"
    },
    {
      "name": "photophobia",
      "severity": "moderate",
      "duration_days": 365,
      "description": "Light sensitivity during episodes"
    },
    {
      "name": "phonophobia",
      "severity": "moderate",
      "duration_days": 365,
      "description": "Sound sensitivity during episodes"
    }
  ],
  "vital_signs": {
    "bp_systolic": 120,
    "bp_diastolic": 69,
    "heart_rate": 51,
    "temperature": 37.0
  },
  "chief_complaint": "Chronic severe headaches occurring 13 days per month"
}
```

**請求欄位說明**：

| 欄位 | 類型 | 必填 | 說明 |
|------|------|------|------|
| `patient_info.age` | integer | ✅ | 病患年齡（0-120） |
| `patient_info.gender` | string | ✅ | 性別（male, female, other） |
| `patient_info.medical_history` | array | ❌ | 病史清單 |
| `patient_info.current_medications` | array | ❌ | 目前用藥清單 |
| `patient_info.allergies` | array | ❌ | 過敏史清單 |
| `symptoms` | array | ✅ | 症狀清單（至少 1 個） |
| `symptoms[].name` | string | ✅ | 症狀名稱 |
| `symptoms[].severity` | string | ✅ | 嚴重程度（mild, moderate, severe） |
| `symptoms[].duration_days` | integer | ✅ | 持續天數 |
| `symptoms[].description` | string | ❌ | 症狀描述 |
| `vital_signs.bp_systolic` | integer | ❌ | 收縮壓（mmHg） |
| `vital_signs.bp_diastolic` | integer | ❌ | 舒張壓（mmHg） |
| `vital_signs.heart_rate` | integer | ❌ | 心跳（bpm） |
| `vital_signs.temperature` | float | ❌ | 體溫（°C） |
| `chief_complaint` | string | ✅ | 主訴 |

**回應範例**（200 OK）：

```json
{
  "case_id": "550e8400-e29b-41d4-a716-446655440000",
  "diagnosis": [
    {
      "condition": "Chronic Migraine without Aura",
      "confidence": 0.85,
      "reasoning": "Throbbing, one-sided headache occurring 13 days/month with photophobia and phonophobia. Duration >3 months meets ICHD-3 criteria for chronic migraine."
    },
    {
      "condition": "Medication Overuse Headache",
      "confidence": 0.40,
      "reasoning": "Long history of chronic pain may indicate analgesic overuse. Requires medication diary review."
    },
    {
      "condition": "Intracranial Mass (to be excluded)",
      "confidence": 0.15,
      "reasoning": "History of ependymoma requires periodic imaging surveillance despite low current suspicion."
    }
  ],
  "recommendations": [
    "Continue anti-CGRP monoclonal antibody trial for at least 3 months",
    "Consider prophylactic therapy if >4 migraine episodes per month",
    "Triptan medication within 2 hours of onset for acute episodes",
    "Avoid analgesic overuse (<10 days per month)"
  ],
  "risk_factors": [
    "History of ependymoma (brain tumor, surgically removed at age 30)",
    "Post-surgical weak neck muscles may affect cervical stability",
    "Chronic migraine for >20 years increases risk of medication overuse"
  ],
  "next_steps": [
    "Maintain headache diary tracking frequency, severity, triggers, and medication use",
    "Follow-up in 4 weeks to assess anti-CGRP trial efficacy",
    "Schedule MRI if no imaging within past 12 months (due to tumor history)",
    "Consider referral to headache specialist if refractory to current treatment"
  ]
}
```

**回應欄位說明**：

| 欄位 | 類型 | 說明 |
|------|------|------|
| `case_id` | string | 病例唯一識別碼（UUID v4） |
| `diagnosis` | array | 鑑別診斷清單（依信心分數降序排列） |
| `diagnosis[].condition` | string | 疾病名稱 |
| `diagnosis[].confidence` | float | 信心分數（0.0-0.85，上限 85%） |
| `diagnosis[].reasoning` | string | 診斷理由 |
| `recommendations` | array | 治療建議清單 |
| `risk_factors` | array | 風險因子清單 |
| `next_steps` | array | 後續步驟建議 |

**Python 範例**：

```python
import requests
import json

# API 設定
API_BASE_URL = "https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod"
JWT_TOKEN = "REDACTED"

headers = {
    "Authorization": f"Bearer {JWT_TOKEN}",
    "Content-Type": "application/json"
}

# 病患資料
patient_data = {
    "patient_info": {
        "age": 45,
        "gender": "female",
        "medical_history": ["Chronic migraine since age 22"],
        "current_medications": ["Anti-CGRP antibodies"],
        "allergies": []
    },
    "symptoms": [
        {
            "name": "throbbing headache",
            "severity": "severe",
            "duration_days": 365,
            "description": "One-sided, 13 days/month, severity 9/10"
        }
    ],
    "vital_signs": {
        "bp_systolic": 120,
        "bp_diastolic": 69,
        "heart_rate": 51,
        "temperature": 37.0
    },
    "chief_complaint": "Chronic severe headaches"
}

# 發送請求
response = requests.post(
    f"{API_BASE_URL}/api/v1/diagnosis",
    headers=headers,
    json=patient_data,
    timeout=30
)

# 處理回應
if response.status_code == 200:
    result = response.json()
    print(f"Case ID: {result['case_id']}")
    print(f"\nTop Diagnosis: {result['diagnosis'][0]['condition']}")
    print(f"Confidence: {result['diagnosis'][0]['confidence']*100}%")
    print(f"\nRecommendations:")
    for rec in result['recommendations']:
        print(f"  - {rec}")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
```

---

### 3. 藥物交互作用檢查

#### `POST /api/v1/drug-interactions`

檢查多種藥物之間的交互作用。

**請求 Body**：

```json
{
  "medications": [
    "warfarin",
    "aspirin",
    "levodopa"
  ]
}
```

**回應範例**（200 OK）：

```json
{
  "medication_count": 3,
  "medications_checked": [
    "warfarin",
    "aspirin",
    "levodopa"
  ],
  "interactions_found": 1,
  "interactions": [
    {
      "drug_1": "warfarin",
      "drug_2": "aspirin",
      "severity": "contraindicated",
      "description": "Concurrent use significantly increases bleeding risk. Warfarin inhibits vitamin K-dependent clotting factors while aspirin inhibits platelet aggregation.",
      "recommendation": "Avoid combination unless absolutely necessary. If combined, closely monitor INR and watch for bleeding signs (melena, hematuria, bruising). Consider alternative antiplatelet agents."
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

**嚴重程度分級**：

| 等級 | 說明 | 處理建議 |
|------|------|----------|
| `contraindicated` | 禁忌併用 | 絕對避免同時使用 |
| `severe` | 嚴重交互作用 | 需調整劑量或密切監測 |
| `moderate` | 中度交互作用 | 注意監測與追蹤 |
| `minor` | 輕微交互作用 | 臨床意義不大 |

**Python 範例**：

```python
import requests

API_BASE_URL = "https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod"
JWT_TOKEN = "your_jwt_token_here"

headers = {
    "Authorization": f"Bearer {JWT_TOKEN}",
    "Content-Type": "application/json"
}

# 藥物清單
medications = {
    "medications": ["warfarin", "aspirin", "levodopa"]
}

response = requests.post(
    f"{API_BASE_URL}/api/v1/drug-interactions",
    headers=headers,
    json=medications,
    timeout=10
)

if response.status_code == 200:
    result = response.json()
    print(f"檢查 {result['medication_count']} 種藥物")
    print(f"發現 {result['interactions_found']} 個交互作用\n")

    for interaction in result['interactions']:
        print(f"⚠️ {interaction['drug_1']} ⚡ {interaction['drug_2']}")
        print(f"   嚴重程度: {interaction['severity']}")
        print(f"   說明: {interaction['description']}")
        print(f"   建議: {interaction['recommendation']}\n")
```

**支援的藥物清單**（14 種）：

```
抗凝血/抗血小板：
- warfarin（華法林）
- aspirin（阿斯匹靈）
- clopidogrel（保栓通）

抗癲癇藥物：
- carbamazepine（卡巴氮平）
- phenytoin（苯妥英鈉）
- valproic acid（丙戊酸）
- levetiracetam（樂命達）

帕金森氏症用藥：
- levodopa（左旋多巴）
- MAO-B inhibitors（單胺氧化酶 B 抑制劑）

偏頭痛用藥：
- ergotamine（麥角胺）
- triptans（翠普登類）

其他：
- amitriptyline（阿米替林）
- baclofen（巴氯芬）
- diazepam（地西泮）
```

---

### 4. 醫學影像上傳與分析

#### `POST /api/v1/upload-image`

上傳醫學影像（MRI、CT、X-ray）並取得 AI 分析結果。

**請求標頭**：

```http
POST /api/v1/upload-image HTTP/1.1
Host: 1w80v6fnw1.execute-api.us-east-1.amazonaws.com
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW
Authorization: Bearer REDACTED
```

**請求 Body**（multipart/form-data）：

```
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="file"; filename="brain_mri_t1.jpg"
Content-Type: image/jpeg

[Binary Image Data]
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

**支援的檔案格式**：
- `.jpg` / `.jpeg`（JPEG 影像）
- `.png`（PNG 影像）
- `.dcm`（DICOM 醫學影像格式）

**檔案大小限制**：10 MB

**回應範例**（200 OK）：

```json
{
  "image_id": "img-550e8400-e29b-41d4-a716-446655440000",
  "file_name": "brain_mri_t1.jpg",
  "file_size": 2457600,
  "upload_time": "2025-10-13T14:32:15Z",
  "analysis_result": {
    "image_type": "MRI T1-weighted",
    "findings": [
      "Brain parenchyma: No abnormal signal detected",
      "Ventricular system: Normal size, no enlargement or shift",
      "Midline structures: No deviation",
      "Suspicious lesions: None identified"
    ],
    "recommendations": [
      "Image quality is good for diagnostic purposes",
      "No acute abnormalities detected",
      "Final interpretation should be performed by board-certified radiologist"
    ],
    "confidence": 0.75
  },
  "s3_url": "s3://neuroagent-images-100939136870-us-east-1/img-550e8400.jpg"
}
```

**Python 範例**：

```python
import requests

API_BASE_URL = "https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod"
JWT_TOKEN = "your_jwt_token_here"

headers = {
    "Authorization": f"Bearer {JWT_TOKEN}"
}

# 開啟影像檔案
with open("brain_mri_t1.jpg", "rb") as image_file:
    files = {
        "file": ("brain_mri_t1.jpg", image_file, "image/jpeg")
    }

    response = requests.post(
        f"{API_BASE_URL}/api/v1/upload-image",
        headers=headers,
        files=files,
        timeout=60  # 影像分析需要較長時間
    )

if response.status_code == 200:
    result = response.json()
    print(f"Image ID: {result['image_id']}")
    print(f"檔案大小: {result['file_size']/1024/1024:.2f} MB")
    print(f"\nAI 分析結果:")
    for finding in result['analysis_result']['findings']:
        print(f"  - {finding}")
```

**cURL 範例**：

```bash
curl -X POST \
  https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod/api/v1/upload-image \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -F "file=@brain_mri_t1.jpg"
```

---

### 5. 取得病例清單

#### `GET /api/v1/cases`

取得所有病例的清單（支援分頁）。

**請求參數**（Query Parameters）：

| 參數 | 類型 | 必填 | 預設值 | 說明 |
|------|------|------|--------|------|
| `page` | integer | ❌ | 1 | 頁碼 |
| `limit` | integer | ❌ | 10 | 每頁筆數（1-100） |
| `sort_by` | string | ❌ | `created_at` | 排序欄位（created_at, age, confidence） |
| `order` | string | ❌ | `desc` | 排序方向（asc, desc） |

**請求範例**：

```bash
curl -X GET \
  "https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod/api/v1/cases?page=1&limit=10&sort_by=created_at&order=desc" \
  -H "Authorization: Bearer $JWT_TOKEN"
```

**回應範例**（200 OK）：

```json
{
  "total_cases": 48,
  "page": 1,
  "limit": 10,
  "total_pages": 5,
  "cases": [
    {
      "case_id": "550e8400-e29b-41d4-a716-446655440000",
      "created_at": "2025-10-13T14:32:15Z",
      "patient_age": 45,
      "patient_gender": "female",
      "primary_diagnosis": "Chronic Migraine without Aura",
      "confidence": 0.85
    },
    {
      "case_id": "660f9511-f39c-52e5-b827-557766551111",
      "created_at": "2025-10-12T10:15:30Z",
      "patient_age": 57,
      "patient_gender": "female",
      "primary_diagnosis": "Type 3 Hemiplegic Migraine",
      "confidence": 0.82
    }
  ]
}
```

**Python 範例**：

```python
import requests

API_BASE_URL = "https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod"
JWT_TOKEN = "your_jwt_token_here"

headers = {
    "Authorization": f"Bearer {JWT_TOKEN}"
}

params = {
    "page": 1,
    "limit": 10,
    "sort_by": "created_at",
    "order": "desc"
}

response = requests.get(
    f"{API_BASE_URL}/api/v1/cases",
    headers=headers,
    params=params
)

if response.status_code == 200:
    result = response.json()
    print(f"總共 {result['total_cases']} 筆病例，顯示第 {result['page']} 頁\n")

    for case in result['cases']:
        print(f"Case ID: {case['case_id']}")
        print(f"  病患: {case['patient_age']}歲 {case['patient_gender']}")
        print(f"  診斷: {case['primary_diagnosis']} ({case['confidence']*100}%)")
        print(f"  日期: {case['created_at']}\n")
```

---

### 6. 取得特定病例

#### `GET /api/v1/cases/{case_id}`

取得特定病例的完整資料。

**請求範例**：

```bash
curl -X GET \
  https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod/api/v1/cases/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer $JWT_TOKEN"
```

**回應範例**（200 OK）：

```json
{
  "case_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2025-10-13T14:32:15Z",
  "patient_info": {
    "age": 45,
    "gender": "female",
    "medical_history": ["Chronic migraine since age 22"],
    "current_medications": ["Anti-CGRP antibodies"],
    "allergies": []
  },
  "symptoms": [...],
  "vital_signs": {...},
  "chief_complaint": "Chronic severe headaches",
  "diagnosis": [...],
  "recommendations": [...],
  "risk_factors": [...],
  "next_steps": [...]
}
```

**Python 範例**：

```python
import requests

API_BASE_URL = "https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod"
JWT_TOKEN = "your_jwt_token_here"
CASE_ID = "550e8400-e29b-41d4-a716-446655440000"

headers = {
    "Authorization": f"Bearer {JWT_TOKEN}"
}

response = requests.get(
    f"{API_BASE_URL}/api/v1/cases/{CASE_ID}",
    headers=headers
)

if response.status_code == 200:
    case = response.json()
    print(f"病例 ID: {case['case_id']}")
    print(f"建立時間: {case['created_at']}")
    print(f"主要診斷: {case['diagnosis'][0]['condition']}")
elif response.status_code == 404:
    print("病例不存在")
```

---

## 完整範例：診斷流程

### 範例情境

某醫院急診室，66 歲男性病患突發左側無力、構音障礙。急診醫師需快速鑑別診斷是中風或其他神經疾病。

### 完整 Python 腳本

```python
#!/usr/bin/env python3
"""
NeuroAgent API 完整診斷流程範例
情境：急診室急性神經症狀評估
"""

import requests
import json
import jwt
import datetime
from typing import Dict, Any

# ===== 設定區 =====
API_BASE_URL = "https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod"
JWT_SECRET_KEY = "REDACTED"
JWT_ALGORITHM = "HS256"

# ===== Step 1: 產生 JWT Token =====
def generate_jwt_token(user_id: str, role: str = "doctor") -> str:
    """產生 JWT Token"""
    payload = {
        'user_id': user_id,
        'role': role,
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token

print("Step 1: 產生 JWT Token...")
token = generate_jwt_token("er-physician-001", "doctor")
print(f"✓ Token 已產生: {token[:50]}...\n")

# ===== Step 2: 健康檢查 =====
print("Step 2: 檢查 API 健康狀態...")
health_response = requests.get(f"{API_BASE_URL}/health")
if health_response.status_code == 200:
    health = health_response.json()
    print(f"✓ API 狀態: {health['status']}")
    print(f"✓ Bedrock 連線: {health['services']['bedrock']}\n")
else:
    print("❌ API 健康檢查失敗")
    exit(1)

# ===== Step 3: 準備病患資料 =====
print("Step 3: 準備病患資料...")
patient_case = {
    "patient_info": {
        "age": 66,
        "gender": "male",
        "medical_history": [
            "Chronic obstructive pulmonary disease (COPD)",
            "Atrial fibrillation",
            "Previous ischemic stroke",
            "COVID-19 infection (concurrent)"
        ],
        "current_medications": [
            "COPD medications",
            "Anticoagulants for atrial fibrillation"
        ],
        "allergies": []
    },
    "symptoms": [
        {
            "name": "left-sided weakness",
            "severity": "severe",
            "duration_days": 1,
            "description": "Left upper limb power 2/5, bilateral lower limb power 2/5"
        },
        {
            "name": "facial droop",
            "severity": "mild",
            "duration_days": 1,
            "description": "Mild left facial droop"
        },
        {
            "name": "dysarthria",
            "severity": "moderate",
            "duration_days": 1,
            "description": "Difficulty articulating words"
        },
        {
            "name": "respiratory distress",
            "severity": "severe",
            "duration_days": 1,
            "description": "Oxygen saturation 88-92%, requiring 15L oxygen"
        }
    ],
    "vital_signs": {
        "bp_systolic": 144,
        "bp_diastolic": 76,
        "heart_rate": 92,
        "temperature": 37.0
    },
    "chief_complaint": "Acute onset of left-sided weakness, facial droop, and difficulty speaking"
}

print(f"✓ 病患資料準備完成")
print(f"  年齡: {patient_case['patient_info']['age']} 歲")
print(f"  主訴: {patient_case['chief_complaint']}")
print(f"  症狀數: {len(patient_case['symptoms'])} 個\n")

# ===== Step 4: 發送診斷請求 =====
print("Step 4: 發送診斷請求至 NeuroAgent AI...")
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

diagnosis_response = requests.post(
    f"{API_BASE_URL}/api/v1/diagnosis",
    headers=headers,
    json=patient_case,
    timeout=30
)

if diagnosis_response.status_code == 200:
    result = diagnosis_response.json()
    print(f"✓ 診斷完成！Case ID: {result['case_id']}\n")

    # ===== Step 5: 顯示鑑別診斷 =====
    print("=" * 70)
    print("鑑別診斷結果".center(70))
    print("=" * 70)

    for idx, diagnosis in enumerate(result['diagnosis'], 1):
        print(f"\n{idx}. {diagnosis['condition']}")
        print(f"   信心分數: {diagnosis['confidence']*100:.1f}%")
        print(f"   理由: {diagnosis['reasoning']}")

    # ===== Step 6: 顯示治療建議 =====
    print("\n" + "=" * 70)
    print("治療建議".center(70))
    print("=" * 70)
    for idx, rec in enumerate(result['recommendations'], 1):
        print(f"{idx}. {rec}")

    # ===== Step 7: 顯示風險因子 =====
    print("\n" + "=" * 70)
    print("風險因子".center(70))
    print("=" * 70)
    for idx, risk in enumerate(result['risk_factors'], 1):
        print(f"{idx}. ⚠️ {risk}")

    # ===== Step 8: 顯示後續步驟 =====
    print("\n" + "=" * 70)
    print("後續步驟".center(70))
    print("=" * 70)
    for idx, step in enumerate(result['next_steps'], 1):
        print(f"{idx}. {step}")

    # ===== Step 9: 檢查藥物交互作用 =====
    print("\n" + "=" * 70)
    print("藥物交互作用檢查".center(70))
    print("=" * 70)

    medications = {
        "medications": ["warfarin", "aspirin"]  # 從病患用藥中擷取
    }

    drug_response = requests.post(
        f"{API_BASE_URL}/api/v1/drug-interactions",
        headers=headers,
        json=medications,
        timeout=10
    )

    if drug_response.status_code == 200:
        drug_result = drug_response.json()
        print(f"\n檢查 {drug_result['medication_count']} 種藥物")
        print(f"發現 {drug_result['interactions_found']} 個交互作用\n")

        if drug_result['interactions_found'] > 0:
            for interaction in drug_result['interactions']:
                print(f"❌ {interaction['drug_1']} ⚡ {interaction['drug_2']}")
                print(f"   嚴重程度: {interaction['severity']}")
                print(f"   說明: {interaction['description']}")
                print(f"   建議: {interaction['recommendation']}\n")
        else:
            print("✓ 未發現危險交互作用\n")

    # ===== Step 10: 儲存結果 =====
    print("=" * 70)
    print("儲存診斷報告".center(70))
    print("=" * 70)

    output_filename = f"diagnosis_report_{result['case_id']}.json"
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n✓ 完整診斷報告已儲存至: {output_filename}")

    print("\n" + "=" * 70)
    print("診斷流程完成！".center(70))
    print("=" * 70)

else:
    print(f"❌ 診斷請求失敗: {diagnosis_response.status_code}")
    print(diagnosis_response.text)
```

### 執行範例

```bash
$ python3 neuroagent_diagnosis_example.py

Step 1: 產生 JWT Token...
✓ Token 已產生: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2...

Step 2: 檢查 API 健康狀態...
✓ API 狀態: healthy
✓ Bedrock 連線: connected

Step 3: 準備病患資料...
✓ 病患資料準備完成
  年齡: 66 歲
  主訴: Acute onset of left-sided weakness, facial droop, and difficulty speaking
  症狀數: 4 個

Step 4: 發送診斷請求至 NeuroAgent AI...
✓ 診斷完成！Case ID: 550e8400-e29b-41d4-a716-446655440000

======================================================================
                              鑑別診斷結果
======================================================================

1. Right Frontal Cerebral Infarct (Acute Ischemic Stroke)
   信心分數: 85.0%
   理由: Acute onset of left-sided weakness, facial droop, and dysarthria...

2. Hemorrhagic Stroke
   信心分數: 35.0%
   理由: Need to exclude with CT imaging...

3. Todd's Paralysis (post-seizure)
   信心分數: 10.0%
   理由: Transient weakness after seizure, but no seizure history...

======================================================================
                              治療建議
======================================================================
1. Immediate CT scan to differentiate ischemic vs hemorrhagic stroke
2. Activate stroke code and prepare for potential thrombolysis
3. Maintain blood pressure <185/110 mmHg if thrombolysis considered
4. Monitor oxygen saturation and provide supplemental oxygen

======================================================================
                              風險因子
======================================================================
1. ⚠️ History of previous ischemic stroke increases recurrence risk
2. ⚠️ Atrial fibrillation (cardioembolic source)
3. ⚠️ Concurrent COVID-19 infection (hypercoagulable state)

======================================================================
                              後續步驟
======================================================================
1. Immediate non-contrast CT head
2. Neurology consultation
3. Consider MRI if CT inconclusive
4. Monitor neurological status (NIHSS score)

======================================================================
                            藥物交互作用檢查
======================================================================

檢查 2 種藥物
發現 1 個交互作用

❌ warfarin ⚡ aspirin
   嚴重程度: contraindicated
   說明: Increased bleeding risk
   建議: Avoid combination or monitor INR closely

======================================================================
                            儲存診斷報告
======================================================================

✓ 完整診斷報告已儲存至: diagnosis_report_550e8400-e29b-41d4-a716-446655440000.json

======================================================================
                            診斷流程完成！
======================================================================
```

---

## 錯誤處理

### HTTP 狀態碼

| 狀態碼 | 說明 | 處理建議 |
|--------|------|----------|
| `200 OK` | 請求成功 | 正常處理回應 |
| `400 Bad Request` | 請求格式錯誤或必填欄位缺失 | 檢查請求 JSON 格式與必填欄位 |
| `401 Unauthorized` | JWT Token 無效或過期 | 重新產生 Token |
| `403 Forbidden` | 沒有權限存取資源 | 檢查 Token 的 role 欄位 |
| `404 Not Found` | 資源不存在（如 Case ID 錯誤） | 確認資源 ID 正確 |
| `413 Payload Too Large` | 請求 Body 過大（影像 >10MB） | 壓縮影像或分割請求 |
| `429 Too Many Requests` | 超過速率限制（100 req/min） | 實作重試機制或降低請求頻率 |
| `500 Internal Server Error` | 伺服器內部錯誤 | 重試請求，持續失敗請聯繫支援 |
| `503 Service Unavailable` | 服務暫時無法使用（Bedrock 維護） | 稍後重試 |

### 錯誤回應格式

```json
{
  "detail": "Error message description",
  "status_code": 400,
  "timestamp": "2025-10-13T14:32:15Z"
}
```

### Python 錯誤處理範例

```python
import requests
from requests.exceptions import Timeout, ConnectionError

def diagnose_patient(patient_data: dict, jwt_token: str) -> dict:
    """
    發送診斷請求並處理錯誤
    """
    API_BASE_URL = "https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod"

    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/diagnosis",
            headers=headers,
            json=patient_data,
            timeout=30
        )

        # 檢查 HTTP 狀態碼
        if response.status_code == 200:
            return response.json()

        elif response.status_code == 400:
            error = response.json()
            raise ValueError(f"請求格式錯誤: {error['detail']}")

        elif response.status_code == 401:
            raise PermissionError("JWT Token 無效或過期，請重新產生")

        elif response.status_code == 429:
            raise Exception("超過速率限制，請稍後再試")

        elif response.status_code == 500:
            raise Exception("伺服器內部錯誤，請稍後重試")

        else:
            raise Exception(f"未預期的錯誤: {response.status_code} - {response.text}")

    except Timeout:
        raise TimeoutError("請求逾時（>30 秒），請檢查網路連線")

    except ConnectionError:
        raise ConnectionError("無法連線至 API，請檢查網路設定")

# 使用範例
try:
    result = diagnose_patient(patient_data, jwt_token)
    print(f"診斷成功: {result['diagnosis'][0]['condition']}")
except ValueError as e:
    print(f"輸入錯誤: {e}")
except PermissionError as e:
    print(f"認證失敗: {e}")
except TimeoutError as e:
    print(f"逾時: {e}")
except Exception as e:
    print(f"其他錯誤: {e}")
```

---

## 效能優化

### 1. 啟用 Redis 快取

NeuroAgent 使用 ElastiCache Redis 快取常見查詢結果，可減少 60-70% 的 Bedrock API 呼叫。

```python
# API 自動處理快取，無需額外設定
# 相同病患資料的請求會自動從快取讀取
```

**快取策略**：
- **快取鍵**：基於 `patient_info` + `symptoms` + `vital_signs` 的 SHA-256 雜湊
- **快取時間**：60 分鐘（TTL）
- **快取命中率**：60-70%

### 2. 批次請求

如果需要同時處理多筆病例，使用非同步請求提升效能：

```python
import asyncio
import aiohttp

async def diagnose_patient_async(session, patient_data, jwt_token):
    """非同步診斷請求"""
    url = "https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod/api/v1/diagnosis"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }

    async with session.post(url, headers=headers, json=patient_data) as response:
        return await response.json()

async def batch_diagnose(patient_list, jwt_token):
    """批次診斷多筆病例"""
    async with aiohttp.ClientSession() as session:
        tasks = [
            diagnose_patient_async(session, patient, jwt_token)
            for patient in patient_list
        ]
        results = await asyncio.gather(*tasks)
        return results

# 使用範例
patient_list = [patient1, patient2, patient3]
results = asyncio.run(batch_diagnose(patient_list, jwt_token))
```

### 3. 壓縮請求 Body

對於大型病例資料，啟用 gzip 壓縮：

```python
import gzip
import json

def compress_request(data: dict) -> bytes:
    """壓縮 JSON 資料"""
    json_str = json.dumps(data)
    return gzip.compress(json_str.encode('utf-8'))

headers = {
    "Authorization": f"Bearer {jwt_token}",
    "Content-Type": "application/json",
    "Content-Encoding": "gzip"
}

compressed_data = compress_request(patient_data)

response = requests.post(
    f"{API_BASE_URL}/api/v1/diagnosis",
    headers=headers,
    data=compressed_data
)
```

---

## SDK 與工具

### Python SDK（官方）

```bash
# 安裝（未來發布）
pip install neuroagent-sdk

# 使用範例
from neuroagent import NeuroAgentClient

client = NeuroAgentClient(api_key="your_jwt_token")

result = client.diagnose(
    age=45,
    gender="female",
    symptoms=[
        {"name": "headache", "severity": "severe", "duration_days": 365}
    ],
    chief_complaint="Chronic headaches"
)

print(result.top_diagnosis)
```

### Postman Collection

下載 Postman Collection 快速測試 API：

```
GitHub: https://github.com/thc1006/neuro-agent/tree/main/docs/postman
檔案: NeuroAgent_API_Collection.json
```

### Swagger UI（線上文件）

互動式 API 文件：

```
URL: https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod/docs
```

---

## 安全性最佳實踐

### 1. 保護 JWT Secret Key

```python
# ❌ 錯誤：硬編碼在程式中
JWT_SECRET_KEY = "REDACTED"

# ✅ 正確：使用環境變數
import os
JWT_SECRET_KEY = os.getenv("NEUROAGENT_JWT_SECRET")
```

### 2. 使用 HTTPS

```python
# ❌ 錯誤：使用 HTTP
API_BASE_URL = "http://api.neuroagent.com"

# ✅ 正確：強制 HTTPS
API_BASE_URL = "https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod"
```

### 3. 驗證 SSL 憑證

```python
# ❌ 錯誤：停用 SSL 驗證
response = requests.post(url, verify=False)

# ✅ 正確：啟用 SSL 驗證
response = requests.post(url, verify=True)
```

### 4. 限制 Token 有效期

```python
# ❌ 錯誤：長效 Token（30 天）
exp = datetime.datetime.utcnow() + datetime.timedelta(days=30)

# ✅ 正確：短效 Token（24 小時）
exp = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
```

### 5. 匿名化病患資料

```python
# ❌ 錯誤：包含可識別資訊
patient_data = {
    "patient_info": {
        "name": "王小明",  # ❌ 真實姓名
        "id": "A123456789",  # ❌ 身分證字號
        "phone": "0912-345-678"  # ❌ 電話
    }
}

# ✅ 正確：使用匿名代碼
patient_data = {
    "patient_info": {
        "case_number": "ER-2025-001",  # ✅ 病例編號
        "age": 45,
        "gender": "female"
    }
}
```

---

## 常見問題

### Q1：如何整合至醫院資訊系統（HIS）？

**A**：使用 RESTful API 整合：

```python
# 從 HIS 系統擷取病患資料
patient = his_system.get_patient("ER-2025-001")

# 轉換為 NeuroAgent 格式
neuroagent_data = {
    "patient_info": {
        "age": patient.age,
        "gender": patient.gender,
        "medical_history": patient.medical_history,
        "current_medications": patient.medications
    },
    "symptoms": patient.symptoms,
    "vital_signs": patient.vital_signs,
    "chief_complaint": patient.chief_complaint
}

# 發送至 NeuroAgent
result = neuroagent_client.diagnose(neuroagent_data)

# 寫回 HIS 系統
his_system.update_case(
    case_id="ER-2025-001",
    ai_diagnosis=result['diagnosis'],
    ai_recommendations=result['recommendations']
)
```

---

### Q2：API 有速率限制嗎？

**A**：是的，目前限制為 **100 requests/minute per user**。

如果超過限制，會回傳 `429 Too Many Requests`。

**建議**：實作 exponential backoff 重試機制：

```python
import time

def api_call_with_retry(func, max_retries=3):
    """帶重試機制的 API 呼叫"""
    for attempt in range(max_retries):
        try:
            return func()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"速率限制，等待 {wait_time} 秒後重試...")
                time.sleep(wait_time)
            else:
                raise

    raise Exception("達到最大重試次數")
```

---

### Q3：如何除錯 API 請求？

**A**：啟用請求日誌：

```python
import logging
import http.client as http_client

# 啟用 HTTP 請求日誌
http_client.HTTPConnection.debuglevel = 1
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

# 發送請求（會顯示詳細 HTTP 日誌）
response = requests.post(url, headers=headers, json=data)
```

---

### Q4：如何處理大量影像上傳？

**A**：使用 S3 Presigned URL 直接上傳（未來功能）：

```python
# 未來版本將支援
presigned_url = client.get_upload_url(file_name="brain_mri.jpg")
requests.put(presigned_url, data=open("brain_mri.jpg", "rb"))
```

**目前版本**：透過 `/api/v1/upload-image` 端點上傳，檔案大小限制 10 MB。

---

### Q5：API 回應時間多久？

**A**：平均回應時間：

| 端點 | 平均時間 | p95 時間 | p99 時間 |
|------|----------|----------|----------|
| `/health` | 50 ms | 100 ms | 200 ms |
| `/api/v1/diagnosis` | 800 ms | 1500 ms | 2000 ms |
| `/api/v1/drug-interactions` | 100 ms | 200 ms | 300 ms |
| `/api/v1/upload-image` | 3000 ms | 5000 ms | 8000 ms |

**影響因素**：
- Lambda 冷啟動（首次呼叫 +5 秒）
- Bedrock API 延遲（500-1000 ms）
- Redis 快取命中率（命中時 <100 ms）

---

## 進階主題

### WebSocket 串流（未來功能）

未來版本將支援 WebSocket 串流回應，即時顯示 AI 分析進度：

```python
import websocket

ws = websocket.WebSocket()
ws.connect("wss://api.neuroagent.com/v1/diagnosis/stream")

ws.send(json.dumps(patient_data))

while True:
    response = ws.recv()
    print(f"Progress: {response}")
    if response['status'] == 'completed':
        break
```

---

## 總結

本教學涵蓋了 NeuroAgent API 的完整使用方式，包括：

✅ JWT 認證機制
✅ 7 個主要 API 端點
✅ 完整診斷流程範例
✅ 錯誤處理與效能優化
✅ 安全性最佳實踐

**下一步**：
1. 查閱 [前端使用手冊](./FRONTEND_USER_GUIDE.zh-TW.md)
2. 閱讀 [醫療專業人員快速入門](./MEDICAL_PROFESSIONAL_QUICKSTART.zh-TW.md)
3. 加入 GitHub Discussions 與開發者交流

---

**文檔版本**：1.0.0
**最後更新**：2025年10月13日
**維護者**：NeuroAgent Development Team
**聯絡方式**：https://github.com/thc1006/neuro-agent/issues
