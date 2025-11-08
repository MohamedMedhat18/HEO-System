"""Main frontend application using Streamlit."""
import streamlit as st
import os
import sys
import requests
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from frontend.utils.theme import apply_custom_theme, render_header, render_metric_card, show_live_indicator
from frontend.pages import dashboard, invoices, clients, settings

# Page configuration
st.set_page_config(
    page_title="HEO System - Professional Invoice Management",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom theme
apply_custom_theme()

# API base URL (can be configured via environment variable)
API_BASE_URL = os.environ.get('API_BASE_URL', 'http://localhost:8000')

# Session state initialization
if 'user' not in st.session_state:
    st.session_state.user = None
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'
if 'language' not in st.session_state:
    st.session_state.language = 'en'

# Translations
TRANSLATIONS = {
    'en': {
        'app_title': 'HEO Medical Systems',
        'app_subtitle': 'Professional Invoice Management & AI-Driven Analytics',
        'login': 'Login',
        'username': 'Username',
        'password': 'Password',
        'logout': 'Logout',
        'welcome': 'Welcome',
        'menu': {
            'dashboard': 'Dashboard',
            'invoices': 'Invoices',
            'clients': 'Clients',
            'products': 'Products',
            'settings': 'Settings',
            'agents': 'AI Agents'
        }
    },
    'ar': {
        'app_title': 'أنظمة HEO الطبية',
        'app_subtitle': 'إدارة الفواتير الاحترافية والتحليلات المدعومة بالذكاء الاصطناعي',
        'login': 'تسجيل الدخول',
        'username': 'اسم المستخدم',
        'password': 'كلمة المرور',
        'logout': 'تسجيل الخروج',
        'welcome': 'مرحبا',
        'menu': {
            'dashboard': 'لوحة التحكم',
            'invoices': 'الفواتير',
            'clients': 'العملاء',
            'products': 'المنتجات',
            'settings': 'الإعدادات',
            'agents': 'عملاء الذكاء الاصطناعي'
        }
    }
}

def get_text(key: str) -> str:
    """Get translated text."""
    lang = st.session_state.language
    keys = key.split('.')
    text = TRANSLATIONS[lang]
    for k in keys:
        text = text.get(k, key)
    return text


def authenticate(username: str, password: str) -> bool:
    """Authenticate user via API."""
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
                return True
    except Exception as e:
        st.error(f"Authentication error: {str(e)}")
    
    return False


def render_sidebar():
    """Render sidebar with navigation and settings."""
    with st.sidebar:
        # Logo and branding
        st.markdown("""
            <div style='text-align: center; padding: 1rem 0;'>
                <h2 style='color: #3880fa; margin: 0;'>🏥 HEO</h2>
                <p style='font-size: 0.8rem; opacity: 0.7;'>Medical Systems</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Language selector
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🇬🇧 EN"):
                st.session_state.language = 'en'
                st.rerun()
        with col2:
            if st.button("🇸🇦 AR"):
                st.session_state.language = 'ar'
                st.rerun()
        
        # Authentication
        if not st.session_state.user:
            st.subheader(get_text('login'))
            
            with st.form("login_form"):
                username = st.text_input(get_text('username'))
                password = st.text_input(get_text('password'), type='password')
                submit = st.form_submit_button(get_text('login'))
                
                if submit:
                    if authenticate(username, password):
                        st.success(f"{get_text('welcome')} {username}!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
        else:
            # User info
            st.success(f"{get_text('welcome')}, {st.session_state.user['username']}!")
            
            if st.button(get_text('logout')):
                st.session_state.user = None
                st.rerun()
            
            st.markdown("---")
            
            # Navigation menu
            st.subheader("📋 Menu")
            
            menu_items = [
                ('dashboard', '📊'),
                ('invoices', '📄'),
                ('clients', '👥'),
                ('products', '📦'),
                ('settings', '⚙️'),
                ('agents', '🤖')
            ]
            
            for item, icon in menu_items:
                if st.button(f"{icon} {get_text(f'menu.{item}')}", key=f"nav_{item}", use_container_width=True):
                    st.session_state.current_page = item
        
        st.markdown("---")
        
        # Live indicator
        show_live_indicator()
        st.caption(f"Updated: {datetime.now().strftime('%H:%M:%S')}")


def main():
    """Main application entry point."""
    # Render sidebar
    render_sidebar()
    
    # Check authentication
    if not st.session_state.user:
        # Landing page
        render_header(
            get_text('app_title'),
            get_text('app_subtitle'),
            logo_path="assets/logo.png" if os.path.exists("assets/logo.png") else ""
        )
        
        st.markdown("""
            <div style='text-align: center; padding: 3rem 0;'>
                <h2>Welcome to HEO System</h2>
                <p style='font-size: 1.2rem; color: #6b7280;'>
                    Professional invoice management with AI-powered insights
                </p>
                <br>
                <p>Please login from the sidebar to continue →</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Feature showcase
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
                <div class='card animated-card'>
                    <h3>🎨 Modern UI</h3>
                    <p>Beautiful, responsive design with dark mode support</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
                <div class='card animated-card'>
                    <h3>🤖 AI-Powered</h3>
                    <p>Self-improving system with intelligent agents</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
                <div class='card animated-card'>
                    <h3>⚡ Real-time</h3>
                    <p>Live updates and instant invoice generation</p>
                </div>
            """, unsafe_allow_html=True)
        
        return
    
    # Initialize current page
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'dashboard'
    
    # Route to appropriate page
    page = st.session_state.current_page
    
    if page == 'dashboard':
        dashboard.render(API_BASE_URL, st.session_state.user)
    elif page == 'invoices':
        invoices.render(API_BASE_URL, st.session_state.user)
    elif page == 'clients':
        clients.render(API_BASE_URL, st.session_state.user)
    elif page == 'settings':
        settings.render(API_BASE_URL, st.session_state.user)
    elif page == 'agents':
        render_agents_page()


def render_agents_page():
    """Render AI agents monitoring page."""
    render_header("🤖 AI Agents", "Self-improving system monitoring")
    
    st.markdown("""
        <div class='card'>
            <h3>AI Agent System</h3>
            <p>The HEO System includes four specialized AI agents that continuously analyze and improve the codebase:</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <div class='card animated-card'>
                <h4>🎨 UI Agent</h4>
                <p><strong>Responsibility:</strong> Frontend code analysis and improvements</p>
                <ul>
                    <li>Analyzes component structure</li>
                    <li>Suggests UI/UX improvements</li>
                    <li>Ensures accessibility compliance</li>
                    <li>Monitors theme consistency</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div class='card animated-card'>
                <h4>📚 Documentation Agent</h4>
                <p><strong>Responsibility:</strong> Documentation quality and completeness</p>
                <ul>
                    <li>Analyzes code documentation</li>
                    <li>Generates API documentation</li>
                    <li>Ensures README completeness</li>
                    <li>Tracks docstring coverage</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class='card animated-card'>
                <h4>⚙️ Logic Agent</h4>
                <p><strong>Responsibility:</strong> Backend code and business logic</p>
                <ul>
                    <li>Analyzes code quality</li>
                    <li>Identifies security vulnerabilities</li>
                    <li>Suggests performance improvements</li>
                    <li>Ensures proper error handling</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div class='card animated-card'>
                <h4>🧪 Test Agent</h4>
                <p><strong>Responsibility:</strong> Test coverage and quality</p>
                <ul>
                    <li>Measures test coverage</li>
                    <li>Identifies untested modules</li>
                    <li>Suggests test improvements</li>
                    <li>Ensures test quality</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Agent execution status
    st.subheader("📊 Agent Status")
    
    # Check for log files
    if os.path.exists('logs'):
        log_files = [f for f in os.listdir('logs') if f.endswith('_log.json')]
        
        if log_files:
            st.success(f"Found {len(log_files)} agent log files")
            
            # Show recent activity
            for log_file in log_files[:4]:  # Show last 4 agents
                agent_name = log_file.replace('_log.json', '').replace('_', ' ').title()
                st.info(f"**{agent_name}** - Active")
        else:
            st.info("No agent logs found yet. Agents will run on schedule.")
    else:
        st.info("Agent logs directory not created yet. Run agents to generate logs.")
    
    # Manual trigger button (for demo)
    if st.button("🚀 Run All Agents Now", type="primary"):
        with st.spinner("Running AI agents..."):
            try:
                from agents.ui_agent.agent import UIAgent
                from agents.logic_agent.agent import LogicAgent
                from agents.docs_agent.agent import DocsAgent
                from agents.test_agent.agent import TestAgent
                
                results = {}
                
                # Run each agent
                for agent_class, name in [
                    (UIAgent, "UI Agent"),
                    (LogicAgent, "Logic Agent"),
                    (DocsAgent, "Documentation Agent"),
                    (TestAgent, "Test Agent")
                ]:
                    agent = agent_class()
                    result = agent.run()
                    results[name] = result
                
                st.success("All agents completed successfully!")
                
                # Display summary
                st.json(results)
            except Exception as e:
                st.error(f"Error running agents: {str(e)}")


if __name__ == "__main__":
    main()
