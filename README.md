# HEO System - Professional Invoice Management with AI

> **A self-improving, AI-driven invoice management system that's more advanced than Replit's or Lovable's AI Agents.**

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🌟 Overview

HEO System is a professional, AI-driven invoice management platform designed for medical device suppliers and engineering solutions providers. Built with a modern, modular architecture, it features:

- 🎨 **Professional UI**: Beautiful Streamlit interface with dark mode, animations, and real-time updates
- ⚡ **FastAPI Backend**: High-performance REST API with async support
- 🤖 **AI Agents**: Self-improving system with 4 specialized agents
- 🌍 **Bilingual**: Full English and Arabic support
- 📱 **Responsive**: Works seamlessly on desktop and mobile
- 🔒 **Secure**: Authentication, password hashing, and SQL injection prevention

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- pip package manager

### One-Command Setup

```bash
# Clone the repository
git clone https://github.com/MohamedMedhat18/HEO-System.git
cd HEO-System

# Install dependencies
pip install -r requirements.txt

# Run the unified application (recommended)
streamlit run unified_app.py

# OR run with the start script (backend + frontend separately)
./start.sh

# OR run the standalone app
streamlit run app.py
```

The application will be available at:
- **Unified App**: http://localhost:8501 (Backend auto-starts on 8000)
- Frontend: http://localhost:8501
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Manual Setup (Legacy)

```bash
# Install dependencies
pip install -r requirements.txt

# Option 1: Unified App (Recommended - Auto-starts backend)
streamlit run unified_app.py

# Option 2: Standalone App (All-in-one)
streamlit run app.py

# Option 3: Separate Backend + Frontend
# Terminal 1: Start Backend API
python backend/api/main.py

# Terminal 2: Start Frontend
streamlit run frontend/app.py
```

### Default Login
- **Username**: `admin1`
- **Password**: `admin_password` (or set via `ADMIN_PASSWORD` env variable)

## 🏗️ Architecture

The system follows a modular, three-tier architecture:

```
├── frontend/          # Streamlit UI (pages, components, theme)
├── backend/           # FastAPI (API, services, models)
├── agents/            # AI agents (ui, logic, docs, test)
├── .github/workflows/ # CI/CD and AI automation
└── docs/              # Documentation
```

### AI Agents System

Four specialized agents continuously improve the codebase:

1. **🎨 UI Agent**: Analyzes frontend code, suggests UI/UX improvements
2. **⚙️ Logic Agent**: Monitors backend quality, identifies security issues
3. **📚 Documentation Agent**: Ensures comprehensive documentation
4. **🧪 Test Agent**: Tracks test coverage and quality

Agents run weekly via GitHub Actions and generate detailed reports.

## ✨ Features

### Frontend
- ✅ **Unified Application** - Single entry point with auto-starting backend
- ✅ **Professional Modern UI** - Gradient themes, animations, and responsive design
- ✅ **Quotation Request System** - Dynamic items support (up to 30+ items per request)
- ✅ Modern dashboard with real-time metrics
- ✅ Animated card components with live indicators
- ✅ Bilingual interface (EN/AR) with RTL support
- ✅ Responsive design for desktop and mobile
- ✅ Professional invoice/quotation forms
- ✅ Client management with full CRUD operations
- ✅ Settings panel with system configuration

### Backend
- ✅ RESTful API with FastAPI
- ✅ Pydantic data validation
- ✅ JWT-ready authentication
- ✅ Async database operations
- ✅ PDF generation (bilingual)
- ✅ Auto-generated API docs
- ✅ Error handling
- ✅ CORS configuration

### AI Capabilities
- ✅ Automated code analysis
- ✅ Security vulnerability detection
- ✅ Performance optimization suggestions
- ✅ Documentation coverage tracking
- ✅ Test coverage monitoring
- ✅ Weekly automated reports
- ✅ Self-improvement cycle

## 📖 Documentation

### Quick Start Guides
- 🚀 **[Streamlit Cloud Deployment](STREAMLIT_CLOUD_DEPLOYMENT.md)** - Deploy to cloud in 5 minutes
- 🖥️ **[Windows Setup](run_minimal.ps1)** - PowerShell startup script
- 🐧 **[Linux/Mac Setup](start.sh)** - Bash startup script

### Complete Documentation
- 📁 **[Project Structure](PROJECT_STRUCTURE.md)** - Complete file/folder organization
- 🔧 **[Fixes & Improvements](FIXES_AND_IMPROVEMENTS.md)** - What's been fixed and how
- 🌐 **[Deployment Guide](DEPLOYMENT.md)** - All deployment options (Docker, AWS, etc.)
- 🏗️ **[Architecture Guide](docs/ARCHITECTURE.md)** - System design and components
- 📡 **[API Documentation](http://localhost:8000/docs)** - Interactive API docs (when running)
- 🤝 **[Contributing Guide](CONTRIBUTING.md)** - How to contribute

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test type
pytest tests/unit/
pytest tests/integration/
```

## 🔧 Development

### Project Structure

```
HEO-System/
├── frontend/              # Streamlit application
│   ├── app.py            # Main entry point
│   ├── pages/            # Page modules
│   └── utils/            # Theme & utilities
├── backend/               # FastAPI application
│   ├── api/              # API endpoints
│   ├── models/           # Pydantic models
│   └── services/         # Business logic
├── agents/                # AI agents
│   ├── base_agent.py     # Base class
│   ├── ui_agent/         # UI analyzer
│   ├── logic_agent/      # Backend analyzer
│   ├── docs_agent/       # Documentation checker
│   └── test_agent/       # Test coverage tracker
└── tests/                 # Test suite
```

### Adding New Features

1. **Frontend**: Add page modules in `frontend/pages/`
2. **Backend**: Add endpoints in `backend/api/main.py`
3. **Models**: Define in `backend/models/`
4. **Services**: Add business logic in `backend/services/`

## 🤖 AI Agents

### Running Agents Manually

```python
# Run individual agent
from agents.ui_agent.agent import UIAgent
agent = UIAgent()
results = agent.run()
print(results)

# Run all agents
from agents.ui_agent.agent import UIAgent
from agents.logic_agent.agent import LogicAgent
from agents.docs_agent.agent import DocsAgent
from agents.test_agent.agent import TestAgent

for AgentClass in [UIAgent, LogicAgent, DocsAgent, TestAgent]:
    agent = AgentClass()
    agent.run()
```

### Automated Runs

Agents run automatically every Sunday at midnight via GitHub Actions. See `.github/workflows/ai_autoupdate.yml`.

## 🌐 Deployment

### Production Deployment

```bash
# Backend (with workers)
uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --workers 4

# Frontend
streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0
```

### Environment Variables

```bash
DATABASE_URL=sqlite:///db/database.db
ADMIN_PASSWORD=secure_password
API_BASE_URL=http://localhost:8000
```

## 📊 Performance

- API Response: <200ms (95th percentile)
- Frontend Load: <2 seconds
- PDF Generation: <5 seconds
- Agent Analysis: <2 minutes per agent

## 🔒 Security

- ✅ Password hashing with bcrypt
- ✅ SQL injection prevention
- ✅ Input validation with Pydantic
- ✅ CORS configuration
- ✅ Secure session management
- ✅ Environment-based secrets

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with ❤️ for medical device suppliers
- Powered by Streamlit, FastAPI, and AI
- Inspired by the need for intelligent, self-improving systems

## 📧 Contact

- **Company**: EL HEKMA ENGINEERING OFFICE Co.
- **Email**: info@heomed.com
- **Website**: www.heomed.com
- **Address**: 41 Al-Mawardi Street, Al-Qasr Al-Aini, Cairo, Egypt

---

**Made with 🤖 AI-Powered Architecture** | **More Advanced than Replit & Lovable**