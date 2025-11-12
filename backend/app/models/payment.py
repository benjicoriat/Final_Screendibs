import enum
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, Column, DateTime, CheckConstraint, Index
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

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

    id: Any = Column(Integer, primary_key=True, index=True)
    user_id: Any = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    stripe_payment_id: Any = Column(String(255), unique=True, nullable=False, index=True)
    amount: Any = Column(Integer, nullable=False)  # Amount in cents for precision
    currency: Any = Column(String(3), default="usd", nullable=False)
    status: Any = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False, index=True)
    plan_type: Any = Column(SQLEnum(PlanType), nullable=False)
    book_title: Any = Column(String(255), nullable=False)
    book_author: Any = Column(String(255), nullable=False)
    pdf_sent: Any = Column(Boolean, default=False, nullable=False)
    created_at: Any = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Any = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Soft delete tracking
    deleted_at: Any = Column(DateTime, nullable=True, default=None)
    
    # Audit fields
    created_by: Any = Column(Integer, nullable=True)  # User ID who created this record
    updated_by: Any = Column(Integer, nullable=True)  # User ID who last updated this record
    
    user = relationship("User", back_populates="payments")  # type: ignore[misc]

    # Table constraints
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_payments_amount_positive"),
        CheckConstraint("book_title != ''", name="ck_payments_book_title_not_empty"),
        CheckConstraint("book_author != ''", name="ck_payments_book_author_not_empty"),
        Index("ix_payments_user_id_created_at", "user_id", "created_at"),
        Index("ix_payments_status_created_at", "status", "created_at"),
        Index("ix_payments_deleted_at", "deleted_at"),  # For soft delete queries
    )
    
    @property
    def is_deleted(self) -> bool:
        """Check if payment is soft-deleted."""
        return self.deleted_at is not None
