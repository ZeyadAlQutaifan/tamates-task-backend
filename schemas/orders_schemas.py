from datetime import datetime

from pydantic import  BaseModel

class CreateOrderRequest(BaseModel):
    product_id: int
    quantity: int

class OrderResponse(BaseModel):
    order_id: int
    trx_id: str
    product_id: str
    quantity: int
    price: float
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
