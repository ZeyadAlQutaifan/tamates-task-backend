from datetime import datetime
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import jwt

from utils.security import decode_token


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, excluded_paths: list = None):
        super().__init__(app)
        # Default excluded paths
        self.excluded_paths = excluded_paths or [
            "/auth/",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/favicon.ico",
            "/",
            "/health"
        ]

    def create_error_response(self, status_code: int, message: str, errors: list = None):
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

    async def dispatch(self, request: Request, call_next):
        # Check if the path should be excluded from authentication
        path = request.url.path

        # Skip authentication for excluded paths
        for excluded_path in self.excluded_paths:
            if path.startswith(excluded_path):
                response = await call_next(request)
                return response

        # Extract and validate token
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return self.create_error_response(
                status_code=status.HTTP_401_UNAUTHORIZED,
                message="Authentication required",
                errors=["Authorization header missing"]
            )

        # Extract token from "Bearer <token>" format
        try:
            scheme, token = auth_header.split(" ", 1)
            if scheme.lower() != "bearer":
                raise ValueError("Invalid authentication scheme")
        except ValueError:
            return self.create_error_response(
                status_code=status.HTTP_401_UNAUTHORIZED,
                message="Invalid authorization format",
                errors=["Invalid authorization header format. Use 'Bearer <token>'"]
            )

        # Verify and decode token
        try:
            payload = decode_token(token)
            # Add user info to request state for use in route handlers
            request.state.user = payload
            request.state.user_id = payload.get("user_id")  # Get actual user_id from payload

        except jwt.ExpiredSignatureError:
            return self.create_error_response(
                status_code=status.HTTP_401_UNAUTHORIZED,
                message="Token expired",
                errors=["Token has expired, please login again"]
            )
        except jwt.InvalidTokenError:
            return self.create_error_response(
                status_code=status.HTTP_401_UNAUTHORIZED,
                message="Invalid token",
                errors=["Token is invalid or malformed"]
            )
        except Exception as e:
            return self.create_error_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Authentication failed",
                errors=["Token validation failed", str(e)]
            )

        # Proceed with the request
        response = await call_next(request)
        return response