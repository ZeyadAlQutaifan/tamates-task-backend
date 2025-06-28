from typing import Annotated

from fastapi import APIRouter, Depends

from dependencies import get_auth_service
from schemas.auth_schemas import LoginRequest, RegisterRequest
from services.auth_service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)
auth_service_dependency = Annotated[AuthService, Depends(get_auth_service)]


@router.post("/login")
async def login(login_request: LoginRequest, auth_service: auth_service_dependency):
    return auth_service.login(login_request)

@router.post("/register")
async def register(register_request: RegisterRequest, auth_service: auth_service_dependency):
    return auth_service.register(register_request)

@router.post("/refresh/{refresh_token}")
async def refresh(refresh_token: str, auth_service: auth_service_dependency):
    return auth_service.refresh_token(refresh_token)
