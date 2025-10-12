# Pytest-BDD Quick Reference Card

## 🚀 Quick Start (3 Steps)

```bash
# 1. Install dependencies
pip install -r backend/tests/acceptance/requirements.txt

# 2. Run tests with mocks (no backend required)
export ENABLE_MOCKS=true
pytest backend/tests/acceptance/ -v

# 3. View HTML report
open reports/acceptance/report.html
```

---

## 📂 File Locations

| What | Where |
|------|-------|
| **Gherkin Scenarios** | `backend/tests/acceptance/features/migraine_diagnosis.feature` |
| **Step Definitions** | `backend/tests/acceptance/test_migraine_diagnosis.py` |
| **Shared Fixtures** | `backend/tests/acceptance/conftest.py` |
| **Documentation** | `backend/tests/acceptance/README.md` |
| **Test Runner** | `backend/tests/acceptance/run_tests.sh` |

---

## 🧪 Run Tests

### Using Pytest Directly

```bash
# All tests
pytest backend/tests/acceptance/ -v

# Critical tests only
pytest backend/tests/acceptance/ -m critical -v

# Specific scenario
pytest backend/tests/acceptance/ -k "typical_migraine" -v

# With HTML report
pytest backend/tests/acceptance/ --html=reports/acceptance/report.html --self-contained-html

# With coverage
pytest backend/tests/acceptance/ --cov=backend --cov-report=html:reports/acceptance/coverage
```

### Using Test Runner Script

```bash
# Run all tests
./backend/tests/acceptance/run_tests.sh all

# Run by marker
./backend/tests/acceptance/run_tests.sh critical
./backend/tests/acceptance/run_tests.sh red_flag
./backend/tests/acceptance/run_tests.sh performance

# With coverage
./backend/tests/acceptance/run_tests.sh coverage

# Help
./backend/tests/acceptance/run_tests.sh help
```

---

## 🏷️ Test Markers (Tags)

| Marker | Run Command | Count | Description |
|--------|-------------|-------|-------------|
| `@critical` | `pytest -m critical` | 3 | Must pass for MVP |
| `@positive` | `pytest -m positive` | 4 | Expected success |
| `@negative` | `pytest -m negative` | 3 | Expected errors |
| `@validation` | `pytest -m validation` | 1 | Input validation |
| `@red_flag` | `pytest -m red_flag` | 1 | Red flag detection |
| `@performance` | `pytest -m performance` | 1 | Performance SLA |
| `@localization` | `pytest -m localization` | 1 | Multi-language |
| `@drug_interaction` | `pytest -m drug_interaction` | 1 | Drug interactions |

---

## 🎯 7 Test Scenarios

1. **Typical Migraine** - High confidence diagnosis (≥0.85)
2. **Invalid Input** - Validation error handling (HTTP 422)
3. **Thunderclap Headache** - Red flag detection (SAH)
4. **Confidence Scoring** - Parameterized (6 examples)
5. **Medication Overuse** - MOH detection and recommendations
6. **Performance SLA** - Response time <5s
7. **Localization** - Traditional Chinese (zh-TW)

---

## 🔧 Environment Variables

```bash
# Required for integration testing
export TEST_API_BASE_URL="http://localhost:8000"
export ENABLE_MOCKS="false"

# Or use mocks (no backend required)
export ENABLE_MOCKS="true"

# AWS configuration (if not using mocks)
export AWS_REGION="us-east-1"
export TEST_DYNAMODB_TABLE="NeuroAgent-PatientCases-Test"
```

---

## 📊 Test Data Fixtures

Available in `conftest.py`:

- `typical_migraine_patient` - Scenario 1 data
- `thunderclap_headache_patient` - Scenario 3 data (SAH)
- `invalid_patient_data` - Scenario 2 validation errors
- `medication_overuse_patient` - Scenario 5 MOH data

Usage:
```python
def test_example(typical_migraine_patient, api_client):
    response = api_client.post("/api/v1/diagnosis", json=typical_migraine_patient)
    assert response.status_code == 200
```

---

## 🛠️ Common Tasks

### Add New Scenario

1. Edit `features/migraine_diagnosis.feature`
2. Add Given/When/Then steps
3. Implement step definitions in `test_migraine_diagnosis.py`
4. Run: `pytest backend/tests/acceptance/ -k "new_scenario" -v`

### Mock Bedrock Response

Edit `conftest.py` fixture:
```python
@pytest.fixture
def bedrock_mock():
    class MockBedrockService:
        def invoke_model(self, model_id, body):
            # Return custom diagnosis here
            return {"diagnosis": [...], ...}
    return MockBedrockService()
```

### Debug Test Failure

```bash
# Run with verbose output
pytest backend/tests/acceptance/ -v -s

# Run with debugging
pytest backend/tests/acceptance/ --pdb

# Show local variables on failure
pytest backend/tests/acceptance/ -l
```

---

## 📈 Reports

| Report Type | Command | Output Location |
|-------------|---------|-----------------|
| **HTML** | `pytest --html=...` | `reports/acceptance/report.html` |
| **JUnit XML** | `pytest --junit-xml=...` | `reports/acceptance/junit.xml` |
| **Coverage** | `pytest --cov=...` | `reports/acceptance/coverage/` |
| **JSON** | `pytest --json-report` | `reports/acceptance/report.json` |

---

## 🐛 Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'pytest_bdd'`
**Fix**: `pip install -r backend/tests/acceptance/requirements.txt`

### Issue: `ImportError: cannot import name 'app' from 'backend.main'`
**Fix**: Set `ENABLE_MOCKS=true` to use mock services

### Issue: Tests fail with "TODO: Replace with actual implementation"
**Expected**: Implement TODO items in step definitions as you build backend

### Issue: All tests pass but no backend exists
**Expected**: Mocks are being used. Set `ENABLE_MOCKS=false` for integration testing

---

## 📚 Documentation

| Document | Description | Lines |
|----------|-------------|-------|
| **README.md** | Full usage guide | 396 |
| **IMPLEMENTATION_SUMMARY.md** | Complete deliverables summary | 400+ |
| **QUICK_REFERENCE.md** | This cheat sheet | 200+ |
| **MIGRAINE_SCENARIOS_VALIDATION.md** | Medical validation report | 486 |

---

## 🎓 Step Definition Pattern

```python
# Given step (setup)
@given(parsers.parse('患者年齡為 {age:d} 歲'))
def patient_age(context, age):
    context.patient_info.age = age
    return context

# When step (action)
@when(parsers.parse('送出診斷請求到 "{endpoint}"'))
def send_request(context, endpoint, api_client):
    response = api_client.post(endpoint, json=context.request_payload)
    context.response = response

# Then step (assertion)
@then(parsers.parse('API 應回應成功 (HTTP {status:d})'))
def assert_status(context, status):
    assert context.response.status_code == status
```

---

## 🔗 Related Commands

```bash
# Check Python version
python3 --version

# List installed packages
pip list | grep pytest

# Validate test structure
pytest --collect-only backend/tests/acceptance/

# Show available markers
pytest --markers backend/tests/acceptance/

# Dry run (no execution)
pytest --collect-only backend/tests/acceptance/
```

---

## ✅ Quick Checklist

Before running tests:
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Environment variables set (or use mocks)
- [ ] Reports directory exists (`mkdir -p reports/acceptance`)

For integration testing:
- [ ] Backend server running (`uvicorn backend.main:app`)
- [ ] AWS credentials configured
- [ ] DynamoDB table created
- [ ] `ENABLE_MOCKS=false`

---

## 🎯 Demo Day Checklist

- [ ] Run critical tests: `pytest -m critical`
- [ ] Generate HTML report
- [ ] Verify all 7 scenarios pass
- [ ] Check performance metrics (<5s)
- [ ] Validate Traditional Chinese output
- [ ] Demo red flag detection (SAH scenario)

---

**Quick Reference Version**: 1.0
**Last Updated**: October 12, 2025
**See Also**: README.md, IMPLEMENTATION_SUMMARY.md
