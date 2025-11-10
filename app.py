# Auto-install & safe-import helper (Windows compatible, Python 3.10+)
# New helpers added in this file:
# - generate_pdf_bytes(invoice_data: dict, out_lang: str = 'en') -> bytes
# - save_pdf_bytes(bytes, filename) -> str (writes to invoices/ and returns path)
# - ensure_invoice_columns() -> ensures required columns exist in invoices table (auto-migration)
# - ensure_employees_table() -> ensures employees table exists
# Developer quick check: run `python -m py_compile app.py` to syntax-check the file.
import sys
import subprocess
import importlib
import traceback
import os
import sqlite3
import json
import io
from datetime import datetime, timedelta

# List of required packages mapped to the import path we will try and the pip package name
_REQUIRED = {
    "streamlit": "streamlit",
    "bcrypt": "bcrypt",
    "plotly.express": "plotly",
    "reportlab": "reportlab",
    "arabic_reshaper": "arabic-reshaper",
    "bidi.algorithm": "python-bidi",
    "pandas": "pandas",
    "openpyxl": "openpyxl",  # Excel engine for pandas
}

_installed_modules = {}
_missing = []

def _try_import(name):
    try:
        return importlib.import_module(name)
    except Exception:
        return None

def _ensure_packages():
    global _installed_modules, _missing
    for import_name, pip_name in _REQUIRED.items():
        mod = _try_import(import_name)
        if mod is None:
            # attempt installation
            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", pip_name],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                mod = _try_import(import_name)
            except Exception:
                mod = None
        if mod is None:
            _missing.append((import_name, pip_name))
        else:
            _installed_modules[import_name] = mod

# Run ensure (will attempt to pip install missing packages)
try:
    _ensure_packages()
except Exception:
    _missing.append(("package_install", "see traceback"))
    traceback.print_exc()

# Map dynamic imports to local variables used in the app
st = _installed_modules.get("streamlit")
bcrypt = _installed_modules.get("bcrypt")
px = _installed_modules.get("plotly.express")  # plotly.express module or None
pd = _installed_modules.get("pandas")
# reportlab submodules (we'll import platypus/register font when needed)
reportlab_available = "reportlab" in _installed_modules
arabic_reshaper = _installed_modules.get("arabic_reshaper")
get_display = None
if "bidi.algorithm" in _installed_modules:
    try:
        _bidi_mod = importlib.import_module("bidi.algorithm")
        get_display = getattr(_bidi_mod, "get_display", None)
    except Exception:
        get_display = None

# If streamlit isn't available we cannot render UI; provide console instruction and exit gracefully
if st is None:
    print("⚠️ Missing required module 'streamlit'.")
    print("Run: pip install -r requirements.txt")
    raise SystemExit("Missing streamlit")

# If there are other missing packages, build messages for UI
# _missing is list of tuples (import_name, pip_name)
def show_missing_packages_notice():
    if _missing:
        st.sidebar.markdown("### ⚠️ Missing Python packages")
        for imp, pipname in _missing:
            st.sidebar.error(f"Module '{imp}' is missing (pip: {pipname}). Run `pip install {pipname}` or `pip install -r requirements.txt`")

# -------------------------
# Project paths
# -------------------------
ROOT = os.path.abspath(os.path.dirname(__file__))
ASSETS_DIR = os.path.join(ROOT, "assets")
LOGO_PATH = os.path.join(ASSETS_DIR, "logo.png")
INVOICES_DIR = os.path.join(ROOT, "invoices")
TAJAWAL_TTF = os.path.join(ROOT, "Tajawal-Regular.ttf")
ROBOTO_REG = os.path.join(ROOT, "Roboto-Regular.ttf")
ROBOTO_BOLD = os.path.join(ROOT, "Roboto-Bold.ttf")

os.makedirs(ASSETS_DIR, exist_ok=True)
os.makedirs(INVOICES_DIR, exist_ok=True)

# -------------------------
# Database helpers and migrations
# -------------------------
DB_PATH = os.environ.get('DATABASE_URL', 'db/database.db')
if DB_PATH.startswith('sqlite:///'):
    DB_PATH = DB_PATH.replace('sqlite:///', '')

def get_db_connection():
    _ensure_directory_for_db(DB_PATH)
    conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def _ensure_directory_for_db(path):
    dirn = os.path.dirname(path)
    if dirn:
        os.makedirs(dirn, exist_ok=True)

def ensure_db():
    _ensure_directory_for_db(DB_PATH)
    with get_db_connection() as conn:
        cur = conn.cursor()
        # Base tables
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
        # Original invoices table (legacy) - we'll migrate/add columns afterwards
        cur.execute("""CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id INTEGER,
            client_id INTEGER,
            items TEXT,
            total REAL,
            status TEXT DEFAULT 'Pending' CHECK(status IN ('Pending','Paid','Cancelled')),
            invoice_date TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )""")
        conn.commit()
    # migrations / ensure extra tables/columns
    ensure_employees_table()
    ensure_invoice_columns()
    create_default_users()

def ensure_employees_table():
    """Create employees table if missing"""
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                role TEXT DEFAULT 'agent',
                email TEXT
            )
        """)
        conn.commit()

def ensure_invoice_columns():
    """Add missing columns to invoices table (auto-migration)."""
    required = {
        "client_name": "TEXT",
        "client_address": "TEXT",
        "created_at": "TEXT",
        "currency": "TEXT",
        "exchange_rate": "REAL",
        "invoice_type": "TEXT",
        "language": "TEXT",
        "agent_id": "INTEGER",
        "pdf_path": "TEXT",
        "notes": "TEXT"
    }
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(invoices)")
        existing = {row["name"] for row in cur.fetchall()}
        for col, coltype in required.items():
            if col not in existing:
                try:
                    cur.execute(f"ALTER TABLE invoices ADD COLUMN {col} {coltype}")
                except Exception:
                    pass
        conn.commit()

def hash_password(plain):
    if bcrypt is None:
        # fallback insecure hash to avoid crashing (but notify user)
        import hashlib
        return hashlib.sha256(plain.encode('utf-8')).hexdigest()
    return bcrypt.hashpw(plain.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain, hashed):
    try:
        if bcrypt is None:
            import hashlib
            return hashlib.sha256(plain.encode('utf-8')).hexdigest() == hashed
        return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False

def create_default_users():
    # keep minimal admin users if not present
    admins = [
        ("admin1", os.environ.get('ADMIN_PASSWORD', 'admin_password')),
    ]
    with get_db_connection() as conn:
        cur = conn.cursor()
        for username, pwd in admins:
            cur.execute("SELECT id FROM users WHERE username = ?", (username,))
            if cur.fetchone() is None:
                cur.execute("INSERT INTO users (username,password,role) VALUES (?,?,?)",
                            (username, hash_password(pwd), 'admin'))
        conn.commit()

# -------------------------
# Automated status update: Pending > 15 days -> Cancelled
# -------------------------
def auto_cancel_pending():
    cutoff_dt = datetime.utcnow() - timedelta(days=15)
    cutoff = cutoff_dt.strftime('%Y-%m-%d %H:%M:%S')
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE invoices SET status='Cancelled', updated_at=? WHERE status='Pending' AND invoice_date<=?",
                    (now, cutoff))
        conn.commit()

# Ensure DB and apply background maintenance once
ensure_db()
auto_cancel_pending()

# -------------------------
# Caching
# -------------------------
@st.cache_data(ttl=60)
def load_invoices():
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

@st.cache_data(ttl=60)
def load_users():
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, username, role FROM users")
        return [dict(r) for r in cur.fetchall()]

@st.cache_data(ttl=60)
def load_employees():
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, name, role, email FROM employees ORDER BY name")
        return [dict(r) for r in cur.fetchall()]

# -------------------------
# Helpers: robust JSON loader (strip JS-style comments)
# -------------------------
def load_json_strip_comments(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception:
        return {}
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith('//'):
            continue
        if '//' in line:
            idx = line.index('//')
            line = line[:idx]
        lines.append(line)
    cleaned = '\n'.join(lines)
    try:
        return json.loads(cleaned)
    except Exception:
        return {}

# Load translations (safe)
en_text = load_json_strip_comments(os.path.join('locales', 'en.json')) or {}
ar_text = load_json_strip_comments(os.path.join('locales', 'ar.json')) or {}

# -------------------------
# PDF generation & saving
# -------------------------
def _shape_text_for_pdf(text, rtl=False):
    if not isinstance(text, str):
        text = str(text)
    if rtl and arabic_reshaper is not None and get_display is not None:
        try:
            shaped = arabic_reshaper.reshape(text)
            return get_display(shaped)
        except Exception:
            return text
    return text

def save_pdf_bytes(pdf_bytes: bytes, filename: str) -> str:
    """Save bytes to invoices/ and return relative path."""
    os.makedirs(INVOICES_DIR, exist_ok=True)
    out_path = os.path.join(INVOICES_DIR, filename)
    with open(out_path, "wb") as f:
        f.write(pdf_bytes)
    return out_path

def generate_pdf_bytes(invoice_data: dict, out_lang: str = 'en') -> bytes:
    """
    Professional, language-aware PDF generator (replacement).
    Replaced internal layout with the provided new professional template while keeping all
    previous integration points (returns PDF bytes, supports Arabic shaping, fonts, logo, etc.)
    """
    # Fallback: if reportlab missing, return readable text bytes
    if not reportlab_available:
        text = f"Invoice (fallback)\n\n{json.dumps(invoice_data, ensure_ascii=False, indent=2)}"
        return text.encode("utf-8")

    # Dynamic imports (safe)
    try:
        rl_pages = importlib.import_module("reportlab.lib.pagesizes")
        rl_colors = importlib.import_module("reportlab.lib.colors")
        platypus = importlib.import_module("reportlab.platypus")
        rl_tables = platypus  # for Table, Paragraph, Image, Spacer usage
        ttfonts = importlib.import_module("reportlab.pdfbase.ttfonts")
        pdfmetrics = importlib.import_module("reportlab.pdfbase.pdfmetrics")
        rl_styles = importlib.import_module("reportlab.lib.styles")
        rl_paragraph = importlib.import_module("reportlab.platypus.paragraph")
        rl_table_style = importlib.import_module("reportlab.platypus.tables")
        rl_enums = importlib.import_module("reportlab.lib.enums")
        # for ParagraphStyle
        ParagraphStyle = getattr(rl_styles, "ParagraphStyle", rl_paragraph.Paragraph)
    except Exception:
        text = f"Invoice (fallback)\n\n{json.dumps(invoice_data, ensure_ascii=False, indent=2)}"
        return text.encode("utf-8")

    # PIL dynamic import for image sizing
    PIL_Image = _try_import("PIL.Image")

    A4 = rl_pages.A4
    colors = rl_colors
    SimpleDocTemplate = platypus.SimpleDocTemplate
    Table = platypus.Table
    TableStyle = platypus.TableStyle
    Paragraph = platypus.Paragraph
    Image = platypus.Image
    Spacer = platypus.Spacer
    TA_CENTER = rl_enums.TA_CENTER
    TA_LEFT = rl_enums.TA_LEFT
    TA_RIGHT = rl_enums.TA_RIGHT

    # Register fonts: prefer Roboto, fall back to Tajawal for Arabic, else Helvetica
    FONT = "Helvetica"
    FONTB = "Helvetica-Bold"
    try:
        # Try Roboto first if files available
        if os.path.exists(ROBOTO_REG) and os.path.exists(ROBOTO_BOLD):
            pdfmetrics.registerFont(ttfonts.TTFont("Roboto", ROBOTO_REG))
            pdfmetrics.registerFont(ttfonts.TTFont("Roboto-Bold", ROBOTO_BOLD))
            FONT, FONTB = "Roboto", "Roboto-Bold"
        elif out_lang == 'ar' and os.path.exists(TAJAWAL_TTF):
            pdfmetrics.registerFont(ttfonts.TTFont("Tajawal", TAJAWAL_TTF))
            FONT, FONTB = "Tajawal", "Tajawal"
        else:
            # keep Helvetica - usually available
            FONT, FONTB = "Helvetica", "Helvetica-Bold"
    except Exception:
        FONT, FONTB = "Helvetica", "Helvetica-Bold"

    def get_logo_image(path, max_height):
        try:
            if path and os.path.exists(path):
                if PIL_Image is not None:
                    try:
                        pil_img = PIL_Image.open(path)
                        aspect = pil_img.width / pil_img.height if pil_img.height else 1
                        width = int(max_height * aspect)
                        return Image(path, width=width, height=max_height)
                    except Exception:
                        return Image(path, width=int(max_height * 2.5), height=max_height)
                else:
                    return Image(path, width=int(max_height * 2.5), height=max_height)
            # fallback spacer
            return Spacer(1, max_height)
        except Exception:
            return Spacer(1, max_height)

    def currency(val):
        try:
            v = str(val)
            # remove redundant LE if present and normalize spacing
            v = v.replace("LE", "").replace("EGP", "").strip()
            # Keep thousands separators if present, else format numeric
            try:
                f = float(v.replace(",", ""))
                v = f"{f:,.2f}"
            except Exception:
                pass
            if out_lang == 'ar':
                # Arabic: place currency after number
                return f"{_shape_text_for_pdf(v, rtl=True)} <font color='#3880fa'><b>{_shape_text_for_pdf('LE', rtl=True)}</b></font>"
            else:
                return f"{v} <font color='#3880fa'><b>LE</b></font>"
        except Exception:
            return f"{val}"

    # page drawing: outer border + watermark
    def draw_outer_and_watermark(canvas, doc):
        PAGE_WIDTH, PAGE_HEIGHT = A4
        margin = 14
        content_width = PAGE_WIDTH - 2*margin
        content_height = PAGE_HEIGHT - 2*margin

        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#b6c5e3"))
        canvas.setLineWidth(2)
        canvas.roundRect(margin, margin, content_width, content_height, 15, stroke=1, fill=0)

        try:
            canvas.setFont(FONTB, 92)
            canvas.setFillColor(colors.HexColor("#eaf2fa"))
            canvas.saveState()
            canvas.translate(PAGE_WIDTH/2, margin+110)
            canvas.rotate(17)
            canvas.drawCentredString(0, 0, "HEO")
            canvas.restoreState()
        except Exception:
            pass
        canvas.restoreState()

    # Build document in memory buffer
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=14, rightMargin=14, topMargin=14, bottomMargin=14)
    elements = []

    # Prepare localized text shaping
    def local_s(t):
        return _shape_text_for_pdf(t, rtl=(out_lang == 'ar'))

    # Build company info from constants (keeps same company used elsewhere)
    company = {
        "logo": LOGO_PATH if os.path.exists(LOGO_PATH) else "",
        "name": "EL HEKMA ENGINEERING OFFICE Co.",
        "desc":      "For Medical Devices & Supplies AND Professional Engineering Solutions",
        "address": "41 Al-Mawardi Street, Al-Qasr Al-Aini, Cairo, Egypt",
        "tel": "+201026531004 / +201147304880",
        "fax": "+2027932115",
        "email": "info@heomed.com",
        "website": "www.heomed.com"
    }

    # Prepare invoice data mapping to expected structure of the new template
    # Title (use invoice_type or default)
    inv_title = invoice_data.get("invoice_type") or (local_s("فاتورة") if out_lang == 'ar' else "Invoice")
    title = inv_title if out_lang == 'en' else local_s(inv_title)

    # Client mapping
    client = {
        "name": invoice_data.get("client_name", "") or "",
        "ref": invoice_data.get("client_ref", "") or invoice_data.get("client_id", "") or "",
        "tel": invoice_data.get("client_phone", "") or "",
        "country": invoice_data.get("client_country", "") or "",
        "currency": invoice_data.get("currency", "") or "EGP"
    }

    # Items mapping - adapt from existing items structure
    items_in = invoice_data.get("items", []) or []
    items = []
    for it in items_in:
        # support both old keys and new template keys
        desc = it.get("description") or it.get("desc") or ""
        qty = it.get("quantity") or it.get("qty") or 0
        unit_price = it.get("price") or it.get("unit") or 0
        total_price = it.get("total") or (float(qty or 0) * float(unit_price or 0))
        code = it.get("code") or ""
        items.append({
            "code": code,
            "desc": desc,
            "qty": qty,
            "unit": unit_price,
            "total": total_price
        })

    # Totals mapping and numeric aggregation
    try:
        subtotal = float(invoice_data.get("subtotal") or sum(float(it.get("total", 0) or 0) for it in items))
    except Exception:
        try:
            subtotal = float(invoice_data.get("total") or 0)
        except Exception:
            subtotal = 0.0
    try:
        tax = float(invoice_data.get("tax", 0) or 0)
    except Exception:
        tax = 0.0
    try:
        discount = float(invoice_data.get("discount", 0) or 0)
    except Exception:
        discount = 0.0
    net_total = subtotal + tax - discount

    totals = {
        "subtotal": f"LE{subtotal:,.2f}",
        "sales": f"LE{tax:,.2f}",
        "discount": f"LE{discount:,.2f}",
        "net": f"LE{net_total:,.2f}"
    }

    seller = {
        "sign": invoice_data.get("agent_name") or (invoice_data.get("seller", {}) or {}).get("sign") or ""
    }

    # COLORS & STYLES
    blue = colors.HexColor("#183475")
    accent = colors.HexColor("#3880fa")
    table_zebra = colors.HexColor("#f3f7fd")
    banner_bg = colors.HexColor("#e5eeff")
    seller_bg = colors.HexColor("#f8fafc")

    h1 = ParagraphStyle("h1", fontName=FONTB, fontSize=21, textColor=blue, alignment=TA_CENTER, leading=26)
    h2 = ParagraphStyle("h2", fontName=FONTB, fontSize=14, textColor=blue, alignment=TA_LEFT)
    subtitle = ParagraphStyle("subtitle", fontName=FONT, fontSize=11, textColor="#333", leading=17)
    header_info = ParagraphStyle("header_info", fontName=FONT, fontSize=9, alignment=TA_LEFT, leading=11, textColor="#222")
    table_header = ParagraphStyle("table_header", fontName=FONTB, fontSize=11, textColor=colors.white, alignment=TA_CENTER)
    table_cell = ParagraphStyle("table_cell", fontName=FONT, fontSize=10, alignment=TA_RIGHT)
    table_left = ParagraphStyle("table_left", fontName=FONT, fontSize=10, alignment=TA_LEFT)
    net_total_style = ParagraphStyle("net", fontName=FONTB, fontSize=15, textColor=accent, alignment=TA_RIGHT)
    seller_label = ParagraphStyle("seller_label", fontName=FONTB, fontSize=10, textColor=blue, alignment=TA_LEFT)
    seller_value = ParagraphStyle("seller_value", fontName=FONT, fontSize=10, textColor="#222", alignment=TA_LEFT)

    # Header block (company + logo)
    logo = get_logo_image(company.get("logo", ""), 40)
    company_head = [
        [
            logo,
            [
                Paragraph(f"<b>{local_s(company['name']) if out_lang=='ar' else company['name']}</b>", h2),
                Paragraph(local_s(company['desc']) if out_lang=='ar' else company['desc'], subtitle),
                Paragraph(f"<b>{local_s('ADDRESS') if out_lang=='ar' else 'ADDRESS'}:</b> {local_s(company['address']) if out_lang=='ar' else company['address']}", header_info),
                Paragraph(f"<b>{local_s('TEL') if out_lang=='ar' else 'TEL'}:</b> {company['tel']}    <b>{local_s('FAX') if out_lang=='ar' else 'FAX'}:</b> {company['fax']}", header_info),
                Paragraph(f"<b>{local_s('EMAIL') if out_lang=='ar' else 'EMAIL'}:</b> {company['email']}    <b>{local_s('WEB') if out_lang=='ar' else 'WEB'}:</b> {company['website']}", header_info)
            ]
        ]
    ]
    try:
        elements.append(
            Table(company_head, colWidths=[(A4[0]-28)*0.13, (A4[0]-28)*0.87], style=[
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f6f9fc")),
                ('BOX', (0,0), (-1,-1), 0.9, colors.HexColor("#c2d1e3")),
                ('BOTTOMPADDING', (0,0), (-1,-1), 7),
                ('LEFTPADDING', (1,0), (1,0), 16),
            ])
        )
    except Exception:
        # fallback simple paragraphs
        elements.append(Paragraph(company.get("name", ""), h2))
        elements.append(Spacer(1, 6))

    elements.append(Spacer(1, 13))

    # Title banner
    try:
        elements.append(Table([[Paragraph(local_s(title) if out_lang=='ar' else title, h1)]], colWidths=[A4[0]-28],
            style=TableStyle([
                ('BACKGROUND', (0,0), (0,0), banner_bg),
                ('BOX', (0,0), (0,0), 1, accent),
                ('ALIGN', (0,0), (0,0), 'CENTER'),
                ('TOPPADDING', (0,0), (0,0), 6),
                ('BOTTOMPADDING', (0,0), (0,0), 6),
            ])
        ))
    except Exception:
        elements.append(Paragraph(title, h1))
    elements.append(Spacer(1, 6))

    # Client Info table
    info_data = [
        [Paragraph(f"<b>{local_s('Client') if out_lang=='ar' else 'Client'}:</b> {local_s(client['name']) if out_lang=='ar' else client['name']}", table_left),
         Paragraph(f"<b>{local_s('Date') if out_lang=='ar' else 'Date'}:</b> {invoice_data.get('date', datetime.utcnow().strftime('%Y-%m-%d'))}", table_left),
         Paragraph(f"<b>{local_s('Ref. No.') if out_lang=='ar' else 'Ref. No.'}:</b> {local_s(str(client['ref'])) if out_lang=='ar' else client['ref']}", table_left)],
        [Paragraph(f"<b>{local_s('Tel') if out_lang=='ar' else 'Tel'}:</b> {client['tel']}", table_left),
         Paragraph(f"<b>{local_s('Country') if out_lang=='ar' else 'Country'}:</b> {client['country']}", table_left),
         Paragraph(f"<b>{local_s('Currency') if out_lang=='ar' else 'Currency'}:</b> {client['currency']}", table_left)],
    ]
    info_table = Table(info_data, colWidths=[(A4[0]-28)*0.34, (A4[0]-28)*0.33, (A4[0]-28)*0.33])
    info_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.7, colors.HexColor("#c2d1e3")),
        ('TOPPADDING', (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 13),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 13))

    # Product table header labels (localized)
    hdr_num = local_s("#") if out_lang=='ar' else "#"
    hdr_code = local_s("Code") if out_lang=='ar' else "Code"
    hdr_desc = local_s("Description") if out_lang=='ar' else "Description"
    hdr_qty = local_s("Quantity") if out_lang=='ar' else "Quantity"
    hdr_unit = local_s("Unit Price") if out_lang=='ar' else "Unit Price"
    hdr_total = local_s("Total Price") if out_lang=='ar' else "Total Price"

    items_data = [
        [Paragraph(hdr_num, table_header), Paragraph(hdr_code, table_header),
         Paragraph(hdr_desc, table_header), Paragraph(hdr_qty, table_header),
         Paragraph(hdr_unit, table_header), Paragraph(hdr_total, table_header)]
    ]
    for idx, item in enumerate(items, 1):
        desc_par = Paragraph(local_s(item['desc']) if out_lang=='ar' else (item['desc'] or ""), table_left)
        unit_val = currency(item['unit'])
        total_val = currency(item['total'])
        items_data.append([
            str(idx), item.get('code',''), desc_par,
            str(item.get('qty','')), Paragraph(unit_val, table_cell),
            Paragraph(total_val, table_cell)
        ])
    content_width = A4[0]-28
    items_col_widths = [
        content_width*0.07, content_width*0.13, content_width*0.35,
        content_width*0.13, content_width*0.15, content_width*0.17
    ]
    try:
        items_table = Table(items_data, colWidths=items_col_widths, style=[
            ('BACKGROUND', (0,0), (-1,0), blue),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 0.2, colors.HexColor("#b6c5e3")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, table_zebra]),
            ('TOPPADDING', (0,0), (-1,-1), 7),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ])
        elements.append(items_table)
    except Exception:
        # fallback simple listing
        for it in items:
            elements.append(Paragraph(f"{it.get('desc')} - {it.get('qty')} x {it.get('unit')} = {it.get('total')}", table_left))
    elements.append(Spacer(1, 13))

    # Totals table (localized labels)
    lbl_sub = local_s("Sub-Total:") if out_lang=='ar' else "Sub-Total:"
    lbl_sales = local_s("Sales (18%):") if out_lang=='ar' else "Sales (18%):"
    lbl_disc = local_s("Discount (0%):") if out_lang=='ar' else "Discount (0%):"

    totals_data = [
        [Paragraph(lbl_sub, table_left), Paragraph(currency(totals['subtotal']), table_cell)],
        [Paragraph(lbl_sales, table_left), Paragraph(currency(totals['sales']), table_cell)],
        [Paragraph(lbl_disc, table_left), Paragraph(currency(totals['discount']), table_cell)]
    ]
    totals_table = Table(totals_data, colWidths=[content_width*0.55, content_width*0.45])
    totals_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.8, colors.HexColor("#c2d1e3")),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.HexColor("#ecedfa")),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(totals_table)
    elements.append(Spacer(1, 10))

    # Net total block
    lbl_net = local_s("NET TOTAL:") if out_lang=='ar' else "NET TOTAL:"
    net_total_table = Table([
        [Paragraph(f"<b>{lbl_net}</b>", net_total_style),
         Paragraph(f"<b>{currency(totals['net'])}</b>", net_total_style)]
    ], colWidths=[content_width*0.55, content_width*0.45])
    net_total_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), banner_bg),
        ('BOX', (0,0), (-1,-1), 1, accent),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(net_total_table)
    elements.append(Spacer(1, 13))

    # Seller box
    seller_box = Table([
        [Paragraph(f"<b>{local_s('THE SELLER') if out_lang=='ar' else 'THE SELLER'}</b>", seller_label)],
        [Paragraph(local_s(company['name']) if out_lang=='ar' else company['name'], seller_value)],
        [Paragraph(f"{local_s('Signature') if out_lang=='ar' else 'Signature'}: <b>{local_s(seller['sign']) if out_lang=='ar' else seller['sign']}</b>", seller_value)],
        [Paragraph(f"{local_s('Date') if out_lang=='ar' else 'Date'}: {invoice_data.get('date', datetime.utcnow().strftime('%Y-%m-%d'))}", seller_value)]
    ], colWidths=[content_width - 40])
    seller_box.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#b6c5e3")),
        ('BACKGROUND', (0,0), (-1,-1), seller_bg),
        ('LEFTPADDING', (0,0), (-1,-1), 14),
        ('RIGHTPADDING', (0,0), (-1,-1), 14),
        ('TOPPADDING', (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
    ]))
    elements.append(seller_box)
    elements.append(Spacer(1, 10))

    # Footer note
    try:
        elements.append(Paragraph(
            local_s("This is an electronic invoice. Powered by HEO Systems.") if out_lang=='ar' else "This is an electronic invoice. Powered by HEO Systems.",
            ParagraphStyle("footer", fontName=FONT, fontSize=8, alignment=TA_CENTER, textColor=colors.HexColor("#bbb"))
        ))
    except Exception:
        pass

    # Build PDF
    try:
        doc.build(elements, onFirstPage=draw_outer_and_watermark, onLaterPages=draw_outer_and_watermark)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
    except Exception:
        # final fallback to readable bytes
        text = f"Invoice (generation failed)\n\n{json.dumps(invoice_data, ensure_ascii=False, indent=2)}"
        return text.encode("utf-8")

# -------------------------
# UI: Streamlit app
# -------------------------
st.set_page_config(page_title=en_text.get("app_title", "Invoice App"), layout="wide")
st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700&family=Roboto:wght@400;700&family=Tajawal:wght@400;700&display=swap" rel="stylesheet">
    <style>
    body { font-family: Lato, Roboto, sans-serif; }
    .card { background: white; padding: 16px; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }
    .rtl { direction: rtl; font-family: 'Tajawal', sans-serif; }
    </style>
    """,
    unsafe_allow_html=True,
)
# --- Company Logo and Header ---
st.markdown(
    """
    <div style='display: flex; align-items: center; gap: 12px; margin-top: 10px; margin-bottom: 20px;'>
        <img src='assets/logo1.png' width='85'>
        <h2 style='margin: 0; color: #183475;'>HEO Medical Systems</h2>
    </div>
    <hr style='border: 1px solid #e0e0e0; margin-top: 0;'>
    """,
    unsafe_allow_html=True
)


show_missing_packages_notice()

# initialize session user safely
st.session_state.setdefault('user', None)
st.session_state.setdefault('default_agent_id', None)

st.sidebar.title(en_text.get("app_title", "Invoice Management System"))
lang_choice = st.sidebar.selectbox("UI Language", options=["English", "Arabic"], index=0, key="ui_lang")
is_rtl = (lang_choice == "Arabic")
texts = en_text if not is_rtl else ar_text

# Authentication UI (simplified)
st.sidebar.subheader(texts.get("login", {}).get("login_button", "Login"))
with st.sidebar.form("login_form_v1"):
    username = st.text_input(texts.get("login", {}).get("username", "Username"), key="sid_username")
    password = st.text_input(texts.get("login", {}).get("password", "Password"), type="password", key="sid_password")
    submitted = st.form_submit_button(texts.get("login", {}).get("login_button", "Login"))

login_error = None
if submitted:
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, username, password, role FROM users WHERE username = ?", (username,))
        row = cur.fetchone()
        if row and verify_password(password, row["password"]):
            st.session_state.user = {"id": row["id"], "username": row["username"], "role": row["role"]}
            try:
                load_invoices.clear()
            except Exception:
                pass
            st.rerun()
        else:
            login_error = texts.get("login", {}).get("login_error", "Invalid username or password.")

if st.session_state.user:
    st.sidebar.success(f"{texts.get('dashboard', {}).get('welcome', 'Welcome')} — {st.session_state.user['username']}")
    if st.sidebar.button(texts.get("dashboard", {}).get("logout", "Logout"), key="sid_logout"):
        st.session_state.user = None
        st.rerun()
else:
    if login_error:
        st.sidebar.error(login_error)
    st.stop()

# Main navigation
menu_options = [
    texts.get("dashboard", {}).get("menu_dashboard", "Dashboard"),
    texts.get("invoices", {}).get("menu_invoices", "Invoices"),
    texts.get("clients", {}).get("menu_clients", "Clients"),
    texts.get("products", {}).get("menu_products", "Products"),
    texts.get("settings", {}).get("menu_settings", "Settings"),
]
menu = st.sidebar.selectbox(texts.get("dashboard", {}).get("menu_label", "Menu"), options=menu_options, key="main_menu")
menu_map = {
    texts.get("dashboard", {}).get("menu_dashboard", "Dashboard"): "Dashboard",
    texts.get("invoices", {}).get("menu_invoices", "Invoices"): "Invoices",
    texts.get("clients", {}).get("menu_clients", "Clients"): "Clients",
    texts.get("products", {}).get("menu_products", "Products"): "Products",
    texts.get("settings", {}).get("menu_settings", "Settings"): "Settings",
}
menu_key = menu_map.get(menu, "Dashboard")

# -------------------------
# Utility functions interacting with DB (extended)
# -------------------------
def _now_str():
    return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

def create_invoice_db(agent_id, client_id, items,
                      invoice_type=None, language=None, notes=None,
                      client_name=None, client_address=None,
                      currency=None, exchange_rate=None):
    """
    Fixed and extended create_invoice_db:
    - Restores the missing/broken function signature and parameters.
    - Accepts the keyword args used where the function is called elsewhere in the app.
    - Preserves existing behavior and table columns.
    - Returns the inserted invoice id.
    """
    created_at = _now_str()
    # compute total defensively
    try:
        total = sum(float(i.get('total', i.get('quantity', 0) * i.get('price', 0))) for i in items)
    except Exception:
        total = 0.0

    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO invoices (agent_id, client_id, items, total, status, invoice_date, updated_at,
               client_name, client_address, created_at, currency, exchange_rate, invoice_type, language, notes)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
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
                currency or "",
                (exchange_rate if exchange_rate is not None else 1.0),
                invoice_type or "",
                language or "",
                notes or ""
            )
        )
        conn.commit()
        return cur.lastrowid

def update_invoice_pdf_path(invoice_id, pdf_path):
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE invoices SET pdf_path=?, updated_at=? WHERE id=?", (pdf_path, _now_str(), invoice_id))
        conn.commit()

def get_agent_invoices(agent_id):
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT invoices.*, clients.name AS client_name
            FROM invoices
            LEFT JOIN clients ON invoices.client_id = clients.id
            WHERE agent_id=?
            ORDER BY invoice_date DESC
        """, (agent_id,))
        return [dict(r) for r in cur.fetchall()]

def get_all_invoices():
    return load_invoices()

def update_invoice_status(invoice_id, status):
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE invoices SET status=?, updated_at=? WHERE id=?", (status, _now_str(), invoice_id))
        conn.commit()
        try:
            load_invoices.clear()
        except Exception:
            pass

# -------------------------
# Dashboards and pages
# -------------------------
if menu_key == "Dashboard":
    st.title(texts.get("dashboard", {}).get("welcome", "Dashboard"))
    invoices = get_all_invoices()
    total_invoices = len(invoices)
    total_sales = sum(float(inv.get('total', 0) or 0) for inv in invoices)
    col1, col2, col3 = st.columns(3)
    col1.metric(texts.get("dashboard", {}).get("total_invoices", "Total Invoices"), total_invoices)
    col2.metric(texts.get("dashboard", {}).get("total_sales", "Total Sales"), f"{total_sales:.2f}")
    col3.metric(texts.get("dashboard", {}).get("status_summary", "Pending / Paid / Cancelled"),
                f"{sum(1 for i in invoices if i.get('status')=='Pending')} / {sum(1 for i in invoices if i.get('status')=='Paid')} / {sum(1 for i in invoices if i.get('status')=='Cancelled')}")
    # basic charts if available
    if px is not None and pd is not None:
        try:
            df = pd.DataFrame(invoices)
            if not df.empty:
                df['total'] = pd.to_numeric(df['total'], errors='coerce').fillna(0)
                fig_bar = px.bar(df.groupby('status', as_index=False).sum(), x='status', y='total', title="Sales by Status", labels={'total': 'Amount'})
                st.plotly_chart(fig_bar, use_container_width=True)
        except Exception:
            st.info("Plotly charts are not available.")

elif menu_key == "Invoices":
    st.title(texts.get("invoices", {}).get("view_invoices", "View Invoices"))
    if st.session_state.user['role'] == 'admin':
        invoices = get_all_invoices()
    else:
        invoices = get_agent_invoices(st.session_state.user['id'])

    # Search & filter
    search = st.text_input(texts.get("invoices", {}).get("search_placeholder", "Search by client, invoice id or product"), key="search_inv")
    status_filter = st.selectbox(texts.get("invoices", {}).get("status_filter_label", "Status"), options=["All", "Pending", "Paid", "Cancelled"], key="status_filter")
    filtered = []
    for inv in invoices:
        if search:
            s_txt = search.lower()
            if s_txt not in str(inv.get('id','')).lower() and s_txt not in str(inv.get('client_name','')).lower() and s_txt not in str(inv.get('agent_username','') or '').lower() and s_txt not in (inv.get('items') or '').lower():
                continue
        if status_filter != "All" and inv.get('status') != status_filter:
            continue
        filtered.append(inv)

    if pd is not None:
        df = pd.DataFrame(filtered) if filtered else pd.DataFrame()
        if not df.empty:
            st.dataframe(df)
        else:
            st.info(texts.get("invoices", {}).get("no_invoices", "No invoices found."))
    else:
        if filtered:
            for inv in filtered:
                st.write(inv)
        else:
            st.info(texts.get("invoices", {}).get("no_invoices", "No invoices found."))

    # Create invoice UI with dynamic items support (up to 30 items)
    st.subheader(texts.get("invoices", {}).get("create_invoice", "Create Invoice / Quotation Request"))
    employees = load_employees()
    employee_options = {str(e["id"]): e["name"] for e in employees}
    
    with st.form("create_invoice_form_v2"):
        st.markdown("### Client Information")
        col1, col2 = st.columns(2)
        with col1:
            client_name = st.text_input(texts.get("clients", {}).get("name_label", "Client Name"), key="ci_client_name")
            client_email = st.text_input(texts.get("clients", {}).get("email_label", "Client Email"), key="ci_client_email")
        with col2:
            client_address = st.text_input(texts.get("clients", {}).get("address_label", "Client Address"), key="ci_client_address")
            client_phone = st.text_input("Client Phone", key="ci_client_phone")
        
        st.markdown("### Document Details")
        col1, col2, col3 = st.columns(3)
        with col1:
            invoice_type = st.selectbox("Document Type", options=["Quotation Request", "Commercial Invoice", "Proforma Invoice"], key="ci_type")
        with col2:
            invoice_language = st.selectbox("Language", options=["en", "ar"], index=0, key="ci_lang")
        with col3:
            agent_choice = st.selectbox("Agent / Signer", options=["(none)"] + list(employee_options.values()), index=0, key="ci_agent")
        
        st.markdown("### Items")
        num_items = st.number_input("Number of Items", min_value=1, max_value=30, value=3, key="ci_num_items", help="Supports up to 30 items per request")
        
        items_data = []
        for i in range(num_items):
            st.markdown(f"**Item {i+1}**")
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col1:
                desc = st.text_input(f"Description", key=f"ci_item_desc_{i}", label_visibility="collapsed", placeholder="Enter item description...")
            with col2:
                qty = st.number_input(f"Qty", min_value=0, value=1, key=f"ci_item_qty_{i}", label_visibility="collapsed")
            with col3:
                price = st.number_input(f"Price", min_value=0.0, value=0.0, step=0.01, key=f"ci_item_price_{i}", label_visibility="collapsed")
            with col4:
                total = qty * price
                st.metric("Total", f"{total:.2f}", label_visibility="collapsed")
            
            if desc:  # Only add items with descriptions
                items_data.append({
                    "description": desc,
                    "quantity": int(qty),
                    "price": float(price),
                    "total": float(total)
                })
        
        # Show grand total
        grand_total = sum(item["total"] for item in items_data)
        st.markdown(f"### Grand Total: **LE {grand_total:,.2f}**")
        
        notes = st.text_area("Notes", key="ci_notes")
        submit_create = st.form_submit_button("🚀 Create " + invoice_type, use_container_width=True)

    if submit_create and client_name and items_data:
        # ensure client exists or create
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM clients WHERE email=?", (client_email,))
            row = cur.fetchone()
            if row:
                client_id = row['id']
            else:
                cur.execute("INSERT INTO clients (name,email,address,phone) VALUES (?,?,?,?)", (client_name, client_email, client_address, client_phone))
                client_id = cur.lastrowid
                conn.commit()
        
        # map agent name -> id
        agent_id = None
        agent_name = ""
        if agent_choice != "(none)":
            # find id by name
            for e in employees:
                if e["name"] == agent_choice:
                    agent_id = e["id"]
                    agent_name = e["name"]
                    break
        
        inv_id = create_invoice_db(agent_id, client_id, items_data, invoice_type=invoice_type, language=invoice_language, notes=notes, client_name=client_name, client_address=client_address)
        
        # generate PDF and save
        invoice_record = {
            "id": inv_id,
            "invoice_number": inv_id,
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "client_name": client_name,
            "client_address": client_address,
            "client_phone": client_phone,
            "items": items_data,
            "total": grand_total,
            "invoice_type": invoice_type,
            "language": invoice_language,
            "agent_id": agent_id,
            "agent_name": agent_name,
            "notes": notes,
            "tax": 0.0,
            "discount": 0.0
        }
        pdf_bytes = generate_pdf_bytes(invoice_record, out_lang=invoice_language)
        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        out_fname = f"{invoice_type.replace(' ', '_').lower()}_{inv_id}_{ts}_{invoice_language}.pdf"
        out_path = save_pdf_bytes(pdf_bytes, out_fname)
        update_invoice_pdf_path(inv_id, out_path)
        
        st.success(f"✅ {invoice_type} #{inv_id} created successfully!")
        st.info(f"📄 PDF saved: {out_path}")
        st.balloons()
        
        # Show summary
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1.5rem; border-radius: 12px; margin: 1rem 0;'>
            <h3>Document Summary</h3>
            <p><strong>Type:</strong> {invoice_type}</p>
            <p><strong>Client:</strong> {client_name}</p>
            <p><strong>Items:</strong> {len(items_data)}</p>
            <p><strong>Total Amount:</strong> LE {grand_total:,.2f}</p>
            <p><strong>Language:</strong> {'English' if invoice_language == 'en' else 'Arabic'}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # show download button
        st.download_button("📥 Download PDF", pdf_bytes, file_name=out_fname, mime="application/pdf", key=f"download_{inv_id}", use_container_width=True)
        try:
            load_invoices.clear()
        except Exception:
            pass
    elif submit_create and not items_data:
        st.error("⚠️ Please add at least one item with a description!")
    elif submit_create and not client_name:
        st.error("⚠️ Please provide a client name!")

elif menu_key == "Clients":
    st.title(texts.get("clients", {}).get("title", "Clients"))
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM clients ORDER BY created_at DESC")
        rows = cur.fetchall()
        if pd is not None:
            st.dataframe(pd.DataFrame([dict(r) for r in rows]))
        else:
            for r in rows:
                st.write(dict(r))

elif menu_key == "Products":
    st.title(texts.get("products", {}).get("title", "Products"))
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM products ORDER BY created_at DESC")
        rows = cur.fetchall()
        if pd is not None:
            st.dataframe(pd.DataFrame([dict(r) for r in rows]))
        else:
            for r in rows:
                st.write(dict(r))

else:  # Settings page
    st.title("Settings")
    if st.session_state.user['role'] != 'admin':
        st.info("Settings are for admins only.")
    else:
        st.subheader("Company Logo")
        uploaded = st.file_uploader("Upload company logo (PNG)", type=["png","jpg","jpeg"], key="logo_up")
        if uploaded:
            bytes_data = uploaded.read()
            with open(LOGO_PATH, "wb") as f:
                f.write(bytes_data)
            st.success("Logo uploaded.")
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=300)

        st.subheader("Employees")
        with st.form("add_employee_form"):
            emp_name = st.text_input("Name", key="emp_name")
            emp_role = st.selectbox("Role", options=["agent","admin"], key="emp_role")
            emp_email = st.text_input("Email", key="emp_email")
            add_emp = st.form_submit_button("Add Employee")
        if add_emp and emp_name:
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute("INSERT INTO employees (name, role, email) VALUES (?,?,?)", (emp_name, emp_role, emp_email))
                conn.commit()
            st.success("Employee added.")
            try:
                load_employees.clear()
            except Exception:
                pass

        st.subheader("Existing Employees")
        employees = load_employees()
        for e in employees:
            cols = st.columns([4,2,2])
            cols[0].write(e["name"])
            cols[1].write(e.get("role",""))
            if cols[2].button("Delete", key=f"del_emp_{e['id']}"):
                with get_db_connection() as conn:
                    cur = conn.cursor()
                    cur.execute("DELETE FROM employees WHERE id=?", (e['id'],))
                    conn.commit()
                st.experimental_rerun()

        st.subheader("PDF Template Preview")
        sample_inv = {
            "id": 0,
            "invoice_number": "SAMPLE-001",
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "client_name": "Sample Client",
            "client_address": "Sample Address",
            "items": [
                {"description": "Product A / منتج أ", "quantity": 2, "price": 50.0, "total": 100.0},
                {"description": "Product B / منتج ب", "quantity": 1, "price": 75.0, "total": 75.0},
            ],
            "total": 175.0,
            "invoice_type": "Quotation Request",
            "language": "en",
            "agent_name": "Demo Agent",
            "notes": "Sample notes here."
        }
        col1, col2 = st.columns(2)
        if col1.button("Preview EN PDF", key="preview_en"):
            pdf = generate_pdf_bytes(sample_inv, out_lang='en')
            st.download_button("Download Sample EN PDF", pdf, file_name="sample_en.pdf", mime="application/pdf", key="sample_en_dl")
        if col2.button("Preview AR PDF", key="preview_ar"):
            pdf = generate_pdf_bytes(sample_inv, out_lang='ar')
            st.download_button("Download Sample AR PDF", pdf, file_name="sample_ar.pdf", mime="application/pdf", key="sample_ar_dl")

# Footer
st.markdown("---")
st.write(texts.get("footer", {}).get("contact", "Contact Us"))

# -------------------------
# Additional helpers (Signatures, QR, Live preview, invoice-age check)
# Added: load_signatories_from_excel, get_signatory_image_path, render_signature_bytes,
# generate_qr_bytes, invoice_age_check_live, render_invoice_preview
#
# These helper functions are added (only) to extend functionality without modifying existing logic.
# They use dynamic imports and graceful fallbacks so missing optional packages don't break runtime.
# -------------------------

import base64
import tempfile
from typing import List, Dict, Optional

def load_signatories_from_excel(path: str = "signatories.xlsx") -> List[Dict]:
    """
    Try to load signatories from an Excel file with columns:
    name | role | signature_base64 | position
    Returns list of dicts with keys: name, role, signature_base64, position
    Graceful fallback to an empty list if file or library missing.
    """
    try:
        # prefer pandas if available
        pd_mod = _installed_modules.get("pandas")
        if pd_mod:
            df = pd_mod.read_excel(path, engine="openpyxl")
            rows = []
            for _, r in df.fillna("").iterrows():
                rows.append({
                    "name": str(r.get("name", "")).strip(),
                    "role": str(r.get("role", "")).strip(),
                    "signature_base64": str(r.get("signature_base64", "")).strip(),
                    "position": str(r.get("position", "")).strip()
                })
            return [r for r in rows if r["name"]]
        else:
            # try openpyxl directly
            openpyxl = _try_import("openpyxl")
            if openpyxl is None or not os.path.exists(path):
                return []
            wb = openpyxl.load_workbook(path)
            ws = wb.active
            headers = [c.value for c in next(ws.iter_rows(min_row=1, max_row=1))]
            col_map = {h: i for i, h in enumerate(headers) if h}
            rows = []
            for row in ws.iter_rows(min_row=2, values_only=True):
                rows.append({
                    "name": str(row[col_map.get("name")]) if col_map.get("name") is not None and row[col_map.get("name")] is not None else "",
                    "role": str(row[col_map.get("role")]) if col_map.get("role") is not None and row[col_map.get("role")] is not None else "",
                    "signature_base64": str(row[col_map.get("signature_base64")]) if col_map.get("signature_base64") is not None and row[col_map.get("signature_base64")] is not None else "",
                    "position": str(row[col_map.get("position")]) if col_map.get("position") is not None and row[col_map.get("position")] is not None else "",
                })
            return [r for r in rows if r["name"]]
    except Exception:
        return []

def get_signatory_image_path(signatory: Dict, ensure_folder: str = os.path.join(ASSETS_DIR, "signatures")) -> Optional[str]:
    """
    Decode a base64 signature (if provided) and save to assets/signatures/<name>.png.
    Returns the file path or None on failure.
    """
    try:
        sig_b64 = signatory.get("signature_base64") or ""
        if not sig_b64:
            return None
        os.makedirs(ensure_folder, exist_ok=True)
        # Some spreadsheets include the data URI prefix; strip if present
        if sig_b64.startswith("data:"):
            sig_b64 = sig_b64.split(",", 1)[1]
        data = base64.b64decode(sig_b64)
        safe_name = "".join(c for c in signatory.get("name", "sig") if c.isalnum() or c in ("_", "-")).strip() or "sig"
        out_path = os.path.join(ensure_folder, f"{safe_name}.png")
        with open(out_path, "wb") as f:
            f.write(data)
        return out_path
    except Exception:
        return None

def render_signature_bytes(signatory: Dict) -> Optional[bytes]:
    """
    Return PNG bytes for a signatory, decoding base64 value. None if not available.
    """
    try:
        sig_b64 = signatory.get("signature_base64") or ""
        if not sig_b64:
            return None
        if sig_b64.startswith("data:"):
            sig_b64 = sig_b64.split(",", 1)[1]
        return base64.b64decode(sig_b64)
    except Exception:
        return None

def generate_qr_bytes(invoice_number: str, invoice_date: str, url: str = "https://www.heomed.com", box_size: int = 10) -> bytes:
    """
    Generate QR PNG bytes encoding a small JSON with invoice_number, invoice_date, and company URL.
    Uses qrcode + PIL when available; otherwise returns empty bytes.
    """
    try:
        qrcode_mod = _try_import("qrcode")
        pil_mod = _try_import("PIL.Image")
        if qrcode_mod is None:
            return b""
        payload = json.dumps({"invoice": str(invoice_number), "date": str(invoice_date), "url": url}, ensure_ascii=False)
        qr = qrcode_mod.QRCode(error_correction=qrcode_mod.constants.ERROR_CORRECT_M, box_size=box_size, border=2)
        qr.add_data(payload)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        # PIL image objects might not expose save if not present; try generic
        try:
            img.save(buf, format="PNG")
        except Exception:
            # if PIL module name loaded differently, attempt conversion
            pil = _try_import("PIL.Image")
            if pil is not None:
                pil_img = pil.fromarray(img)
                pil_img.save(buf, format="PNG")
            else:
                return b""
        return buf.getvalue()
    except Exception:
        return b""

def invoice_age_check_live(days: int = 15):
    """
    Extra safety wrapper to cancel Pending invoices older than `days`.
    This duplicates auto_cancel_pending logic but can be invoked explicitly on dashboard load.
    It's safe to call repeatedly.
    """
    try:
        cutoff_dt = datetime.utcnow() - timedelta(days=days)
        cutoff = cutoff_dt.strftime('%Y-%m-%d %H:%M:%S')
        now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE invoices SET status='Cancelled', updated_at=? WHERE status='Pending' AND invoice_date<=?",
                        (now, cutoff))
            conn.commit()
    except Exception:
        pass

def render_invoice_preview(invoice_data: dict, out_lang: str = "en", container_key: str = "invoice_preview"):
    """
    Render a lightweight HTML/CSS preview of the invoice that mirrors the PDF style.
    Uses CSS fade-in animation for a simple print-preview feel.
    This function exclusively renders to Streamlit using st.markdown and an outer container.
    """
    try:
        # Build simple HTML with inline styles to approximate the PDF layout.
        company_lines = [
            "🏭 41 Al-Mawardi Street, Al-Qasr Al-Aini, Cairo, Egypt",
            "📞 +201026531004 / +201147304880",
            "📭 Fax: +2027932115",
            "📧 info@heomed.com",
            "🌍 www.heomed.com",
        ]
        title_map = {
            "Quotation Request": ("Quotation Request", "طلب عرض سعر"),
            "Commercial Invoice": ("Commercial Invoice", "فاتورة تجارية"),
            "Proforma Invoice": ("Proforma Invoice", "فاتورة أولية"),
        }
        inv_type = invoice_data.get("invoice_type", "Quotation Request")
        t_en, t_ar = title_map.get(inv_type, (inv_type, inv_type))
        title_text = f"{t_en} / {t_ar}" if out_lang == "en" else f"{t_ar} / {t_en}"

        # build items rows
        rows_html = ""
        items = invoice_data.get("items", [])
        for i, it in enumerate(items):
            bg = "#fafafa" if i % 2 == 0 else "#ffffff"
            rows_html += f"""
            <tr style="background:{bg}">
              <td style="padding:6px;border-bottom:1px solid #eee">{_shape_text_for_pdf(it.get('description',''), rtl=(out_lang=='ar'))}</td>
              <td style="padding:6px;text-align:center;border-bottom:1px solid #eee">{it.get('quantity','')}</td>
              <td style="padding:6px;text-align:right;border-bottom:1px solid #eee">{float(it.get('price',0)):.2f}</td>
              <td style="padding:6px;text-align:right;border-bottom:1px solid #eee">{float(it.get('total',0)):.2f}</td>
            </tr>
            """

        html = f"""
        <style>
        /* fade-in print animation */
        @keyframes fadeInBuild {{
          0% {{opacity: 0; transform: translateY(8px)}}
          60% {{opacity: 0.9; transform: translateY(-2px)}}
          100% {{opacity: 1; transform: translateY(0)}}
        }}
        .inv-preview {{ animation: fadeInBuild 600ms ease-out; border:1px solid #e6e6e6; padding:12px; border-radius:6px; max-width:900px; background:white; }}
        .inv-header {{ display:flex; justify-content:space-between; align-items:flex-start; }}
        .company-block {{ font-size:12px; color:#333; line-height:1.3; }}
        .inv-title {{ font-weight:700; font-size:18px; margin-top:6px; text-align:center; }}
        .inv-table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:13px; }}
        </style>
        <div class="inv-preview">
          <div class="inv-header">
            <div class="company-block" style="text-align:left;">
              {"<br>".join(company_lines)}
            </div>
            <div style="width:220px;text-align:right;">
              {"<img src='data:image/png;base64," + base64.b64encode(open(LOGO_PATH,"rb").read()).decode() + "' width='170' />" if os.path.exists(LOGO_PATH) else ""}
            </div>
          </div>
          <div class="inv-title">{title_text}</div>
          <div style="margin-top:8px;font-size:13px;">
            <strong>Invoice #</strong> {invoice_data.get("invoice_number","")} &nbsp;&nbsp;
            <strong>Date</strong> {invoice_data.get("date","")}
          </div>
          <table class="inv-table" border="0">
            <thead>
              <tr style="background:#2F4F4F;color:white">
                <th style="text-align:left;padding:8px">{"الصنف" if out_lang=='ar' else "Item"}</th>
                <th style="text-align:center;padding:8px">{"الكمية" if out_lang=='ar' else "Qty"}</th>
                <th style="text-align:right;padding:8px">{"السعر" if out_lang=='ar' else "Unit Price"}</th>
                <th style="text-align:right;padding:8px">{"الإجمالي" if out_lang=='ar' else "Subtotal"}</th>
              </tr>
            </thead>
            <tbody>
              {rows_html}
            </tbody>
          </table>
          <div style="margin-top:12px;text-align:right;font-weight:700;">
            Total: {invoice_data.get('total',0):.2f}
          </div>
        </div>
        """
        # render in a container to keep it isolated
        container = st.container()
        container.markdown(html, unsafe_allow_html=True)
    except Exception:
        st.info("Live preview is unavailable (missing assets or rendering issue).")