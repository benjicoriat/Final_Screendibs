"""Audit log model for tracking all data modifications."""

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import Column, DateTime, Integer, String, Text, Index

from ..core.database import Base


class AuditLog(Base):
    """Audit log entry for tracking all data modifications."""
    
    __tablename__ = "audit_logs"

    id: Any = Column(Integer, primary_key=True, index=True)
    
    # What was modified
    entity_type: Any = Column(String(50), nullable=False)  # e.g., "User", "Payment"
    entity_id: Any = Column(Integer, nullable=False)
    
    # How it was modified
    action: Any = Column(String(20), nullable=False)  # "INSERT", "UPDATE", "DELETE"
    
    # The changes
    changes: Any = Column(Text, nullable=True)  # JSON string of field changes {old: value, new: value}
    
    # Who modified it
    user_id: Any = Column(Integer, nullable=True)  # User who made the change (null for system)
    
    # When it was modified
    created_at: Any = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Additional context
    ip_address: Any = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent: Any = Column(String(500), nullable=True)  # Browser/client info
    reason: Any = Column(String(255), nullable=True)  # Optional reason for the change
    
    # Table constraints
    __table_args__ = (
        Index("ix_audit_logs_entity", "entity_type", "entity_id"),
        Index("ix_audit_logs_created_at", "created_at"),
        Index("ix_audit_logs_user_id", "user_id"),
        Index("ix_audit_logs_action", "action"),
    )
    
    def __repr__(self) -> str:
        return f"<AuditLog({self.entity_type} {self.entity_id} {self.action} @ {self.created_at})>"
