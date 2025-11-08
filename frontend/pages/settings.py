"""Settings page for system configuration."""
import streamlit as st
import requests
from frontend.utils.theme import render_header


def render(api_base_url: str, user: dict):
    """Render the settings page."""
    render_header("⚙️ Settings", "System configuration and preferences")
    
    # Only admins can access settings
    if user['role'] != 'admin':
        st.warning("Settings are only accessible to administrators")
        return
    
    # Tabs for different settings sections
    tab1, tab2, tab3 = st.tabs(["👥 Employees", "🎨 Appearance", "🔧 System"])
    
    with tab1:
        render_employees_section(api_base_url)
    
    with tab2:
        render_appearance_section()
    
    with tab3:
        render_system_section(api_base_url)


def render_employees_section(api_base_url: str):
    """Render employees management section."""
    st.subheader("Employee Management")
    
    # Fetch employees
    try:
        response = requests.get(f"{api_base_url}/api/employees", timeout=5)
        
        if response.status_code == 200:
            employees = response.json()
            
            st.metric("Total Employees", len(employees))
            
            # Display employees
            if employees:
                for emp in employees:
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                    
                    with col1:
                        st.write(f"**{emp.get('name', 'N/A')}**")
                    
                    with col2:
                        st.write(emp.get('role', 'agent'))
                    
                    with col3:
                        st.write(emp.get('email', 'No email'))
                    
                    with col4:
                        if st.button("🗑️", key=f"del_emp_{emp['id']}"):
                            delete_employee(api_base_url, emp['id'])
            else:
                st.info("No employees found")
        else:
            st.error("Failed to load employees")
    except Exception as e:
        st.error(f"Error loading employees: {str(e)}")
    
    # Add employee form
    st.markdown("---")
    st.subheader("➕ Add Employee")
    
    with st.form("add_employee_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            emp_name = st.text_input("Name *")
        
        with col2:
            emp_role = st.selectbox("Role", options=["agent", "admin"])
        
        with col3:
            emp_email = st.text_input("Email")
        
        submitted = st.form_submit_button("Add Employee", type="primary", use_container_width=True)
        
        if submitted:
            if not emp_name:
                st.error("Employee name is required")
            else:
                try:
                    response = requests.post(
                        f"{api_base_url}/api/employees",
                        json={
                            "name": emp_name,
                            "role": emp_role,
                            "email": emp_email or None
                        },
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        st.success("Employee added successfully!")
                        st.rerun()
                    else:
                        st.error(f"Failed to add employee: {response.text}")
                except Exception as e:
                    st.error(f"Error adding employee: {str(e)}")


def delete_employee(api_base_url: str, employee_id: int):
    """Delete an employee."""
    try:
        response = requests.delete(
            f"{api_base_url}/api/employees/{employee_id}",
            timeout=5
        )
        
        if response.status_code == 200:
            st.success("Employee deleted successfully!")
            st.rerun()
        else:
            st.error("Failed to delete employee")
    except Exception as e:
        st.error(f"Error deleting employee: {str(e)}")


def render_appearance_section():
    """Render appearance settings."""
    st.subheader("Appearance Settings")
    
    # Theme selector
    st.write("**Theme**")
    theme = st.radio(
        "Choose theme",
        options=["Light", "Dark", "Auto"],
        horizontal=True
    )
    
    if st.button("Apply Theme"):
        st.session_state.theme = theme.lower()
        st.success(f"Theme set to {theme}")
    
    # Language
    st.markdown("---")
    st.write("**Language**")
    language = st.radio(
        "Choose language",
        options=["English", "Arabic"],
        horizontal=True
    )
    
    if st.button("Apply Language"):
        st.session_state.language = 'en' if language == "English" else 'ar'
        st.success(f"Language set to {language}")
    
    # Color scheme preview
    st.markdown("---")
    st.subheader("Color Scheme Preview")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 2rem; border-radius: 8px; text-align: center; color: white;'>
                <strong>Primary</strong>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                        padding: 2rem; border-radius: 8px; text-align: center; color: white;'>
                <strong>Secondary</strong>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                        padding: 2rem; border-radius: 8px; text-align: center; color: white;'>
                <strong>Accent</strong>
            </div>
        """, unsafe_allow_html=True)


def render_system_section(api_base_url: str):
    """Render system settings."""
    st.subheader("System Information")
    
    # API health check
    try:
        response = requests.get(f"{api_base_url}/health", timeout=5)
        
        if response.status_code == 200:
            st.success("✅ API is healthy and operational")
        else:
            st.error("❌ API health check failed")
    except Exception as e:
        st.error(f"❌ Cannot connect to API: {str(e)}")
    
    # System info
    st.markdown("---")
    st.write("**API Base URL:**", api_base_url)
    
    # Database info
    st.markdown("---")
    st.subheader("Database Maintenance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Run Auto-Cancel Check", use_container_width=True):
            st.info("Auto-cancel check runs automatically on system startup")
    
    with col2:
        if st.button("📊 View Statistics", use_container_width=True):
            try:
                response = requests.get(f"{api_base_url}/api/stats", timeout=5)
                if response.status_code == 200:
                    st.json(response.json())
            except Exception as e:
                st.error(f"Error fetching stats: {str(e)}")
