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
    """
    Render create invoice form with dynamic item management.
    
    Uses st.session_state to manage multiple invoice items (up to 20).
    Provides professional validation and error handling.
    """
    st.subheader("Create New Invoice")
    
    # Initialize session state for invoice items
    if 'invoice_items' not in st.session_state:
        st.session_state.invoice_items = [{'description': '', 'quantity': 1, 'price': 0.0}]
    
    # Client Information Section
    st.markdown("### 📋 Client Information")
    col1, col2 = st.columns(2)
    
    with col1:
        client_name = st.text_input(
            "Client Name *", 
            placeholder="Enter client name",
            help="Required: Client or company name"
        )
        client_email = st.text_input(
            "Client Email", 
            placeholder="client@example.com",
            help="Optional: Email for invoice delivery"
        )
        client_address = st.text_area(
            "Client Address", 
            placeholder="Enter full address",
            help="Optional: Client billing address"
        )
    
    with col2:
        invoice_type = st.selectbox(
            "Invoice Type",
            options=["Quotation Request", "Commercial Invoice", "Proforma Invoice"],
            help="Select the type of invoice to generate"
        )
        language = st.selectbox(
            "Language", 
            options=["en", "ar"], 
            index=0,
            format_func=lambda x: "English" if x == "en" else "Arabic"
        )
        currency = st.selectbox(
            "Currency", 
            options=["EGP", "USD", "EUR"], 
            index=0,
            help="Currency for invoice amounts"
        )
    
    st.markdown("---")
    
    # Invoice Items Section
    st.markdown("### 🛒 Invoice Items")
    
    # Display all items with ability to edit
    items_to_remove = []
    total_amount = 0.0
    
    for idx, item in enumerate(st.session_state.invoice_items):
        with st.container():
            col1, col2, col3, col4 = st.columns([4, 1, 1, 0.5])
            
            with col1:
                item['description'] = st.text_input(
                    f"Item Description {idx + 1} *",
                    value=item.get('description', ''),
                    placeholder="Product or service description",
                    key=f"desc_{idx}"
                )
            
            with col2:
                item['quantity'] = st.number_input(
                    f"Qty {idx + 1} *",
                    min_value=1,
                    max_value=9999,
                    value=int(item.get('quantity', 1)),
                    key=f"qty_{idx}"
                )
            
            with col3:
                item['price'] = st.number_input(
                    f"Price {idx + 1} *",
                    min_value=0.0,
                    value=float(item.get('price', 0.0)),
                    format="%.2f",
                    key=f"price_{idx}"
                )
            
            with col4:
                if len(st.session_state.invoice_items) > 1:
                    if st.button("🗑️", key=f"remove_{idx}", help="Remove this item"):
                        items_to_remove.append(idx)
            
            # Calculate item total
            item_total = float(item['quantity']) * float(item['price'])
            total_amount += item_total
            st.caption(f"Item Total: {currency} {item_total:,.2f}")
    
    # Remove items marked for deletion
    for idx in reversed(items_to_remove):
        st.session_state.invoice_items.pop(idx)
        st.rerun()
    
    # Add Item and Summary
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if st.button(
            "➕ Add Item", 
            use_container_width=True,
            disabled=len(st.session_state.invoice_items) >= 20
        ):
            st.session_state.invoice_items.append({
                'description': '',
                'quantity': 1,
                'price': 0.0
            })
            st.rerun()
        
        if len(st.session_state.invoice_items) >= 20:
            st.warning("Maximum 20 items reached")
    
    with col2:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 1rem; border-radius: 8px; text-align: center; color: white;'>
            <div style='font-size: 0.9rem;'>Total Items: {len(st.session_state.invoice_items)}</div>
            <div style='font-size: 1.5rem; font-weight: 700;'>{currency} {total_amount:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Notes Section
    st.markdown("### 📝 Additional Notes")
    notes = st.text_area(
        "Notes", 
        placeholder="Add any additional information or special instructions",
        help="Optional: Additional notes to include in the invoice"
    )
    
    # Action Buttons
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("🗑️ Clear All Items", use_container_width=True):
            st.session_state.invoice_items = [{'description': '', 'quantity': 1, 'price': 0.0}]
            st.rerun()
    
    with col2:
        generate_pdf = st.button(
            "📄 Generate PDF & Create Invoice", 
            type="primary", 
            use_container_width=True
        )
    
    # Form Submission Handler
    if generate_pdf:
        # Validation
        validation_errors = []
        
        if not client_name or client_name.strip() == '':
            validation_errors.append("❌ Client name is required")
        
        # Validate items
        valid_items = []
        for idx, item in enumerate(st.session_state.invoice_items):
            if item['description'].strip():
                if item['quantity'] <= 0:
                    validation_errors.append(f"❌ Item {idx + 1}: Quantity must be greater than 0")
                if item['price'] < 0:
                    validation_errors.append(f"❌ Item {idx + 1}: Price cannot be negative")
                valid_items.append(item)
        
        if len(valid_items) == 0:
            validation_errors.append("❌ At least one item with description is required")
        
        # Display validation errors
        if validation_errors:
            st.error("### Please fix the following errors:")
            for error in validation_errors:
                st.error(error)
        else:
            # All validation passed, create invoice
            with st.spinner("Creating invoice and generating PDF..."):
                try:
                    create_invoice_with_items(
                        api_base_url,
                        user,
                        client_name,
                        client_email,
                        client_address,
                        invoice_type,
                        language,
                        currency,
                        valid_items,
                        notes
                    )
                    
                    # Clear items after successful creation
                    st.session_state.invoice_items = [{'description': '', 'quantity': 1, 'price': 0.0}]
                    
                except Exception as e:
                    st.error(f"❌ Error creating invoice: {str(e)}")


def create_invoice_with_items(api_base_url, user, client_name, client_email, client_address,
                               invoice_type, language, currency, items, notes):
    """
    Create a new invoice with multiple items via API.
    
    This function handles the complete invoice creation workflow:
    1. Creates or retrieves the client
    2. Prepares invoice items with calculated totals
    3. Submits to backend API
    4. Displays success message with download option
    
    Args:
        api_base_url: Base URL for the API
        user: Current user object
        client_name: Name of the client
        client_email: Client's email address
        client_address: Client's billing address
        invoice_type: Type of invoice (Quotation, Commercial, Proforma)
        language: Invoice language ('en' or 'ar')
        currency: Currency code (EGP, USD, EUR)
        items: List of invoice items with description, quantity, price
        notes: Additional notes for the invoice
    """
    try:
        # Step 1: Create or get client
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
            
            # Step 2: Prepare invoice items with calculated totals
            formatted_items = []
            for item in items:
                item_total = float(item['quantity']) * float(item['price'])
                formatted_items.append({
                    "description": item['description'],
                    "quantity": int(item['quantity']),
                    "price": float(item['price']),
                    "total": item_total
                })
            
            # Step 3: Create invoice via API
            invoice_data = {
                "agent_id": user['id'],
                "client_id": client_id,
                "items": formatted_items,
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
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                invoice_id = result.get('id')
                
                # Display success message with details
                st.success(f"✅ Invoice #{invoice_id} created successfully!")
                
                # Show summary
                total_items = len(formatted_items)
                total_amount = sum(item['total'] for item in formatted_items)
                
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); 
                            padding: 1.5rem; border-radius: 12px; margin: 1rem 0;'>
                    <h3 style='color: white; margin: 0;'>📄 Invoice Summary</h3>
                    <div style='color: white; margin-top: 1rem;'>
                        <p><strong>Invoice ID:</strong> #{invoice_id}</p>
                        <p><strong>Client:</strong> {client_name}</p>
                        <p><strong>Total Items:</strong> {total_items}</p>
                        <p><strong>Total Amount:</strong> {currency} {total_amount:,.2f}</p>
                        <p><strong>Type:</strong> {invoice_type}</p>
                        <p><strong>Language:</strong> {'English' if language == 'en' else 'Arabic'}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Note: PDF generation happens on backend automatically
                st.info("📄 PDF invoice has been generated and saved. You can view it in the invoice list.")
                
                st.balloons()
                
                # Show button to view invoices
                if st.button("📋 View All Invoices", type="primary"):
                    st.rerun()
                    
            else:
                st.error(f"❌ Failed to create invoice: {response.text}")
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
