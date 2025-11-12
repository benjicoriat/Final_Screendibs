"""SQLAlchemy event listeners for automatic audit logging."""

import json
from typing import Any, Dict, Optional, Callable

from sqlalchemy import event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.inspection import inspect as sa_inspect

from app.models.audit import AuditLog
from app.models.user import User
from app.models.payment import Payment


# Models to audit
AUDITED_MODELS = {User, Payment}

# Global session maker - will be set during app initialization
_session_factory: Optional[sessionmaker[Session]] = None  # type: ignore[type-arg]


def set_session_factory(factory: sessionmaker[Session]) -> None:  # type: ignore[type-arg]
    """Set the session factory for audit logging."""
    global _session_factory
    _session_factory = factory


def get_audit_session() -> Session:
    """Get a new session for audit logging."""
    global _session_factory
    if _session_factory is None:
        raise RuntimeError("Session factory not initialized. Call set_session_factory() on app startup.")
    return _session_factory()


def log_audit_event(
    session: Session,
    entity_type: str,
    entity_id: int,
    action: str,
    changes: Optional[Dict[str, Any]] = None,
    user_id: Optional[int] = None,
) -> None:
    """Create an audit log entry."""
    try:
        audit_log = AuditLog(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            changes=json.dumps(changes) if changes else None,
            user_id=user_id,
        )
        session.add(audit_log)
        session.flush()
    except Exception as e:
        # Log but don't fail the main transaction
        print(f"Error creating audit log: {e}")


def extract_changes(instance: Any) -> Dict[str, Any]:
    """Extract changed fields from an ORM instance."""
    changes: Dict[str, Any] = {}
    insp = sa_inspect(instance)
    
    if insp is None:
        return changes
    
    mapper = insp.mapper
    for col in mapper.columns:
        if col.name in ("created_at", "updated_at", "id"):
            continue
        
        history = insp.get_attribute_history(col.name)
        if history.has_changes():
            old_value = history.deleted[0] if history.deleted else None
            new_value = history.added[0] if history.added else None
            
            changes[col.name] = {
                "old": str(old_value) if old_value is not None else None,
                "new": str(new_value) if new_value is not None else None,
            }
    
    return changes


@event.listens_for(User, "after_insert", propagate=True)
def receive_user_after_insert(mapper: Any, connection: Any, target: User) -> None:
    """Audit log for user creation."""
    try:
        session = get_audit_session()
        try:
            entity_id: Optional[int] = getattr(target, "id", None)
            user_id: Optional[int] = getattr(target, "created_by", None)
            if entity_id is not None:
                log_audit_event(
                    session,
                    entity_type="User",
                    entity_id=entity_id,
                    action="INSERT",
                    user_id=user_id,
                )
                session.commit()
        except Exception as e:
            session.rollback()
            print(f"Audit log error: {e}")
        finally:
            session.close()
    except Exception as e:
        print(f"Failed to get audit session: {e}")


@event.listens_for(User, "after_update", propagate=True)
def receive_user_after_update(mapper: Any, connection: Any, target: User) -> None:
    """Audit log for user updates."""
    try:
        session = get_audit_session()
        try:
            changes = extract_changes(target)
            entity_id: Optional[int] = getattr(target, "id", None)
            user_id: Optional[int] = getattr(target, "updated_by", None)
            
            if changes and entity_id is not None:
                log_audit_event(
                    session,
                    entity_type="User",
                    entity_id=entity_id,
                    action="UPDATE",
                    changes=changes,
                    user_id=user_id,
                )
                session.commit()
        except Exception as e:
            session.rollback()
            print(f"Audit log error: {e}")
        finally:
            session.close()
    except Exception as e:
        print(f"Failed to get audit session: {e}")


@event.listens_for(Payment, "after_insert", propagate=True)
def receive_payment_after_insert(mapper: Any, connection: Any, target: Payment) -> None:
    """Audit log for payment creation."""
    try:
        session = get_audit_session()
        try:
            entity_id: Optional[int] = getattr(target, "id", None)
            user_id: Optional[int] = getattr(target, "created_by", None)
            if entity_id is not None:
                log_audit_event(
                    session,
                    entity_type="Payment",
                    entity_id=entity_id,
                    action="INSERT",
                    user_id=user_id,
                )
                session.commit()
        except Exception as e:
            session.rollback()
            print(f"Audit log error: {e}")
        finally:
            session.close()
    except Exception as e:
        print(f"Failed to get audit session: {e}")


@event.listens_for(Payment, "after_update", propagate=True)
def receive_payment_after_update(mapper: Any, connection: Any, target: Payment) -> None:
    """Audit log for payment updates."""
    try:
        session = get_audit_session()
        try:
            changes = extract_changes(target)
            entity_id: Optional[int] = getattr(target, "id", None)
            user_id: Optional[int] = getattr(target, "updated_by", None)
            
            if changes and entity_id is not None:
                log_audit_event(
                    session,
                    entity_type="Payment",
                    entity_id=entity_id,
                    action="UPDATE",
                    changes=changes,
                    user_id=user_id,
                )
                session.commit()
        except Exception as e:
            session.rollback()
            print(f"Audit log error: {e}")
        finally:
            session.close()
    except Exception as e:
        print(f"Failed to get audit session: {e}")


def register_audit_listeners() -> None:
    """Register all audit event listeners. Call this on application startup."""
    # Listeners are registered via decorators above
    # This function can be expanded for additional setup
    pass
