import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app
from app.services.book_search import BookSearchService
from app.models.schemas import BookSearchRequest
from app.utils.auth import get_current_active_user
from app.models.user import User
from datetime import datetime

async def mock_get_current_active_user():
    return User(
        id=1, 
        email="test@example.com", 
        full_name="Test User",
        hashed_password="fake_hashed_password",
        is_active=True,
        is_verified=True,
        created_at=datetime.utcnow()
    )

def mock_groq():
    mock_instance = MagicMock()
    mock_completion = MagicMock(
        choices=[
            MagicMock(
                message=MagicMock(
                    content='[{"title": "Test Book", "author": "Test Author", "year": "2023", "type": "Fiction", "description": "A test book. Another sentence about the book."}]'
                )
            )
        ]
    )
    mock_instance.chat.completions.create.return_value = mock_completion
    return mock_instance

@pytest.fixture(autouse=True)
def setup_groq_mock():
    with patch('app.services.book_search.Groq', return_value=mock_groq()) as _mock:
        yield _mock

# Using client fixture from conftest.py

def test_search_books_success(client):
    mock_books = [
        {
            "id": "1",
            "title": "Test Book",
            "author": "Test Author",
            "year": 2023,
            "genre": "Fiction",
            "description": "A test book",
        }
    ]
    
    with patch.object(
        BookSearchService,
        'search_books',
        return_value=mock_books
    ):
            response = test_client.post(
                "/api/v1/books/search",
                json={"description": "test book", "additional_details": "Fiction"}
            )
            assert response.status_code == 200
            assert response.json() == mock_books

def test_search_books_empty_query(test_client):
    response = test_client.post(
        "/api/v1/books/search",
        json={"description": ""}
    )

    assert response.status_code == 422

def test_search_books_service_error(test_client):
    with patch.object(
        BookSearchService,
        'search_books',
        side_effect=Exception("Search service error")
    ):
        response = test_client.post(
            "/api/v1/books/search",
            json={"description": "test book"}
        )
        
        assert response.status_code == 500
        assert "error" in response.json()

def test_search_validation():
    request = BookSearchRequest(description="test", additional_details="Fiction book")
    assert request.description == "test"
    assert request.additional_details == "Fiction book"

    with pytest.raises(ValueError):
        BookSearchRequest(query="", filters={})

@pytest.mark.asyncio
async def test_book_search_service():
    service = BookSearchService()
    
    # Mock external API call
    with patch('app.services.book_search.Groq') as mock_groq:
        mock_groq_instance = MagicMock()
        mock_groq_instance.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(
                content='[{"title": "Test Book", "author": "Test Author", "year": 2023, "type": "Fiction", "description": "A test book. Another sentence about the book."}]'
            ))]
        )
        mock_groq.return_value = mock_groq_instance
        
        result = service.search_books("test book")
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert result[0].title == "Test Book"
        assert result[0].author == "Test Author"
        assert result[0].year == "2023"
        assert result[0].type == "Fiction"