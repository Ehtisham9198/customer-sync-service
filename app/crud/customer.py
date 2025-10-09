from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.core.exceptions import (
    NotFoundException,
    ConflictException,
    UnprocessableEntityException,
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
    try:
        # duplicate email check
        existing = db.query(Customer).filter(Customer.email == customer.email).first()
        if existing:
            raise ConflictException("A customer with this email already exists")

        db_customer = Customer(**customer.model_dump())
        db.add(db_customer)
        db.commit()
        db.refresh(db_customer)
        return db_customer
    except IntegrityError:
        db.rollback()
        raise UnprocessableEntityException("Invalid customer data")
    except SQLAlchemyError:
        db.rollback()
        raise InternalServerErrorException("Database error while creating customer")





def update_customer(db: Session, db_customer: Customer, update_data: CustomerUpdate):
    try:
        for key, value in update_data.model_dump(exclude_unset=True).items():
            setattr(db_customer, key, value)
        db.commit()
        db.refresh(db_customer)
        return db_customer
    except IntegrityError:
        db.rollback()
        raise UnprocessableEntityException("Invalid update data")
    except SQLAlchemyError:
        db.rollback()
        raise InternalServerErrorException("Failed to update customer")





def delete_customer(db: Session, db_customer: Customer):
    try:
        db.delete(db_customer)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise InternalServerErrorException("Failed to delete customer")
