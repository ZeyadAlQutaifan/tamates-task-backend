import base64

import bcrypt
import jwt
from datetime import datetime, timedelta
from config.setting import settings


def hash_password(password: str) -> str:
    """Hash password for storage"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')  # bcrypt hashes are ASCII-safe


def verify_password(plain_password: str, stored_hash: str) -> bool:
    """Verify password against stored hash"""
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            stored_hash.encode('utf-8')
        )
    except Exception:
        return False

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict):
    return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str):
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
