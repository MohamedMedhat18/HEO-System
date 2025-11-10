# HEO System - Unified Application Guide

## Overview

The HEO System has been upgraded to a **unified professional application** that integrates both the FastAPI backend and Streamlit frontend into a single, seamless system.

## Key Improvements

### 1. **Unified Architecture**
- **Single Entry Point**: Run everything with one command: `streamlit run unified_app.py`
- **Auto-Start Backend**: FastAPI backend starts automatically within Streamlit
- **No Manual Setup Required**: Just run the app and everything works!

### 2. **Professional Modern Theme**
- **Gradient Designs**: Beautiful gradient color schemes throughout
- **Animated Cards**: Smooth animations and transitions
- **Responsive Layout**: Works perfectly on desktop and mobile
- **Professional Typography**: Using Inter and Poppins fonts
- **Status Badges**: Visual status indicators with color coding
- **Glassmorphism Effects**: Modern UI elements with depth

### 3. **Feature Updates**

#### Quotation Request System
- ✅ Replaced "Quotation Invoice" with "Quotation Request" throughout
- ✅ Supports **20+ dynamic items** per request
- ✅ Real-time total calculation
- ✅ Professional PDF generation
- ✅ Bilingual support (English/Arabic)

#### Enhanced UI Components
- 📊 **Dashboard**: Real-time metrics with gradient cards
- 📝 **Quotation Requests**: Dynamic item addition (up to 50 items)
- 📄 **Invoices**: Advanced filtering and search
- 👥 **Clients**: Comprehensive client management
- ⚙️ **Settings**: System configuration and about info

### 4. **Technical Enhancements**
- **Backend Integration**: Automatic FastAPI startup via threading
- **API Communication**: RESTful API calls with proper error handling
- **Session Management**: Persistent user sessions
- **Real-time Updates**: Live status indicators
- **Modular Architecture**: Clean separation of concerns

## Quick Start

### Prerequisites
- Python 3.12+
- All dependencies installed via `requirements.txt`

### Running the Unified App

```bash
# Install dependencies (if not already done)
pip install -r requirements.txt

# Run the unified application
streamlit run unified_app.py
```

The application will:
1. Start the FastAPI backend on port 8000 automatically
2. Launch the Streamlit frontend on port 8501
3. Open in your default browser

### Default Login
- **Username**: `admin1`
- **Password**: `admin_password` (or set via `ADMIN_PASSWORD` env variable)

## Features

### Creating Quotation Requests

1. **Login** to the system
2. Navigate to **"Quotation Requests"**
3. Fill in client information
4. Add items (supports 1-50 items dynamically)
5. Set quantity and unit price for each item
6. System automatically calculates totals
7. Click **"Create Quotation Request"** to generate

### Managing Invoices

- View all invoices/quotations
- Filter by status (Pending, Paid, Cancelled)
- Search by client name or ID
- Update invoice status
- View detailed information

### Dashboard Analytics

- Total requests/invoices count
- Total sales amount
- Pending requests
- Paid invoices
- Recent activity feed

## Architecture

```
unified_app.py (Main Entry Point)
├── Backend Thread
│   └── FastAPI (port 8000)
│       ├── Authentication API
│       ├── Invoice API
│       ├── Client API
│       └── Statistics API
└── Streamlit Frontend (port 8501)
    ├── Dashboard
    ├── Quotation Requests
    ├── Invoices
    ├── Clients
    └── Settings
```

## API Endpoints

The backend exposes the following endpoints:

- `GET /health` - Health check
- `POST /api/auth/login` - User authentication
- `GET /api/invoices` - List all invoices
- `POST /api/invoices` - Create new invoice
- `PATCH /api/invoices/{id}/status` - Update status
- `GET /api/clients` - List clients
- `POST /api/clients` - Create client
- `GET /api/stats` - Get statistics

## Customization

### Theme Colors

Edit the CSS in `unified_app.py` to customize colors:

```python
# Primary gradient
background: linear-gradient(90deg, #183475 0%, #3880fa 100%);

# Card colors
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

### Adding More Items

The system supports up to 50 items per quotation. Adjust in the form:

```python
num_items = st.number_input("Number of Items", min_value=1, max_value=50, value=3)
```

### Language Support

Switch between English and Arabic using the sidebar buttons:
- 🇬🇧 EN - English interface
- 🇸🇦 AR - Arabic interface (RTL support)

## Troubleshooting

### Backend Won't Start
- Check if port 8000 is already in use
- Ensure all dependencies are installed
- Check backend logs in the console

### Can't Login
- Verify default credentials: `admin1` / `admin_password`
- Check database exists: `db/database.db`
- Run database initialization: `python -c "from backend.services.database import init_db; init_db()"`

### PDF Generation Issues
- Ensure `reportlab` is installed
- Check font files exist in root directory
- Verify write permissions for `invoices/` directory

## File Structure

```
HEO-System/
├── unified_app.py          # Main unified application
├── app.py                  # Original standalone app (backup)
├── backend/
│   ├── api/
│   │   └── main.py        # FastAPI application
│   ├── models/
│   │   └── __init__.py    # Pydantic models
│   └── services/
│       ├── auth.py        # Authentication
│       ├── database.py    # Database operations
│       └── invoice_service.py
├── frontend/               # Modular frontend (legacy)
└── requirements.txt
```

## Best Practices

1. **Always use the unified app** for production
2. **Keep backend and frontend in sync** when making changes
3. **Test with multiple items** (20+) to ensure scalability
4. **Use proper status updates** to track invoice lifecycle
5. **Regular backups** of the database

## Future Enhancements

- [ ] PDF preview before download
- [ ] Email quotations directly to clients
- [ ] Advanced analytics and charts
- [ ] Multi-user collaboration
- [ ] Document versioning
- [ ] Export to Excel/CSV
- [ ] Mobile app integration

## Support

For issues or questions:
- **Email**: info@heomed.com
- **Website**: www.heomed.com
- **Address**: 41 Al-Mawardi Street, Al-Qasr Al-Aini, Cairo, Egypt

## License

Copyright © 2024 EL HEKMA ENGINEERING OFFICE Co.

---

**Powered by AI | Professional Medical Systems** 🏥
