"""Comprehensive tests for payment routes and functionality."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.models.payment import Payment, PaymentStatus, PlanType
from app.models.schemas import PaymentCreate
from app.core.database import get_db
from sqlalchemy.orm import Session


@pytest.fixture
def auth_headers(client, test_user_data):
    """Get authenticated headers."""
    client.post("/auth/register", json=test_user_data)
    response = client.post("/auth/login", json={
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def payment_data():
    """Fixture for payment data."""
    return {
        "plan_type": "basic",
        "book_title": "Test Book",
        "book_author": "Test Author"
    }


class TestCreatePaymentIntent:
    """Test payment intent creation."""
    
    @patch('stripe.PaymentIntent.create')
    def test_create_payment_intent_basic(self, mock_stripe, client, auth_headers, payment_data, test_user_data):
        """Test creating a payment intent for basic plan."""
        # Mock Stripe response
        mock_stripe.return_value = MagicMock(
            id="pi_test_123",
            client_secret="pi_test_123_secret",
            status="requires_payment_method"
        )
        
        response = client.post(
            "/payments/create-payment-intent",
            json=payment_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "clientSecret" in data
        assert "paymentId" in data
        assert data["clientSecret"] == "pi_test_123_secret"
    
    @patch('stripe.PaymentIntent.create')
    def test_create_payment_intent_detailed(self, mock_stripe, client, auth_headers, test_user_data):
        """Test creating payment intent for detailed plan."""
        payment_data = {
            "plan_type": "detailed",
            "book_title": "Book Title",
            "book_author": "Author Name"
        }
        
        mock_stripe.return_value = MagicMock(
            id="pi_test_456",
            client_secret="pi_test_456_secret",
            status="requires_payment_method"
        )
        
        response = client.post(
            "/payments/create-payment-intent",
            json=payment_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
    
    @patch('stripe.PaymentIntent.create')
    def test_create_payment_intent_premium(self, mock_stripe, client, auth_headers, test_user_data):
        """Test creating payment intent for premium plan."""
        payment_data = {
            "plan_type": "premium",
            "book_title": "Book Title",
            "book_author": "Author Name"
        }
        
        mock_stripe.return_value = MagicMock(
            id="pi_test_789",
            client_secret="pi_test_789_secret",
            status="requires_payment_method"
        )
        
        response = client.post(
            "/payments/create-payment-intent",
            json=payment_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
    
    def test_create_payment_intent_invalid_plan(self, client, auth_headers):
        """Test creating payment intent with invalid plan type."""
        response = client.post(
            "/payments/create-payment-intent",
            json={
                "plan_type": "invalid_plan",
                "book_title": "Book",
                "book_author": "Author"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 422
    
    def test_create_payment_intent_unauthenticated(self, client, payment_data):
        """Test creating payment intent without authentication."""
        response = client.post(
            "/payments/create-payment-intent",
            json=payment_data
        )
        
        assert response.status_code == 403


class TestPaymentVerification:
    """Test payment verification."""
    
    @patch('stripe.PaymentIntent.retrieve')
    def test_verify_payment_success(self, mock_retrieve, client, auth_headers, test_user_data):
        """Test verifying a successful payment."""
        # First create payment
        with patch('stripe.PaymentIntent.create') as mock_create:
            mock_create.return_value = MagicMock(
                id="pi_test_123",
                client_secret="secret"
            )
            
            client.post(
                "/payments/create-payment-intent",
                json={
                    "plan_type": "basic",
                    "book_title": "Book",
                    "book_author": "Author"
                },
                headers=auth_headers
            )
        
        # Now verify payment
        mock_retrieve.return_value = MagicMock(
            id="pi_test_123",
            status="succeeded"
        )
        
        response = client.post(
            "/payments/verify/1",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert "success" in response.json()["status"].lower()
    
    @patch('stripe.PaymentIntent.retrieve')
    def test_verify_payment_pending(self, mock_retrieve, client, auth_headers, test_user_data):
        """Test verifying a pending payment."""
        with patch('stripe.PaymentIntent.create'):
            client.post(
                "/payments/create-payment-intent",
                json={
                    "plan_type": "basic",
                    "book_title": "Book",
                    "book_author": "Author"
                },
                headers=auth_headers
            )
        
        mock_retrieve.return_value = MagicMock(
            status="requires_payment_method"
        )
        
        response = client.post(
            "/payments/verify/1",
            headers=auth_headers
        )
        
        assert response.status_code == 400


class TestPaymentHistory:
    """Test payment history retrieval."""
    
    @patch('stripe.PaymentIntent.create')
    def test_get_payment_history_empty(self, mock_stripe, client, auth_headers):
        """Test getting payment history when no payments exist."""
        response = client.get(
            "/payments/history",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert response.json() == []
    
    @patch('stripe.PaymentIntent.create')
    def test_get_payment_history_with_payments(self, mock_stripe, client, auth_headers, test_user_data):
        """Test getting payment history with existing payments."""
        mock_stripe.return_value = MagicMock(
            id="pi_test_123",
            client_secret="secret"
        )
        
        # Create a payment
        client.post(
            "/payments/create-payment-intent",
            json={
                "plan_type": "basic",
                "book_title": "Book 1",
                "book_author": "Author 1"
            },
            headers=auth_headers
        )
        
        # Get history
        response = client.get(
            "/payments/history",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert data[0]["book_title"] == "Book 1"
    
    def test_get_payment_history_unauthenticated(self, client):
        """Test getting payment history without authentication."""
        response = client.get("/payments/history")
        assert response.status_code == 403


class TestPaymentValidation:
    """Test payment data validation."""
    
    def test_payment_missing_fields(self, client, auth_headers):
        """Test payment creation with missing fields."""
        response = client.post(
            "/payments/create-payment-intent",
            json={"plan_type": "basic"},
            headers=auth_headers
        )
        
        assert response.status_code == 422
    
    def test_payment_empty_book_title(self, client, auth_headers):
        """Test payment with empty book title."""
        response = client.post(
            "/payments/create-payment-intent",
            json={
                "plan_type": "basic",
                "book_title": "",
                "book_author": "Author"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 422
    
    def test_payment_empty_author(self, client, auth_headers):
        """Test payment with empty author."""
        response = client.post(
            "/payments/create-payment-intent",
            json={
                "plan_type": "basic",
                "book_title": "Book",
                "book_author": ""
            },
            headers=auth_headers
        )
        
        assert response.status_code == 422
