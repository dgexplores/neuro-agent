# NeuroAgent Backend Testing Guide
## 直接测试后端 API，无需通过前端

---

## 📋 快速开始

### 方式 1: Python 自动化测试（推荐）

最简单、自动化程度最高

**Windows 命令行：**
```bash
cd C:\Users\thc1006\Desktop\dev\neuro-agent
python run_backend_tests.py
```

**输出示例：**
```
[Test] Case 1: Chronic Migraine
Status: 200
Case ID: 550e8400-e29b-41d4-a716-446655440000
Confidence: 75%
Diagnoses (3):
  1. Migraine with Aura (88%)
  2. Tension Headache (45%)
  3. Cluster Headache (25%)

[Test] Case 2: Acute Ischemic Stroke
Status: 200
Confidence: 85%
Diagnoses (3):
  1. Acute Ischemic Stroke (92%)
  2. Hemiplegic Migraine (15%)
  3. ...
```

**优点：**
- ✅ 自动运行所有 5 个测试案例
- ✅ 自动验证不同诊断
- ✅ 自动生成摘要报告
- ✅ 无需手动操作

---

### 方式 2: curl 命令测试

如果您更喜欢看实时命令执行

**Linux/Mac:**
```bash
bash test_backend_with_curl.sh
```

**Windows (Git Bash):**
```bash
bash test_backend_with_curl.sh
```

**或手动运行单个测试：**

#### 健康检查（无需认证）
```bash
curl -X GET "https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod/health"
```

#### 偏头痛诊断
```bash
curl -X POST "https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod/api/v1/diagnosis" \
  -H "Authorization: Bearer REDACTED" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_info": {"age": 35, "gender": "female", "medical_history": [], "current_medications": [], "allergies": []},
    "symptoms": [
      {"name": "throbbing headache", "severity": "severe", "duration_days": 3, "description": ""},
      {"name": "photophobia", "severity": "moderate", "duration_days": 3, "description": ""},
      {"name": "nausea", "severity": "moderate", "duration_days": 3, "description": ""}
    ],
    "vital_signs": {"bp_systolic": 130, "bp_diastolic": 85, "heart_rate": 72, "temperature": 36.8},
    "lab_results": {},
    "imaging_studies": [],
    "chief_complaint": "Severe throbbing headache",
    "history_present_illness": "Acute onset"
  }'
```

#### 中风诊断
```bash
curl -X POST "https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod/api/v1/diagnosis" \
  -H "Authorization: Bearer REDACTED" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_info": {"age": 68, "gender": "male", "medical_history": ["hypertension", "diabetes"], "current_medications": ["lisinopril"], "allergies": []},
    "symptoms": [
      {"name": "acute onset weakness", "severity": "severe", "duration_days": 0, "description": ""},
      {"name": "facial drooping", "severity": "severe", "duration_days": 0, "description": ""},
      {"name": "speech difficulty", "severity": "severe", "duration_days": 0, "description": ""}
    ],
    "vital_signs": {"bp_systolic": 165, "bp_diastolic": 98, "heart_rate": 92, "temperature": 37.2},
    "lab_results": {},
    "imaging_studies": [],
    "chief_complaint": "Sudden weakness and speech difficulty",
    "history_present_illness": "Acute stroke"
  }'
```

#### 癫痫诊断
```bash
curl -X POST "https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod/api/v1/diagnosis" \
  -H "Authorization: Bearer REDACTED" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_info": {"age": 28, "gender": "female", "medical_history": [], "current_medications": [], "allergies": []},
    "symptoms": [
      {"name": "loss of consciousness", "severity": "severe", "duration_days": 0, "description": ""},
      {"name": "muscle convulsions", "severity": "severe", "duration_days": 0, "description": ""},
      {"name": "tongue biting", "severity": "moderate", "duration_days": 0, "description": ""}
    ],
    "vital_signs": {"bp_systolic": 145, "bp_diastolic": 92, "heart_rate": 118, "temperature": 37.5},
    "lab_results": {},
    "imaging_studies": [],
    "chief_complaint": "First seizure",
    "history_present_illness": "Sudden loss of consciousness"
  }'
```

---

### 方式 3: Postman 或 Insomnia

使用图形化 API 工具

#### 导入测试集合：

1. 打开 [Postman](https://www.postman.com/)
2. 创建新集合："NeuroAgent Backend Tests"
3. 添加请求：

**POST 请求 - Migraine**
```
URL: https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod/api/v1/diagnosis
Method: POST
Headers:
  Authorization: Bearer REDACTED
  Content-Type: application/json

Body: (参考上面的 curl 命令中的 JSON)
```

---

## 📊 测试用例列表

您有 6 个不同的测试案例：

| # | 病例 | 年龄 | 性别 | 关键症状 |
|---|------|------|------|---------|
| 1 | 慢性偏头痛 | 35 | 女 | 搏动性头痛、畏光、恶心 |
| 2 | 急性缺血性卒中 | 68 | 男 | 急性无力、面部下垂、言语困难 |
| 3 | 全身强直-阵挛性癫痫 | 28 | 女 | 意识丧失、肌肉抽搐、咬舌 |
| 4 | 帕金森病 | 72 | 男 | 静止性震颤、运动缓慢、僵硬 |
| 5 | 多发性硬化症 | 35 | 女 | 视力模糊、感觉异常、无力 |
| 6 | 阿尔茨海默病 | 78 | 男 | 记忆丧失、认知下降、情绪改变 |

---

## 🔍 验证结果

### ✅ 成功标志：

1. **不同的诊断**
   ```
   Case 1 -> Migraine with Aura
   Case 2 -> Acute Ischemic Stroke
   Case 3 -> Generalized Tonic-Clonic Seizure
   Case 4 -> Parkinson's Disease
   Case 5 -> Multiple Sclerosis
   Case 6 -> Mild Cognitive Impairment
   ```

2. **HTTP 200 响应**
   ```
   Status: 200
   ```

3. **有效的诊断结构**
   ```json
   {
     "case_id": "uuid",
     "diagnosis": [
       {
         "condition": "...",
         "confidence": 0.85,
         "reasoning": "..."
       }
     ],
     "confidence": 0.85,
     "recommendations": [...],
     "risk_factors": [...],
     "next_steps": [...]
   }
   ```

### ❌ 故障迹象：

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| HTTP 401 | 认证令牌无效 | 检查 `Authorization: Bearer` 头 |
| HTTP 400 | 请求格式错误 | 检查 JSON 有效性 |
| HTTP 500 | 服务器错误 | 检查后端日志 |
| 相同诊断 | 硬编码响应 | 您的修复应该已解决此问题 |
| 超时 | 服务冷启动 | 等待 10 秒后重试 |

---

## 🚀 本地测试（可选）

如果您想在本地测试后端：

```bash
# 1. 启动后端
python -m backend.main

# 2. 在新终端中运行测试
# 编辑 run_backend_tests.py，更改 BACKEND_URL 为：
# BACKEND_URL = "http://localhost:8000"

python run_backend_tests.py
```

---

## 📝 文件清单

| 文件 | 用途 | 使用方式 |
|------|------|---------|
| `test_cases.json` | 所有 6 个测试案例的 JSON 数据 | 参考/手动复制 |
| `run_backend_tests.py` | Python 自动化测试脚本 | `python run_backend_tests.py` |
| `test_backend_with_curl.sh` | bash curl 测试脚本 | `bash test_backend_with_curl.sh` |
| `TESTING_GUIDE.md` | 此文档 | 参考 |

---

## 💡 提示

### 前端不会看到这些测试
- ✅ 直接调用后端 API
- ✅ 无需通过前端
- ✅ 后端日志中可见

### 不同病例会返回不同诊断吗？
- ✅ 是！每个测试案例都设计得独特
- ✅ 系统应该返回不同的主诊断
- ✅ 这证明了系统在正确处理不同输入

### 如何在竞赛中使用？
1. 运行 `python run_backend_tests.py` 验证系统
2. 展示输出中不同的诊断结果
3. 证明您的系统不是硬编码的

---

## 📞 故障排除

**Q: 得到 HTTP 401 错误？**
```
A: 检查 Authorization header
   正确: Authorization: Bearer REDACTED
   错误: Authorization: REDACTED (缺少 Bearer)
```

**Q: 得到 HTTP 400 错误？**
```
A: 检查 JSON 格式
   使用在线 JSON 验证器: https://jsonlint.com/
   或使用 Python: python -m json.tool test_cases.json
```

**Q: 后端响应超时？**
```
A: 冷启动延迟
   第一次调用可能需要 10-30 秒
   后续调用会更快（<2 秒）
```

**Q: 所有病例都返回相同诊断？**
```
A: 您的修复可能没有正确部署
   运行: python run_backend_tests.py
   查看是否有错误消息
```

---

## ✨ 下一步

1. **测试系统**：运行 `python run_backend_tests.py`
2. **验证结果**：检查 6 个不同的诊断
3. **展示竞赛**：使用这些结果作为证明

**祝您竞赛顺利！** 🎉

