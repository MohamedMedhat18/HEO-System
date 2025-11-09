"""Data models for the HEO System."""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user model."""
    username: str
    role: str = Field(..., pattern="^(admin|agent)$")


class UserCreate(UserBase):
    """User creation model."""
    password: str


class User(UserBase):
    """User model with ID."""
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ClientBase(BaseModel):
    """Base client model."""
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class ClientCreate(ClientBase):
    """Client creation model."""
    pass


class Client(ClientBase):
    """Client model with ID."""
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    """Base product model."""
    name: str
    description: Optional[str] = None
    price: float


class ProductCreate(ProductBase):
    """Product creation model."""
    pass


class Product(ProductBase):
    """Product model with ID."""
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class InvoiceItem(BaseModel):
    """Invoice item model."""
    description: str
    quantity: int
    price: float
    total: Optional[float] = None
    code: Optional[str] = None


class InvoiceBase(BaseModel):
    """Base invoice model."""
    agent_id: Optional[int] = None
    client_id: int
    items: List[InvoiceItem]
    invoice_type: Optional[str] = "Quotation Invoice"
    language: Optional[str] = "en"
    notes: Optional[str] = None
    client_name: Optional[str] = None
    client_address: Optional[str] = None
    currency: Optional[str] = "EGP"
    exchange_rate: Optional[float] = 1.0


class InvoiceCreate(InvoiceBase):
    """Invoice creation model."""
    pass


class Invoice(InvoiceBase):
    """Invoice model with ID and computed fields."""
    id: int
    total: float
    status: str = "Pending"
    invoice_date: datetime
    updated_at: datetime
    pdf_path: Optional[str] = None

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    """Login request model."""
    username: str
    password: str


class LoginResponse(BaseModel):
    """Login response model."""
    success: bool
    user: Optional[User] = None
    message: Optional[str] = None


class EmployeeBase(BaseModel):
    """Base employee model."""
    name: str
    role: str = "agent"
    email: Optional[str] = None


class EmployeeCreate(EmployeeBase):
    """Employee creation model."""
    pass


class Employee(EmployeeBase):
    """Employee model with ID."""
    id: int

    class Config:
        from_attributes = True
