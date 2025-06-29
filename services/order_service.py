from sqlalchemy.orm import Session
from modles.order_models import Order, PaymentRequest
from modles.users_models import User
from schemas.orders_schemas import CreateOrderRequest, InitiateOrderResponse, OrderResponse
from schemas.api_response_schemas import PaginatedResponse
from services.products_service import ProductService
from config.setting import settings

def calculate_price(order_price: float, quantity: int) -> float:
    return order_price * quantity


class OrderService:
    def __init__(self, db: Session):
        self.db = db

    @classmethod
    def mock_payment_callback(cls, callback, db: Session):
        order = db.query(Order).get(callback.reference_id)
        if callback.status == "CAPTURED":
            order.status = "SUCCESS"
        else:
            order.status = "FAILED"
        order.trx_number = callback.trx_number
        db.add(order)
        db.commit()
        db.refresh(order)

    def initiate(self, order_request: CreateOrderRequest, user: User,
                 product_service: ProductService) -> InitiateOrderResponse:
        db_product = product_service.get_product_by_id(order_request.product_id)
        price = calculate_price(db_product.price, order_request.quantity)
        new_order = Order(
            user_id=user.id,
            product_id=order_request.product_id,
            quantity=order_request.quantity,
            price=price,
            status='INITIATED'
        )

        self.db.add(new_order)
        self.db.commit()
        self.db.refresh(new_order)

        payment = self.mock_initialize_payment(new_order.id, new_order.price)

        return InitiateOrderResponse(payment_url=f"{settings.PAYMENT_BASE_URL}/payment/{payment.payment_id}")

    def mock_initialize_payment(self, order_id: int, price: float) -> PaymentRequest:
        new_payment = PaymentRequest(reference_id=order_id, price=price, status="NEW",
                                     redirect_url=settings.PAYMENT_REDIRECT_URL,
                                     callback_url=settings.PAYMENT_CALLBACK_URL)
        self.db.add(new_payment)
        self.db.commit()
        self.db.refresh(new_payment)
        return new_payment

    def get_orders(self, user: User, page: int = 1, size: int = 10) -> PaginatedResponse[OrderResponse]:
        """
        Get paginated orders for a specific user
        """
        # Calculate offset
        offset = (page - 1) * size

        # Get orders for the user with pagination
        orders = (self.db.query(Order)
                  .filter(Order.user_id == user.id)
                  .order_by(Order.created_at.desc())
                  .offset(offset)
                  .limit(size)
                  .all())

        # Get total count for the user
        total_count = self.db.query(Order).filter(Order.user_id == user.id).count()

        # Calculate pagination info
        total_pages = (total_count + size - 1) // size
        has_next = page < total_pages
        has_previous = page > 1

        # Convert to response format
        order_responses = [
            OrderResponse(
                order_id=order.id,
                trx_id=order.trx_number or "",
                product_id=str(order.product_id),
                quantity=order.quantity,
                price=order.price,
                status=order.status,
                created_at=order.created_at
            )
            for order in orders
        ]

        return PaginatedResponse[OrderResponse](
            content=order_responses,
            total=total_count,
            page=page,
            size=size,
            total_pages=total_pages,
            has_next=has_next,
            has_previous=has_previous
        )