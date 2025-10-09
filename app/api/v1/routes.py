from fastapi import APIRouter
from app.api.v1 import customers,stripe_webhook

router = APIRouter()
router.include_router(customers.router, prefix="/customers", tags=["Customers"])
router.include_router(stripe_webhook.router, prefix="/stripe", tags=["Stripe Webhook"])

