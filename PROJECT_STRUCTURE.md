# HEO System - Project Structure

## Overview

This document describes the complete file and folder structure of the HEO System invoice management application.

## Directory Tree

```
HEO-System/
│
├── 📄 unified_app.py               # ⭐ Main entry point (all-in-one: backend + frontend)
├── 📄 app.py                       # Alternative standalone Streamlit app
├── 📄 start.sh                     # Bash startup script (Linux/Mac)
├── 📄 run_minimal.ps1              # PowerShell startup script (Windows)
├── 📄 requirements.txt             # Python dependencies
├── 📄 .env.example                 # Environment variables template
├── 📄 .gitignore                   # Git ignore patterns
│
├── 📁 .streamlit/                  # Streamlit configuration
│   └── config.toml                 # Theme and server settings
│
├── 📁 backend/                     # 🔧 FastAPI Backend
│   ├── __init__.py
│   ├── 📁 api/
│   │   ├── __init__.py
│   │   └── main.py                 # FastAPI app with all endpoints
│   ├── 📁 models/
│   │   └── __init__.py             # Pydantic models (User, Client, Invoice, etc.)
│   └── 📁 services/
│       ├── __init__.py
│       ├── auth.py                 # Authentication logic
│       ├── database.py             # Database initialization and connection
│       └── invoice_service.py      # Invoice CRUD operations
│
├── 📁 frontend/                    # 🎨 Modular Streamlit Frontend
│   ├── __init__.py
│   ├── app.py                      # Modular frontend entry point
│   ├── 📁 pages/
│   │   ├── __init__.py
│   │   ├── dashboard.py            # Dashboard page
│   │   ├── invoices.py             # Invoices management
│   │   ├── clients.py              # Clients management
│   │   └── settings.py             # Settings page
│   └── 📁 utils/
│       ├── __init__.py
│       ├── theme.py                # Theme and styling utilities
│       └── pdf_utils.py            # PDF generation utilities
│
├── 📁 agents/                      # 🤖 AI Agents (GitHub Actions)
│   ├── __init__.py
│   ├── base_agent.py               # Base agent class
│   ├── 📁 ui_agent/
│   │   ├── __init__.py
│   │   └── agent.py                # UI/UX improvement agent
│   ├── 📁 logic_agent/
│   │   ├── __init__.py
│   │   └── agent.py                # Business logic agent
│   ├── 📁 docs_agent/
│   │   ├── __init__.py
│   │   └── agent.py                # Documentation agent
│   └── 📁 test_agent/
│       ├── __init__.py
│       └── agent.py                # Testing agent
│
├── 📁 assets/                      # 🖼️ Static Assets
│   ├── logo.png                    # Company logo (primary)
│   ├── logo1.png                   # Company logo (alternative)
│   ├── 📁 fonts/                   # Font files (fallback location)
│   └── 📁 signatures/              # Digital signature images (generated)
│
├── 📁 fonts/                       # 🔤 Font Files (primary location)
│   ├── Roboto-Regular.ttf
│   ├── Roboto-Bold.ttf
│   ├── Roboto-*.ttf                # All Roboto variants
│   ├── Roboto_Condensed-*.ttf      # Roboto Condensed variants
│   └── Tajawal-Regular.ttf         # Arabic font (if available)
│
├── 📁 locales/                     # 🌐 Internationalization
│   ├── en.json                     # English translations
│   └── ar.json                     # Arabic translations
│
├── 📁 db/                          # 💾 Database (created at runtime)
│   └── database.db                 # SQLite database file
│
├── 📁 invoices/                    # 📄 Generated PDFs (created at runtime)
│   └── *.pdf                       # Invoice/quotation PDF files
│
├── 📁 logs/                        # 📝 Application Logs (created at runtime)
│   └── *.log                       # Log files
│
├── 📁 tests/                       # 🧪 Unit and Integration Tests
│   └── test_app.py                 # Basic app tests
│
├── 📁 streamlit-invoice-app/       # Legacy/Alternative Implementation
│   ├── app.py
│   ├── requirements.txt
│   ├── 📁 utils/
│   ├── 📁 tests/
│   └── 📁 scripts/
│       └── setup_windows.ps1
│
├── 📁 docs/                        # 📚 Documentation
│   └── (various documentation files)
│
├── 📁 styles/                      # 🎨 CSS Styles
│   └── (custom CSS files)
│
├── 📁 templates/                   # 📋 HTML Templates (if any)
│   └── (email/report templates)
│
├── 📁 scripts/                     # 🛠️ Utility Scripts
│   └── (setup and maintenance scripts)
│
└── 📁 .github/                     # GitHub Configuration
    ├── 📁 workflows/               # CI/CD workflows
    └── 📁 agents/                  # Agent configurations
```

## Key Files Description

### Entry Points

| File | Description | Use Case |
|------|-------------|----------|
| `unified_app.py` | **Recommended**: All-in-one app that starts backend + frontend | Production, Streamlit Cloud |
| `app.py` | Standalone Streamlit app with embedded backend logic | Development, testing |
| `frontend/app.py` | Modular frontend (requires separate backend) | Microservices architecture |

### Startup Scripts

| File | Platform | Description |
|------|----------|-------------|
| `run_minimal.ps1` | Windows | PowerShell script with venv management |
| `start.sh` | Linux/Mac | Bash script for Unix-like systems |

### Configuration Files

| File | Purpose |
|------|---------|
| `requirements.txt` | Python package dependencies |
| `.env.example` | Template for environment variables |
| `.streamlit/config.toml` | Streamlit theme and server config |
| `.gitignore` | Files to exclude from version control |

### Documentation

| File | Contents |
|------|----------|
| `README.md` | Project overview and quick start |
| `DEPLOYMENT.md` | Detailed deployment instructions |
| `STREAMLIT_CLOUD_DEPLOYMENT.md` | Streamlit Cloud specific guide |
| `PROJECT_STRUCTURE.md` | This file - project organization |
| `FEATURES.md` | Feature list and capabilities |
| `IMPLEMENTATION_COMPLETE.md` | Implementation notes |

## Backend Architecture

### API Endpoints (`backend/api/main.py`)

```
GET  /                           # Root - API info
GET  /health                     # Health check
POST /api/auth/login            # User authentication
POST /api/auth/register         # User registration
GET  /api/invoices              # List all invoices
GET  /api/invoices/{id}         # Get specific invoice
POST /api/invoices              # Create new invoice
PATCH /api/invoices/{id}/status # Update invoice status
PATCH /api/invoices/{id}/pdf    # Update PDF path
GET  /api/clients               # List all clients
GET  /api/clients/{id}          # Get specific client
POST /api/clients               # Create new client
GET  /api/products              # List all products
GET  /api/employees             # List all employees
POST /api/employees             # Create new employee
DELETE /api/employees/{id}      # Delete employee
GET  /api/stats                 # System statistics
```

### Database Schema (`backend/services/database.py`)

**Tables:**

1. **users**
   - id (PRIMARY KEY)
   - username (UNIQUE)
   - password (hashed)
   - role (admin/agent)
   - created_at

2. **clients**
   - id (PRIMARY KEY)
   - name
   - email (UNIQUE)
   - phone
   - address
   - created_at

3. **products**
   - id (PRIMARY KEY)
   - name
   - description
   - price
   - created_at

4. **invoices**
   - id (PRIMARY KEY)
   - agent_id (FOREIGN KEY → users)
   - client_id (FOREIGN KEY → clients)
   - items (JSON)
   - total
   - status (Pending/Paid/Cancelled)
   - invoice_date
   - updated_at
   - client_name
   - client_address
   - created_at
   - currency
   - exchange_rate
   - invoice_type
   - language
   - pdf_path
   - notes

5. **employees**
   - id (PRIMARY KEY)
   - name
   - role
   - email

## Frontend Architecture

### Page Structure

1. **Dashboard** (`pages/dashboard.py` or main page in unified app)
   - Statistics cards (total invoices, sales, pending, paid)
   - Recent activity feed
   - Charts and visualizations

2. **Quotation Requests / Invoices** (`pages/invoices.py`)
   - Create new quotation/invoice form
   - Dynamic item entry (up to 30 items)
   - List and filter existing invoices
   - Status management
   - PDF generation and download

3. **Clients** (`pages/clients.py`)
   - Client list with contact information
   - Add new clients
   - View client history

4. **Settings** (`pages/settings.py`)
   - Company information
   - Logo upload
   - Employee management
   - PDF template preview
   - System configuration

### Theme and Styling

- Professional gradient-based UI
- Responsive design (mobile-friendly)
- Bilingual support (English/Arabic)
- Custom color scheme (blue/purple gradients)
- Animated components and transitions

## Data Flow

```
User Input (Streamlit UI)
    ↓
Frontend Logic (unified_app.py or frontend/app.py)
    ↓
HTTP Request (requests library)
    ↓
Backend API (FastAPI - backend/api/main.py)
    ↓
Service Layer (backend/services/)
    ↓
Database (SQLite - db/database.db)
    ↓
Response (JSON)
    ↓
Frontend Display (Streamlit)
```

## PDF Generation Flow

```
Invoice Data (dict)
    ↓
generate_pdf_bytes() (app.py or frontend/utils/pdf_utils.py)
    ↓
ReportLab (reportlab library)
    ↓
Font Loading (Roboto, Tajawal from fonts/)
    ↓
Arabic Text Shaping (arabic-reshaper + python-bidi)
    ↓
PDF Layout (tables, headers, totals, watermark)
    ↓
PDF Bytes (in memory)
    ↓
save_pdf_bytes() → invoices/filename.pdf
    ↓
Update Database (pdf_path column)
```

## Asset Management

### Logo Files

- **Primary**: `assets/logo.png` (10 KB)
- **Alternative**: `assets/logo1.png` (22 KB)
- **Usage**: Company branding in UI and PDFs
- **Format**: PNG with transparency

### Font Files

- **Location**: `fonts/` directory (primary), `assets/fonts/` (fallback)
- **English**: Roboto family (Regular, Bold, and variants)
- **Arabic**: Tajawal-Regular.ttf
- **Total Size**: ~8 MB (all Roboto variants)
- **Usage**: PDF generation with proper Arabic shaping

### Translations

- **English**: `locales/en.json` (1 KB)
- **Arabic**: `locales/ar.json` (1.2 KB)
- **Format**: JSON key-value pairs
- **Coverage**: UI labels, buttons, messages

## Environment Variables

### Required

- `DATABASE_URL`: Database connection string (default: `sqlite:///db/database.db`)
- `ADMIN_PASSWORD`: Default admin password (default: `admin_password`)

### Optional

- `API_BASE_URL`: Backend API URL (default: `http://localhost:8000`)
- `STREAMLIT_SERVER_PORT`: Frontend port (default: `8501`)

## Dependencies

### Core Frameworks

- **streamlit**: Web UI framework
- **fastapi**: Backend API framework
- **uvicorn**: ASGI server for FastAPI

### Database

- **sqlite3**: Built-in (Python standard library)
- **pydantic**: Data validation

### PDF Generation

- **reportlab**: PDF creation
- **arabic-reshaper**: Arabic text shaping
- **python-bidi**: Bidirectional text display
- **pillow**: Image processing

### Data Processing

- **pandas**: Data manipulation
- **openpyxl**: Excel file handling
- **plotly**: Interactive charts

### Authentication & Security

- **bcrypt**: Password hashing
- **email-validator**: Email validation

### Others

- **requests**: HTTP client
- **httpx**: Async HTTP client
- **qrcode**: QR code generation

## Development Workflow

### Local Development

1. Clone repository
2. Create virtual environment: `python -m venv venv`
3. Activate venv:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run app:
   - All-in-one: `streamlit run unified_app.py`
   - Separate: `python backend/api/main.py` + `streamlit run frontend/app.py`

### Testing

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_app.py

# Run with coverage
pytest --cov=backend --cov=frontend tests/
```

### Deployment

See:
- `DEPLOYMENT.md` - General deployment guide
- `STREAMLIT_CLOUD_DEPLOYMENT.md` - Streamlit Cloud specific

## File Sizes (Approximate)

- **Code**: ~500 KB (Python files)
- **Fonts**: ~8 MB (all Roboto variants)
- **Assets**: ~35 KB (logos)
- **Dependencies**: ~200 MB (installed packages)
- **Database**: Variable (starts at ~20 KB)
- **Generated PDFs**: 50-200 KB per file

## Security Considerations

### Sensitive Files (Never Commit!)

- `.env` - Environment variables
- `db/*.db` - Database files with user data
- `invoices/*.pdf` - Generated invoices with client info
- `logs/*.log` - Log files may contain sensitive data
- `venv/` - Virtual environment

### Safe to Commit

- `.env.example` - Template without secrets
- `requirements.txt` - Dependency list
- All source code files
- Documentation
- Font files and logos (public assets)
- Empty directory structure

## Maintenance

### Regular Tasks

1. **Update Dependencies**: `pip install -r requirements.txt --upgrade`
2. **Backup Database**: Copy `db/database.db` to safe location
3. **Clean Old PDFs**: Remove old files from `invoices/` directory
4. **Check Logs**: Review `logs/` for errors
5. **Test Arabic Support**: Generate sample Arabic invoice monthly

### Version Updates

When updating major dependencies (FastAPI, Streamlit, etc.):

1. Test locally first
2. Check for breaking changes in changelogs
3. Update code if necessary
4. Run full test suite
5. Deploy to staging environment
6. Monitor for issues
7. Deploy to production

## Troubleshooting Common Issues

### Import Errors

```bash
# Reinstall all dependencies
pip install -r requirements.txt --force-reinstall
```

### Database Locked

```bash
# Delete and recreate database
rm db/database.db
python -c "from backend.services.database import init_db; init_db()"
```

### Font Not Found

```bash
# Verify fonts exist
ls -la fonts/*.ttf

# If missing, download Roboto from Google Fonts
# https://fonts.google.com/specimen/Roboto
```

### PDF Generation Fails

```bash
# Test PDF dependencies
python -c "import reportlab; import arabic_reshaper; import bidi"

# If failed, reinstall
pip install reportlab arabic-reshaper python-bidi --force-reinstall
```

## Contributing

When adding new features:

1. Follow existing file structure
2. Add documentation to relevant .md files
3. Update `requirements.txt` if new dependencies added
4. Write tests for new functionality
5. Update this `PROJECT_STRUCTURE.md` if structure changes

## Support

- **Repository**: https://github.com/MohamedMedhat18/HEO-System
- **Issues**: https://github.com/MohamedMedhat18/HEO-System/issues
- **Email**: info@heomed.com
- **Documentation**: All `.md` files in root directory

---

**Last Updated**: November 2024  
**Version**: 2.0.0  
**Maintained By**: HEO Medical Systems
