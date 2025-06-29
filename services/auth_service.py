from typing import Any

from sqlalchemy.orm import Session
from datetime import datetime
from modles.users_models import User
from schemas.auth_schemas import LoginRequest, RegisterRequest, AuthResponse
from utils.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def login(self, login_request: LoginRequest) -> AuthResponse:
        """
        Authenticate user with email and password
        """
        # Find user by email
        user = self.db.query(User).filter(User.email == login_request.email).first()
        if not user:
            raise ValueError("Invalid email or password")

        # Verify password
        if not verify_password(login_request.password, user.password_hashed):
            raise ValueError("Invalid email or password")

        # Create token data
        token_data = {
            "sub": user.username,
            "user_id": user.id,
            "role": user.role,
            "email": user.email
        }

        return AuthResponse(
            access_token=create_access_token(token_data),
            token_type="Bearer",
            refresh_token=create_refresh_token(token_data)
        )

    def register(self, register_request: RegisterRequest) -> AuthResponse:
        """
        Register a new user account
        """
        # Check if user already exists
        existing_user = self.db.query(User).filter(
            (User.username == register_request.username) |
            (User.email == register_request.email)
        ).first()

        if existing_user:
            if existing_user.email == register_request.email:
                raise ValueError("Email already registered")
            else:
                raise ValueError("Username already taken")

        # Create new user
        user = User(
            username=register_request.username,
            password_hashed=hash_password(register_request.password),
            email=register_request.email,
            role="User",
            registered_on=datetime.utcnow().isoformat()
        )

        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Failed to create user account: {str(e)}")

        # Create tokens for new user
        token_data = {
            "sub": user.username,
            "user_id": user.id,
            "role": user.role,
            "email": user.email
        }

        return AuthResponse(
            access_token=create_access_token(token_data),
            token_type="Bearer",
            refresh_token=create_refresh_token(token_data)
        )

    def refresh_token(self, refresh_token: str) -> AuthResponse:
        """
        Refresh access token using refresh token
        """
        try:
            # Decode and validate refresh token
            payload = decode_token(refresh_token)
            user_id = payload.get("user_id")

            if not user_id:
                raise ValueError("Invalid refresh token payload")

            # Find user
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError("User not found")

            # Create new tokens
            new_token_data = {
                "sub": user.username,
                "user_id": user.id,
                "role": user.role,
                "email": user.email
            }

            return AuthResponse(
                access_token=create_access_token(new_token_data),
                token_type="Bearer",
                refresh_token=create_refresh_token(new_token_data)
            )

        except ValueError:
            # Re-raise validation errors
            raise
        except Exception as e:
            raise ValueError(f"Invalid or expired refresh token: {str(e)}")

    def get_user_by_id(self, user_id: int) -> type[User]:
        """
        Get user by ID (for dependency injection)
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        return user