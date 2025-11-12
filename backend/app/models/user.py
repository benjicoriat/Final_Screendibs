from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, Column, DateTime, Integer, String, CheckConstraint, Index
from sqlalchemy.orm import relationship

from ..core.database import Base

if TYPE_CHECKING:
    from .payment import Payment


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(512), nullable=True)  # Nullable for OAuth users
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    google_id = Column(String(255), unique=True, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Soft delete tracking
    deleted_at = Column(DateTime, nullable=True, default=None)
    
    # Audit fields
    created_by = Column(Integer, nullable=True)  # User ID who created this record
    updated_by = Column(Integer, nullable=True)  # User ID who last updated this record

    # Table constraints
    __table_args__ = (
        CheckConstraint("email != ''", name="ck_users_email_not_empty"),
        Index("ix_users_is_active", "is_active"),
        Index("ix_users_created_at", "created_at"),
        Index("ix_users_deleted_at", "deleted_at"),  # For soft delete queries
    )

    # Relationships
    payments = relationship("Payment", back_populates="user", cascade="all, delete-orphan")  # type: ignore[misc]
    
    @property
    def is_deleted(self) -> bool:
        """Check if user is soft-deleted."""
        return self.deleted_at is not None
