# language: en
@diagnosis @migraine @critical
Feature: 偏頭痛診斷 (Migraine Diagnosis)
  作為一名神經科醫師
  我希望 NeuroAgent 能夠根據 ICHD-3 診斷標準準確識別偏頭痛
  以便快速做出臨床決策並減少漏診率

  Background: 系統初始化
    Given NeuroAgent 診斷服務已啟動
    And AWS Bedrock 連線正常
    And 醫學知識庫載入完成
    And ICHD-3 偏頭痛診斷標準已載入

  # ============================================================
  # Scenario 1: 正常案例 - 典型無先兆偏頭痛 (Must Have - F1.2)
  # ============================================================
  @positive @high-confidence @ICHD3-compliant
  Scenario: 典型無先兆偏頭痛診斷 - 高信心度
    Given 患者基本資料如下:
      | 欄位     | 值       |
      | age      | 32       |
      | gender   | female   |
      | case_id  | MIG-001  |
    And 患者主訴為 "右側太陽穴搏動性頭痛，持續12小時，伴噁心和畏光"
    And 患者症狀清單包含:
      | symptom_name         | severity | duration_hours | location            | quality     |
      | headache             | 8        | 12             | right frontotemporal| throbbing   |
      | nausea               | 6        | 12             | -                   | -           |
      | photophobia          | 7        | 12             | -                   | -           |
      | phonophobia          | 7        | 12             | -                   | -           |
    And 患者病史包含:
      | 欄位                  | 值                                    |
      | previous_migraine_attacks | 6                                |
      | family_history        | mother has migraine                  |
      | triggers              | stress, menstruation, lack of sleep  |
      | medications           | ibuprofen PRN                        |
    And 患者生命徵象正常:
      | vital_sign          | value  | unit  |
      | blood_pressure      | 118/76 | mmHg  |
      | heart_rate          | 78     | bpm   |
      | temperature         | 36.8   | °C    |
      | respiratory_rate    | 16     | /min  |
    And 患者確認 "頭痛因日常活動加重（如爬樓梯）"
    And 患者無紅旗症狀（無發燒、頸部僵硬、意識改變、神經學缺損）

    When 送出診斷請求到 "POST /api/v1/diagnosis"
    Then API 應在 5 秒內回應成功 (HTTP 200)
    And 診斷結果應包含 3 項鑑別診斷
    And 第一鑑別診斷應為:
      | condition                           | confidence | category      |
      | Migraine without aura (ICHD-3 1.1) | >= 0.85    | Neurological |
    And 診斷依據應包含 ICHD-3 標準:
      """
      符合 ICHD-3 無先兆偏頭痛診斷標準：
      - Criterion A: 病史顯示至少 5 次相似發作 (已有 6 次)
      - Criterion B: 頭痛持續 4-72 小時 (本次 12 小時) ✓
      - Criterion C: 至少符合兩項特徵 (4/4 項符合) ✓
        1. 單側位置 (右側額顳部) ✓
        2. 搏動性質 (throbbing) ✓
        3. 中重度強度 (8/10) ✓
        4. 日常活動加重 (爬樓梯) ✓
      - Criterion D: 至少符合一項伴隨症狀 (3/3 項符合) ✓
        1. 噁心 (有)
        2. 畏光 (有)
        3. 畏聲 (有)
      """
    And 第二鑑別診斷應為:
      | condition                    | confidence | category      |
      | Tension-type headache        | 0.10-0.15  | Neurological |
    And 第三鑑別診斷應為:
      | condition                    | confidence | category      |
      | Medication overuse headache  | 0.05-0.08  | Neurological |
    And 建議應包含:
      | recommendation_type | content                                                |
      | treatment           | 考慮給予 triptan 類藥物（如 sumatriptan 100mg）        |
      | prophylaxis         | 發作頻率 >2 次/月，建議預防性治療（如 propranolol）   |
      | lifestyle           | 建立頭痛日記、規律睡眠、避免已知誘發因素               |
      | follow_up           | 2 週內門診追蹤評估治療效果                             |
    And 風險警示應為空（無紅旗症狀）
    And 回應應包含信心度元數據:
      | metadata_key              | expected_value |
      | confidence_score          | >= 0.85        |
      | evidence_strength         | strong         |
      | criteria_met_percentage   | 100%           |
      | red_flags_detected        | 0              |
    And 診斷結果應儲存至 DynamoDB "NeuroAgent-PatientCases" 表格
    And case_id "MIG-001" 應可查詢且狀態為 "completed"

  # ============================================================
  # Scenario 2: 錯誤輸入驗證 (Must Have - F1.1)
  # ============================================================
  @negative @validation @error-handling
  Scenario: 無效輸入 - 缺少必填欄位與數據驗證失敗
    Given 患者基本資料不完整:
      | 欄位     | 值          | 預期錯誤         |
      | age      | -5          | 年齡必須 0-120   |
      | gender   | unknown     | 無效的性別枚舉   |
      | case_id  | MIG-ERR-001 | (有效)           |
    And 患者主訴為空字串 ""
    And 患者症狀清單為空陣列 []
    And 患者病史缺少關鍵欄位:
      | 欄位                  | 狀態   |
      | previous_attacks      | null   |
      | medications           | null   |
    And 患者生命徵象包含無效數值:
      | vital_sign          | value     | 預期錯誤              |
      | blood_pressure      | 999/999   | 超出正常範圍 (60-200) |
      | heart_rate          | -10       | 心率必須 > 0          |
      | temperature         | "高燒"    | 必須為數值型態        |
      | respiratory_rate    | null      | 缺少呼吸速率          |

    When 送出診斷請求到 "POST /api/v1/diagnosis"
    Then API 應在 2 秒內回應錯誤 (HTTP 422 Unprocessable Entity)
    And 錯誤訊息應包含 "Validation Error"
    And 錯誤詳情應列出所有驗證失敗項目:
      """
      {
        "detail": [
          {
            "loc": ["body", "patient_info", "age"],
            "msg": "年齡必須在 0-120 之間",
            "type": "value_error.number.not_range"
          },
          {
            "loc": ["body", "patient_info", "gender"],
            "msg": "性別必須為 male, female, other 之一",
            "type": "value_error.enum"
          },
          {
            "loc": ["body", "chief_complaint"],
            "msg": "主訴不可為空",
            "type": "value_error.missing"
          },
          {
            "loc": ["body", "symptoms"],
            "msg": "症狀清單至少需包含 1 項症狀",
            "type": "value_error.list.min_items"
          },
          {
            "loc": ["body", "vital_signs", "blood_pressure"],
            "msg": "收縮壓必須在 60-200 mmHg 之間",
            "type": "value_error.number.not_range"
          },
          {
            "loc": ["body", "vital_signs", "heart_rate"],
            "msg": "心率必須為正數",
            "type": "value_error.number.not_gt"
          },
          {
            "loc": ["body", "vital_signs", "temperature"],
            "msg": "體溫必須為數值型態",
            "type": "type_error.float"
          }
        ]
      }
      """
    And 回應標頭應包含 "X-Validation-Failed: true"
    And 不應產生 DynamoDB 記錄
    And CloudWatch 應記錄 "ValidationError" 日誌事件
    And 錯誤回應應包含建議修正方式:
      | field                     | suggested_fix                              |
      | age                       | 請輸入有效年齡 (0-120)                     |
      | gender                    | 請選擇 male/female/other                   |
      | chief_complaint           | 請輸入患者主訴 (至少 10 字元)             |
      | symptoms                  | 請至少勾選 1 項症狀                        |
      | vital_signs.heart_rate    | 請輸入正數心率值 (典型範圍 40-200 bpm)    |

  # ============================================================
  # Scenario 3: 紅旗症狀檢測 - 應排除偏頭痛 (Should Have - F1.8)
  # ============================================================
  @negative @red-flag @critical-alert
  Scenario: 雷擊頭痛 - 應警示可能為蜘蛛膜下腔出血而非偏頭痛
    Given 患者基本資料如下:
      | 欄位     | 值       |
      | age      | 58       |
      | gender   | male     |
      | case_id  | SAH-001  |
    And 患者主訴為 "突然劇烈頭痛，像被雷擊，1分鐘內達到最高峰"
    And 患者症狀清單包含紅旗症狀:
      | symptom_name         | severity | onset_speed | location    | quality                |
      | sudden_severe_headache | 10     | <1 minute   | diffuse     | worst headache of life |
      | neck_stiffness       | 7        | 5 minutes   | neck        | rigid                  |
      | photophobia          | 9        | 2 minutes   | -           | -                      |
      | confusion            | 5        | 10 minutes  | -           | disoriented            |
    And 患者病史顯示:
      | 欄位                  | 值                    |
      | previous_attacks      | 0 (首次發作)          |
      | risk_factors          | hypertension, smoking |
      | medications           | amlodipine 5mg daily  |
    And 患者生命徵象異常:
      | vital_sign          | value  | unit  | status   |
      | blood_pressure      | 178/102| mmHg  | elevated |
      | heart_rate          | 105    | bpm   | elevated |
      | temperature         | 37.2   | °C    | normal   |
      | GCS_score           | 14     | -     | decreased|
    And 神經學檢查發現 "頸部僵硬陽性 (positive meningismus)"

    When 送出診斷請求到 "POST /api/v1/diagnosis"
    Then API 應在 5 秒內回應成功 (HTTP 200)
    And 應觸發緊急警示標誌 "CRITICAL_RED_FLAG_DETECTED"
    And 第一鑑別診斷應為:
      | condition                          | confidence | category   | urgency  |
      | Subarachnoid hemorrhage (SAH)      | 0.75-0.85  | Emergency  | CRITICAL |
    And 第二鑑別診斷應為:
      | condition                          | confidence | category   | urgency  |
      | Meningitis                         | 0.10-0.15  | Emergency  | CRITICAL |
    And 第三鑑別診斷應為:
      | condition                          | confidence | category   | urgency  |
      | Cerebral venous thrombosis         | 0.05-0.08  | Emergency  | HIGH     |
    And Migraine 應 NOT 出現在鑑別診斷清單中
    And 紅旗症狀警示應包含:
      """
      🚨 CRITICAL RED FLAGS DETECTED - IMMEDIATE ACTION REQUIRED 🚨

      檢測到以下危急症狀：
      1. ⚠️ 雷擊頭痛 (Thunderclap onset <1 min) - 蜘蛛膜下腔出血特徵
      2. ⚠️ 首次發作且年齡 >50 歲 - 腦部病變風險增加
      3. ⚠️ 頸部僵硬 - 疑似腦膜刺激症狀
      4. ⚠️ 意識混亂 (GCS 14) - 顱內壓升高可能
      5. ⚠️ 血壓顯著升高 (178/102) - 惡性高血壓或顱內出血

      建議立即處置：
      - 🚑 立即啟動急診綠色通道
      - 🧠 優先安排非顯影劑頭部 CT 掃描 (<30 分鐘)
      - 💉 若 CT 陰性，考慮腰椎穿刺檢查 CSF 黃變 (xanthochromia)
      - 📞 通知神經外科會診待命
      - 🩺 持續監測生命徵象與神經學狀態
      - ⏱️ 時間窗關鍵 - 延遲診斷增加死亡率

      ⚠️ 此案例不符合偏頭痛診斷標準，切勿以偏頭痛治療
      """
    And 建議應包含緊急處置流程:
      | action_priority | action_type      | action_detail                              | time_frame  |
      | 1               | emergency_imaging| Non-contrast head CT                       | <30 minutes |
      | 2               | consultation     | Neurosurgery on-call alert                 | <15 minutes |
      | 3               | lab_work         | CBC, coagulation profile, troponin        | STAT        |
      | 4               | monitoring       | Continuous vital signs + neuro checks Q15min| ongoing    |
      | 5               | lumbar_puncture  | If CT negative - check xanthochromia      | <6 hours    |
    And 信心度元數據應反映緊急性:
      | metadata_key              | expected_value        |
      | confidence_score          | 0.75-0.85             |
      | red_flags_detected        | 5                     |
      | urgency_level             | CRITICAL              |
      | safe_to_discharge         | false                 |
      | requires_imaging          | true (emergent)       |
      | differential_includes_migraine | false            |
    And 診斷結果應儲存並標記為 "high_priority"
    And 應觸發自動通知給值班醫師
    And CloudWatch Alarm "RedFlagDetected" 應被觸發

  # ============================================================
  # Scenario Outline: 偏頭痛信心度分級測試 (Should Have - F1.2)
  # ============================================================
  @parameterized @confidence-scoring
  Scenario Outline: 不同臨床表現下的偏頭痛診斷信心度
    Given 患者年齡為 <age> 歲，性別為 <gender>
    And 既往偏頭痛發作次數為 <previous_attacks> 次
    And 頭痛持續 <duration_hours> 小時
    And 符合 ICHD-3 Criterion C 項數為 <criterion_c_met> 項
    And 符合 ICHD-3 Criterion D 項數為 <criterion_d_met> 項
    And 紅旗症狀數量為 <red_flags_count> 個

    When 送出診斷請求到 "POST /api/v1/diagnosis"
    Then API 應成功回應 (HTTP 200)
    And 偏頭痛診斷信心度應在 <expected_confidence_range> 範圍內
    And 診斷品質評級應為 "<quality_rating>"

    Examples: 信心度分級測試案例
      | case_description        | age | gender | previous_attacks | duration_hours | criterion_c_met | criterion_d_met | red_flags_count | expected_confidence_range | quality_rating     |
      | 典型高信心              | 35  | female | 8                | 18             | 4               | 2               | 0               | 0.85-0.95                 | Very High          |
      | 高信心                  | 28  | female | 5                | 12             | 3               | 2               | 0               | 0.70-0.85                 | High               |
      | 中等信心-少一項         | 42  | male   | 4                | 8              | 2               | 2               | 0               | 0.55-0.70                 | Moderate/Probable  |
      | 中低信心-初診且少標準   | 25  | female | 2                | 6              | 2               | 1               | 0               | 0.40-0.55                 | Low-Moderate       |
      | 低信心-首發             | 52  | male   | 1                | 4              | 2               | 1               | 0               | 0.30-0.45                 | Low/Uncertain      |
      | 極低信心-紅旗症狀       | 65  | male   | 0                | 0.5            | 1               | 0               | 3               | <0.30                     | Very Low/Alternative|

  # ============================================================
  # Scenario: 藥物過度使用性頭痛鑑別 (Should Have - F2.4)
  # ============================================================
  @differential @drug-interaction @medication-history
  Scenario: 慢性偏頭痛患者懷疑藥物過度使用性頭痛 (MOH)
    Given 患者基本資料如下:
      | 欄位     | 值       |
      | age      | 45       |
      | gender   | female   |
      | case_id  | MOH-001  |
    And 患者主訴為 "幾乎每天頭痛，持續3個月，止痛藥越吃越多"
    And 患者症狀清單顯示慢性化:
      | symptom_name         | frequency         | duration_days | pattern       |
      | daily_headache       | 20+ days/month    | 90            | chronic       |
      | medication_escalation| increasing use    | 90            | progressive   |
    And 患者病史顯示:
      | 欄位                  | 值                                           |
      | previous_attacks      | 15 years of episodic migraine                |
      | medication_history    | acetaminophen+caffeine daily for 6 months    |
      | frequency_change      | from 2-3 attacks/month to 20+ days/month     |
    And 患者用藥記錄顯示過度使用:
      | medication                  | frequency         | duration_months | overuse_criteria_met |
      | acetaminophen 500mg + caffeine| 15+ days/month | 6               | Yes (>15 days/month) |
      | ibuprofen 400mg             | 10+ days/month    | 4               | Yes (>15 days/month) |
      | sumatriptan 100mg           | 8+ days/month     | 3               | Yes (>10 days/month) |

    When 送出診斷請求到 "POST /api/v1/diagnosis" 並同時觸發 "POST /api/v1/drug-interaction-check"
    Then API 應成功回應 (HTTP 200)
    And 第一鑑別診斷應為:
      | condition                                    | confidence | category      |
      | Medication overuse headache (MOH, ICHD-3 8.2)| 0.80-0.90  | Neurological |
    And 第二鑑別診斷應為:
      | condition                                    | confidence | category      |
      | Chronic migraine (ICHD-3 1.3)                | 0.70-0.80  | Neurological |
    And 診斷依據應包含 MOH 標準:
      """
      符合藥物過度使用性頭痛診斷標準 (ICHD-3 8.2)：
      - Criterion A: 頭痛 ≥15 天/月 (目前 20+ 天/月) ✓
      - Criterion B: 既往有偏頭痛病史 (15 年) ✓
      - Criterion C: 規律過度使用急性/症狀性頭痛藥物 >3 個月 ✓
        * 簡單止痛藥 ≥15 天/月: acetaminophen (15+ days) ✓
        * NSAIDs ≥15 天/月: ibuprofen (10+ days) ✓
        * Triptans ≥10 天/月: sumatriptan (8+ days) ✓
      """
    And 藥物交互檢查應回傳警告:
      | interaction_type      | severity | message                                      |
      | medication_overuse    | HIGH     | 檢測到 3 種頭痛藥物過度使用，符合 MOH 診斷標準 |
      | rebound_headache_risk | HIGH     | 簡單止痛藥使用 >15 天/月 達 6 個月            |
      | triptan_overuse       | MODERATE | Triptan 使用 >10 天/月 達 3 個月              |
    And 建議應包含停藥與預防治療:
      | recommendation_type   | content                                                        |
      | withdrawal_plan       | 建議完全停用所有急性頭痛藥物 2 個月（withdrawal period）       |
      | bridge_therapy        | 考慮短期使用類固醇或抗嘔吐藥緩解停藥症狀                       |
      | prophylaxis_start     | 同時開始預防性治療：Topiramate 25mg qd 逐步增量至 100mg bid   |
      | behavioral_therapy    | 轉介頭痛門診，搭配認知行為療法 (CBT)                           |
      | patient_education     | 衛教藥物過度使用風險，建立頭痛日記限制止痛藥使用               |
      | follow_up_schedule    | 停藥後 2 週、1 個月、2 個月追蹤頭痛頻率與嚴重度變化             |
    And 應產生藥物使用報告供病歷參考

  # ============================================================
  # Scenario: 性能與回應時間驗證 (Non-Functional Requirement)
  # ============================================================
  @performance @non-functional @SLA
  Scenario: 偏頭痛診斷 API 回應時間必須符合 SLA 要求
    Given 系統負載為正常狀態 (並發用戶 <50)
    And AWS Bedrock API quota 剩餘 >10%
    And Lambda 函式已處於溫啟動狀態 (warm start)
    And 患者資料包含完整的偏頭痛症狀 (參照 Scenario 1)

    When 送出診斷請求到 "POST /api/v1/diagnosis"
    And 記錄以下時間戳:
      | timestamp_name          | description                      |
      | t0_request_sent         | 客戶端送出請求時間               |
      | t1_api_gateway_received | API Gateway 接收請求時間         |
      | t2_lambda_invoked       | Lambda 函式開始執行時間          |
      | t3_bedrock_call_start   | Bedrock API 呼叫開始時間         |
      | t4_bedrock_call_end     | Bedrock API 回應完成時間         |
      | t5_dynamo_write_start   | DynamoDB 寫入開始時間            |
      | t6_dynamo_write_end     | DynamoDB 寫入完成時間            |
      | t7_response_returned    | Lambda 回傳結果時間              |
      | t8_client_received      | 客戶端接收回應時間               |

    Then 總回應時間 (t8 - t0) 應 ≤5 秒 (warm start)
    And Bedrock API 呼叫時間 (t4 - t3) 應 ≤3 秒
    And DynamoDB 寫入時間 (t6 - t5) 應 ≤500 毫秒
    And API Gateway 延遲 (t1 - t0) 應 ≤200 毫秒
    And Lambda 執行時間 (t7 - t2) 應 ≤4 秒
    And 回應應包含效能元數據:
      | metadata_key              | max_acceptable_value |
      | total_latency_ms          | 5000                 |
      | bedrock_latency_ms        | 3000                 |
      | dynamodb_latency_ms       | 500                  |
      | lambda_execution_time_ms  | 4000                 |
    And CloudWatch Metrics 應記錄效能指標以供 SLA 監控

  # ============================================================
  # Scenario: 多語系支援 - 繁體中文輸出 (Could Have - F1.10)
  # ============================================================
  @i18n @localization @traditional-chinese
  Scenario: 偏頭痛診斷結果應以繁體中文呈現
    Given 患者使用繁體中文介面 (locale="zh-TW")
    And 患者輸入症狀使用中文醫療術語:
      | symptom_zh                | symptom_en          |
      | 單側搏動性頭痛            | unilateral throbbing headache |
      | 噁心嘔吐                  | nausea and vomiting |
      | 畏光畏聲                  | photophobia and phonophobia |
    And API 請求標頭包含 "Accept-Language: zh-TW"

    When 送出診斷請求到 "POST /api/v1/diagnosis"
    Then 診斷結果應以繁體中文回傳
    And 診斷名稱應為 "無先兆偏頭痛 (Migraine without aura)"
    And 診斷依據應使用繁體中文醫學術語:
      """
      符合國際頭痛疾病分類第三版 (ICHD-3) 無先兆偏頭痛診斷標準：
      - 標準 A：至少五次符合標準 B-D 的發作
      - 標準 B：頭痛持續 4-72 小時（未經治療或治療無效）
      - 標準 C：頭痛至少具備以下兩項特徵：
        1. 單側位置
        2. 搏動性質
        3. 中度或重度疼痛強度
        4. 日常身體活動（如步行或爬樓梯）會加重或導致避免此類活動
      - 標準 D：頭痛期間至少有下列一項：
        1. 噁心和/或嘔吐
        2. 畏光和畏聲
      """
    And 治療建議應使用繁體中文:
      | recommendation_zh                                       |
      | 建議給予翠普登類藥物（如舒馬曲普坦 100 毫克）            |
      | 發作頻率超過每月兩次，建議使用預防性治療（如普洛帕諾爾） |
      | 建立頭痛日記，記錄誘發因素與治療反應                     |
    And 所有欄位標籤應為繁體中文:
      | field_en            | field_zh       |
      | diagnosis           | 診斷           |
      | confidence          | 信心度         |
      | recommendations     | 建議           |
      | red_flags           | 危險徵兆       |
      | follow_up           | 追蹤           |
    And 回應不應包含簡體中文字元

# ============================================================
# Tags 說明
# ============================================================
# @diagnosis - 診斷相關測試
# @migraine - 偏頭痛專項測試
# @critical - 關鍵路徑測試（必須通過）
# @positive - 正向測試案例（預期成功）
# @negative - 負向測試案例（預期失敗/錯誤處理）
# @validation - 輸入驗證測試
# @error-handling - 錯誤處理測試
# @high-confidence - 高信心度診斷測試
# @ICHD3-compliant - 符合 ICHD-3 標準的測試
# @red-flag - 紅旗症狀檢測測試
# @critical-alert - 緊急警示測試
# @parameterized - 參數化測試
# @confidence-scoring - 信心度評分測試
# @differential - 鑑別診斷測試
# @drug-interaction - 藥物交互作用測試
# @medication-history - 用藥史相關測試
# @performance - 效能測試
# @non-functional - 非功能性需求測試
# @SLA - 服務等級協議測試
# @i18n - 國際化測試
# @localization - 在地化測試
# @traditional-chinese - 繁體中文測試

# ============================================================
# 驗收標準 (Acceptance Criteria)
# ============================================================
# 1. 所有 @critical 標記的 Scenario 必須 100% 通過
# 2. Scenario 1 (正常案例) 必須達成 Top-1 accuracy ≥85%
# 3. Scenario 2 (錯誤輸入) 必須正確回傳所有驗證錯誤
# 4. Scenario 3 (紅旗症狀) 必須正確排除偏頭痛診斷並觸發緊急警示
# 5. 所有診斷結果必須符合 ICHD-3 診斷標準
# 6. API 回應時間必須符合效能 SLA（warm start ≤5 秒）
# 7. 藥物過度使用檢測準確率 ≥90%
# 8. 繁體中文在地化覆蓋率 100%（所有欄位與訊息）

# ============================================================
# 測試執行指令
# ============================================================
# 執行所有偏頭痛診斷測試：
#   behave backend/tests/bdd/features/migraine_diagnosis.feature
#
# 執行關鍵路徑測試：
#   behave --tags=critical backend/tests/bdd/features/migraine_diagnosis.feature
#
# 執行正向測試案例：
#   behave --tags=positive backend/tests/bdd/features/migraine_diagnosis.feature
#
# 執行效能測試：
#   behave --tags=performance backend/tests/bdd/features/migraine_diagnosis.feature
#
# 產生 HTML 測試報告：
#   behave -f html -o reports/migraine_diagnosis_report.html backend/tests/bdd/features/migraine_diagnosis.feature
