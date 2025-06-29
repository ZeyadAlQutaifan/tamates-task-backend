import csv
import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ValidationError
from typing import List, Annotated
import modles
from database import engine, SessionLocal, get_db, Base
from sqlalchemy.orm import Session

from middlewares.audit_middleware import AuditMiddleware
from middlewares.auth_middleware import AuthMiddleware
from modles.product_models import Product
from routers.questions_router import router as questions_router
from routers.products_router import router as products_router
from routers.auth_router import router as auth_router
from routers.orders_router import router as orders_router
from routers.payment_router import router as payment_router
from excpetions.global_exception_handler import (
    not_found_handler,
    validation_error_handler,
    http_exception_handler,
    general_exception_handler,
    pydantic_validation_error_handler
)
from fastapi import FastAPI, Request


def populate_products_from_csv():
    """
    Auto-populate products from CSV on startup
    """
    db = SessionLocal()

    try:
        csv_file_path = "items.csv"

        # Check if file exists
        if not os.path.exists(csv_file_path):
            print(f"⚠️  CSV file '{csv_file_path}' not found! Skipping auto-import.")
            return

        # Check if products already exist
        existing_count = db.query(Product).count()
        if existing_count > 0:
            print(f" Found {existing_count} existing products. Skipping CSV import.")
            return

        print("No products found. Starting CSV import...")

        products_created = 0

        with open(csv_file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)

            for row in csv_reader:
                try:
                    product = Product(
                        id=int(row['id']),
                        title=row['title'].strip(),
                        description=row['description'].strip(),
                        price=float(row['price']),
                        location=row['location'].strip()
                    )

                    db.add(product)
                    products_created += 1

                except Exception as e:
                    print(f" Error processing row {row}: {e}")
                    continue

        db.commit()
        print(f"✅ Successfully imported {products_created} products on startup!")

    except Exception as e:
        print(f" Error during startup import: {e}")
        db.rollback()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🌟 FastAPI application is starting up...")

    # Create tables
    Base.metadata.create_all(bind=engine)

    # Auto-import CSV data
    populate_products_from_csv()

    yield

    # Shutdown
    print("🛑 FastAPI application is shutting down...")


app = FastAPI(lifespan=lifespan,
              title="Tamatem Plus API",
              description="API for Tamatem Plus with JWT Authentication",
              version="1.0.0",
              )

app.include_router(questions_router)
app.include_router(products_router)
app.include_router(auth_router)
app.include_router(orders_router)
app.include_router(payment_router)

app.add_middleware(AuthMiddleware)
app.add_middleware(AuditMiddleware)

app.add_exception_handler(404, not_found_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(ValidationError, pydantic_validation_error_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

Base.metadata.create_all(bind=engine)

db_dependency = Annotated[Session, Depends(get_db)]
