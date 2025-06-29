from typing import Annotated

import security
from fastapi import APIRouter, Depends, Query, Security
from fastapi.security import HTTPBearer

from dependencies import get_order_service, get_current_user, get_product_service
from modles.users_models import User
from schemas.api_response_schemas import ApiResponse, PaginatedResponse, success_response, error_response
from schemas.orders_schemas import CreateOrderRequest, PaymentCallback, InitiateOrderResponse, OrderResponse
from services.order_service import OrderService
from services.products_service import ProductService

router = APIRouter(
    prefix="/orders",
    tags=["orders"]
)

security = HTTPBearer()

order_service_dependency = Annotated[OrderService, Depends(get_order_service)]
product_service_dependency = Annotated[ProductService, Depends(get_product_service)]
current_user_dependency = Annotated[User, Depends(get_current_user)]


@router.post(
    "/initiate",
    response_model=ApiResponse[InitiateOrderResponse],
    summary="Initiate Order",
    description="Create a new order and get payment URL",
    dependencies=[Security(security)]
)
async def initiate(
        order_request: CreateOrderRequest,
        user: current_user_dependency,
        service: order_service_dependency,
        product_service: product_service_dependency,
) -> ApiResponse[InitiateOrderResponse]:
    """
    Initiate a new order and return payment URL
    """
    try:
        result = service.initiate(order_request, user, product_service)
        return success_response(
            data=result,
            message="Order initiated successfully"
        )
    except ValueError as e:
        return error_response(
            message="Invalid order data",
            errors=[str(e)]
        )
    except Exception as e:
        return error_response(
            message="Failed to initiate order",
            errors=[str(e)]
        )



@router.get(
    "/",
    response_model=ApiResponse[PaginatedResponse[OrderResponse]],
    summary="Get My Orders",
    description="Get paginated list of current user's orders",
    dependencies=[Security(security)]
)
async def get_my_orders(
    user: current_user_dependency,
    service: order_service_dependency,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page")
) -> ApiResponse[PaginatedResponse[OrderResponse]]:
    """
    Get current user's orders with pagination
    """
    try:
        result = service.get_orders(user, page, size)
        return success_response(
            data=result,
            message=f"Retrieved {len(result.content)} orders"
        )
    except Exception as e:
        return error_response(
            message="Failed to retrieve orders",
            errors=[str(e)]
        )