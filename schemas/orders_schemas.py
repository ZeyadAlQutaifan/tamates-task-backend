from datetime import datetime

from pydantic import BaseModel, Field, conint

from schemas.products_schemas import ProductResponse


class CreateOrderRequest(BaseModel):
    product_id: conint(strict=True, gt=0) = Field(..., description="ID of the product to order (must be > 0)")
    quantity: conint(strict=True, gt=0, le=100) = Field(..., description="Quantity of the product (1–100)")

class OrderResponse(BaseModel):
    order_id: int
    trx_id: str
    product: ProductResponse
    quantity: int
    price: float
    status: str
    created_at: datetime


class InitiateOrderResponse(BaseModel):
    payment_url: str

class ProcessPayment(BaseModel):
    payment_id: int
    card_number: str
    cvv: str
    expiry_date: str


class PaymentCallback(BaseModel):
    reference_id: int
    trx_number: str
    status: str
