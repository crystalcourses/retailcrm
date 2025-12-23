from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


class CustomerFilter(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    created_at_from: Optional[datetime] = None
    created_at_to: Optional[datetime] = None


class CustomerCreate(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class CustomerResponse(BaseModel):
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    created_at: Optional[str] = None


class OrderItem(BaseModel):
    product_name: str
    quantity: int = Field(gt=0)
    price: float = Field(gt=0)


class OrderCreate(BaseModel):
    customer_id: int
    items: List[OrderItem]
    number: Optional[str] = None


class OrderResponse(BaseModel):
    id: int
    number: Optional[str] = None
    customer_id: Optional[int] = None
    created_at: Optional[str] = None
    status: Optional[str] = None
    total_sum: Optional[float] = None


class PaymentCreate(BaseModel):
    amount: float = Field(gt=0)
    type: Optional[str] = "cash"
    status: Optional[str] = "paid"


class PaymentResponse(BaseModel):
    id: int
    order_id: int
    amount: float
    type: Optional[str] = None
    status: Optional[str] = None