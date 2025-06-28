from typing import Annotated

from fastapi import APIRouter, Depends
from dependencies import get_product_service
from schemas.products_schemas import ProductBase
from services.products_service import ProductService

router = APIRouter(
    prefix="/products",
    tags=["products"]
)
product_service_dependency = Annotated[ProductService, Depends(get_product_service)]

@router.get("/{product_id}")
async def get_product(product_id: int, service: product_service_dependency):
    return service.get_product_by_id(product_id)

@router.get("/")
async def get_products(service: product_service_dependency, page: int = 0, per_page: int = 10):
    return {"products": service.get_products(page, per_page)}

@router.post("/")
async def create_product(product: ProductBase, service: product_service_dependency):
    return service.create_product(product)
