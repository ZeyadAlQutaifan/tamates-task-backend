import random
import string
from sqlalchemy.orm import Session

from modles.order_models import PaymentRequest
from schemas.orders_schemas import ProcessPayment, PaymentCallback
from services.order_service import OrderService


def deduct_amount(request: ProcessPayment, amount: float) -> bool:
    """
    Mock function to simulate payment processing
    Returns False if card number ends with '0000' (simulate failed payment)
    """
    if request.card_number.endswith("0000"):
        return False
    else:
        return True


def _generate_reference() -> str:
    """Generate random transaction reference"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))


class PaymentService:
    def __init__(self, db: Session):
        self.db = db

    def get_payment_details(self, payment_id: int) -> PaymentRequest:
        """
        Get payment details by payment ID
        """
        try:
            payment = self.db.get(PaymentRequest, payment_id)
            return payment
        except Exception as e:
            raise ValueError(f"Failed to retrieve payment with ID {payment_id}: {str(e)}")

    def process_payment(self, request: ProcessPayment, order_service: OrderService) -> PaymentCallback:
        """
        Process payment and update order status
        """
        try:
            # Validate request
            if not request.payment_id:
                raise ValueError("Payment ID is required")
            if not request.card_number:
                raise ValueError("Card number is required")
            if not request.cvv:
                raise ValueError("CVV is required")
            if not request.expiry_date:
                raise ValueError("Expiry date is required")

            # Get payment details
            payment_details = self.get_payment_details(request.payment_id)
            if not payment_details:
                raise ValueError(f"Payment with ID {request.payment_id} not found")

            # Validate payment status
            if payment_details.status != "NEW":
                raise ValueError(f"Payment already processed with status: {payment_details.status}")

            # Process payment
            transaction_reference = _generate_reference()

            if deduct_amount(request, payment_details.price):
                # Payment successful
                callback = PaymentCallback(
                    trx_number=transaction_reference,
                    reference_id=payment_details.reference_id,
                    status="CAPTURED"
                )

                # Update payment status
                payment_details.status = "CAPTURED"
                payment_details.trx_number = transaction_reference

            else:
                # Payment failed
                callback = PaymentCallback(
                    trx_number=transaction_reference,
                    reference_id=payment_details.reference_id,
                    status="FAILED"
                )

                # Update payment status
                payment_details.status = "FAILED"
                payment_details.trx_number = transaction_reference

            # Save payment status
            self.db.add(payment_details)
            self.db.commit()
            self.db.refresh(payment_details)

            # Update order status via callback
            # In real implementation, this should be a separate service/webhook
            order_service.mock_payment_callback(callback, self.db)

            return callback

        except ValueError:
            # Re-raise validation errors
            raise
        except Exception as e:
            # Handle unexpected errors
            self.db.rollback()
            raise Exception(f"Payment processing failed: {str(e)}")

    def get_payment_status(self, payment_id: int) -> dict:
        """
        Get current payment status
        """
        try:
            payment = self.get_payment_details(payment_id)
            if not payment:
                raise ValueError(f"Payment with ID {payment_id} not found")

            return {
                "payment_id": payment.payment_id,
                "status": payment.status,
                "trx_number": payment.trx_number,
                "amount": payment.price,
                "reference_id": payment.reference_id
            }

        except Exception as e:
            raise ValueError(f"Failed to get payment status: {str(e)}")