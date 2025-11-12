"""Database query utilities for common patterns and optimizations."""

from typing import Any, Dict, List, Optional, Type, TypeVar

from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload

from .database import Base

T = TypeVar("T", bound=Base)


class QueryHelper:
    """Helper class for common database query patterns."""

    @staticmethod
    def get_by_id(db: Session, model: Type[T], id: Any) -> Optional[T]:
        """Get a single record by ID."""
        return db.query(model).filter(model.id == id).first()  # type: ignore[attr-defined]

    @staticmethod
    def get_all(db: Session, model: Type[T], skip: int = 0, limit: int = 100) -> List[T]:
        """Get all records with pagination."""
        return db.query(model).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_filter(
        db: Session, model: Type[T], filter_dict: Dict[str, Any]
    ) -> Optional[T]:
        """Get a single record matching multiple filters."""
        query = db.query(model)
        for key, value in filter_dict.items():
            if hasattr(model, key):
                query = query.filter(getattr(model, key) == value)
        return query.first()

    @staticmethod
    def get_all_by_filter(
        db: Session,
        model: Type[T],
        filter_dict: Dict[str, Any],
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[Any] = None,
    ) -> List[T]:
        """Get all records matching multiple filters with pagination."""
        query = db.query(model)
        for key, value in filter_dict.items():
            if hasattr(model, key):
                query = query.filter(getattr(model, key) == value)  # type: ignore[attr-defined]

        if order_by is not None:
            query = query.order_by(order_by)

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def create(db: Session, model: Type[T], **kwargs: Any) -> T:
        """Create a new record."""
        obj = model(**kwargs)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    @staticmethod
    def update(db: Session, obj: Any, update_dict: Dict[str, Any]) -> Any:
        """Update an existing record."""
        for key, value in update_dict.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        db.commit()
        db.refresh(obj)
        return obj

    @staticmethod
    def delete(db: Session, obj: Any) -> None:
        """Delete a record."""
        db.delete(obj)
        db.commit()

    @staticmethod
    def count(db: Session, model: Type[T], filter_dict: Optional[Dict[str, Any]] = None) -> int:
        """Count records matching optional filters."""
        query = db.query(model)
        if filter_dict:
            for key, value in filter_dict.items():
                if hasattr(model, key):
                    query = query.filter(getattr(model, key) == value)  # type: ignore[attr-defined]
        return query.count()
