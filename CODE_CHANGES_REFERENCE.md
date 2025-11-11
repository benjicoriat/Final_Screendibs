# 🔧 AUDIT REMEDIATION - CODE CHANGES REFERENCE

## File-by-File Changes Required

---

## PHASE 1: CRITICAL SECURITY FIXES

### 1️⃣ backend/app/core/security.py
**Issue:** Weak HMAC-SHA256 password hashing  
**Fix:** Replace with bcrypt via passlib

**REPLACE THIS:**
```python
import hashlib
import hmac

class SimplePasswordContext:
    """Fallback password hasher using HMAC"""
    
    @staticmethod
    def hash(password: str) -> str:
        """Hash password using HMAC"""
        salt = "screendibs_demo"
        hashed = hmac.new(
            salt.encode(),
            password.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"hmac_sha256${hashed}"
    
    @staticmethod
    def verify(plain_password: str, hashed_password: str) -> bool:
        """Verify password"""
        if not hashed_password.startswith("hmac_sha256$"):
            return False
        
        salt = "screendibs_demo"
        expected_hash = hmac.new(
            salt.encode(),
            plain_password.encode(),
            hashlib.sha256
        ).hexdigest()
        
        stored_hash = hashed_password.replace("hmac_sha256$", "")
        return hmac.compare_digest(expected_hash, stored_hash)

pwd_context = SimplePasswordContext()
```

**WITH THIS:**
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
```

---

### 2️⃣ backend/app/main.py
**Issue:** Missing security headers and rate limiting  
**Fix:** Add middleware

**ADD AFTER line 50 (after GZipMiddleware):**
```python
# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if settings.ENVIRONMENT == "production":
        response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response

# Rate limiting middleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def _rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please try again later."}
    )
```

**THEN ADD to routes:**
```python
# In backend/app/routes/auth.py, add to imports:
from fastapi import Depends, HTTPException, status
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# Apply to endpoints:
@router.post("/register")
@limiter.limit("3/minute")
async def register(user: UserCreate, request: Request, db: Session = Depends(get_db)):
    # ... existing code

@router.post("/login")
@limiter.limit("5/minute")
async def login(user: UserLogin, request: Request, db: Session = Depends(get_db)):
    # ... existing code
```

---

### 3️⃣ .gitignore
**Issue:** .env file tracked in git with exposed keys  
**Fix:** Add to .gitignore

**ADD:**
```
# Environment variables (SECURITY: Never commit these)
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
.pytest_cache/
.coverage
.mypy_cache/

# Node
node_modules/
npm-debug.log
yarn-error.log

# OS
.DS_Store
Thumbs.db

# Logs
logs/
*.log

# Database
*.db
screendibs.db
```

---

## PHASE 2: TESTING & TYPE SAFETY

### 4️⃣ frontend/tsconfig.json
**Issue:** Strict mode disabled allows dead code  
**Fix:** Enable strict mode

**CHANGE:**
```json
"noUnusedLocals": false,       // Change to: true
"noUnusedParameters": false    // Change to: true
```

**ALSO ADD:**
```json
"forceConsistentCasingInFileNames": true,
"resolveJsonModule": true
```

---

### 5️⃣ backend/pyproject.toml
**Issue:** Coverage threshold not enforced  
**Fix:** Verify configuration

**ENSURE THIS EXISTS:**
```toml
[tool.coverage.report]
fail_under = 80
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "pass",
    "raise ImportError",
]
```

---

### 6️⃣ backend/tests/test_auth.py (NEW FILE)
**Create comprehensive auth tests:**

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.user import User
from datetime import datetime

client = TestClient(app)

@pytest.mark.asyncio
async def test_register_success():
    """Test successful user registration"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "TestPass123!",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

@pytest.mark.asyncio
async def test_register_duplicate_email():
    """Test registration with existing email"""
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "TestPass123!",
            "full_name": "Test User"
        }
    )
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "AnotherPass123!",
            "full_name": "Another User"
        }
    )
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_login_success():
    """Test successful login"""
    # Register first
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "login@example.com",
            "password": "LoginPass123!",
            "full_name": "Login User"
        }
    )
    # Login
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "login@example.com",
            "password": "LoginPass123!"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_wrong_password():
    """Test login with wrong password"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "WrongPass123!"
        }
    )
    assert response.status_code == 401
```

---

### 7️⃣ frontend/src/setupTests.ts
**Configure Jest environment:**

```typescript
import '@testing-library/jest-dom';
import { server } from './mocks/server';

// Establish API mocking before all tests
beforeAll(() => server.listen());

// Reset any request handlers that we may add during the tests
afterEach(() => server.resetHandlers());

// Clean up after the tests are finished
afterAll(() => server.close());

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});
```

---

## PHASE 3: COMPLETE TODOs

### 8️⃣ backend/app/routes/auth.py
**Issue:** Google OAuth not validating token  
**Location:** Line 117

**REPLACE TODO:**
```python
# TODO: Verify Google token with Google's API

# WITH:

from google.auth.transport import requests
from google.oauth2 import id_token

@router.post("/google-login")
async def google_login(token: str, db: Session = Depends(get_db)):
    """Login or register with Google OAuth token"""
    try:
        # Verify the token with Google
        request = requests.Request()
        id_info = id_token.verify_oauth2_token(
            token, 
            request, 
            settings.GOOGLE_CLIENT_ID
        )
        
        # Get or create user
        user = db.query(User).filter(User.google_id == id_info['sub']).first()
        if not user:
            user = User(
                email=id_info.get('email'),
                full_name=id_info.get('name'),
                google_id=id_info['sub'],
                is_verified=True  # Google already verified
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Create access token
        access_token = create_access_token(data={"sub": user.email})
        return {"access_token": access_token, "token_type": "bearer"}
        
    except ValueError as e:
        raise HTTPException(
            status_code=401,
            detail="Invalid Google token",
            headers={"WWW-Authenticate": "Bearer"}
        )
```

---

### 9️⃣ backend/app/routes/payments.py
**Issue:** No retry logic for PDF sending  
**Location:** Line 116

**ADD RETRY LOGIC:**
```python
import asyncio
from functools import wraps

def retry_with_backoff(max_retries: int = 3, base_delay: int = 1):
    """Decorator for retry logic with exponential backoff"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Failed after {max_retries} attempts: {e}")
                        raise
                    delay = base_delay * (2 ** attempt)
                    logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay}s: {e}")
                    await asyncio.sleep(delay)
        return wrapper
    return decorator

@retry_with_backoff(max_retries=3)
async def send_report_with_retry(payment_id: int, db: Session):
    """Generate and send report with retry logic"""
    # Get payment details
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise Exception(f"Payment {payment_id} not found")
    
    # Generate PDF
    report_service = ReportGeneratorService()
    pdf_path = report_service.generate_pdf(payment)
    
    # Send email
    email_service = EmailService()
    email_service.send_report_email(
        to_email=payment.user.email,
        subject=f"Your {payment.book_title} Analysis Report",
        pdf_path=pdf_path
    )
    
    # Update payment status
    payment.pdf_sent = True
    payment.status = PaymentStatus.COMPLETED
    db.commit()
    
    logger.info(f"Successfully sent report for payment {payment_id}")

# Update the create_payment_intent response:
async def handle_successful_payment(payment_id: int, background_tasks: BackgroundTasks, db: Session):
    """Handle successful payment in background"""
    try:
        await send_report_with_retry(payment_id, db)
    except Exception as e:
        logger.error(f"Failed to send report for payment {payment_id}: {e}")
        # Update payment to failed
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if payment:
            payment.status = PaymentStatus.FAILED
            db.commit()
        # Could also send notification to admin here
```

---

## PHASE 4: CODE QUALITY

### 🔟 Commands to Run

```bash
# Backend formatting
cd backend
black app --line-length=120
isort app

# Backend type checking
mypy app --strict

# Backend testing
pytest --cov=app --cov-report=term-missing tests/

# Frontend linting
cd ../frontend
npm run lint --fix

# Frontend type checking
npm run type-check

# Frontend testing
npm test -- --coverage --watchAll=false
```

---

## SECURITY CHECKLIST

- [ ] Rotated Groq API key
- [ ] Replaced HMAC with bcrypt in security.py
- [ ] Added security headers middleware
- [ ] Added rate limiting to auth endpoints
- [ ] Moved .env to .gitignore
- [ ] Created GitHub Secrets for all API keys
- [ ] Updated CI/CD to use secrets
- [ ] Tested login/registration with new password hashing
- [ ] Verified rate limiting blocks excessive requests
- [ ] Confirmed security headers in responses

---

## DEPLOYMENT CHECKLIST

After all changes:

```bash
# 1. Test locally
docker-compose up -d
# Visit http://localhost:3000 for frontend
# Visit http://localhost:8000/docs for API

# 2. Run all tests
cd backend && pytest --cov=app tests/
cd ../frontend && npm test -- --coverage

# 3. Type check
cd backend && mypy app --strict
cd ../frontend && npm run type-check

# 4. Lint check
cd backend && black app --check && isort app --check
cd ../frontend && npm run lint

# 5. Build docker
docker-compose build

# 6. Create .env from .env.example (with real secrets)
cp backend/.env.example backend/.env
# Edit backend/.env with actual keys

# 7. Push to production
git push origin main
# GitHub Actions will build and deploy
```

---

**Total Implementation Time: 20-27 hours**  
**Critical Fixes Only: 2-3 hours**
