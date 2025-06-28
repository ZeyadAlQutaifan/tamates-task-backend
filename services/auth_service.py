from sqlalchemy.orm import Session

from schemas.auth_schemas import AuthResponse, LoginRequest, RegisterRequest

# services/auth_service.py
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import HTTPException
from modles.users_models import User
from schemas.auth_schemas import LoginRequest, RegisterRequest, AuthResponse
from utils.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def login(self, login_request: LoginRequest) -> AuthResponse:
        user = self.db.query(User).filter(User.email == login_request.email).first()
        if not user or not verify_password(login_request.password, user.password_hashed):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token_data = {"sub": user.username, "user_id": user.id, "role": user.role, "email": user.email}
        return AuthResponse(
            access_token=create_access_token(token_data),
            token_type="bearer",
            refresh_token=create_refresh_token(token_data)
        )


    def register(self, register_request: RegisterRequest) -> AuthResponse:
        if self.db.query(User).filter((User.username == register_request.username) | (User.email == register_request.email)).first():
            raise HTTPException(status_code=400, detail="User already exists")

        user = User(
            username=register_request.username,
            password_hashed=hash_password(register_request.password),
            email=register_request.email,
            role="User",
            registered_on=datetime.utcnow().isoformat()
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        token_data = {"sub": user.username, "user_id": user.id, "role": user.role}
        return AuthResponse(
            access_token=create_access_token(token_data),
            token_type="bearer",
            refresh_token=create_refresh_token(token_data)
        )

    def refresh_token(self, refresh_token: str) -> AuthResponse:
        try:
            payload = decode_token(refresh_token)
            user = self.db.query(User).filter(User.id == payload.get("user_id")).first()
            if not user:
                raise HTTPException(status_code=401, detail="User not found")

            new_data = {"sub": user.username, "user_id": user.id, "role": user.role}
            return AuthResponse(
                access_token=create_access_token(new_data),
                token_type="bearer",
                refresh_token=create_refresh_token(new_data)
            )
        except Exception:
            raise HTTPException(status_code=403, detail="Invalid refresh token")


