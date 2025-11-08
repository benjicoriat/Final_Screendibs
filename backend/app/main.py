from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import datetime
from .core.config import settings
from .core.exceptions import global_exception_handler
from .core.logging import setup_logging, log_request_info
from .routes import auth, books, payments

# Set up logging
logger = setup_logging()

app = FastAPI(
    title="Screendibs API",
    description="Literary analysis report generation API",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc"
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    try:
        log_request_info({
            "method": request.method,
            "url": str(request.url),
            "client": request.client.host if request.client else "unknown"
        })
    except Exception:
        # don't let logging break requests
        pass
    response = await call_next(request)
    return response

# Security middlewares
allowed_host = settings.FRONTEND_URL.replace("http://", "").replace("https://", "").split(":")[0]
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[allowed_host, "localhost", "127.0.0.1"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# Compression middleware
app.add_middleware(GZipMiddleware)

# Exception handlers
app.add_exception_handler(Exception, global_exception_handler)

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Screendibs API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth")
app.include_router(books.router, prefix="/api/v1/books")
app.include_router(payments.router, prefix="/api/v1/payments")