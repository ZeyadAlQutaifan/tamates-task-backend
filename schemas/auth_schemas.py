from pydantic import BaseModel, Field, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., example="john@example.com")
    password: str = Field(..., min_length=6, example="password123")
    class Config:
        # Disable any automatic masking
        hide_input_in_errors = False
        validate_assignment = False

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=30, example="john_doe")
    password: str = Field(..., min_length=6, example="password123")
    email: EmailStr = Field(..., example="john@example.com")


class AuthResponse(BaseModel):
    access_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    token_type: str = Field(default="Bearer", example="Bearer")
    refresh_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")