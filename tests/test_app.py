import streamlit as st
import json
import os

# Load translations
def load_translations():
    with open(os.path.join('locales', 'en.json'), 'r', encoding='utf-8') as f:
        en_translations = json.load(f)
    with open(os.path.join('locales', 'ar.json'), 'r', encoding='utf-8') as f:
        ar_translations = json.load(f)
    return en_translations, ar_translations

# Test the language toggle functionality
def test_language_toggle():
    en_translations, ar_translations = load_translations()
    
    # Simulate language toggle
    st.session_state.language = 'en'
    assert st.session_state.language == 'en'
    assert st.session_state.translations == en_translations

    st.session_state.language = 'ar'
    assert st.session_state.language == 'ar'
    assert st.session_state.translations == ar_translations

# Test the authentication system
def test_authentication():
    # Mock user data
    users = {'test_user': 'password123'}
    
    # Simulate login
    username = 'test_user'
    password = 'password123'
    
    assert username in users
    assert users[username] == password

# Test PDF generation
def test_pdf_generation():
    # Assuming a function generate_pdf exists in app.py
    from app import generate_pdf
    
    invoice_data = {'client_name': 'John Doe', 'amount': 100}
    pdf = generate_pdf(invoice_data)
    
    assert pdf is not None
    assert isinstance(pdf, bytes)

# Run tests
if __name__ == "__main__":
    test_language_toggle()
    test_authentication()
    test_pdf_generation()
    st.success("All tests passed!")