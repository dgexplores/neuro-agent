/**
 * NeuroAgent Demo Video Script
 *
 * Automated Playwright test for recording 3-minute demo video
 *
 * Demo Workflow:
 * 1. Landing page introduction (20 seconds)
 * 2. Navigate to diagnosis page and input patient case (60 seconds)
 * 3. Display diagnosis results with AI analysis (60 seconds)
 * 4. View case history page (40 seconds)
 *
 * Total Duration: ~3 minutes
 *
 * Usage:
 *   # Install dependencies
 *   npm install -D @playwright/test
 *
 *   # Run with video recording
 *   npx playwright test demo.spec.ts --headed --video=on
 *
 *   # Run with slow motion for better visualization
 *   npx playwright test demo.spec.ts --headed --slow-mo=1000
 */

import { test, expect, Page } from '@playwright/test';

// Configuration
const BASE_URL = process.env.FRONTEND_URL || 'http://localhost:3000';
const SLOW_MOTION_DELAY = 1500; // 1.5 seconds between actions for demo clarity

/**
 * Helper function to add dramatic pauses for video recording
 */
async function dramaticPause(page: Page, seconds: number = 2): Promise<void> {
  await page.waitForTimeout(seconds * 1000);
}

/**
 * Helper function to smoothly scroll to element
 */
async function smoothScrollTo(page: Page, selector: string): Promise<void> {
  await page.locator(selector).scrollIntoViewIfNeeded({ behavior: 'smooth' });
  await page.waitForTimeout(500);
}

/**
 * Helper function to type with realistic human-like delays
 */
async function humanTypeDelay(page: Page, selector: string, text: string): Promise<void> {
  await page.locator(selector).click();
  await page.locator(selector).pressSequentially(text, { delay: 80 }); // 80ms per character
}

test.describe('NeuroAgent Demo Video - 3 Minute Workflow', () => {
  // Configure test timeout for 5 minutes (demo takes ~3 minutes + buffer)
  test.setTimeout(5 * 60 * 1000);

  test('Complete demo workflow: Landing → Diagnosis → Case History', async ({ page }) => {
    console.log('🎬 Starting NeuroAgent Demo Recording...');

    // ========================================
    // SCENE 1: Landing Page Introduction (20 seconds)
    // ========================================
    console.log('📍 Scene 1: Landing Page Introduction');

    // Navigate to home page
    await page.goto(BASE_URL);
    await expect(page).toHaveTitle(/NeuroAgent/);

    // Wait for page to fully load
    await page.waitForLoadState('networkidle');
    await dramaticPause(page, 2);

    // Verify app header
    await expect(page.getByText('NeuroAgent - AI診療助手')).toBeVisible();
    await dramaticPause(page, 1);

    // Highlight navigation menu
    const diagnosisNavLink = page.getByRole('link', { name: /診斷分析|diagnosis/i });
    await diagnosisNavLink.hover();
    await dramaticPause(page, 1);

    // Take screenshot of landing page
    await page.screenshot({ path: 'demo-screenshots/01-landing-page.png', fullPage: true });
    console.log('✅ Scene 1 Complete: Landing page introduction');

    // ========================================
    // SCENE 2: Patient Case Input (60 seconds)
    // ========================================
    console.log('📍 Scene 2: Patient Case Input - Neurological Diagnosis');

    // Navigate to diagnosis page
    await diagnosisNavLink.click();
    await page.waitForURL(/\/diagnosis/);
    await dramaticPause(page, 2);

    // Verify diagnosis page header
    await expect(page.getByRole('heading', { name: /神經疾病診斷分析/ })).toBeVisible();
    await dramaticPause(page, 1);

    // ===== Fill Patient Demographics =====
    console.log('  ↳ Entering patient demographics...');

    // Age: 67 years old
    await smoothScrollTo(page, 'input[type="number"][label*="年齡"]');
    await humanTypeDelay(page, 'input[type="number"]', '67');
    await dramaticPause(page, 1);

    // Gender: Male
    const genderSelect = page.locator('div[role="button"]').filter({ hasText: /性別|gender/i });
    await genderSelect.click();
    await page.waitForTimeout(500);
    await page.getByRole('option', { name: /男性|male/i }).click();
    await dramaticPause(page, 1);

    // ===== Chief Complaint =====
    console.log('  ↳ Entering chief complaint...');

    const chiefComplaintField = page.locator('textarea').filter({ has: page.locator('label', { hasText: /主訴/ }) }).first();
    await smoothScrollTo(page, 'textarea');
    await humanTypeDelay(
      page,
      'textarea',
      '突發左側肢體無力，伴隨言語不清'
    );
    await dramaticPause(page, 2);

    // ===== Symptoms Description =====
    console.log('  ↳ Entering detailed symptoms...');

    const symptomsField = page.locator('textarea').nth(1);
    await smoothScrollTo(page, 'textarea:nth-of-type(2)');
    await humanTypeDelay(
      page,
      'textarea:nth-of-type(2)',
      '左側上下肢無力，左側面部下垂，說話困難，吞嚥困難，頭暈'
    );
    await dramaticPause(page, 2);

    // ===== Medical History =====
    console.log('  ↳ Entering medical history...');

    await smoothScrollTo(page, 'input[helperText*="病史"]');
    await humanTypeDelay(
      page,
      'input[label*="既往病史"]',
      '高血壓10年，糖尿病5年，高血脂'
    );
    await dramaticPause(page, 1.5);

    // ===== Current Medications =====
    console.log('  ↳ Entering current medications...');

    await humanTypeDelay(
      page,
      'input[label*="目前用藥"]',
      'Amlodipine 5mg, Metformin 1000mg, Atorvastatin 20mg'
    );
    await dramaticPause(page, 1.5);

    // ===== Vital Signs =====
    console.log('  ↳ Entering vital signs...');

    // Blood Pressure
    await smoothScrollTo(page, 'input[placeholder*="120/80"]');
    await humanTypeDelay(page, 'input[placeholder*="120/80"]', '165/95');
    await dramaticPause(page, 1);

    // Heart Rate
    await humanTypeDelay(page, 'input[label*="心率"]', '88');
    await dramaticPause(page, 1);

    // Temperature
    await humanTypeDelay(page, 'input[label*="體溫"]', '37.2');
    await dramaticPause(page, 1);

    // Take screenshot of completed form
    await page.screenshot({ path: 'demo-screenshots/02-diagnosis-form-filled.png', fullPage: true });
    console.log('✅ Scene 2 Complete: Patient case input');

    // ========================================
    // SCENE 3: AI Diagnosis Analysis (60 seconds)
    // ========================================
    console.log('📍 Scene 3: AI Diagnosis Analysis');

    // Submit diagnosis form
    const submitButton = page.getByRole('button', { name: /開始診斷分析/ });
    await smoothScrollTo(page, 'button[type="submit"]');
    await dramaticPause(page, 1);

    await submitButton.click();
    console.log('  ↳ Submitting diagnosis request to AI agent...');

    // Wait for loading spinner
    await expect(page.locator('div[role="progressbar"]')).toBeVisible({ timeout: 2000 });
    await dramaticPause(page, 2);

    // Wait for results to appear (timeout: 30 seconds for Bedrock response)
    await page.waitForSelector('text=/診斷結果|Diagnosis Results/', {
      timeout: 30000,
      state: 'visible'
    });
    console.log('  ↳ AI analysis complete!');
    await dramaticPause(page, 2);

    // ===== Examine Diagnosis Results =====
    console.log('  ↳ Reviewing diagnosis results...');

    // Scroll to results section
    await smoothScrollTo(page, 'text=/診斷結果|Diagnosis Results/');
    await dramaticPause(page, 2);

    // Verify case ID is generated
    await expect(page.locator('text=/case_id|病例編號/')).toBeVisible();
    await dramaticPause(page, 1);

    // Look for confidence scores
    const confidenceElements = page.locator('text=/信度|Confidence|%/');
    if (await confidenceElements.count() > 0) {
      await confidenceElements.first().scrollIntoViewIfNeeded();
      await dramaticPause(page, 2);
    }

    // Check for differential diagnoses
    const diagnosisSection = page.locator('text=/鑑別診斷|Differential Diagnosis|可能診斷/');
    if (await diagnosisSection.count() > 0) {
      await diagnosisSection.first().scrollIntoViewIfNeeded();
      await dramaticPause(page, 2);
    }

    // Check for recommendations
    const recommendationsSection = page.locator('text=/建議|Recommendations|治療建議/');
    if (await recommendationsSection.count() > 0) {
      await recommendationsSection.first().scrollIntoViewIfNeeded();
      await dramaticPause(page, 2);
    }

    // Scroll through entire results
    await page.evaluate(() => {
      window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
    });
    await dramaticPause(page, 2);

    // Scroll back to top of results
    await page.evaluate(() => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
    await dramaticPause(page, 1);

    // Take screenshot of diagnosis results
    await page.screenshot({ path: 'demo-screenshots/03-diagnosis-results.png', fullPage: true });
    console.log('✅ Scene 3 Complete: AI diagnosis analysis displayed');

    // ========================================
    // SCENE 4: Case History Page (40 seconds)
    // ========================================
    console.log('📍 Scene 4: Case History Review');

    // Navigate to case history page
    const historyNavLink = page.getByRole('link', { name: /病例記錄|history|歷史/i });
    await historyNavLink.hover();
    await dramaticPause(page, 1);

    await historyNavLink.click();
    await page.waitForURL(/\/history/);
    await dramaticPause(page, 2);

    // Verify case history page header
    await expect(page.getByRole('heading', { name: /病例記錄/ })).toBeVisible();
    await dramaticPause(page, 1);

    // ===== Examine Case List =====
    console.log('  ↳ Reviewing case history...');

    // Check for search bar
    const searchInput = page.locator('input[placeholder*="搜尋"]');
    if (await searchInput.count() > 0) {
      await searchInput.scrollIntoViewIfNeeded();
      await dramaticPause(page, 1);

      // Demonstrate search functionality
      await humanTypeDelay(page, 'input[placeholder*="搜尋"]', '頭痛');
      await dramaticPause(page, 2);

      // Clear search
      await searchInput.clear();
      await dramaticPause(page, 1);
    }

    // Scroll through case list
    const caseCards = page.locator('div[role="listitem"], li');
    const caseCount = await caseCards.count();

    if (caseCount > 0) {
      console.log(`  ↳ Found ${caseCount} cases in history`);

      // Hover over each case card to highlight
      for (let i = 0; i < Math.min(caseCount, 3); i++) {
        await caseCards.nth(i).scrollIntoViewIfNeeded();
        await caseCards.nth(i).hover();
        await dramaticPause(page, 1.5);
      }
    } else {
      // If no cases, show the empty state
      await expect(page.getByText(/目前沒有病例記錄|No cases/)).toBeVisible();
      await dramaticPause(page, 2);
    }

    // Take screenshot of case history
    await page.screenshot({ path: 'demo-screenshots/04-case-history.png', fullPage: true });
    console.log('✅ Scene 4 Complete: Case history review');

    // ========================================
    // FINALE: Return to Home (10 seconds)
    // ========================================
    console.log('📍 Finale: Return to Home');

    // Navigate back to home page
    const homeLink = page.getByRole('link', { name: /首頁|home/i });
    if (await homeLink.count() > 0) {
      await homeLink.click();
      await page.waitForURL(BASE_URL);
      await dramaticPause(page, 2);
    }

    // Take final screenshot
    await page.screenshot({ path: 'demo-screenshots/05-demo-complete.png', fullPage: true });

    console.log('🎬 Demo Recording Complete!');
    console.log('📁 Screenshots saved to: demo-screenshots/');
    console.log('🎥 Video saved to: test-results/ (if --video=on flag used)');
  });
});

/**
 * Additional test: Demo with mock API responses (for offline recording)
 */
test.describe('NeuroAgent Demo - Mock API Mode', () => {
  test.setTimeout(5 * 60 * 1000);

  test('Demo with mocked Bedrock responses (offline mode)', async ({ page }) => {
    console.log('🎬 Starting Demo with Mock API Responses...');

    // Mock API responses for consistent demo
    await page.route('**/api/v1/diagnosis', async (route) => {
      await page.waitForTimeout(3000); // Simulate 3s Bedrock delay

      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          case_id: 'demo-case-001',
          status: 'analyzed',
          timestamp: new Date().toISOString(),
          diagnosis: {
            primary_diagnosis: {
              condition: '急性缺血性腦中風 (Acute Ischemic Stroke)',
              confidence: 0.94,
              icd10_code: 'I63.9',
              rationale: '患者突發左側肢體無力、言語不清，伴隨面部下垂，符合腦中風FAST徵象。既往高血壓、糖尿病、高血脂為高危險因子。'
            },
            differential_diagnoses: [
              {
                condition: '出血性腦中風 (Hemorrhagic Stroke)',
                confidence: 0.15,
                rationale: '需透過CT掃描排除腦出血可能性'
              },
              {
                condition: '短暫性腦缺血發作 (TIA)',
                confidence: 0.08,
                rationale: '症狀持續時間較長，TIA可能性較低'
              }
            ],
            risk_factors: [
              '高血壓控制不佳 (BP: 165/95)',
              '糖尿病病史',
              '高血脂',
              '年齡 (67歲)'
            ],
            recommendations: [
              {
                category: 'immediate',
                action: '🚨 立即啟動急性腦中風處理流程 (Code Stroke)',
                priority: 'critical',
                details: '時間即腦細胞！建議立即進行腦部CT掃描排除出血，並評估血栓溶解治療適應症。'
              },
              {
                category: 'diagnostic',
                action: '影像學檢查',
                priority: 'urgent',
                details: '緊急腦部CT掃描、CT血管攝影 (CTA)、心電圖、血液檢查 (CBC, PT/aPTT, 血糖, 電解質)'
              },
              {
                category: 'treatment',
                action: '考慮靜脈血栓溶解治療 (rtPA)',
                priority: 'urgent',
                details: '若症狀發作於4.5小時內且無禁忌症，考慮rtPA治療。需神經科專科醫師評估。'
              },
              {
                category: 'monitoring',
                action: '神經加護病房監測',
                priority: 'high',
                details: '密切監測生命徵象、神經學狀態、血糖、血壓管理'
              }
            ],
            next_steps: [
              '神經科專科醫師會診',
              '啟動腦中風急性處理小組',
              '聯絡家屬說明病情',
              '準備可能的介入性治療 (血栓溶解或血栓移除)'
            ],
            clinical_notes: '根據NIHSS評分標準，患者呈現中等嚴重度腦中風症狀。時間窗口內的積極治療可能顯著改善預後。',
            drug_interactions: {
              warnings: [
                {
                  severity: 'high',
                  drugs: ['Amlodipine', 'Atorvastatin'],
                  interaction: '血栓溶解治療前需評估抗凝血藥物風險',
                  recommendation: '暫停抗血小板與降血脂藥物，待神經科醫師評估'
                }
              ],
              safe_combinations: [
                'Metformin可繼續使用，但需監測腎功能'
              ]
            }
          },
          metadata: {
            model_used: 'anthropic.claude-3-sonnet-20240229-v1:0',
            processing_time_ms: 2847,
            bedrock_agent_id: 'demo-agent',
            confidence_threshold: 0.75
          },
          disclaimer: '⚠️ 此為AI輔助診斷建議，所有診斷與治療決策需由專業醫師確認。本系統不可取代臨床醫師判斷。'
        })
      });
    });

    // Mock case history API
    await page.route('**/api/v1/cases', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          cases: [
            {
              case_id: 'case-001',
              patient_age: 45,
              patient_gender: 'female',
              chief_complaint: '頭痛三天，伴隨噁心嘔吐',
              diagnosis: '偏頭痛 (Migraine)',
              confidence: 0.85,
              created_at: '2025-10-12T10:30:00Z',
              status: 'completed'
            },
            {
              case_id: 'case-002',
              patient_age: 67,
              patient_gender: 'male',
              chief_complaint: '左側肢體無力',
              diagnosis: '急性缺血性腦中風',
              confidence: 0.94,
              created_at: '2025-10-12T14:20:00Z',
              status: 'completed'
            },
            {
              case_id: 'case-003',
              patient_age: 34,
              patient_gender: 'female',
              chief_complaint: '記憶力減退，注意力不集中',
              diagnosis: '需進一步神經心理評估',
              confidence: 0.65,
              created_at: '2025-10-11T09:15:00Z',
              status: 'pending'
            }
          ],
          total: 3,
          page: 1,
          page_size: 10
        })
      });
    });

    // Run the same demo workflow with mocked APIs
    // (Same test steps as above, but with consistent mock responses)
    await page.goto(BASE_URL);
    await dramaticPause(page, 2);

    // Navigate to diagnosis
    await page.getByRole('link', { name: /診斷分析|diagnosis/i }).click();
    await page.waitForURL(/\/diagnosis/);

    // Fill form (abbreviated for mock demo)
    await humanTypeDelay(page, 'input[type="number"]', '67');
    await page.locator('div[role="button"]').filter({ hasText: /性別/ }).click();
    await page.getByRole('option', { name: /男性/ }).click();
    await humanTypeDelay(page, 'textarea', '突發左側肢體無力');

    // Submit and wait for mock response
    await page.getByRole('button', { name: /開始診斷分析/ }).click();
    await page.waitForSelector('text=/急性缺血性腦中風/', { timeout: 10000 });
    await dramaticPause(page, 3);

    // Navigate to case history
    await page.getByRole('link', { name: /病例記錄|history/i }).click();
    await page.waitForURL(/\/history/);
    await dramaticPause(page, 2);

    console.log('🎬 Mock API Demo Complete!');
  });
});
