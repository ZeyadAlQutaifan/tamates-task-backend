from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
from services.auth_service import AuthService
from services.products_service import ProductService
from utils import security
from utils.security import decode_token


def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    return ProductService(db)

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)



