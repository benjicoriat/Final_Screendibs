# 🚀 SCREENDIBS AUDIT - QUICK START GUIDE

## 📌 ONE-PAGE SUMMARY

**Status:** ✅ Functional | ❌ NOT PRODUCTION READY  
**Main Issues:** 4 Critical Security Flaws + Low Test Coverage

---

## 🔴 DO THIS TODAY (2-3 hours)

### 1. ROTATE API KEYS NOW
```bash
# Your Groq key is exposed:
GROQ_API_KEY=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

# Action: https://console.groq.com → Create new key
# Then update .env with new key
```

### 2. FIX PASSWORD HASHING (30 minutes)
**File:** `backend/app/core/security.py`  
**Change From:** HMAC-SHA256 (weak)  
**Change To:** bcrypt (strong, already in requirements.txt)

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
```

### 3. ADD SECURITY HEADERS (15 minutes)
**File:** `backend/app/main.py`

```python
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=31536000"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response
```

### 4. ADD RATE LIMITING (20 minutes)
**File:** `backend/app/main.py`

```python
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@router.post("/register")
@limiter.limit("3/minute")
async def register(...):
    pass

@router.post("/login")
@limiter.limit("5/minute")
async def login(...):
    pass
```

### 5. MOVE SECRETS OUT OF GIT (10 minutes)
```bash
# Add to .gitignore
echo ".env" >> backend/.gitignore

# Store in GitHub Secrets:
# - GROQ_API_KEY (NEW KEY from step 1)
# - STRIPE_SECRET_KEY
# - STRIPE_WEBHOOK_SECRET
# - SENDGRID_API_KEY
# - DATABASE_URL
# - SECRET_KEY
```

---

## 🟠 DO THIS IN DAYS 1-2

### Testing Gaps (Fill These)
```bash
# Backend Coverage: Currently ~30%, need 80%+
cd backend
pytest --cov=app tests/

# Frontend Coverage: Currently 0%, need 70%+
cd frontend
npm test -- --coverage
```

### Type Safety (Enable This)
```bash
# Frontend TypeScript strict mode
# In frontend/tsconfig.json:
"noUnusedLocals": true,        # ← Change from false
"noUnusedParameters": true     # ← Change from false

npm run type-check
```

### Code Quality (Run These)
```bash
# Backend
cd backend
black app --line-length=120
isort app
mypy app

# Frontend
cd frontend
npm run lint --fix
npm run type-check
```

### Complete TODOs (Find & Fix These)
1. `backend/app/routes/auth.py:117` - Verify Google token
2. `backend/app/routes/payments.py:116` - Retry PDF failures

---

## ✅ WHAT'S ALREADY GOOD

- ✅ Clean architecture (routes → services → models)
- ✅ FastAPI async setup with middleware
- ✅ SQLAlchemy ORM + Alembic migrations
- ✅ Docker multi-stage builds
- ✅ Stripe integration
- ✅ Groq LLM with retries
- ✅ SendGrid email service
- ✅ React auth context
- ✅ Protected routes
- ✅ Error handling & logging

---

## 📊 CRITICAL ISSUES SUMMARY

| Issue | Severity | Time to Fix | Impact |
|-------|----------|-------------|--------|
| Exposed API Key | CRITICAL | 5 min | Attacker can use Groq quota |
| Weak Password Hashing | CRITICAL | 30 min | All user passwords at risk |
| Missing Rate Limiting | HIGH | 20 min | Brute force attacks possible |
| Missing Security Headers | HIGH | 15 min | Clickjacking/XSS attacks |
| Low Test Coverage | HIGH | 8+ hours | Hidden bugs, regressions |
| Incomplete TODOs | HIGH | 3-4 hours | Features not fully working |
| TypeScript Strict Mode | MEDIUM | 2 hours | Dead code allowed |

**Total Time to CRITICAL fixes: 1.5 hours**  
**Total Time to PRODUCTION READY: 3-4 days**

---

## 🎯 15-ITEM TODO LIST (Organized)

### Phase 1: SECURITY (Today - 3 hours)
1. ✓ Rotate Groq API key
2. ✓ Replace HMAC password hashing with bcrypt
3. ✓ Add security headers middleware
4. ✓ Add rate limiting
5. ✓ Move .env to .gitignore and use GitHub Secrets

### Phase 2: TESTING (Days 1-2 - 10 hours)
6. ✓ Improve backend test coverage to 80%+
7. ✓ Add frontend component tests
8. ✓ Mock external services (Stripe, SendGrid, Groq)
9. ✓ Add integration tests for auth
10. ✓ Test payment routes

### Phase 3: CODE QUALITY (Days 1-2 - 6 hours)
11. ✓ Enable TypeScript strict mode
12. ✓ Run linting and fix all warnings
13. ✓ Fix mypy type errors
14. ✓ Remove unused imports/code
15. ✓ Add missing docstrings

### Phase 4: COMPLETION (Days 2-3 - 4 hours)
16. ✓ Complete Google OAuth verification
17. ✓ Implement PDF failure retry logic
18. ✓ Test database migrations
19. ✓ Add CSRF protection
20. ✓ Optimize database queries

---

## 📁 KEY FILES TO MODIFY

### Backend
- `backend/app/core/security.py` - Replace password hashing
- `backend/app/main.py` - Add middleware (headers, rate limiting)
- `backend/app/routes/auth.py` - Complete Google OAuth (line 117)
- `backend/app/routes/payments.py` - Add retry logic (line 116)
- `backend/requirements.txt` - Already has everything needed
- `backend/tests/` - Expand test coverage

### Frontend
- `frontend/tsconfig.json` - Enable strict mode
- `frontend/src/setupTests.ts` - Add test utilities
- `frontend/src/` - Add Jest tests

### DevOps
- `.gitignore` - Add `.env` entry
- `.github/workflows/ci-cd.yml` - Use GitHub Secrets
- `docker-compose.yml` - Already good

---

## 🔗 USEFUL COMMANDS

```bash
# Run backend tests with coverage
cd backend
pytest --cov=app --cov-report=term-missing tests/

# Run frontend tests with coverage
cd frontend
npm test -- --coverage

# Type checking
cd backend && mypy app
cd frontend && npm run type-check

# Linting
cd backend && black app --line-length=120 && isort app
cd frontend && npm run lint --fix

# Docker build test
docker-compose build

# Local dev server
cd backend && uvicorn app.main:app --reload --port 8000
cd frontend && npm run dev
```

---

## ⏰ TIMELINE ESTIMATE

| Phase | Duration | Checklist |
|-------|----------|-----------|
| **Phase 1: Security Critical** | 2-3 hours | [ ] Rotate keys [ ] Fix hashing [ ] Add headers [ ] Rate limit [ ] Update secrets |
| **Phase 2: High Priority** | 8-10 hours | [ ] Expand tests [ ] Enable strict TS [ ] Run linters [ ] Complete TODOs |
| **Phase 3: Medium Priority** | 6-8 hours | [ ] DB optimization [ ] Add CSRF [ ] Docker test [ ] Health checks |
| **Phase 4: Polish** | 4-6 hours | [ ] E2E tests [ ] Performance [ ] Documentation |
| **TOTAL** | **20-27 hours** | Production ready |

---

## 🚨 BEFORE YOU DEPLOY TO PRODUCTION

- [ ] All critical security issues fixed
- [ ] Test coverage ≥80% (backend), ≥70% (frontend)
- [ ] Zero high-severity lint/type errors
- [ ] All TODO items completed
- [ ] Database migrations tested
- [ ] HTTPS/TLS configured
- [ ] Secrets properly managed
- [ ] Rate limiting active
- [ ] Monitoring configured
- [ ] Backups tested

**Current Status: 🔴 NOT READY** - 4 critical blockers

---

**For full details, see:** `AUDIT_REPORT.md`
