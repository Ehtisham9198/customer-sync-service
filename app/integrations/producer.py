import json
from confluent_kafka import Producer
from app.core.settings import settings
from app.core.exceptions import InternalServerErrorException


producer = Producer({"bootstrap.servers": settings.KAFKA_BROKER_URL})


def _delivery_report(err, msg):
    if err:
        raise InternalServerErrorException(f"Kafka delivery failed: {err}")


def publish_event(event_type: str, payload: dict):
    try:
        event = json.dumps({"type": event_type, "payload": payload})
        producer.produce(
            topic=settings.KAFKA_CUSTOMER_TOPIC,
            value=event.encode("utf-8"),
            callback=_delivery_report,
        )
        producer.flush()
    except Exception as e:
        raise InternalServerErrorException(f"Kafka publish error: {str(e)}")
