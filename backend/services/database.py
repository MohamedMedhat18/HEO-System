"""Database connection and utility functions."""
import os
import sqlite3
from typing import Optional
from contextlib import contextmanager


DB_PATH = os.environ.get('DATABASE_URL', 'db/database.db')
if DB_PATH.startswith('sqlite:///'):
    DB_PATH = DB_PATH.replace('sqlite:///', '')


def _ensure_directory_for_db(path: str) -> None:
    """Ensure the directory for the database file exists."""
    dirn = os.path.dirname(path)
    if dirn:
        os.makedirs(dirn, exist_ok=True)


@contextmanager
def get_db_connection():
    """Get a database connection with row factory."""
    _ensure_directory_for_db(DB_PATH)
    conn = sqlite3.connect(
        DB_PATH,
        detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
        check_same_thread=False
    )
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db() -> None:
    """Initialize database with required tables."""
    _ensure_directory_for_db(DB_PATH)
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        # Users table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin','agent')),
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        
        # Clients table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                phone TEXT,
                address TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        
        # Products table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        
        # Invoices table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id INTEGER,
                client_id INTEGER,
                items TEXT,
                total REAL,
                status TEXT DEFAULT 'Pending' CHECK(status IN ('Pending','Paid','Cancelled')),
                invoice_date TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now')),
                client_name TEXT,
                client_address TEXT,
                created_at TEXT,
                currency TEXT,
                exchange_rate REAL,
                invoice_type TEXT,
                language TEXT,
                notes TEXT,
                pdf_path TEXT
            )
        """)
        
        # Employees table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                role TEXT DEFAULT 'agent',
                email TEXT
            )
        """)
        
        conn.commit()
