import json
import threading
from confluent_kafka import Consumer
from app.db.base import SessionLocal
from app.integrations.stripe_integration import StripeIntegration
from app.models.customer import Customer
from app.core.settings import settings
from app.core.exceptions import InternalServerErrorException

stripe_client = StripeIntegration()


def worker():
    """Kafka consumer that syncs customer data between local DB and Stripe."""
    consumer = Consumer({
        "bootstrap.servers": settings.KAFKA_BROKER_URL,
        "group.id": "zenskar-consumer-group",
        "auto.offset.reset": "earliest",
    })

    consumer.subscribe([settings.KAFKA_CUSTOMER_TOPIC])
    print("[Kafka Consumer] Listening for messages...")

    while True:
        msg = consumer.poll(1.0)
        if not msg:
            continue
        if msg.error():
            print(f"[Kafka Consumer] Error: {msg.error()}")
            continue

        try:
            event = json.loads(msg.value().decode("utf-8"))
            event_type = event.get("type")
            data = event.get("payload", {})

            with SessionLocal() as db:
                # Create
                if event_type == "customer.created":
                    if data.get("id"):  # Local → Stripe
                        stripe_id = stripe_client.create_customer(data)
                        if stripe_id:
                            db_customer = db.query(Customer).filter(Customer.id == data["id"]).first()
                            if db_customer:
                                db_customer.stripe_customer_id = stripe_id
                                db.commit()
                    else:
                        if not db.query(Customer).filter(
                                Customer.stripe_customer_id == data.get("stripe_customer_id")
                        ).first():
                            db.add(Customer(
                                name=data.get("name"),
                                email=data.get("email"),
                                stripe_customer_id=data.get("stripe_customer_id"),
                            ))
                            db.commit()

                # Update
                elif event_type == "customer.updated":
                    if data.get("id"):
                        stripe_client.update_customer(data)
                    elif data.get("stripe_customer_id"):
                        db_customer = db.query(Customer).filter(
                            Customer.stripe_customer_id == data["stripe_customer_id"]
                        ).first()
                        if db_customer:
                            db_customer.name = data.get("name", db_customer.name)
                            db_customer.email = data.get("email", db_customer.email)
                            db.commit()

                # delete
                elif event_type == "customer.deleted":
                    if data.get("id"):
                        stripe_client.delete_customer(data)
                    elif data.get("stripe_customer_id"):
                        db_customer = db.query(Customer).filter(
                            Customer.stripe_customer_id == data["stripe_customer_id"]
                        ).first()
                        if db_customer:
                            db.delete(db_customer)
                            db.commit()

        except Exception as e:
            raise InternalServerErrorException(f"Kafka consumer error: {str(e)}")


def start_consumer_thread():
    """Start Kafka consumer in a background thread."""
    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
