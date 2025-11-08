#!/bin/bash

# HEO System Startup Script
# This script starts both the backend API and frontend application

echo "🚀 Starting HEO System..."

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.12+."
    exit 1
fi

# Check if dependencies are installed
echo "📦 Checking dependencies..."
if ! python -c "import streamlit" &> /dev/null; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
fi

# Create necessary directories
mkdir -p logs db invoices

echo "🔧 Initializing database..."
python -c "from backend.services.database import init_db; from backend.services.auth import create_default_admin; init_db(); create_default_admin()"

# Start backend in background
echo "🌐 Starting Backend API on port 8000..."
python backend/api/main.py &
BACKEND_PID=$!

# Wait for backend to be ready
sleep 3

# Start frontend
echo "🎨 Starting Frontend on port 8501..."
streamlit run frontend/app.py --server.port 8501

# Cleanup on exit
trap "kill $BACKEND_PID" EXIT
