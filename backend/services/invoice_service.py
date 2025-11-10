"""Invoice service for business logic."""
import json
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from .database import get_db_connection


def get_all_invoices() -> List[Dict]:
    """Get all invoices with client and agent information."""
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT invoices.*, clients.name AS client_name, users.username AS agent_username
            FROM invoices
            LEFT JOIN clients ON invoices.client_id = clients.id
            LEFT JOIN users ON invoices.agent_id = users.id
            ORDER BY invoice_date DESC
        """)
        rows = cur.fetchall()
        return [dict(row) for row in rows]


def get_agent_invoices(agent_id: int) -> List[Dict]:
    """Get invoices for a specific agent."""
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT invoices.*, clients.name AS client_name
            FROM invoices
            LEFT JOIN clients ON invoices.client_id = clients.id
            WHERE agent_id = ?
            ORDER BY invoice_date DESC
        """, (agent_id,))
        return [dict(r) for r in cur.fetchall()]


def get_invoice_by_id(invoice_id: int) -> Optional[Dict]:
    """Get a single invoice by ID."""
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT invoices.*, clients.name AS client_name, users.username AS agent_username
            FROM invoices
            LEFT JOIN clients ON invoices.client_id = clients.id
            LEFT JOIN users ON invoices.agent_id = users.id
            WHERE invoices.id = ?
        """, (invoice_id,))
        row = cur.fetchone()
        return dict(row) if row else None


def create_invoice(
    agent_id: Optional[int],
    client_id: int,
    items: List[Dict],
    invoice_type: Optional[str] = None,
    language: Optional[str] = None,
    notes: Optional[str] = None,
    client_name: Optional[str] = None,
    client_address: Optional[str] = None,
    currency: Optional[str] = None,
    exchange_rate: Optional[float] = None
) -> int:
    """Create a new invoice and return its ID."""
    created_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    
    # Calculate total
    try:
        total = sum(
            float(item.get('total', item.get('quantity', 0) * item.get('price', 0)))
            for item in items
        )
    except Exception:
        total = 0.0
    
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO invoices (
                agent_id, client_id, items, total, status, invoice_date, updated_at,
                client_name, client_address, created_at, currency, exchange_rate,
                invoice_type, language, notes
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                agent_id,
                client_id,
                json.dumps(items, ensure_ascii=False),
                total,
                'Pending',
                created_at,
                created_at,
                client_name or "",
                client_address or "",
                created_at,
                currency or "EGP",
                exchange_rate if exchange_rate is not None else 1.0,
                invoice_type or "Quotation Request",
                language or "en",
                notes or ""
            )
        )
        conn.commit()
        return cur.lastrowid


def update_invoice_status(invoice_id: int, status: str) -> None:
    """Update the status of an invoice."""
    updated_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE invoices SET status = ?, updated_at = ? WHERE id = ?",
            (status, updated_at, invoice_id)
        )
        conn.commit()


def update_invoice_pdf_path(invoice_id: int, pdf_path: str) -> None:
    """Update the PDF path for an invoice."""
    updated_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE invoices SET pdf_path = ?, updated_at = ? WHERE id = ?",
            (pdf_path, updated_at, invoice_id)
        )
        conn.commit()


def auto_cancel_pending_invoices(days: int = 15) -> None:
    """Automatically cancel invoices that have been pending for more than specified days."""
    cutoff_dt = datetime.utcnow() - timedelta(days=days)
    cutoff = cutoff_dt.strftime('%Y-%m-%d %H:%M:%S')
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE invoices SET status='Cancelled', updated_at=? WHERE status='Pending' AND invoice_date<=?",
            (now, cutoff)
        )
        conn.commit()


def get_clients() -> List[Dict]:
    """Get all clients."""
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM clients ORDER BY created_at DESC")
        return [dict(r) for r in cur.fetchall()]


def get_client_by_id(client_id: int) -> Optional[Dict]:
    """Get a single client by ID."""
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
        row = cur.fetchone()
        return dict(row) if row else None


def create_client(name: str, email: Optional[str], phone: Optional[str], address: Optional[str]) -> int:
    """Create a new client or return existing client ID."""
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        # Check if client exists by email
        if email:
            cur.execute("SELECT id FROM clients WHERE email = ?", (email,))
            row = cur.fetchone()
            if row:
                return row['id']
        
        # Create new client
        cur.execute(
            "INSERT INTO clients (name, email, phone, address) VALUES (?, ?, ?, ?)",
            (name, email, phone, address)
        )
        conn.commit()
        return cur.lastrowid


def get_products() -> List[Dict]:
    """Get all products."""
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM products ORDER BY created_at DESC")
        return [dict(r) for r in cur.fetchall()]


def get_employees() -> List[Dict]:
    """Get all employees."""
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, name, role, email FROM employees ORDER BY name")
        return [dict(r) for r in cur.fetchall()]


def create_employee(name: str, role: str, email: Optional[str]) -> int:
    """Create a new employee."""
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO employees (name, role, email) VALUES (?, ?, ?)",
            (name, role, email)
        )
        conn.commit()
        return cur.lastrowid


def delete_employee(employee_id: int) -> None:
    """Delete an employee."""
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM employees WHERE id = ?", (employee_id,))
        conn.commit()
