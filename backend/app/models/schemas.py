import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator

from .payment import PaymentStatus, PlanType


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        password = value or ""
        has_min_length = len(password) >= 8
        has_upper = any(char.isupper() for char in password)
        has_lower = any(char.islower() for char in password)
        has_digit = any(char.isdigit() for char in password)
        has_special = bool(re.search(r"[^A-Za-z0-9]", password))

        if not all([has_min_length, has_upper, has_lower, has_digit, has_special]):
            raise ValueError(
                "Password must be at least 8 characters long and include upper, lower, digit, and special characters."
            )

        return password


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


# Book Search Schemas
class BookSearchRequest(BaseModel):
    description: str
    additional_details: Optional[str] = None

    @property
    def is_valid(self) -> bool:
        return bool(self.description and self.description.strip())

    # Use pydantic field validator so FastAPI/Pydantic return a 422 on invalid input
    @field_validator("description")
    @classmethod
    def check_description(cls, v):
        if v is None or not str(v).strip():
            raise ValueError("Description cannot be empty")
        return v


class BookInfo(BaseModel):
    title: str
    author: str
    year: str
    type: str
    description: str


# Payment Schemas
class PaymentCreate(BaseModel):
    plan_type: PlanType
    book_title: str
    book_author: str


class PaymentResponse(BaseModel):
    id: int
    amount: float  # Display as dollars (convert from cents in serializer)
    status: PaymentStatus
    plan_type: PlanType
    book_title: str
    book_author: str
    created_at: datetime

    @property
    def amount_dollars(self) -> float:
        """Convert cents to dollars for display."""
        return self.amount / 100

    class Config:
        from_attributes = True


# Report Generation
class ReportRequest(BaseModel):
    payment_id: int
