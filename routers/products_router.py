from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query, Security
from fastapi.security import HTTPBearer

from dependencies import get_product_service
from schemas.api_response_schemas import ApiResponse, PaginatedResponse, success_response, error_response
from schemas.products_schemas import ProductResponse
from services.products_service import ProductService

router = APIRouter(
    prefix="/products",
    tags=["products"]
)

product_service_dependency = Annotated[ProductService, Depends(get_product_service)]


@router.get(
    "/{product_id}",
    response_model=ApiResponse[ProductResponse],
    summary="Get Product by ID",
    description="Retrieve a specific product by its ID"
)
async def get_product(
        product_id: int,
        service: product_service_dependency
) -> ApiResponse[ProductResponse]:
    """
    Get a specific product by ID:

    - **product_id**: The ID of the product to retrieve

    Returns product information including title, description, price, and location.
    """
    try:
        product = service.get_product_by_id(product_id)
        return success_response(
            data=product,
            message="Product retrieved successfully"
        )
    except ValueError as e:
        return error_response(
            message="Product not found",
            errors=[str(e)]
        )
    except Exception as e:
        return error_response(
            message="Failed to retrieve product",
            errors=[str(e)]
        )

security = HTTPBearer()
@router.get(
    "/",
    response_model=ApiResponse[PaginatedResponse[ProductResponse]],
    summary="Get All Products",
    description="Retrieve paginated list of all products",
    dependencies=[Security(security)]
)
async def get_products(
        service: product_service_dependency,
        page: int = Query(1, ge=1, description="Page number (starts from 1)"),
        size: int = Query(10, ge=1, le=100, description="Number of products per page (1-100)"),
        location: Optional[str] = Query(None, description="Location of Item (JO/SA") ,
) -> ApiResponse[PaginatedResponse[ProductResponse]]:
    try:
        products = service.get_products(page, size, location)
        return success_response(
            data=products,
            message=f"Retrieved {len(products.content)} products"
        )
    except Exception as e:
        return error_response(
            message="Failed to retrieve products",
            errors=[str(e)]
        )