from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from .payment import PlanType, PaymentStatus

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
        
    def __init__(self, **data):
        super().__init__(**data)
        if not self.description or not self.description.strip():
            raise ValueError("Description cannot be empty")

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
    amount: float
    status: PaymentStatus
    plan_type: PlanType
    book_title: str
    book_author: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Report Generation
class ReportRequest(BaseModel):
    payment_id: int