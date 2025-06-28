from pydantic import  BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    email: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str