import stripe
from app.core.settings import settings

class StripeIntegration:
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY

    def create_customer(self, data):
        try:
            customer = stripe.Customer.create(
                name=data["name"],
                email=data["email"]
            )
            return customer["id"]
        except Exception as e:
            print("[Stripe] Error creating customer:", e)
            return None


    def update_customer(self, data):
        try:
            if not data.get("stripe_customer_id"):
                return None
            print("[Stripe] Updating customer:", data)
            stripe.Customer.modify(
                data["stripe_customer_id"],
                name=data.get("name"),
                email=data.get("email")
            )
        except Exception as e:
            print("[Stripe] Error updating customer:", e)




    def delete_customer(self, data):
        try:
            if not data.get("stripe_customer_id"):
                print("[Stripe] Missing stripe_customer_id")
                return
            print("[Stripe] Deleting customer:", data)
            stripe.Customer.delete(data["stripe_customer_id"])
        except Exception as e:
            print("[Stripe] Error deleting customer:", e)
