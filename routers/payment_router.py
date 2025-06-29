from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

from dependencies import get_payment_service, get_order_service
from schemas.orders_schemas import PaymentCallback, ProcessPayment
from schemas.api_response_schemas import ApiResponse, success_response, error_response
from services.order_service import OrderService
from services.payment_service import PaymentService

router = APIRouter(
    prefix="/payment",
    tags=["payment"]
)

payment_service_dependency = Annotated[PaymentService, Depends(get_payment_service)]
order_service_dependency = Annotated[OrderService, Depends(get_order_service)]
security = HTTPBearer()

@router.get(
    "/{payment_id}",
    response_model=ApiResponse[dict],
    summary="Get Payment Details",
    description="Retrieve payment information by payment ID"
)
async def get_payment(
        payment_id: int,
        payment_service: payment_service_dependency
) -> ApiResponse[dict]:
    """
    Get payment details by payment ID
    """
    try:
        payment_details = payment_service.get_payment_details(payment_id)
        if not payment_details:
            return error_response(
                message="Payment not found",
                errors=[f"No payment found with ID {payment_id}"]
            )

        payment_data = {
            "payment_id": payment_details.payment_id,
            "reference_id": payment_details.reference_id,
            "price": payment_details.price,
            "status": payment_details.status,
            "redirect_url": payment_details.redirect_url,
            "callback_url": payment_details.callback_url
        }

        return success_response(
            data=payment_data,
            message="Payment details retrieved successfully"
        )

    except Exception as e:
        return error_response(
            message="Failed to retrieve payment details",
            errors=[str(e)]
        )


@router.post(
    "/process",
    response_model=ApiResponse[PaymentCallback],
    summary="Process Payment",
    description="Process payment with card details"
)
async def process_payment(
        process_payment_request: ProcessPayment,
        payment_service: payment_service_dependency,
        order_service: order_service_dependency
) -> ApiResponse[PaymentCallback]:
    """
    Process payment with card details:

    - **payment_id**: Payment ID to process
    - **card_number**: Credit card number
    - **cvv**: Card verification value
    - **expiry_date**: Card expiry date (MM/YY format)

    Returns payment callback with transaction details.
    """
    try:
        callback = payment_service.process_payment(process_payment_request, order_service)

        if callback.status == "CAPTURED":
            return success_response(
                data=callback,
                message="Payment processed successfully"
            )
        else:
            return success_response(
                data=callback,
                message="Payment failed - transaction declined"
            )

    except ValueError as e:
        return error_response(
            message="Invalid payment data",
            errors=[str(e)]
        )
    except Exception as e:
        return error_response(
            message="Payment processing failed",
            errors=[str(e)]
        )