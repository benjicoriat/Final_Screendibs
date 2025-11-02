from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..core.database import Base

class PlanType(str, enum.Enum):
    BASIC = "basic"
    DETAILED = "detailed"
    PREMIUM = "premium"

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stripe_payment_id = Column(String, unique=True, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="usd")
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)
    plan_type = Column(SQLEnum(PlanType), nullable=False)
    book_title = Column(String, nullable=False)
    book_author = Column(String, nullable=False)
    pdf_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User", back_populates="payments")