#!/usr/bin/env python
"""
Demo setup script - creates a test account for the frontend demo
"""
import os
import sys
import hashlib
import hmac

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import SessionLocal
from app.models.user import User
from datetime import datetime

def create_demo_user():
    """Create a demo user account"""
    db = SessionLocal()
    
    try:
        # Check if user already exists and delete it
        existing = db.query(User).filter(User.email == "ben.coriat@gmail.com").first()
        if existing:
            print(f"Deleting existing user...")
            db.delete(existing)
            db.commit()
        
        # Create HMAC hash for password
        password = "DemoPass123!"
        salt = "screendibs_demo"
        hashed_password = f"hmac_sha256${hmac.new(salt.encode(), password.encode(), hashlib.sha256).hexdigest()}"
        
        # Create new user
        demo_user = User(
            email="ben.coriat@gmail.com",
            full_name="Ben Coriat",
            hashed_password=hashed_password,
            is_active=True,
            is_verified=True,
            created_at=datetime.utcnow()
        )
        
        db.add(demo_user)
        db.commit()
        
        print("✅ Demo user created successfully!")
        print(f"Email: ben.coriat@gmail.com")
        print(f"Password: DemoPass123!")
        print(f"Full Name: Ben Coriat")
        
    except Exception as e:
        print(f"❌ Error creating demo user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_demo_user()
