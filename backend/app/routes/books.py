from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..models.schemas import BookSearchRequest, BookInfo
from ..models.user import User
from ..utils.auth import get_current_active_user
from ..services.book_search import BookSearchService

router = APIRouter(prefix="/api/books", tags=["books"])

@router.post("/search", response_model=List[BookInfo])
async def search_books(
    search_request: BookSearchRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Search for books based on description and criteria."""
    
    try:
        book_service = BookSearchService()
        books = book_service.search_books(
            description=search_request.description,
            additional_details=search_request.additional_details
        )
        return books
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching for books: {str(e)}"
        )