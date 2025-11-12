import datetime

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from .core.config import settings
from .core.database import SessionLocal
from .core.exceptions import global_exception_handler
from .core.logging import log_request_info, setup_logging
from .models.audit_listeners import set_session_factory, register_audit_listeners
from .routes import auth, books, payments

# Set up logging
logger = setup_logging()

app = FastAPI(
    title="Screendibs API",
    description="Literary analysis report generation API",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
)


@app.on_event("startup")
async def startup_event() -> None:
    """Initialize audit logging on app startup."""
    set_session_factory(SessionLocal)
    register_audit_listeners()
    logger.info("Audit listeners initialized")


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {"message": "Welcome to Screendibs API", "version": "1.0.0", "docs": "/docs"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


public_paths = ["/", "/health", "/api/v1/docs", "/api/v1/redoc", "/api/v1/openapi.json"]


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    try:
        log_request_info(
            {
                "method": request.method,
                "url": str(request.url),
                "client": request.client.host if request.client else "unknown",
            }
        )
    except Exception:
        # don't let logging break requests
        pass

    if request.url.path in public_paths:
        return await call_next(request)

    response = await call_next(request)
    return response


# Security middlewares
allowed_host = settings.FRONTEND_URL.replace("http://", "").replace("https://", "").split(":")[0]
# Allow common local/test hosts; include 'testserver' so TestClient requests don't get rejected
app.add_middleware(TrustedHostMiddleware, allowed_hosts=[allowed_host, "localhost", "127.0.0.1", "testserver"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Compression middleware
app.add_middleware(GZipMiddleware)


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


# Exception handlers
app.add_exception_handler(Exception, global_exception_handler)


def handle_rate_limit(request: Request, exc: RateLimitExceeded):
    """Return a consistent response when rate limits are exceeded."""

    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": "Rate limit exceeded"},
    )


app.add_exception_handler(RateLimitExceeded, handle_rate_limit)

# Rate limiting middleware
app.state.limiter = auth.limiter
app.add_middleware(SlowAPIMiddleware)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth")
app.include_router(auth.router, prefix="/auth")
app.include_router(books.router, prefix="/api/v1/books")
app.include_router(payments.router, prefix="/api/v1/payments")
