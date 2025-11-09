"""Clients page for managing clients."""
import streamlit as st
import requests
from frontend.utils.theme import render_header


def render(api_base_url: str, user: dict):
    """Render the clients page."""
    render_header("👥 Clients", "Manage your client database")
    
    # Fetch clients
    try:
        response = requests.get(f"{api_base_url}/api/clients", timeout=5)
        
        if response.status_code == 200:
            clients = response.json()
            
            # Display client count
            st.metric("Total Clients", len(clients))
            
            # Search
            search = st.text_input("🔍 Search clients", placeholder="Search by name or email")
            
            if search:
                search_lower = search.lower()
                clients = [
                    c for c in clients
                    if search_lower in str(c.get('name', '')).lower()
                    or search_lower in str(c.get('email', '')).lower()
                ]
            
            # Display clients as cards
            if clients:
                for client in clients:
                    st.markdown(f"""
                        <div class='card animated-card' style='margin-bottom: 1rem;'>
                            <h4>{client.get('name', 'N/A')}</h4>
                            <p style='margin: 0.5rem 0; color: #6b7280;'>
                                📧 {client.get('email', 'No email')}
                            </p>
                            <p style='margin: 0.5rem 0; color: #6b7280;'>
                                📞 {client.get('phone', 'No phone')}
                            </p>
                            <p style='margin: 0.5rem 0; color: #6b7280;'>
                                📍 {client.get('address', 'No address')}
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No clients found")
        else:
            st.error("Failed to load clients")
    except Exception as e:
        st.error(f"Error loading clients: {str(e)}")
    
    # Add new client form
    st.markdown("---")
    st.subheader("➕ Add New Client")
    
    with st.form("add_client_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Client Name *")
            email = st.text_input("Email")
        
        with col2:
            phone = st.text_input("Phone")
            address = st.text_area("Address")
        
        submitted = st.form_submit_button("Add Client", type="primary", use_container_width=True)
        
        if submitted:
            if not name:
                st.error("Client name is required")
            else:
                try:
                    response = requests.post(
                        f"{api_base_url}/api/clients",
                        json={
                            "name": name,
                            "email": email or None,
                            "phone": phone or None,
                            "address": address or None
                        },
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        st.success("Client added successfully!")
                        st.rerun()
                    else:
                        st.error(f"Failed to add client: {response.text}")
                except Exception as e:
                    st.error(f"Error adding client: {str(e)}")
