"""Audit service for managing soft deletes and audit operations."""

from datetime import datetime
from typing import Any, List, Optional, Type, TypeVar

from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.audit import AuditLog
from app.models.user import User
from app.models.payment import Payment

T = TypeVar("T")


class AuditService:
    """Service for managing soft deletes and audit operations."""

    @staticmethod
    def soft_delete(db: Session, model: Type[T], id: int, user_id: Optional[int] = None) -> Optional[T]:
        """
        Soft delete an entity by setting deleted_at timestamp.
        
        Args:
            db: Database session
            model: Model class (User, Payment, etc)
            id: Entity ID to delete
            user_id: User ID performing the deletion
            
        Returns:
            Deleted entity or None if not found
        """
        obj = db.query(model).filter(model.id == id, model.deleted_at == None).first()  # type: ignore[attr-defined]
        if obj:
            obj.deleted_at = datetime.utcnow()  # type: ignore[attr-defined]
            obj.updated_by = user_id  # type: ignore[attr-defined]
            db.commit()
            db.refresh(obj)
        return obj

    @staticmethod
    def restore(db: Session, model: Type[T], id: int, user_id: Optional[int] = None) -> Optional[T]:
        """
        Restore a soft-deleted entity by clearing deleted_at timestamp.
        
        Args:
            db: Database session
            model: Model class (User, Payment, etc)
            id: Entity ID to restore
            user_id: User ID performing the restoration
            
        Returns:
            Restored entity or None if not found
        """
        obj = db.query(model).filter(model.id == id, model.deleted_at != None).first()  # type: ignore[attr-defined]
        if obj:
            obj.deleted_at = None  # type: ignore[attr-defined]
            obj.updated_by = user_id  # type: ignore[attr-defined]
            db.commit()
            db.refresh(obj)
        return obj

    @staticmethod
    def get_active(db: Session, model: Type[T], id: int) -> Optional[T]:
        """
        Get an entity, excluding soft-deleted ones.
        
        Args:
            db: Database session
            model: Model class
            id: Entity ID
            
        Returns:
            Entity if active, None otherwise
        """
        return db.query(model).filter(model.id == id, model.deleted_at == None).first()  # type: ignore[attr-defined]

    @staticmethod
    def get_all_active(db: Session, model: Type[T], skip: int = 0, limit: int = 100) -> List[T]:
        """
        Get all active (non-deleted) entities with pagination.
        
        Args:
            db: Database session
            model: Model class
            skip: Number of records to skip
            limit: Number of records to return
            
        Returns:
            List of active entities
        """
        return db.query(model).filter(model.deleted_at == None).offset(skip).limit(limit).all()  # type: ignore[attr-defined]

    @staticmethod
    def get_deleted(db: Session, model: Type[T], skip: int = 0, limit: int = 100) -> List[T]:
        """
        Get all soft-deleted entities with pagination.
        
        Args:
            db: Database session
            model: Model class
            skip: Number of records to skip
            limit: Number of records to return
            
        Returns:
            List of soft-deleted entities
        """
        return db.query(model).filter(model.deleted_at != None).offset(skip).limit(limit).all()  # type: ignore[attr-defined]

    @staticmethod
    def count_active(db: Session, model: Type[T]) -> int:
        """
        Count all active (non-deleted) entities.
        
        Args:
            db: Database session
            model: Model class
            
        Returns:
            Count of active entities
        """
        return db.query(model).filter(model.deleted_at == None).count()  # type: ignore[attr-defined]

    @staticmethod
    def count_deleted(db: Session, model: Type[T]) -> int:
        """
        Count all soft-deleted entities.
        
        Args:
            db: Database session
            model: Model class
            
        Returns:
            Count of deleted entities
        """
        return db.query(model).filter(model.deleted_at != None).count()  # type: ignore[attr-defined]

    @staticmethod
    def get_entity_audit_history(
        db: Session,
        entity_type: str,
        entity_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[AuditLog]:
        """
        Get audit history for a specific entity.
        
        Args:
            db: Database session
            entity_type: Type of entity (e.g., "User", "Payment")
            entity_id: ID of the entity
            skip: Number of records to skip
            limit: Number of records to return
            
        Returns:
            List of audit log entries
        """
        return (
            db.query(AuditLog)
            .filter(AuditLog.entity_type == entity_type, AuditLog.entity_id == entity_id)
            .order_by(AuditLog.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_user_audit_history(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[AuditLog]:
        """
        Get audit history for changes made by a specific user.
        
        Args:
            db: Database session
            user_id: ID of the user
            skip: Number of records to skip
            limit: Number of records to return
            
        Returns:
            List of audit log entries
        """
        return (
            db.query(AuditLog)
            .filter(AuditLog.user_id == user_id)
            .order_by(AuditLog.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_recent_audit_logs(
        db: Session,
        days: int = 7,
        skip: int = 0,
        limit: int = 100,
    ) -> List[AuditLog]:
        """
        Get recent audit logs from the last N days.
        
        Args:
            db: Database session
            days: Number of days to look back
            skip: Number of records to skip
            limit: Number of records to return
            
        Returns:
            List of audit log entries
        """
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return (
            db.query(AuditLog)
            .filter(AuditLog.created_at >= cutoff_date)
            .order_by(AuditLog.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
