"""Authentication service."""
import bcrypt
from typing import Optional, Dict
from .database import get_db_connection


def hash_password(plain: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(plain.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    try:
        return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False


def authenticate_user(username: str, password: str) -> Optional[Dict]:
    """Authenticate a user and return user data if successful."""
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, username, password, role FROM users WHERE username = ?",
            (username,)
        )
        row = cur.fetchone()
        
        if row and verify_password(password, row["password"]):
            return {
                "id": row["id"],
                "username": row["username"],
                "role": row["role"]
            }
    return None


def create_user(username: str, password: str, role: str) -> int:
    """Create a new user."""
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, hash_password(password), role)
        )
        conn.commit()
        return cur.lastrowid


def create_default_admin() -> None:
    """Create default admin user if not exists."""
    import os
    admin_user = "admin1"
    admin_pass = os.environ.get('ADMIN_PASSWORD', 'admin_password')
    
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE username = ?", (admin_user,))
        if cur.fetchone() is None:
            cur.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                (admin_user, hash_password(admin_pass), 'admin')
            )
            conn.commit()
