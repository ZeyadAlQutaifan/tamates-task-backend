import uvicorn
from fastapi import  FastAPI, HTTPException, Depends
from pydantic import  BaseModel
from  typing import  List, Annotated
import modles
from database import engine, SessionLocal, get_db, Base
from sqlalchemy.orm import Session

from middlewares.auth_middleware import AuthMiddleware
from routers.questions_router import router as questions_router
from routers.products_router import router as products_router
from routers.auth_router import  router as auth_router

from fastapi import FastAPI, Request

app = FastAPI()
app.include_router(questions_router)
app.include_router(products_router)
app.include_router(auth_router)


app.add_middleware(AuthMiddleware)

Base.metadata.create_all(bind=engine)

db_dependency = Annotated[Session, Depends(get_db)]



