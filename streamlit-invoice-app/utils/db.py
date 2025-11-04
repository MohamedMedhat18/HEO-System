def get_db_connection():
    import sqlite3
    import os

    DB_PATH = os.environ.get('DATABASE_URL', 'db/database.db')
    if DB_PATH.startswith('sqlite:///'):
        DB_PATH = DB_PATH.replace('sqlite:///', '')

    conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def ensure_db():
    from utils.env_checks import check_required_modules

    check_required_modules()
    _ensure_directory_for_db(DB_PATH)
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin','agent')),
            created_at TEXT DEFAULT (datetime('now'))
        )""")
        cur.execute("""CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            phone TEXT,
            address TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )""")
        cur.execute("""CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )""")
        cur.execute("""CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id INTEGER,
            client_id INTEGER,
            items TEXT,
            total REAL,
            status TEXT DEFAULT 'Pending' CHECK(status IN ('Pending','Paid','Cancelled')),
            invoice_date TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY(agent_id) REFERENCES users(id),
            FOREIGN KEY(client_id) REFERENCES clients(id)
        )""")
        conn.commit()

def _ensure_directory_for_db(path):
    dirn = os.path.dirname(path)
    if dirn:
        os.makedirs(dirn, exist_ok=True)