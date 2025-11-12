"""Comprehensive tests for authentication routes and functionality."""

import pytest
from datetime import datetime, timedelta

from app.models.schemas import UserCreate, UserLogin
from app.core.security import get_password_hash, verify_password, create_access_token


@pytest.fixture
def test_user_data():
    """Fixture for test user data."""
    return {
        "email": "testuser@example.com",
        "password": "SecurePassword123!",
        "full_name": "Test User"
    }


class TestAuthRegistration:
    """Test user registration endpoint."""
    
    def test_register_new_user(self, client, test_user_data):
        """Test successful user registration."""
        response = client.post("/auth/register", json=test_user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["full_name"] == test_user_data["full_name"]
        assert "id" in data
    
    def test_register_duplicate_email(self, client, test_user_data):
        """Test registration with duplicate email fails."""
        # Register first user
        client.post("/auth/register", json=test_user_data)
        
        # Try to register with same email
        response = client.post("/auth/register", json=test_user_data)
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    def test_register_invalid_email(self, client):
        """Test registration with invalid email."""
        response = client.post("/auth/register", json={
            "email": "invalid-email",
            "password": "SecurePassword123!",
            "full_name": "Test User"
        })
        assert response.status_code == 422  # Validation error
    
    def test_register_weak_password(self, client):
        """Test registration with weak password."""
        response = client.post("/auth/register", json={
            "email": "test@example.com",
            "password": "weak",
            "full_name": "Test User"
        })
        assert response.status_code == 422


class TestAuthLogin:
    """Test user login and token generation."""
    
    def test_login_success(self, client, test_user_data):
        """Test successful login returns access token."""
        # Register user first
        client.post("/auth/register", json=test_user_data)
        
        # Login
        response = client.post("/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, client, test_user_data):
        """Test login with wrong password fails."""
        client.post("/auth/register", json=test_user_data)
        
        response = client.post("/auth/login", json={
            "email": test_user_data["email"],
            "password": "WrongPassword123!"
        })
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
    
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent email fails."""
        response = client.post("/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "AnyPassword123!"
        })
        assert response.status_code == 401
    
    def test_login_rate_limiting(self, client, test_user_data):
        """Test rate limiting on login attempts."""
        # Make multiple login attempts to trigger rate limit
        for i in range(6):
            response = client.post("/auth/login", json={
                "email": "any@example.com",
                "password": "anypassword"
            })
            if i < 5:
                assert response.status_code in [400, 401]
            else:
                # 6th request should be rate limited
                assert response.status_code == 429


class TestPasswordHashing:
    """Test password hashing and verification."""
    
    def test_password_hash_different(self):
        """Test that same password produces different hashes."""
        password = "TestPassword123!"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        assert hash1 != hash2  # Argon2ID should produce different hashes
    
    def test_password_verify_correct(self):
        """Test password verification with correct password."""
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True
    
    def test_password_verify_incorrect(self):
        """Test password verification with incorrect password."""
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        assert verify_password("WrongPassword", hashed) is False


class TestAccessToken:
    """Test JWT access token generation."""
    
    def test_create_access_token(self):
        """Test access token creation."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data=data)
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_access_token_with_expiry(self):
        """Test access token with custom expiry."""
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(hours=2)
        token = create_access_token(data=data, expires_delta=expires_delta)
        assert isinstance(token, str)
    
    def test_token_used_in_protected_route(self, client, test_user_data):
        """Test using token to access protected routes."""
        # Register and login
        client.post("/auth/register", json=test_user_data)
        login_response = client.post("/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        token = login_response.json()["access_token"]
        
        # Access protected route
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/payments/history", headers=headers)
        assert response.status_code == 200


class TestRegisterRateLimiting:
    """Test rate limiting on registration."""
    
    def test_register_rate_limiting(self, client):
        """Test rate limiting on registration attempts."""
        for i in range(4):
            response = client.post("/auth/register", json={
                "email": f"user{i}@example.com",
                "password": "SecurePassword123!",
                "full_name": f"User {i}"
            })
            assert response.status_code == 201
        
        # 4th request should trigger rate limit
        response = client.post("/auth/register", json={
            "email": "user4@example.com",
            "password": "SecurePassword123!",
            "full_name": "User 4"
        })
        assert response.status_code == 429


class TestTokenEndpoint:
    """Test OAuth2 token endpoint."""
    
    def test_token_endpoint_success(self, client, test_user_data):
        """Test token endpoint for Swagger UI compatibility."""
        # Register user
        client.post("/auth/register", json=test_user_data)
        
        # Get token via token endpoint
        response = client.post("/auth/token", data={
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
