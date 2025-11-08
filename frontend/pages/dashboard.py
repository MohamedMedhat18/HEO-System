"""Dashboard page for metrics and overview."""
import streamlit as st
import requests
from frontend.utils.theme import render_header, render_metric_card


def render(api_base_url: str, user: dict):
    """Render the dashboard page."""
    render_header("📊 Dashboard", "Real-time system overview and analytics")
    
    # Fetch statistics from API
    try:
        response = requests.get(f"{api_base_url}/api/stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()
        else:
            stats = {
                "total_invoices": 0,
                "total_sales": 0,
                "pending": 0,
                "paid": 0,
                "cancelled": 0
            }
    except Exception as e:
        st.error(f"Failed to load statistics: {str(e)}")
        stats = {
            "total_invoices": 0,
            "total_sales": 0,
            "pending": 0,
            "paid": 0,
            "cancelled": 0
        }
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_metric_card(
            "Total Invoices",
            str(stats["total_invoices"]),
            "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
        )
    
    with col2:
        render_metric_card(
            "Total Sales",
            f"${stats['total_sales']:,.2f}",
            "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)"
        )
    
    with col3:
        render_metric_card(
            "Pending",
            str(stats["pending"]),
            "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"
        )
    
    with col4:
        render_metric_card(
            "Paid",
            str(stats["paid"]),
            "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)"
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Recent activity
    st.subheader("📈 Recent Activity")
    
    try:
        # Fetch recent invoices
        params = {}
        if user['role'] != 'admin':
            params['agent_id'] = user['id']
        
        response = requests.get(f"{api_base_url}/api/invoices", params=params, timeout=5)
        
        if response.status_code == 200:
            invoices = response.json()[:10]  # Last 10 invoices
            
            if invoices:
                # Display as cards
                for invoice in invoices:
                    status_color = {
                        'Pending': '#f59e0b',
                        'Paid': '#10b981',
                        'Cancelled': '#ef4444'
                    }.get(invoice.get('status', 'Pending'), '#6b7280')
                    
                    st.markdown(f"""
                        <div class='card animated-card' style='margin-bottom: 1rem;'>
                            <div style='display: flex; justify-content: space-between; align-items: center;'>
                                <div>
                                    <strong>Invoice #{invoice.get('id')}</strong>
                                    <p style='margin: 0.25rem 0; color: #6b7280;'>
                                        Client: {invoice.get('client_name', 'N/A')}
                                    </p>
                                </div>
                                <div style='text-align: right;'>
                                    <div style='color: {status_color}; font-weight: 600;'>
                                        {invoice.get('status', 'Pending')}
                                    </div>
                                    <div style='font-size: 1.25rem; font-weight: 700;'>
                                        ${float(invoice.get('total', 0)):,.2f}
                                    </div>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No invoices found")
        else:
            st.error("Failed to load invoices")
    except Exception as e:
        st.error(f"Error loading recent activity: {str(e)}")
    
    # Quick actions
    st.markdown("---")
    st.subheader("⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("➕ Create Invoice", use_container_width=True, type="primary"):
            st.session_state.current_page = 'invoices'
            st.rerun()
    
    with col2:
        if st.button("👥 Manage Clients", use_container_width=True):
            st.session_state.current_page = 'clients'
            st.rerun()
    
    with col3:
        if st.button("⚙️ Settings", use_container_width=True):
            st.session_state.current_page = 'settings'
            st.rerun()
