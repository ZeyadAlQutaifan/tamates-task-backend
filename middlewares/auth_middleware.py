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
            "/favicon.ico"
        ]

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
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Authorization header missing"}
            )

        # Extract token from "Bearer <token>" format
        try:
            scheme, token = auth_header.split(" ", 1)
            if scheme.lower() != "bearer":
                raise ValueError("Invalid authentication scheme")
        except ValueError:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid authorization header format. Use 'Bearer <token>'"}
            )

        # Verify and decode token
        try:
            payload = decode_token(token)
            # Add user info to request state for use in route handlers
            request.state.user = payload
            request.state.user_id = payload.get("sub")  # Assuming 'sub' contains user ID

        except jwt.ExpiredSignatureError:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Token has expired"}
            )
        except jwt.InvalidTokenError:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid token"}
            )
        except Exception as e:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Token validation failed"}
            )

        # Proceed with the request
        response = await call_next(request)
        return response