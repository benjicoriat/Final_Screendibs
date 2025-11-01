from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .core.database import engine, Base
from .routes import auth, books, payments

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Screendibs API",
    description="Literary analysis report generation API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(books.router)
app.include_router(payments.router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Screendibs API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}