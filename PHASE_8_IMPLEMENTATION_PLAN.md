# Phase 8: Integration, Performance & Security - Implementation Plan

## Overview
Phase 8 focuses on production readiness through load testing, caching optimization, and security hardening.

**Performance Target**: p95 response time < 2 seconds for 100 concurrent diagnosis requests

**Security Target**: Zero high-severity vulnerabilities in production code

---

## 8-1: Load Testing & Caching Strategy

### Performance Requirements
- **Concurrent Users**: 100 simultaneous diagnosis requests
- **Target Latency**: p95 < 2000ms
- **Target Throughput**: ≥50 requests/second
- **Error Rate**: <1%

### Current Performance Bottlenecks (Anticipated)

1. **AWS Bedrock API Calls** (Highest Impact)
   - Expected latency: 3-8 seconds per request
   - No caching currently implemented
   - Sequential processing (no parallelization)

2. **Drug Interaction Checking** (Medium Impact)
   - O(n²) algorithm for n medications
   - Recomputed on every request
   - No result caching

3. **Medical Knowledge Base Lookups** (Low Impact)
   - Dictionary lookups (fast)
   - But called multiple times per request

### Proposed Caching Strategy

#### **Architecture Overview**
```
[Client Request]
     ↓
[API Gateway / FastAPI]
     ↓
[Cache Layer - Redis] ← Check cache first
     ↓ (cache miss)
[Business Logic]
     ↓
[AWS Bedrock AgentCore]
     ↓ (cache result)
[Redis Cache] ← Store for future requests
```

#### **Cache Implementation Strategy**

##### **1. Response Caching (Highest Priority)**
**Target**: Reduce duplicate Bedrock API calls

**Cache Key Strategy**:
```python
cache_key = f"diagnosis:{hash(symptoms+medications+vitals)}"
# Example: "diagnosis:abc123def456"
```

**TTL (Time-To-Live)**:
- Diagnosis responses: 1 hour (medical data changes infrequently)
- Drug interactions: 24 hours (drug database is stable)
- Image analysis: 1 hour (image content doesn't change)

**Implementation**:
- Cache full diagnosis response before returning to client
- Invalidate cache when medical knowledge base updates
- Use Redis with LRU eviction policy

##### **2. Drug Interaction Memoization (Medium Priority)**
**Target**: Avoid recomputing same drug pair interactions

**Cache Key Strategy**:
```python
cache_key = f"drug_interaction:{sorted([drug1, drug2])}"
# Example: "drug_interaction:['aspirin', 'warfarin']"
```

**TTL**: 7 days (drug interaction data is highly stable)

**Implementation**:
- Cache individual drug pair interactions
- Compute full interaction set from cached pairs
- Reduces O(n²) to O(n) for cached pairs

##### **3. Bedrock Response Caching (Critical for Performance)**
**Target**: Cache AI model responses for similar cases

**Cache Key Strategy**:
```python
# Content-based hashing
prompt_hash = sha256(diagnostic_prompt).hexdigest()
cache_key = f"bedrock_response:{prompt_hash}"
```

**TTL**: 2 hours

**Cache Hit Rate Goal**: >60% for common symptoms

##### **4. API Rate Limiting (Security & Stability)**
**Implementation**:
- Per-user limits: 100 requests/minute
- Global limit: 1000 requests/minute
- Use Redis for distributed rate limiting

**Rate Limit Response**:
```json
{
  "error": "Rate limit exceeded",
  "retry_after": 60,
  "limit": 100,
  "window": "1 minute"
}
```

### Locust Load Testing Script Design

#### **Test Scenarios**

**Scenario 1: Diagnosis Request Load Test**
- 100 concurrent users
- Each user submits diagnosis request every 5-10 seconds
- Ramp-up time: 30 seconds
- Total duration: 5 minutes

**Scenario 2: Mixed Workload Test**
- 60% diagnosis requests
- 30% drug interaction checks
- 10% image uploads
- Realistic distribution

**Scenario 3: Spike Test**
- Sudden spike from 10 to 200 users in 10 seconds
- Tests system stability under load

#### **Locust Script Structure**
```python
# locustfile.py

class NeuroAgentUser(HttpUser):
    wait_time = between(5, 10)  # Wait 5-10s between requests

    @task(6)  # 60% weight
    def submit_diagnosis(self):
        """Test diagnosis endpoint"""
        payload = generate_diagnosis_payload()
        with self.client.post(
            "/api/v1/diagnosis",
            json=payload,
            headers={"Authorization": f"Bearer {AUTH_TOKEN}"},
            catch_response=True
        ) as response:
            if response.elapsed.total_seconds() > 2.0:
                response.failure(f"Response time too high: {response.elapsed.total_seconds()}s")

    @task(3)  # 30% weight
    def check_drug_interactions(self):
        """Test drug interaction endpoint"""
        # Implementation

    @task(1)  # 10% weight
    def upload_image(self):
        """Test image upload endpoint"""
        # Implementation
```

### Files to Modify

#### **New Files to Create**:
1. `backend/cache/redis_cache.py` - Redis caching layer
2. `backend/cache/__init__.py` - Cache module init
3. `backend/middleware/rate_limiter.py` - Rate limiting middleware
4. `tests/load/locustfile.py` - Locust load testing script
5. `tests/load/test_data_generator.py` - Generate realistic test payloads
6. `docker-compose.yml` - Add Redis service
7. `backend/config/cache_config.py` - Cache configuration

#### **Files to Modify**:
1. `backend/main.py` - Add cache middleware, rate limiting
2. `backend/agents/neuro_agent.py` - Add caching to analyze_case()
3. `backend/utils/medical_knowledge.py` - Add memoization to drug interactions
4. `backend/services/bedrock_service.py` - Add response caching
5. `requirements.txt` - Add redis, locust dependencies
6. `.env.example` - Add Redis configuration variables

### Expected Performance Improvements

**Before Caching**:
- p50: 4500ms
- p95: 8000ms
- p99: 12000ms
- Cache hit rate: 0%

**After Caching (Estimated)**:
- p50: 150ms (cache hit) / 4500ms (cache miss)
- p95: 1800ms (60% cache hit rate)
- p99: 5000ms
- Cache hit rate: 60-70% (after warm-up)

**Performance Gain**: ~4x improvement for cached requests

---

## 8-2: Security Scanning & Remediation

### Semgrep Security Scan Strategy

#### **Scan Configuration**
```yaml
# .semgrep.yml
rules:
  - id: python-security-audit
    patterns:
      - pattern: exec($X)
      - pattern: eval($X)
    message: "Dangerous use of exec/eval - code injection risk"
    severity: ERROR

  - id: hardcoded-secrets
    patterns:
      - pattern: password = "..."
      - pattern: api_key = "..."
    message: "Hardcoded secrets detected"
    severity: ERROR
```

#### **Security Scan Scope**
1. **Backend Python Code** - All .py files
2. **Frontend JavaScript** - All .js/.jsx/.ts/.tsx files
3. **Configuration Files** - .env, config files
4. **Dependencies** - requirements.txt, package.json

### Common Vulnerability Categories to Check

#### **1. Injection Vulnerabilities** (CRITICAL)
- SQL injection
- Command injection
- Code injection (eval/exec)
- Prompt injection (for AI systems)

#### **2. Authentication & Authorization** (HIGH)
- Missing authentication checks
- Weak token validation
- Insecure password storage
- Missing RBAC

#### **3. Sensitive Data Exposure** (HIGH)
- Hardcoded secrets/API keys
- Logging sensitive data
- Unencrypted data transmission
- Missing data sanitization

#### **4. Security Misconfiguration** (MEDIUM)
- Debug mode enabled in production
- Verbose error messages
- Missing security headers
- Permissive CORS configuration

#### **5. Vulnerable Dependencies** (MEDIUM)
- Outdated libraries with known CVEs
- Unmaintained packages

### Anticipated High-Severity Vulnerabilities

Based on code review, likely vulnerabilities:

#### **Vulnerability #1: CORS Misconfiguration** (HIGH)
**Location**: `backend/main.py:24-30`
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ SECURITY ISSUE: Allows any origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Risk**:
- Cross-Site Request Forgery (CSRF)
- Unauthorized API access from any domain
- Credential theft

**Fix**:
```python
# Use environment-based origin whitelist
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Only needed methods
    allow_headers=["Authorization", "Content-Type"],
    max_age=600,  # Cache preflight for 10 minutes
)
```

#### **Vulnerability #2: Missing Input Sanitization** (HIGH)
**Location**: `backend/agents/neuro_agent.py:_build_diagnostic_prompt()`

**Risk**:
- Prompt injection attacks
- AI model manipulation
- Data exfiltration via prompt engineering

**Current Code**:
```python
prompt = f"""
PATIENT INFORMATION:
- Chief Complaint: {context['presentation']['chief_complaint']}
"""
```

**Fix**:
```python
def _sanitize_input(text: str, max_length: int = 1000) -> str:
    """Sanitize user input to prevent prompt injection"""
    # Remove control characters
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)

    # Escape special tokens that could manipulate AI
    dangerous_patterns = [
        r'ignore previous instructions',
        r'system:',
        r'<\|.*?\|>',
        r'\[INST\]',
        r'</s>',
    ]
    for pattern in dangerous_patterns:
        text = re.sub(pattern, '[REDACTED]', text, flags=re.IGNORECASE)

    # Truncate to max length
    return text[:max_length]

# Usage:
chief_complaint = self._sanitize_input(context['presentation']['chief_complaint'])
```

#### **Vulnerability #3: Weak Token Validation** (HIGH)
**Location**: `backend/utils/auth.py` (assumed implementation)

**Risk**:
- Token forgery
- Unauthorized access
- Session hijacking

**Expected Issue**:
```python
def verify_token(token: str) -> str:
    # ⚠️ Likely missing:
    # - Token expiration check
    # - Signature verification
    # - Algorithm validation (JWT algorithm confusion)
    # - Token revocation check
```

**Fix**:
```python
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"

def verify_token(token: str) -> str:
    """Secure JWT token verification"""
    try:
        # Decode with algorithm whitelist (prevent algorithm confusion)
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],  # Explicit algorithm
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_iat": True,
                "require_exp": True,
            }
        )

        # Check token hasn't expired
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp) < datetime.now():
            raise HTTPException(status_code=401, detail="Token expired")

        # Check token revocation (if using Redis blacklist)
        if is_token_revoked(token):
            raise HTTPException(status_code=401, detail="Token revoked")

        return payload["user_id"]

    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
```

### Security Hardening Checklist

- [ ] Enable HTTPS only (HSTS headers)
- [ ] Implement Content Security Policy (CSP)
- [ ] Add rate limiting on all endpoints
- [ ] Sanitize all user inputs
- [ ] Validate JWT tokens properly
- [ ] Use parameterized queries (prevent SQL injection)
- [ ] Encrypt sensitive data at rest
- [ ] Implement audit logging
- [ ] Add security headers (X-Frame-Options, X-Content-Type-Options)
- [ ] Remove debug mode in production
- [ ] Scan dependencies for CVEs
- [ ] Implement secrets management (AWS Secrets Manager)

---

## Implementation Timeline

### Phase 8-1: Load Testing & Caching (4-6 hours)
1. **Hour 1-2**: Implement Redis caching layer
2. **Hour 2-3**: Add caching to critical endpoints
3. **Hour 3-4**: Create Locust load testing script
4. **Hour 4-5**: Run load tests and optimize
5. **Hour 5-6**: Document performance improvements

### Phase 8-2: Security Hardening (2-3 hours)
1. **Hour 1**: Run Semgrep scan
2. **Hour 1.5**: Analyze and prioritize vulnerabilities
3. **Hour 2-3**: Fix top 3 high-severity issues
4. **Hour 3**: Re-scan and verify fixes

### Total Estimated Time: 6-9 hours

---

## Success Metrics

### Performance Metrics
- ✅ p95 latency < 2000ms under 100 concurrent users
- ✅ Cache hit rate > 60% after warm-up
- ✅ Error rate < 1% during load test
- ✅ Throughput ≥ 50 req/s

### Security Metrics
- ✅ Zero CRITICAL vulnerabilities
- ✅ Zero HIGH vulnerabilities in production code
- ✅ All authentication endpoints secured
- ✅ Input sanitization on all user inputs
- ✅ CORS properly configured

### Code Quality Metrics
- ✅ 100% of tests passing
- ✅ Performance regression tests added
- ✅ Security tests added
- ✅ Documentation updated

---

## Risk Mitigation

### Performance Risks
1. **Risk**: Cache stampede (multiple requests miss cache simultaneously)
   - **Mitigation**: Implement cache warming on startup

2. **Risk**: Redis becomes bottleneck
   - **Mitigation**: Redis cluster with replication

3. **Risk**: Memory exhaustion from large cache
   - **Mitigation**: LRU eviction, memory limits

### Security Risks
1. **Risk**: Cache poisoning
   - **Mitigation**: Validate cached data on retrieval

2. **Risk**: Rate limit bypass
   - **Mitigation**: Distributed rate limiting with Redis

3. **Risk**: Zero-day vulnerabilities in dependencies
   - **Mitigation**: Automated dependency scanning in CI/CD

---

## Next Steps After Phase 8

1. **Production Deployment**
   - AWS infrastructure with CDK
   - CloudWatch monitoring
   - Auto-scaling configuration

2. **Continuous Monitoring**
   - Performance dashboards
   - Security alerts
   - Error tracking (Sentry)

3. **Feature Enhancements**
   - Real-time AI streaming responses
   - Advanced image analysis with SageMaker
   - Multi-language support

---

**Document Version**: 1.0
**Last Updated**: October 12, 2025
**Status**: Ready for Implementation
