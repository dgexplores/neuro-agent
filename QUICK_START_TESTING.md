# 🚀 快速开始 - 后端 API 测试

## ⚡ 最快的方式（30 秒）

```bash
# 1. 打开命令行，进入项目目录
cd C:\Users\thc1006\Desktop\dev\neuro-agent

# 2. 运行完整测试
python complete_test_suite.py
```

完成！✅

---

## 📝 您现在拥有的测试文件

| 文件 | 用途 | 运行方式 |
|------|------|---------|
| `complete_test_suite.py` | 完整测试（包含JWT） | `python complete_test_suite.py` |
| `run_backend_tests.py` | 自动化测试 | `python run_backend_tests.py` |
| `test_backend_with_curl.sh` | curl 命令测试 | `bash test_backend_with_curl.sh` |
| `test_cases.json` | 所有测试数据 | 参考使用 |
| `TESTING_GUIDE.md` | 详细指南 | 查看文档 |

---

## 🎯 6 个测试案例

```
1. 慢性偏头痛 (35F) → 应返回 Migraine 诊断
2. 急性中风 (68M) → 应返回 Stroke 诊断
3. 癫痫发作 (28F) → 应返回 Seizure 诊断
4. 帕金森病 (72M) → 应返回 Parkinson's 诊断
5. 多发性硬化症 (35F) → 应返回 MS 诊断
```

---

## ✨ 测试结果应该显示

```
[PASS] Case 1: Chronic Migraine
       -> Diagnosis: Migraine with Aura

[PASS] Case 2: Acute Ischemic Stroke
       -> Diagnosis: Acute Ischemic Stroke

[PASS] Case 3: Generalized Seizure
       -> Diagnosis: Generalized Tonic-Clonic Seizure

[PASS] Case 4: Parkinson's Disease
       -> Diagnosis: Parkinson's Disease

[PASS] Case 5: Multiple Sclerosis
       -> Diagnosis: Multiple Sclerosis

SUCCESS: All test cases returned DIFFERENT diagnoses!
```

---

## 🔐 JWT Token 自动生成

`complete_test_suite.py` 自动：
- ✅ 生成有效的 JWT token
- ✅ 添加到 Authorization header
- ✅ 无需手动操作

---

## 📊 测试覆盖范围

✅ **后端 API**
- 健康检查 (无认证)
- 诊断端点 (需要 JWT)
- 所有 5 个测试案例
- 错误处理

✅ **不涉及前端**
- 直接调用 API
- 前端看不到
- 后端日志可见

---

## 💡 提示

### 如果收到 401 错误？
```
原因: JWT token 无效
解决: 使用 complete_test_suite.py（自动生成）
```

### 如果收到 500 错误？
```
原因: 后端错误或 Bedrock 不可用
解决: 检查后端是否运行
      如果本地测试，运行: python -m backend.main
```

### 如果超时？
```
原因: 后端冷启动
解决: 等待 10-30 秒，然后重试
      后续调用会更快
```

### 所有诊断都相同？
```
原因: Bedrock 调用失败，使用回退诊断
解决: 检查 AWS 凭证是否正确配置
```

---

## 🎨 竞赛演示方案

```
1. 准备阶段
   python complete_test_suite.py
   （获取测试输出作为证明）

2. 演示阶段
   展示 5 个不同的病例
   每个都返回不同的诊断
   证明系统不是硬编码的

3. 时间
   每个测试 ~3-5 秒
   总共 ~30 秒
```

---

## 📌 文件位置

所有文件都在项目根目录：
```
C:\Users\thc1006\Desktop\dev\neuro-agent\
├── complete_test_suite.py
├── run_backend_tests.py
├── test_backend_with_curl.sh
├── test_cases.json
├── TESTING_GUIDE.md
└── QUICK_START_TESTING.md (本文件)
```

---

## 🌐 API 端点

```
健康检查（无需认证）:
GET https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod/health

诊断（需要 JWT）:
POST https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod/api/v1/diagnosis

API 文档:
https://1w80v6fnw1.execute-api.us-east-1.amazonaws.com/prod/docs
```

---

## ✅ 检查清单

- [ ] 已运行 `python complete_test_suite.py`
- [ ] 看到 5 个不同的诊断结果
- [ ] HTTP 200 状态码
- [ ] 测试时间 < 30 秒
- [ ] 准备好竞赛演示

---

**🎉 准备就绪！运行测试看看您的系统工作情况吧！**

```bash
python complete_test_suite.py
```
