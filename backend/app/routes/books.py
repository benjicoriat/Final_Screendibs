from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.schemas import BookInfo, BookSearchRequest
from ..models.user import User
from ..services.book_search import BookSearchService
from ..utils.auth import get_current_active_user

router = APIRouter(tags=["books"])


@router.post("/search", response_model=List[BookInfo])
async def search_books(search_request: BookSearchRequest, db: Session = Depends(get_db)):
    """Search for books based on description and criteria."""

    try:
        book_service = BookSearchService()
        books = book_service.search_books(
            description=search_request.description, additional_details=search_request.additional_details
        )
        return books
    except Exception as e:
        # Return a JSON body with an 'error' key to match test expectations
        return JSONResponse(status_code=500, content={"error": f"Error searching for books: {str(e)}"})
