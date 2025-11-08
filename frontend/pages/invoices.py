"""Invoices page for creating and managing invoices."""
import streamlit as st
import requests
from frontend.utils.theme import render_header


def render(api_base_url: str, user: dict):
    """Render the invoices page."""
    render_header("📄 Invoices", "Create and manage invoices")
    
    # Tabs for different views
    tab1, tab2 = st.tabs(["📋 View Invoices", "➕ Create Invoice"])
    
    with tab1:
        render_invoice_list(api_base_url, user)
    
    with tab2:
        render_create_invoice(api_base_url, user)


def render_invoice_list(api_base_url: str, user: dict):
    """Render invoice list with filters."""
    st.subheader("Invoice List")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search = st.text_input("🔍 Search", placeholder="Search by client or invoice ID")
    
    with col2:
        status_filter = st.selectbox(
            "Status",
            options=["All", "Pending", "Paid", "Cancelled"]
        )
    
    with col3:
        st.write("")  # Spacing
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    # Fetch invoices
    try:
        params = {}
        if user['role'] != 'admin':
            params['agent_id'] = user['id']
        
        response = requests.get(f"{api_base_url}/api/invoices", params=params, timeout=5)
        
        if response.status_code == 200:
            invoices = response.json()
            
            # Apply filters
            if status_filter != "All":
                invoices = [inv for inv in invoices if inv.get('status') == status_filter]
            
            if search:
                search_lower = search.lower()
                invoices = [
                    inv for inv in invoices
                    if search_lower in str(inv.get('id', '')).lower()
                    or search_lower in str(inv.get('client_name', '')).lower()
                ]
            
            # Display invoices
            if invoices:
                for invoice in invoices:
                    with st.expander(
                        f"Invoice #{invoice.get('id')} - {invoice.get('client_name', 'N/A')} - ${float(invoice.get('total', 0)):,.2f}"
                    ):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Status:** {invoice.get('status', 'Pending')}")
                            st.write(f"**Client:** {invoice.get('client_name', 'N/A')}")
                            st.write(f"**Date:** {invoice.get('invoice_date', 'N/A')}")
                        
                        with col2:
                            st.write(f"**Total:** ${float(invoice.get('total', 0)):,.2f}")
                            st.write(f"**Agent:** {invoice.get('agent_username', 'N/A')}")
                            st.write(f"**Type:** {invoice.get('invoice_type', 'N/A')}")
                        
                        # Actions
                        col1, col2, col3 = st.columns(3)
                        
                        if user['role'] == 'admin':
                            with col1:
                                if st.button("✅ Mark as Paid", key=f"paid_{invoice['id']}"):
                                    update_invoice_status(api_base_url, invoice['id'], 'Paid')
                            
                            with col2:
                                if st.button("❌ Cancel", key=f"cancel_{invoice['id']}"):
                                    update_invoice_status(api_base_url, invoice['id'], 'Cancelled')
                        
                        if invoice.get('pdf_path'):
                            st.info(f"PDF: {invoice['pdf_path']}")
            else:
                st.info("No invoices found")
        else:
            st.error("Failed to load invoices")
    except Exception as e:
        st.error(f"Error loading invoices: {str(e)}")


def render_create_invoice(api_base_url: str, user: dict):
    """Render create invoice form."""
    st.subheader("Create New Invoice")
    
    with st.form("create_invoice_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            client_name = st.text_input("Client Name *", placeholder="Enter client name")
            client_email = st.text_input("Client Email", placeholder="client@example.com")
            client_address = st.text_area("Client Address", placeholder="Enter address")
        
        with col2:
            invoice_type = st.selectbox(
                "Invoice Type",
                options=["Quotation Invoice", "Commercial Invoice", "Proforma Invoice"]
            )
            language = st.selectbox("Language", options=["en", "ar"], index=0)
            currency = st.selectbox("Currency", options=["EGP", "USD", "EUR"], index=0)
        
        st.markdown("---")
        st.subheader("Invoice Items")
        
        # Simple item entry
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            item_desc = st.text_input("Item Description *", placeholder="Product or service description")
        
        with col2:
            item_qty = st.number_input("Quantity *", min_value=1, value=1)
        
        with col3:
            item_price = st.number_input("Price *", min_value=0.0, value=0.0, format="%.2f")
        
        notes = st.text_area("Notes", placeholder="Additional notes or comments")
        
        submitted = st.form_submit_button("Create Invoice", type="primary", use_container_width=True)
        
        if submitted:
            # Validation
            if not client_name or not item_desc:
                st.error("Please fill in all required fields (*)")
            else:
                create_invoice(
                    api_base_url,
                    user,
                    client_name,
                    client_email,
                    client_address,
                    invoice_type,
                    language,
                    currency,
                    item_desc,
                    item_qty,
                    item_price,
                    notes
                )


def create_invoice(api_base_url, user, client_name, client_email, client_address,
                  invoice_type, language, currency, item_desc, item_qty, item_price, notes):
    """Create a new invoice via API."""
    try:
        # First, create or get client
        client_response = requests.post(
            f"{api_base_url}/api/clients",
            json={
                "name": client_name,
                "email": client_email or None,
                "phone": None,
                "address": client_address or None
            },
            timeout=5
        )
        
        if client_response.status_code == 200:
            client_id = client_response.json()['id']
            
            # Create invoice
            invoice_data = {
                "agent_id": user['id'],
                "client_id": client_id,
                "items": [
                    {
                        "description": item_desc,
                        "quantity": int(item_qty),
                        "price": float(item_price),
                        "total": float(item_qty) * float(item_price)
                    }
                ],
                "invoice_type": invoice_type,
                "language": language,
                "notes": notes,
                "client_name": client_name,
                "client_address": client_address,
                "currency": currency,
                "exchange_rate": 1.0
            }
            
            response = requests.post(
                f"{api_base_url}/api/invoices",
                json=invoice_data,
                timeout=5
            )
            
            if response.status_code == 200:
                st.success("Invoice created successfully!")
                st.balloons()
                st.rerun()
            else:
                st.error(f"Failed to create invoice: {response.text}")
        else:
            st.error("Failed to create client")
    except Exception as e:
        st.error(f"Error creating invoice: {str(e)}")


def update_invoice_status(api_base_url: str, invoice_id: int, status: str):
    """Update invoice status."""
    try:
        response = requests.patch(
            f"{api_base_url}/api/invoices/{invoice_id}/status",
            params={"status": status},
            timeout=5
        )
        
        if response.status_code == 200:
            st.success(f"Invoice status updated to {status}")
            st.rerun()
        else:
            st.error("Failed to update status")
    except Exception as e:
        st.error(f"Error updating status: {str(e)}")
