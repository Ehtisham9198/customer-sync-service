from fastapi import APIRouter, Request, status
from app.integrations.producer import publish_event
from app.core.settings import settings
from app.core.exceptions import (
    BadRequestException,
    InternalServerErrorException,
)
import stripe

router = APIRouter()


@router.post("/webhook", status_code=200)
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=settings.STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        raise BadRequestException("Invalid Stripe webhook signature")
    except Exception as e:
        raise InternalServerErrorException(f"Webhook validation failed: {str(e)}")

    try:
        event_type = event["type"]
        data = event["data"]["object"]

        if event_type.startswith("customer."):
            publish_event(event_type, {
                "stripe_customer_id": data["id"],
                "name": data.get("name"),
                "email": data.get("email")
            })

        return {"status": "success"}

    except KeyError as e:
        raise BadRequestException(f"Missing expected field in event payload: {e}")
    except Exception as e:
        raise InternalServerErrorException(f"Unexpected error while processing event: {str(e)}")
