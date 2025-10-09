from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid

class CustomerBase(BaseModel):
    name: str
    email: EmailStr

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    stripe_customer_id: Optional[str] = None

class CustomerOut(CustomerBase):
    id: uuid.UUID
    stripe_customer_id: Optional[str]

    class Config:
        orm_mode = True
