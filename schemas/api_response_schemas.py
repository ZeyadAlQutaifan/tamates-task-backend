from datetime import datetime

# schemas/pagination.py
from pydantic import BaseModel, Field
from typing import List, TypeVar, Generic, Optional

# Generic type for the data
T = TypeVar('T')

class   PaginatedResponse(BaseModel, Generic[T]):
    """
    Generic paginated response that can be used with any data type
    """
    content: List[T] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items", example=25)
    page: int = Field(..., description="Current page number", example=1)
    size: int = Field(..., description="Number of items per page", example=10)
    total_pages: int = Field(..., description="Total number of pages", example=3)
    has_next: bool = Field(..., description="Whether there is a next page", example=True)
    has_previous: bool = Field(..., description="Whether there is a previous page", example=False)

    class Config:
        schema_extra = {
            "example": {
                "data": [],
                "total": 25,
                "page": 1,
                "size": 10,
                "total_pages": 3,
                "has_next": True,
                "has_previous": False
            }
        }


B = TypeVar('B')

class ApiResponse(BaseModel, Generic[B]):
    """
    Generic API response wrapper for all endpoints
    """
    data: Optional[B] = Field(None, description="Response data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    status: str = Field(..., description="Response status", example="success")
    message: str = Field(..., description="Response message", example="Operation completed successfully")
    errors: List[str] = Field(default_factory=list, description="List of error messages")

    class Config:
        schema_extra = {
            "example": {
                "data": {},
                "timestamp": "2025-06-29T10:30:00Z",
                "status": "success",
                "message": "Operation completed successfully",
                "errors": []
            }
        }

# Helper functions to create responses
def success_response(data: T, message: str = "Success") -> ApiResponse[T]:
    """Create a successful API response"""
    return ApiResponse(
        data=data,
        status="success",
        message=message,
        errors=[]
    )

def error_response(message: str, errors: List[str] = None) -> ApiResponse[None]:
    """Create an error API response"""
    return ApiResponse(
        data=None,
        status="error",
        message=message,
        errors=errors or []
    )

def validation_error_response(errors: List[str]) -> ApiResponse[None]:
    """Create a validation error response"""
    return ApiResponse(
        data=None,
        status="validation_error",
        message="Validation failed",
        errors=errors
    )