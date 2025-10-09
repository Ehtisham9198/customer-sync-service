from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.integrations.producer import publish_event

from app.core.exceptions import (
    NotFoundException,
    ConflictException,
    InternalServerErrorException
)


def get_all_customers(db: Session):
    try:
        return db.query(Customer).all()
    except SQLAlchemyError:
        raise InternalServerErrorException("Failed to fetch customers")


def get_customer(db: Session, customer_id):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise NotFoundException("Customer not found")
    return customer


def create_customer(db: Session, customer: CustomerCreate):
    existing = db.query(Customer).filter(Customer.email == customer.email).first()
    if existing:
        raise ConflictException("Customer with this email already exists")

    db_customer = Customer(**customer.model_dump())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)

    publish_event("customer.created", {
        "id": str(db_customer.id),
        "name": db_customer.name,
        "email": db_customer.email
    })

    return db_customer


def update_customer(db: Session, db_customer: Customer, update_data: CustomerUpdate):
    try:
        for key, value in update_data.model_dump(exclude_unset=True).items():
            setattr(db_customer, key, value)
        db.commit()
        db.refresh(db_customer)

        publish_event("customer.updated", {
            "id": str(db_customer.id),
            "stripe_customer_id": db_customer.stripe_customer_id,
            "name": db_customer.name,
            "email": db_customer.email,
        })

        return db_customer
    except Exception as e:
        db.rollback()
        print("Error updating customer:", e)
        raise


def delete_customer(db: Session, db_customer: Customer):
    try:
        event_payload = {
            "id": str(db_customer.id),
            "stripe_customer_id": db_customer.stripe_customer_id,
            "name": db_customer.name,
            "email": db_customer.email,
        }

        db.delete(db_customer)
        db.commit()

        publish_event("customer.deleted", event_payload)

    except SQLAlchemyError:
        db.rollback()
        raise InternalServerErrorException("Failed to delete customer")