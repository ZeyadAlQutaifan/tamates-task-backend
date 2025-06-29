from typing import Annotated

from fastapi import APIRouter, Depends

from dependencies import get_order_service, get_current_user, get_product_service
from modles.users_models import User
from schemas.orders_schemas import CreateOrderRequest, PaymentCallback, InitiateOrderResponse
from services import order_service
from services.order_service import OrderService
from services.products_service import ProductService

router = APIRouter(
    prefix="/orders",
    tags=["orders"]
)

order_service_dependency = Annotated[OrderService, Depends(get_order_service)]
product_service_dependency = Annotated[ProductService, Depends(get_product_service)]
current_user_dependency = Annotated[User, Depends(get_current_user)]


@router.post("/initiate")
async def initiate(
        order_request: CreateOrderRequest,
        user: current_user_dependency,
        service: order_service_dependency,
        product_service: product_service_dependency,
) -> InitiateOrderResponse:
    return service.initiate(order_request, user, product_service)