from typing import Any
from fastapi import Request

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from passlib.ifc import PasswordHash

from sqlalchemy.orm import Session
from database import get_db
from modles.users_models import User
from services.auth_service import AuthService
from services.order_service import OrderService
from services.payment_service import PaymentService
from services.products_service import ProductService
from utils import security
from utils.password_hasher import Hasher
from utils.security import decode_token


def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    return ProductService(db)

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)

def get_order_service(db: Session = Depends(get_db)) -> OrderService:
    return OrderService(db)

def get_payment_service(db: Session =Depends(get_db) ) -> PaymentService:
    return PaymentService(db)

def get_current_user(db: Session = Depends(get_db), request: Request = None) -> type[User]:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header missing or invalid")

    token = auth_header.split(" ")[1]
    payload = decode_token(token)
    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user


