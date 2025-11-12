from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database (default to local SQLite for development/testing)
    DATABASE_URL: str = "sqlite:///./app.db"

    # JWT
    SECRET_KEY: str = "change-me-in-prod"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Groq
    GROQ_API_KEY: Optional[str] = None

    # Stripe
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None

    # SendGrid
    SENDGRID_API_KEY: Optional[str] = None
    FROM_EMAIL: Optional[str] = None

    # Google OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None

    # Frontend
    FRONTEND_URL: str = "http://localhost:5173"

    # Environment
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()  # type: ignore[call-arg]
