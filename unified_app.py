"""
HEO System - Unified Professional Invoice Management App
This application automatically starts the FastAPI backend and runs everything in Streamlit.
"""
import streamlit as st
import os
import sys
import subprocess
import threading
import time
import requests
from datetime import datetime
import json

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Configuration
BACKEND_PORT = 8000
API_BASE_URL = f"http://localhost:{BACKEND_PORT}"
BACKEND_STARTED = False
backend_process = None

# Page configuration - must be first Streamlit command
st.set_page_config(
    page_title="HEO System - Professional Invoice Management",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Theme CSS
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Poppins:wght@400;500;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', 'Poppins', sans-serif;
    }
    
    /* Main container */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
    }
    
    /* Header styling */
    .stApp header {
        background: linear-gradient(90deg, #183475 0%, #3880fa 100%);
    }
    
    /* Sidebar styling */
    .css-1d391kg, [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #183475 0%, #2a4a8a 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Professional card styling */
    .card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
        margin-bottom: 1rem;
        border-left: 4px solid #3880fa;
        transition: all 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #3880fa 0%, #667eea 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(56, 128, 250, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(56, 128, 250, 0.5);
    }
    
    /* Form inputs */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > div,
    .stNumberInput > div > div > input {
        border-radius: 8px;
        border: 2px solid #e0e0e0;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > div:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #3880fa;
        box-shadow: 0 0 0 3px rgba(56, 128, 250, 0.1);
    }
    
    /* Table styling */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
    }
    
    /* Live indicator animation */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .live-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        background: #10b981;
        border-radius: 50%;
        animation: pulse 2s ease-in-out infinite;
        margin-right: 8px;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    .status-pending {
        background: #fef3c7;
        color: #92400e;
    }
    
    .status-paid {
        background: #d1fae5;
        color: #065f46;
    }
    
    .status-cancelled {
        background: #fee2e2;
        color: #991b1b;
    }
    
    /* Header with logo */
    .app-header {
        display: flex;
        align-items: center;
        padding: 1rem 0;
        border-bottom: 2px solid #e0e0e0;
        margin-bottom: 2rem;
    }
    
    .app-logo {
        font-size: 3rem;
        margin-right: 1rem;
    }
    
    .app-title {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #183475 0%, #3880fa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    .app-subtitle {
        font-size: 0.95rem;
        color: #6b7280;
        margin: 0;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 12px 24px;
        background-color: #f3f4f6;
        border: none;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #3880fa 0%, #667eea 100%);
        color: white !important;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .animated-card {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .metric-value {
            font-size: 1.8rem;
        }
        .app-title {
            font-size: 1.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)


def start_backend():
    """Start FastAPI backend in a separate thread."""
    global backend_process, BACKEND_STARTED
    
    try:
        # Check if backend is already running
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                BACKEND_STARTED = True
                return
        except:
            pass
        
        # Start backend
        backend_process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "backend.api.main:app", 
             f"--host=0.0.0.0", f"--port={BACKEND_PORT}", "--reload=False"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.path.dirname(__file__)
        )
        
        # Wait for backend to be ready
        max_retries = 30
        for i in range(max_retries):
            try:
                response = requests.get(f"{API_BASE_URL}/health", timeout=1)
                if response.status_code == 200:
                    BACKEND_STARTED = True
                    break
            except:
                pass
            time.sleep(1)
            
    except Exception as e:
        st.error(f"Failed to start backend: {e}")


# Start backend in background thread (only once)
if 'backend_initialized' not in st.session_state:
    with st.spinner("🚀 Starting backend services..."):
        thread = threading.Thread(target=start_backend, daemon=True)
        thread.start()
        thread.join(timeout=15)  # Wait up to 15 seconds
        st.session_state.backend_initialized = True

# Check backend status
backend_status = "🟢 Online" if BACKEND_STARTED else "🔴 Offline"


# Header
st.markdown(f"""
<div class="app-header">
    <div class="app-logo">🏥</div>
    <div>
        <h1 class="app-title">HEO Medical Systems</h1>
        <p class="app-subtitle">Professional Invoice Management & AI-Driven Analytics</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🎛️ System Control Panel")
    st.markdown(f"**Backend Status:** {backend_status}")
    st.markdown(f"**API URL:** `{API_BASE_URL}`")
    
    st.markdown("---")
    
    # Language selector
    st.markdown("### 🌐 Language")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🇬🇧 EN", use_container_width=True):
            st.session_state.language = 'en'
            st.rerun()
    with col2:
        if st.button("🇸🇦 AR", use_container_width=True):
            st.session_state.language = 'ar'
            st.rerun()
    
    st.markdown("---")
    
    # Authentication
    if 'user' not in st.session_state:
        st.session_state.user = None
    
    if not st.session_state.user:
        st.markdown("### 🔐 Login")
        with st.form("login_form"):
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit and username and password:
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/api/auth/login",
                        json={"username": username, "password": password},
                        timeout=5
                    )
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('success'):
                            st.session_state.user = data.get('user')
                            st.success("✅ Login successful!")
                            st.rerun()
                        else:
                            st.error("❌ Invalid credentials")
                    else:
                        st.error("❌ Login failed")
                except Exception as e:
                    st.error(f"❌ Connection error: {e}")
    else:
        st.success(f"👤 Welcome, **{st.session_state.user['username']}**!")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.user = None
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 📋 Navigation")
        
        # Navigation buttons
        pages = {
            "Dashboard": "📊",
            "Quotation Requests": "📝",
            "Invoices": "📄",
            "Clients": "👥",
            "Settings": "⚙️"
        }
        
        for page_name, icon in pages.items():
            if st.button(f"{icon} {page_name}", key=f"nav_{page_name}", use_container_width=True):
                st.session_state.current_page = page_name
                st.rerun()

# Initialize current page
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Dashboard'

# Main content area
if not st.session_state.user:
    # Landing page
    st.markdown("""
    <div style='text-align: center; padding: 3rem 0;'>
        <h2 style='font-size: 2.5rem; margin-bottom: 1rem;'>Welcome to HEO System</h2>
        <p style='font-size: 1.3rem; color: #6b7280; margin-bottom: 2rem;'>
            Professional invoice management with AI-powered insights
        </p>
        <p style='font-size: 1.1rem;'>👈 Please login from the sidebar to continue</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class='card animated-card'>
            <h3>🎨 Modern UI</h3>
            <p>Beautiful, responsive design with professional theme</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='card animated-card'>
            <h3>🤖 AI-Powered</h3>
            <p>Intelligent automation and insights</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='card animated-card'>
            <h3>⚡ Real-time</h3>
            <p>Live updates and instant generation</p>
        </div>
        """, unsafe_allow_html=True)
    
else:
    # Authenticated user pages
    page = st.session_state.current_page
    
    if page == "Dashboard":
        st.markdown("## 📊 Dashboard")
        
        # Fetch statistics
        try:
            response = requests.get(f"{API_BASE_URL}/api/stats", timeout=5)
            if response.status_code == 200:
                stats = response.json()
                
                # Metrics row
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Total Requests</div>
                        <div class="metric-value">{stats.get('total_invoices', 0)}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                        <div class="metric-label">Total Sales</div>
                        <div class="metric-value">LE {stats.get('total_sales', 0):,.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class="metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                        <div class="metric-label">Pending</div>
                        <div class="metric-value">{stats.get('pending', 0)}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    st.markdown(f"""
                    <div class="metric-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
                        <div class="metric-label">Paid</div>
                        <div class="metric-value">{stats.get('paid', 0)}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Recent activity
                st.markdown("### 📈 Recent Activity")
                response = requests.get(f"{API_BASE_URL}/api/invoices", timeout=5)
                if response.status_code == 200:
                    invoices = response.json()[:10]  # Latest 10
                    
                    if invoices:
                        for inv in invoices:
                            status = inv.get('status', 'Pending')
                            status_class = f"status-{status.lower()}"
                            st.markdown(f"""
                            <div class="card">
                                <strong>Invoice #{inv.get('id')}</strong> - {inv.get('client_name', 'N/A')}
                                <span class="status-badge {status_class}">{status}</span>
                                <br><small>Amount: LE {inv.get('total', 0):,.2f} | Date: {inv.get('invoice_date', 'N/A')[:10]}</small>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No invoices yet. Create your first quotation request!")
        except Exception as e:
            st.error(f"Failed to load dashboard: {e}")
    
    elif page == "Quotation Requests":
        st.markdown("## 📝 Create Quotation Request")
        
        # Import the main app functionality here
        # We'll use the root app.py create invoice functionality
        st.info("This will create a quotation request with dynamic items")
        
        with st.form("create_quotation_form"):
            st.markdown("### Client Information")
            col1, col2 = st.columns(2)
            with col1:
                client_name = st.text_input("Client Name*", key="quot_client_name")
                client_email = st.text_input("Client Email", key="quot_client_email")
            with col2:
                client_phone = st.text_input("Client Phone", key="quot_client_phone")
                client_address = st.text_input("Client Address", key="quot_client_address")
            
            st.markdown("### Request Details")
            col1, col2 = st.columns(2)
            with col1:
                request_type = st.selectbox("Request Type", 
                    ["Quotation Request", "Commercial Invoice", "Proforma Invoice"], 
                    key="quot_type")
                language = st.selectbox("Language", ["en", "ar"], key="quot_lang")
            with col2:
                currency = st.selectbox("Currency", ["EGP", "USD", "EUR"], key="quot_currency")
                exchange_rate = st.number_input("Exchange Rate", value=1.0, step=0.1, key="quot_rate")
            
            st.markdown("### Items")
            num_items = st.number_input("Number of Items", min_value=1, max_value=50, value=3, key="num_items")
            
            items = []
            for i in range(num_items):
                st.markdown(f"#### Item {i+1}")
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    desc = st.text_input(f"Description", key=f"item_desc_{i}")
                with col2:
                    qty = st.number_input(f"Quantity", min_value=0, value=1, key=f"item_qty_{i}")
                with col3:
                    price = st.number_input(f"Unit Price", min_value=0.0, value=0.0, step=0.01, key=f"item_price_{i}")
                
                if desc:
                    items.append({
                        "description": desc,
                        "quantity": qty,
                        "price": price,
                        "total": qty * price
                    })
            
            notes = st.text_area("Notes", key="quot_notes")
            
            submit = st.form_submit_button("🚀 Create Quotation Request", use_container_width=True)
            
            if submit and client_name and items:
                try:
                    # Create client first
                    client_payload = {
                        "name": client_name,
                        "email": client_email or None,
                        "phone": client_phone or None,
                        "address": client_address or None
                    }
                    
                    client_response = requests.post(
                        f"{API_BASE_URL}/api/clients",
                        json=client_payload,
                        timeout=10
                    )
                    
                    if client_response.status_code == 200:
                        client_id = client_response.json()['id']
                    else:
                        # Try to find existing client
                        clients_response = requests.get(f"{API_BASE_URL}/api/clients", timeout=5)
                        clients = clients_response.json()
                        existing = [c for c in clients if c['name'] == client_name]
                        client_id = existing[0]['id'] if existing else 1
                    
                    # Calculate total
                    total = sum(item['total'] for item in items)
                    
                    # Create invoice
                    invoice_payload = {
                        "agent_id": st.session_state.user['id'],
                        "client_id": client_id,
                        "items": items,
                        "invoice_type": request_type,
                        "language": language,
                        "notes": notes,
                        "client_name": client_name,
                        "client_address": client_address,
                        "currency": currency,
                        "exchange_rate": exchange_rate
                    }
                    
                    response = requests.post(
                        f"{API_BASE_URL}/api/invoices",
                        json=invoice_payload,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"✅ Quotation Request #{result['id']} created successfully!")
                        st.balloons()
                        
                        # Show summary
                        st.markdown(f"""
                        <div class="card">
                            <h3>Request Summary</h3>
                            <p><strong>Client:</strong> {client_name}</p>
                            <p><strong>Items:</strong> {len(items)}</p>
                            <p><strong>Total:</strong> {currency} {total:,.2f}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.error(f"Failed to create request: {response.text}")
                        
                except Exception as e:
                    st.error(f"Error creating request: {e}")
    
    elif page == "Invoices":
        st.markdown("## 📄 All Invoices")
        
        try:
            response = requests.get(f"{API_BASE_URL}/api/invoices", timeout=5)
            if response.status_code == 200:
                invoices = response.json()
                
                # Filters
                col1, col2 = st.columns([2, 1])
                with col1:
                    search = st.text_input("🔍 Search", placeholder="Search by client, ID...", key="search_inv")
                with col2:
                    status_filter = st.selectbox("Filter by Status", 
                        ["All", "Pending", "Paid", "Cancelled"], key="status_filter")
                
                # Apply filters
                filtered = invoices
                if search:
                    filtered = [inv for inv in filtered if search.lower() in str(inv).lower()]
                if status_filter != "All":
                    filtered = [inv for inv in filtered if inv.get('status') == status_filter]
                
                # Display
                if filtered:
                    for inv in filtered:
                        status = inv.get('status', 'Pending')
                        status_class = f"status-{status.lower()}"
                        
                        with st.expander(f"Invoice #{inv.get('id')} - {inv.get('client_name', 'N/A')}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Amount:** LE {inv.get('total', 0):,.2f}")
                                st.write(f"**Date:** {inv.get('invoice_date', 'N/A')[:10]}")
                            with col2:
                                st.markdown(f'**Status:** <span class="status-badge {status_class}">{status}</span>', 
                                          unsafe_allow_html=True)
                                st.write(f"**Type:** {inv.get('invoice_type', 'N/A')}")
                            
                            # Status update
                            new_status = st.selectbox("Update Status", 
                                ["Pending", "Paid", "Cancelled"], 
                                key=f"status_{inv.get('id')}")
                            
                            if st.button("Update", key=f"update_{inv.get('id')}"):
                                try:
                                    update_response = requests.patch(
                                        f"{API_BASE_URL}/api/invoices/{inv.get('id')}/status",
                                        params={"status": new_status},
                                        timeout=5
                                    )
                                    if update_response.status_code == 200:
                                        st.success("Status updated!")
                                        st.rerun()
                                except Exception as e:
                                    st.error(f"Update failed: {e}")
                else:
                    st.info("No invoices found")
        except Exception as e:
            st.error(f"Failed to load invoices: {e}")
    
    elif page == "Clients":
        st.markdown("## 👥 Clients Management")
        
        try:
            response = requests.get(f"{API_BASE_URL}/api/clients", timeout=5)
            if response.status_code == 200:
                clients = response.json()
                
                st.markdown(f"**Total Clients:** {len(clients)}")
                
                for client in clients:
                    st.markdown(f"""
                    <div class="card">
                        <h4>{client.get('name', 'N/A')}</h4>
                        <p><strong>Email:</strong> {client.get('email', 'N/A')}</p>
                        <p><strong>Phone:</strong> {client.get('phone', 'N/A')}</p>
                        <p><strong>Address:</strong> {client.get('address', 'N/A')}</p>
                    </div>
                    """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Failed to load clients: {e}")
    
    elif page == "Settings":
        st.markdown("## ⚙️ Settings")
        
        tabs = st.tabs(["General", "Backend", "About"])
        
        with tabs[0]:
            st.markdown("### General Settings")
            theme = st.selectbox("Theme", ["Light", "Dark"], key="theme_select")
            st.info("Theme switching coming soon!")
        
        with tabs[1]:
            st.markdown("### Backend Configuration")
            st.code(f"API URL: {API_BASE_URL}", language="text")
            st.code(f"Status: {backend_status}", language="text")
            
            if st.button("🔄 Restart Backend"):
                st.warning("Restart functionality requires manual intervention")
        
        with tabs[2]:
            st.markdown("### About HEO System")
            st.markdown("""
            <div class="card">
                <h3>HEO Medical Systems</h3>
                <p><strong>Version:</strong> 2.0.0</p>
                <p><strong>Company:</strong> EL HEKMA ENGINEERING OFFICE Co.</p>
                <p><strong>Email:</strong> info@heomed.com</p>
                <p><strong>Website:</strong> www.heomed.com</p>
                <p><strong>Address:</strong> 41 Al-Mawardi Street, Al-Qasr Al-Aini, Cairo, Egypt</p>
            </div>
            """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 1rem; color: #6b7280;'>
    <p><span class="live-indicator"></span>System Online | © 2024 HEO Medical Systems | Powered by AI</p>
</div>
""", unsafe_allow_html=True)
