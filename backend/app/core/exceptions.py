from typing import Union

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from jose import JWTError
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError


class AppException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, AppException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    elif isinstance(exc, RequestValidationError):
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"detail": exc.errors()})
    elif isinstance(exc, JWTError):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "Invalid authentication credentials"}
        )
    elif isinstance(exc, SQLAlchemyError):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": "Database error occurred"}
        )
    elif isinstance(exc, ValidationError):
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"detail": exc.errors()})

    # Default error handler
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": "Internal server error"})
