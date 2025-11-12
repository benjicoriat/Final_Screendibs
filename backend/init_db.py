#!/usr/bin/env python
"""Initialize database with fresh schema"""
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import Base, engine
from app.models.user import User
from app.models.payment import Payment
from app.models.audit import AuditLog
from app.core.security import get_password_hash

print("Dropping all tables...")
Base.metadata.drop_all(bind=engine)

print("Creating all tables...")
Base.metadata.create_all(bind=engine)

print("✅ Database initialized successfully!")
print("\nCreating demo user...")

from app.core.database import SessionLocal

db = SessionLocal()
try:
    demo_user = User(
        email="ben.coriat@gmail.com",
        hashed_password=get_password_hash("DemoPass123!"),
        full_name="Ben Coriat",
        is_active=True,
        is_verified=True
    )
    db.add(demo_user)
    db.commit()
    db.refresh(demo_user)
    print("✅ Demo user created successfully!")
    print(f"   Email: {demo_user.email}")
    print(f"   Password: DemoPass123!")
except Exception as e:
    print(f"❌ Error creating demo user: {e}")
    db.rollback()
finally:
    db.close()
