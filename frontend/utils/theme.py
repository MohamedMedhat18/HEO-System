"""Theme and styling utilities for the application."""
import streamlit as st


def apply_custom_theme():
    """Apply custom theme with dark mode support."""
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Roboto:wght@400;700&family=Tajawal:wght@400;700&display=swap');
        
        /* Root variables for theming */
        :root {
            --primary-color: #3880fa;
            --secondary-color: #183475;
            --accent-color: #4a9eff;
            --success-color: #10b981;
            --warning-color: #f59e0b;
            --danger-color: #ef4444;
            --text-primary: #1f2937;
            --text-secondary: #6b7280;
            --bg-primary: #ffffff;
            --bg-secondary: #f9fafb;
            --border-color: #e5e7eb;
        }
        
        /* Dark mode variables */
        [data-theme="dark"] {
            --text-primary: #f9fafb;
            --text-secondary: #d1d5db;
            --bg-primary: #111827;
            --bg-secondary: #1f2937;
            --border-color: #374151;
        }
        
        /* Global styles */
        body, .main {
            font-family: 'Inter', 'Roboto', sans-serif;
            color: var(--text-primary);
            background-color: var(--bg-primary);
        }
        
        /* Arabic support */
        .rtl {
            direction: rtl;
            font-family: 'Tajawal', sans-serif;
        }
        
        /* Card component */
        .card {
            background: var(--bg-primary);
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06);
            border: 1px solid var(--border-color);
            transition: all 0.3s ease;
        }
        
        .card:hover {
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            transform: translateY(-2px);
        }
        
        /* Animated card entry */
        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .animated-card {
            animation: slideUp 0.4s ease-out;
        }
        
        /* Header styles */
        .header-container {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 2rem;
            padding: 1rem;
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            border-radius: 12px;
            color: white;
        }
        
        .header-title {
            font-size: 2rem;
            font-weight: 700;
            margin: 0;
        }
        
        /* Metric card */
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem;
            border-radius: 12px;
            color: white;
            text-align: center;
            animation: slideUp 0.5s ease-out;
        }
        
        .metric-value {
            font-size: 2.5rem;
            font-weight: 700;
            margin: 0.5rem 0;
        }
        
        .metric-label {
            font-size: 0.875rem;
            opacity: 0.9;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        /* Button styles */
        .stButton > button {
            background: var(--primary-color);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(56, 128, 250, 0.3);
        }
        
        .stButton > button:hover {
            background: var(--accent-color);
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(56, 128, 250, 0.4);
        }
        
        /* Input fields */
        .stTextInput > div > div > input,
        .stSelectbox > div > div > select,
        .stTextArea > div > div > textarea {
            border-radius: 8px;
            border: 2px solid var(--border-color);
            padding: 0.75rem;
            transition: all 0.3s ease;
        }
        
        .stTextInput > div > div > input:focus,
        .stSelectbox > div > div > select:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(56, 128, 250, 0.1);
        }
        
        /* Table styles */
        .dataframe {
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        
        /* Loading animation */
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .loader {
            border: 4px solid var(--border-color);
            border-top: 4px solid var(--primary-color);
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 2rem auto;
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            background: linear-gradient(180deg, var(--bg-secondary) 0%, var(--bg-primary) 100%);
        }
        
        /* Success/Error messages */
        .success-message {
            background: var(--success-color);
            color: white;
            padding: 1rem;
            border-radius: 8px;
            animation: slideUp 0.3s ease-out;
        }
        
        .error-message {
            background: var(--danger-color);
            color: white;
            padding: 1rem;
            border-radius: 8px;
            animation: slideUp 0.3s ease-out;
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            .header-title {
                font-size: 1.5rem;
            }
            
            .metric-value {
                font-size: 2rem;
            }
        }
        
        /* Real-time update indicator */
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .live-indicator {
            display: inline-block;
            width: 8px;
            height: 8px;
            background: var(--success-color);
            border-radius: 50%;
            animation: pulse 2s ease-in-out infinite;
            margin-right: 0.5rem;
        }
        
        /* Invoice preview */
        .invoice-preview {
            background: var(--bg-primary);
            border: 2px solid var(--border-color);
            border-radius: 12px;
            padding: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            animation: slideUp 0.5s ease-out;
        }
        
        /* Dark mode toggle */
        .theme-toggle {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            z-index: 1000;
            background: var(--primary-color);
            color: white;
            border: none;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            transition: all 0.3s ease;
        }
        
        .theme-toggle:hover {
            transform: scale(1.1);
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
        }
        </style>
    """, unsafe_allow_html=True)


def render_header(title: str, subtitle: str = "", logo_path: str = ""):
    """Render professional header with logo."""
    if logo_path:
        st.markdown(f"""
            <div class="header-container">
                <img src="{logo_path}" width="80" style="border-radius: 8px;">
                <div>
                    <h1 class="header-title">{title}</h1>
                    {f'<p style="margin: 0; opacity: 0.9;">{subtitle}</p>' if subtitle else ''}
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="header-container">
                <div>
                    <h1 class="header-title">{title}</h1>
                    {f'<p style="margin: 0; opacity: 0.9;">{subtitle}</p>' if subtitle else ''}
                </div>
            </div>
        """, unsafe_allow_html=True)


def render_metric_card(label: str, value: str, gradient: str = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"):
    """Render animated metric card."""
    st.markdown(f"""
        <div class="metric-card" style="background: {gradient};">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
    """, unsafe_allow_html=True)


def show_loading():
    """Show loading animation."""
    st.markdown('<div class="loader"></div>', unsafe_allow_html=True)


def show_live_indicator():
    """Show live update indicator."""
    st.markdown(
        '<span class="live-indicator"></span><span style="color: var(--success-color); font-weight: 600;">LIVE</span>',
        unsafe_allow_html=True
    )
