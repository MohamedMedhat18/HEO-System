"""FastAPI main application."""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import json

from backend.models import (
    User, UserCreate, Client, ClientCreate, Product, ProductCreate,
    Invoice, InvoiceCreate, LoginRequest, LoginResponse,
    Employee, EmployeeCreate
)
from backend.services.database import init_db
from backend.services.auth import authenticate_user, create_user, create_default_admin
from backend.services.invoice_service import (
    get_all_invoices, get_agent_invoices, get_invoice_by_id,
    create_invoice, update_invoice_status, update_invoice_pdf_path,
    auto_cancel_pending_invoices, get_clients, get_client_by_id,
    create_client, get_products, get_employees, create_employee, delete_employee
)

# Initialize FastAPI app
app = FastAPI(
    title="HEO System API",
    description="Professional Invoice Management System with AI-driven capabilities",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database and create default users on startup."""
    init_db()
    create_default_admin()
    auto_cancel_pending_invoices()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "HEO System API",
        "version": "2.0.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Authentication endpoints
@app.post("/api/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Authenticate user and return user data."""
    user_data = authenticate_user(request.username, request.password)
    
    if user_data:
        return LoginResponse(
            success=True,
            user=User(**user_data),
            message="Login successful"
        )
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password"
    )


@app.post("/api/auth/register", response_model=User)
async def register(user: UserCreate):
    """Register a new user (admin only in production)."""
    try:
        user_id = create_user(user.username, user.password, user.role)
        return User(id=user_id, username=user.username, role=user.role)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create user: {str(e)}"
        )


# Invoice endpoints
@app.get("/api/invoices", response_model=List[dict])
async def list_invoices(agent_id: Optional[int] = None):
    """List all invoices or filter by agent."""
    if agent_id:
        return get_agent_invoices(agent_id)
    return get_all_invoices()


@app.get("/api/invoices/{invoice_id}", response_model=dict)
async def get_invoice(invoice_id: int):
    """Get a single invoice by ID."""
    invoice = get_invoice_by_id(invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    return invoice


@app.post("/api/invoices", response_model=dict)
async def create_new_invoice(invoice_data: InvoiceCreate):
    """Create a new invoice."""
    try:
        # Convert items to dict format
        items_list = [item.dict() for item in invoice_data.items]
        
        invoice_id = create_invoice(
            agent_id=invoice_data.agent_id,
            client_id=invoice_data.client_id,
            items=items_list,
            invoice_type=invoice_data.invoice_type,
            language=invoice_data.language,
            notes=invoice_data.notes,
            client_name=invoice_data.client_name,
            client_address=invoice_data.client_address,
            currency=invoice_data.currency,
            exchange_rate=invoice_data.exchange_rate
        )
        
        return {"id": invoice_id, "message": "Invoice created successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create invoice: {str(e)}"
        )


@app.patch("/api/invoices/{invoice_id}/status")
async def update_status(invoice_id: int, status: str):
    """Update invoice status."""
    try:
        update_invoice_status(invoice_id, status)
        return {"message": "Status updated successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update status: {str(e)}"
        )


@app.patch("/api/invoices/{invoice_id}/pdf")
async def update_pdf(invoice_id: int, pdf_path: str):
    """Update invoice PDF path."""
    try:
        update_invoice_pdf_path(invoice_id, pdf_path)
        return {"message": "PDF path updated successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update PDF path: {str(e)}"
        )


# Client endpoints
@app.get("/api/clients", response_model=List[dict])
async def list_clients():
    """List all clients."""
    return get_clients()


@app.get("/api/clients/{client_id}", response_model=dict)
async def get_client(client_id: int):
    """Get a single client by ID."""
    client = get_client_by_id(client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    return client


@app.post("/api/clients", response_model=dict)
async def create_new_client(client: ClientCreate):
    """Create a new client."""
    try:
        client_id = create_client(
            name=client.name,
            email=client.email,
            phone=client.phone,
            address=client.address
        )
        return {"id": client_id, "message": "Client created successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create client: {str(e)}"
        )


# Product endpoints
@app.get("/api/products", response_model=List[dict])
async def list_products():
    """List all products."""
    return get_products()


# Employee endpoints
@app.get("/api/employees", response_model=List[dict])
async def list_employees():
    """List all employees."""
    return get_employees()


@app.post("/api/employees", response_model=dict)
async def create_new_employee(employee: EmployeeCreate):
    """Create a new employee."""
    try:
        employee_id = create_employee(
            name=employee.name,
            role=employee.role,
            email=employee.email
        )
        return {"id": employee_id, "message": "Employee created successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create employee: {str(e)}"
        )


@app.delete("/api/employees/{employee_id}")
async def remove_employee(employee_id: int):
    """Delete an employee."""
    try:
        delete_employee(employee_id)
        return {"message": "Employee deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete employee: {str(e)}"
        )


# Statistics endpoint
@app.get("/api/stats")
async def get_statistics():
    """Get system statistics."""
    invoices = get_all_invoices()
    
    total_invoices = len(invoices)
    total_sales = sum(float(inv.get('total', 0) or 0) for inv in invoices)
    pending = sum(1 for inv in invoices if inv.get('status') == 'Pending')
    paid = sum(1 for inv in invoices if inv.get('status') == 'Paid')
    cancelled = sum(1 for inv in invoices if inv.get('status') == 'Cancelled')
    
    return {
        "total_invoices": total_invoices,
        "total_sales": round(total_sales, 2),
        "pending": pending,
        "paid": paid,
        "cancelled": cancelled
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
