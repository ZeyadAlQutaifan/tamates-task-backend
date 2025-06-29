# exception_handlers.py
from datetime import datetime
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


def create_error_response(status_code: int, message: str, errors: list = None):
    """Create standardized error response using generic API response format"""
    return JSONResponse(
        status_code=status_code,
        content={
            "data": None,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "status": "error",
            "message": message,
            "errors": errors or []
        }
    )


# 404 Not Found Handler
async def not_found_handler(request: Request, exc: HTTPException):
    """Handle 404 errors"""
    return create_error_response(
        status_code=404,
        message="Resource not found",
        errors=[exc.detail if exc.detail else "The requested resource could not be found"]
    )


# 422 Validation Error Handler
async def validation_error_handler(request: Request, exc: RequestValidationError):
    """Handle 422 validation errors"""
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        errors.append(f"{field}: {message}")

    return create_error_response(
        status_code=422,
        message="Validation failed",
        errors=errors
    )


# General HTTP Exception Handler
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle all HTTP exceptions"""
    status_messages = {
        400: "Bad request",
        401: "Authentication required",
        403: "Access forbidden",
        404: "Resource not found",
        405: "Method not allowed",
        409: "Conflict",
        429: "Too many requests",
        500: "Internal server error",
        502: "Bad gateway",
        503: "Service unavailable"
    }

    message = status_messages.get(exc.status_code, "An error occurred")

    return create_error_response(
        status_code=exc.status_code,
        message=message,
        errors=[exc.detail if exc.detail else message]
    )


# General Exception Handler (500 errors)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    return create_error_response(
        status_code=500,
        message="Internal server error",
        errors=["An unexpected error occurred", str(exc)]
    )


# Pydantic Validation Error Handler
async def pydantic_validation_error_handler(request: Request, exc: ValidationError):
    """Handle Pydantic validation errors"""
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        message = error["msg"]
        errors.append(f"{field}: {message}")

    return create_error_response(
        status_code=422,
        message="Data validation failed",
        errors=errors
    )