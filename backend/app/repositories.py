"""Repository pattern for complex database queries with eager loading."""

from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.models.payment import Payment, PaymentStatus
from app.models.user import User


class UserRepository:
    """Repository for User-related queries with eager loading."""

    @staticmethod
    def get_user_with_payments(db: Session, user_id: int) -> Optional[User]:
        """Get user with all their payments eagerly loaded (excludes soft-deleted)."""
        return (
            db.query(User)
            .options(joinedload(User.payments))
            .filter(User.id == user_id, User.deleted_at == None)
            .first()
        )

    @staticmethod
    def get_active_users_with_payments(
        db: Session, skip: int = 0, limit: int = 100
    ) -> List[User]:
        """Get active users with payments eagerly loaded (excludes soft-deleted)."""
        return (
            db.query(User)
            .filter(User.is_active == True, User.deleted_at == None)
            .options(joinedload(User.payments))
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_user_by_email_with_payments(db: Session, email: str) -> Optional[User]:
        """Get user by email with payments eagerly loaded (excludes soft-deleted)."""
        return (
            db.query(User)
            .options(joinedload(User.payments))
            .filter(User.email == email, User.deleted_at == None)
            .first()
        )


class PaymentRepository:
    """Repository for Payment-related queries with eager loading."""

    @staticmethod
    def get_payment_with_user(db: Session, payment_id: int) -> Optional[Payment]:
        """Get payment with user details eagerly loaded (excludes soft-deleted)."""
        return (
            db.query(Payment)
            .options(joinedload(Payment.user))
            .filter(Payment.id == payment_id, Payment.deleted_at == None)
            .first()
        )

    @staticmethod
    def get_user_payments_with_user(
        db: Session, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Payment]:
        """Get all payments for a user with user details eagerly loaded (excludes soft-deleted)."""
        return (
            db.query(Payment)
            .filter(Payment.user_id == user_id, Payment.deleted_at == None)
            .options(joinedload(Payment.user))
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_user_payments_by_status(
        db: Session,
        user_id: int,
        status: PaymentStatus,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Payment]:
        """Get user payments filtered by status with user eagerly loaded (excludes soft-deleted)."""
        return (
            db.query(Payment)
            .filter(Payment.user_id == user_id, Payment.status == status, Payment.deleted_at == None)
            .options(joinedload(Payment.user))
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_payments_by_status(
        db: Session, status: PaymentStatus, skip: int = 0, limit: int = 100
    ) -> List[Payment]:
        """Get all payments with a specific status (excludes soft-deleted)."""
        return (
            db.query(Payment)
            .filter(Payment.status == status, Payment.deleted_at == None)
            .options(joinedload(Payment.user))
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_payment_by_stripe_id(db: Session, stripe_payment_id: str) -> Optional[Payment]:
        """Get payment by Stripe payment ID with user eagerly loaded (excludes soft-deleted)."""
        return (
            db.query(Payment)
            .options(joinedload(Payment.user))
            .filter(Payment.stripe_payment_id == stripe_payment_id, Payment.deleted_at == None)
            .first()
        )

    @staticmethod
    def count_user_payments(
        db: Session, user_id: int, status: Optional[PaymentStatus] = None
    ) -> int:
        """Count user payments, optionally filtered by status (excludes soft-deleted)."""
        query = db.query(Payment).filter(Payment.user_id == user_id, Payment.deleted_at == None)
        if status:
            query = query.filter(Payment.status == status)
        return query.count()
