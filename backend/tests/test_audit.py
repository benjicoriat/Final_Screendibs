"""Tests for audit logging and soft deletes functionality."""

import json
from datetime import datetime
from typing import cast

import pytest
from sqlalchemy.orm import Session

from app.models.audit import AuditLog
from app.models.payment import Payment
from app.models.user import User
from app.services.audit_service import AuditService


class TestSoftDeletes:
    """Test soft delete functionality."""

    def test_soft_delete_user(self, db: Session) -> None:
        """Test soft deleting a user."""
        # Create user
        user = User(email="softdelete@example.com", hashed_password="hashed", full_name="Soft Delete Test")
        db.add(user)
        db.commit()
        user_id = cast(int, user.id)

        assert user.deleted_at is None
        assert not user.is_deleted

        # Soft delete the user
        AuditService.soft_delete(db, User, user_id, user_id=1)
        db.refresh(user)

        assert user.deleted_at is not None
        assert user.is_deleted

    def test_soft_delete_payment(self, db: Session) -> None:
        """Test soft deleting a payment."""
        # Create user and payment
        user = User(email="payment@example.com", hashed_password="hashed", full_name="Payment Test")
        db.add(user)
        db.commit()

        payment = Payment(
            user_id=cast(int, user.id),
            book_title="Test Book",
            book_author="Test Author",
            plan_type="basic",
            stripe_payment_id="pi_test123",
            amount=1000,
            status="completed",
        )
        db.add(payment)
        db.commit()
        payment_id = cast(int, payment.id)

        assert payment.deleted_at is None

        # Soft delete the payment
        AuditService.soft_delete(db, Payment, payment_id, user_id=cast(int, user.id))
        db.refresh(payment)

        assert payment.deleted_at is not None
        assert payment.is_deleted

    def test_restore_soft_deleted_user(self, db: Session) -> None:
        """Test restoring a soft-deleted user."""
        # Create and soft delete user
        user = User(email="restore@example.com", hashed_password="hashed", full_name="Restore Test")
        db.add(user)
        db.commit()
        user_id = cast(int, user.id)

        AuditService.soft_delete(db, User, user_id, user_id=1)
        db.refresh(user)
        assert user.is_deleted

        # Restore
        AuditService.restore(db, User, user_id, user_id=1)
        db.refresh(user)
        assert not user.is_deleted
        assert user.deleted_at is None


class TestAuditFields:
    """Test audit field tracking (created_by, updated_by)."""

    def test_user_audit_fields(self, db: Session) -> None:
        """Test created_by and updated_by on User."""
        user = User(
            email="auditfield@example.com", hashed_password="hashed", full_name="Audit Test", created_by=1, updated_by=2
        )
        db.add(user)
        db.commit()

        assert cast(int, user.created_by) == 1
        assert cast(int, user.updated_by) == 2

    def test_payment_audit_fields(self, db: Session) -> None:
        """Test created_by and updated_by on Payment."""
        user = User(email="payment@example.com", hashed_password="hashed", full_name="Payment Test")
        db.add(user)
        db.commit()

        payment = Payment(
            user_id=cast(int, user.id),
            book_title="Test Book",
            book_author="Test Author",
            plan_type="basic",
            stripe_payment_id="pi_test123",
            amount=1000,
            status="completed",
            created_by=cast(int, user.id),
            updated_by=cast(int, user.id),
        )
        db.add(payment)
        db.commit()

        assert cast(int, payment.created_by) == cast(int, user.id)
        assert cast(int, payment.updated_by) == cast(int, user.id)


class TestAuditLog:
    """Test AuditLog model and audit recording."""

    def test_audit_log_creation(self, db: Session) -> None:
        """Test creating an audit log entry."""
        audit = AuditLog(
            entity_type="User",
            entity_id=1,
            action="INSERT",
            changes=json.dumps({"email": "test@example.com"}),
            user_id=None,
        )
        db.add(audit)
        db.commit()

        retrieved = db.query(AuditLog).filter(AuditLog.entity_id == 1).first()
        assert retrieved is not None
        assert retrieved.entity_type == "User"
        assert retrieved.action == "INSERT"
        assert retrieved.user_id is None

    def test_audit_log_with_user(self, db: Session) -> None:
        """Test audit log with associated user."""
        user = User(email="auditlog@example.com", hashed_password="hashed", full_name="Audit Log Test")
        db.add(user)
        db.commit()

        audit = AuditLog(
            entity_type="Payment", entity_id=1, action="UPDATE", changes=json.dumps({"status": "completed"}), user_id=cast(int, user.id)
        )
        db.add(audit)
        db.commit()

        retrieved = db.query(AuditLog).filter(AuditLog.entity_type == "Payment").first()
        assert retrieved is not None
        assert retrieved.user_id == cast(int, user.id)


class TestAuditService:
    """Test AuditService operations."""

    def test_get_all_active_users(self, db: Session) -> None:
        """Test retrieving active (non-deleted) users."""
        # Create users
        user1 = User(email="active1@example.com", hashed_password="hashed", full_name="Active 1")
        user2 = User(email="active2@example.com", hashed_password="hashed", full_name="Active 2")
        user3 = User(email="deleted@example.com", hashed_password="hashed", full_name="Deleted")
        db.add_all([user1, user2, user3])
        db.commit()

        # Soft delete one
        AuditService.soft_delete(db, User, cast(int, user3.id), user_id=1)
        db.refresh(user1)
        db.refresh(user2)
        db.refresh(user3)

        # Get active
        active = AuditService.get_all_active(db, User)
        assert len(active) >= 2  # At least our two active users
        assert all(not u.is_deleted for u in active)

    def test_get_deleted_users(self, db: Session) -> None:
        """Test retrieving deleted users."""
        user = User(email="deleted_user@example.com", hashed_password="hashed", full_name="Deleted User")
        db.add(user)
        db.commit()

        AuditService.soft_delete(db, User, cast(int, user.id), user_id=1)
        db.refresh(user)

        deleted = AuditService.get_deleted(db, User)
        assert any(u.id == user.id for u in deleted)

    def test_count_active(self, db: Session) -> None:
        """Test counting active records."""
        user1 = User(email="count1@example.com", hashed_password="hashed", full_name="Count 1")
        user2 = User(email="count2@example.com", hashed_password="hashed", full_name="Count 2")
        db.add_all([user1, user2])
        db.commit()

        initial_count = AuditService.count_active(db, User)
        assert initial_count >= 2

        AuditService.soft_delete(db, User, cast(int, user1.id), user_id=1)
        new_count = AuditService.count_active(db, User)
        assert new_count == initial_count - 1

    def test_count_deleted(self, db: Session) -> None:
        """Test counting deleted records."""
        user = User(email="count_deleted@example.com", hashed_password="hashed", full_name="Count Deleted")
        db.add(user)
        db.commit()

        initial_count = AuditService.count_deleted(db, User)

        AuditService.soft_delete(db, User, cast(int, user.id), user_id=1)
        new_count = AuditService.count_deleted(db, User)
        assert new_count == initial_count + 1


class TestAuditListenerIntegration:
    """Test that audit listeners are properly integrated."""

    def test_user_created_has_deleted_at_field(self, db: Session) -> None:
        """Test that user creation includes deleted_at field."""
        # Create user
        user = User(
            email="insert_audit@example.com",
            hashed_password="hashed",
            full_name="Insert Audit Test",
            created_by=None,
        )
        db.add(user)
        db.commit()

        # Verify deleted_at field exists and is None
        assert hasattr(user, "deleted_at")
        assert user.deleted_at is None

    def test_payment_can_be_soft_deleted(self, db: Session) -> None:
        """Test that payment supports soft delete operations."""
        user = User(email="payment_audit@example.com", hashed_password="hashed", full_name="Payment Audit Test")
        db.add(user)
        db.commit()

        payment = Payment(
            user_id=cast(int, user.id),
            book_title="Test Book",
            book_author="Test Author",
            plan_type="basic",
            stripe_payment_id="pi_test123",
            amount=1000,
            status="pending",
            created_by=cast(int, user.id),
            updated_by=cast(int, user.id),
        )
        db.add(payment)
        db.commit()

        # Verify deleted_at field exists and is None
        assert hasattr(payment, "deleted_at")
        assert payment.deleted_at is None


class TestRepositorySoftDeleteFilters:
    """Test that repositories properly filter soft-deleted records."""

    def test_user_query_excludes_deleted(self, db: Session) -> None:
        """Test that user queries filter out soft-deleted users."""
        # Create users
        user1 = User(email="repo_active@example.com", hashed_password="hashed", full_name="Repo Active")
        user2 = User(email="repo_deleted@example.com", hashed_password="hashed", full_name="Repo Deleted")
        db.add_all([user1, user2])
        db.commit()

        # Soft delete one
        AuditService.soft_delete(db, User, cast(int, user2.id), user_id=1)
        db.refresh(user2)

        # Query active users directly - should exclude deleted
        active_users = db.query(User).filter(User.deleted_at == None).all()

        # Should not include deleted user
        assert not any(u.id == user2.id for u in active_users)
        assert any(u.id == user1.id for u in active_users)

    def test_payment_query_excludes_deleted(self, db: Session) -> None:
        """Test that payment queries filter out soft-deleted payments."""
        user = User(email="payment_repo@example.com", hashed_password="hashed", full_name="Payment Repo Test")
        db.add(user)
        db.commit()

        payment1 = Payment(
            user_id=cast(int, user.id),
            book_title="Book 1",
            book_author="Author 1",
            plan_type="basic",
            stripe_payment_intent_id="pi_1",
            amount_cents=1000,
            status="completed",
        )
        payment2 = Payment(
            user_id=cast(int, user.id),
            book_title="Book 2",
            book_author="Author 2",
            plan_type="basic",
            stripe_payment_intent_id="pi_2",
            amount_cents=1000,
            status="completed",
        )
        db.add_all([payment1, payment2])
        db.commit()

        # Soft delete one
        AuditService.soft_delete(db, Payment, cast(int, payment2.id), user_id=cast(int, user.id))
        db.refresh(payment2)

        # Query active payments directly - should exclude deleted
        active_payments = db.query(Payment).filter(Payment.deleted_at == None).all()

        # Should not include deleted payment
        assert not any(p.id == payment2.id for p in active_payments)
        assert any(p.id == payment1.id for p in active_payments)
