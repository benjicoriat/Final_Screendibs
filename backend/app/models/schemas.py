from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from .payment import PlanType, PaymentStatus
from pydantic import field_validator

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

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
    @field_validator('description')
    @classmethod
    def check_description(cls, v):
        if v is None or not str(v).strip():
            raise ValueError('Description cannot be empty')
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