import pytest
import sqlite3
import os

DB_PATH = os.environ.get('DATABASE_URL', 'db/database.db')

def test_db_schema():
    # Connect to the database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check users table
    cursor.execute("PRAGMA table_info(users);")
    users_columns = [column[1] for column in cursor.fetchall()]
    expected_users_columns = ['id', 'username', 'password', 'role', 'created_at']
    assert all(col in users_columns for col in expected_users_columns)

    # Check clients table
    cursor.execute("PRAGMA table_info(clients);")
    clients_columns = [column[1] for column in cursor.fetchall()]
    expected_clients_columns = ['id', 'name', 'email', 'phone', 'address', 'created_at']
    assert all(col in clients_columns for col in expected_clients_columns)

    # Check products table
    cursor.execute("PRAGMA table_info(products);")
    products_columns = [column[1] for column in cursor.fetchall()]
    expected_products_columns = ['id', 'name', 'description', 'price', 'created_at']
    assert all(col in products_columns for col in expected_products_columns)

    # Check invoices table
    cursor.execute("PRAGMA table_info(invoices);")
    invoices_columns = [column[1] for column in cursor.fetchall()]
    expected_invoices_columns = ['id', 'agent_id', 'client_id', 'items', 'total', 'status', 'invoice_date', 'updated_at']
    assert all(col in invoices_columns for col in expected_invoices_columns)

    # Close the connection
    conn.close()