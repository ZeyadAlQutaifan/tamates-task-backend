from typing import Annotated

from fastapi import APIRouter, Depends, Security
from fastapi.security import HTTPBearer

from dependencies import get_auth_service, get_current_user
from modles.users_models import User
from schemas.auth_schemas import LoginRequest, RegisterRequest, AuthResponse
from schemas.api_response_schemas import ApiResponse, success_response, error_response
from services.auth_service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)

security = HTTPBearer()
auth_service_dependency = Annotated[AuthService, Depends(get_auth_service)]
current_user_dependency = Annotated[User, Depends(get_current_user)]


@router.post(
    "/login",
    response_model=ApiResponse[AuthResponse],
    summary="User Login",
    description="Authenticate user with email and password to get JWT tokens"
)
async def login(
        login_request: LoginRequest,
        auth_service: auth_service_dependency
) -> ApiResponse[AuthResponse]:
    """
    User login with email and password:

    - **email**: User's email address
    - **password**: User's password

    Returns JWT access token and refresh token for authenticated requests.
    """

    try:
        auth_response = auth_service.login(login_request)
        return success_response(
            data=auth_response,
            message="Login successful"
        )
    except Exception as e:
        return error_response(
            message="Login failed",
            errors=[str(e)]
        )


@router.post(
    "/register",
    response_model=ApiResponse[AuthResponse],
    summary="User Registration",
    description="Register a new user account and get JWT tokens"
)
async def register(
        register_request: RegisterRequest,
        auth_service: auth_service_dependency
) -> ApiResponse[AuthResponse]:
    """
    Register a new user account:

    - **username**: Unique username (3-30 characters)
    - **email**: Valid email address
    - **password**: Strong password (minimum 6 characters)

    Returns JWT access token and refresh token for the new user.
    """
    try:
        auth_response = auth_service.register(register_request)
        return success_response(
            data=auth_response,
            message="Registration successful"
        )
    except ValueError as e:
        return error_response(
            message="Registration failed",
            errors=[str(e)]
        )
    except Exception as e:
        return error_response(
            message="Registration failed",
            errors=[str(e)]
        )


@router.post(
    "/refresh/{refresh_token}",
    response_model=ApiResponse[AuthResponse],
    summary="Refresh Token",
    description="Refresh access token using refresh token"
)
async def refresh(
        refresh_token: str,
        auth_service: auth_service_dependency
) -> ApiResponse[AuthResponse]:
    """
    Refresh access token using refresh token:

    - **refresh_token**: Valid refresh token from login/register

    Returns new JWT access token and refresh token.
    """
    try:
        auth_response = auth_service.refresh_token(refresh_token)
        return success_response(
            data=auth_response,
            message="Token refreshed successfully"
        )
    except ValueError as e:
        return error_response(
            message="Token refresh failed",
            errors=[str(e)]
        )
    except Exception as e:
        return error_response(
            message="Token refresh failed",
            errors=[str(e)]
        )


@router.get(
    "/me",
    response_model=ApiResponse[dict],
    summary="Get Current User",
    description="Get current user's profile information",
    dependencies=[Security(security)]
)
async def get_current_user_profile(
        current_user: current_user_dependency
) -> ApiResponse[dict]:
    """
    Get current user's profile information:

    **Authentication required**: You must provide a valid JWT token.

    Returns user profile data including ID, username, email, and role.
    """
    try:
        user_data = {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "role": current_user.role,
            "registered_on": current_user.registered_on
        }

        return success_response(
            data=user_data,
            message="Profile retrieved successfully"
        )
    except Exception as e:
        return error_response(
            message="Failed to retrieve profile",
            errors=[str(e)]
        )