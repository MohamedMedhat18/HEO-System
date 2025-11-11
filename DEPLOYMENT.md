# HEO System Deployment Guide

## Quick Start

### Development Mode

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run with the startup script (easiest)
./start.sh

# OR manually run both services:

# Terminal 1 - Backend API
python backend/api/main.py
# OR with uvicorn
uvicorn backend.api.main:app --reload --port 8000

# Terminal 2 - Frontend
streamlit run frontend/app.py
```

Access the application:
- Frontend: http://localhost:8501
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Default Credentials
- Username: `admin1`
- Password: `admin_password` (change via `ADMIN_PASSWORD` env variable)

## Production Deployment

### 1. Environment Setup

Create a `.env` file:

```env
DATABASE_URL=sqlite:///db/database.db
ADMIN_PASSWORD=your_secure_password_here
API_BASE_URL=http://your-domain.com:8000
```

### 2. Backend Deployment

```bash
# Install production server
pip install gunicorn

# Run with multiple workers
gunicorn backend.api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

### 3. Frontend Deployment

```bash
# Run Streamlit in production mode
streamlit run frontend/app.py \
  --server.port 8501 \
  --server.address 0.0.0.0 \
  --server.headless true \
  --server.enableCORS false
```

### 4. Reverse Proxy (Nginx)

```nginx
# Backend API
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Frontend
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

## Docker Deployment

### Dockerfile (Backend)

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ backend/
COPY db/ db/

EXPOSE 8000

CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Dockerfile (Frontend)

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY frontend/ frontend/
COPY assets/ assets/
COPY locales/ locales/

EXPOSE 8501

CMD ["streamlit", "run", "frontend/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///db/database.db
      - ADMIN_PASSWORD=${ADMIN_PASSWORD}
    volumes:
      - ./db:/app/db
      - ./invoices:/app/invoices
    restart: unless-stopped

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "8501:8501"
    environment:
      - API_BASE_URL=http://backend:8000
    depends_on:
      - backend
    restart: unless-stopped
```

Run with:
```bash
docker-compose up -d
```

## Cloud Platform Deployment

### Streamlit Cloud (Recommended for Quick Deployment)

For the fastest and easiest deployment, see the dedicated guide:

📖 **[STREAMLIT_CLOUD_DEPLOYMENT.md](./STREAMLIT_CLOUD_DEPLOYMENT.md)**

This is the recommended option for:
- Quick demos and prototypes
- Small to medium deployments
- No infrastructure management needed
- Free tier available

### Heroku

1. Create `Procfile`:
```
web: sh setup.sh && streamlit run frontend/app.py
api: uvicorn backend.api.main:app --host 0.0.0.0 --port $PORT
```

2. Create `setup.sh`:
```bash
mkdir -p ~/.streamlit/
echo "[server]" > ~/.streamlit/config.toml
echo "port = $PORT" >> ~/.streamlit/config.toml
echo "enableCORS = false" >> ~/.streamlit/config.toml
echo "headless = true" >> ~/.streamlit/config.toml
```

3. Deploy:
```bash
heroku create your-app-name
git push heroku main
```

### AWS EC2

1. Launch an EC2 instance (Ubuntu 22.04)
2. Install dependencies:
```bash
sudo apt update
sudo apt install python3.12 python3-pip nginx -y
```

3. Clone and setup:
```bash
git clone https://github.com/your-repo/HEO-System.git
cd HEO-System
pip install -r requirements.txt
```

4. Setup systemd services:

`/etc/systemd/system/heo-backend.service`:
```ini
[Unit]
Description=HEO Backend API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/HEO-System
ExecStart=/usr/local/bin/uvicorn backend.api.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

`/etc/systemd/system/heo-frontend.service`:
```ini
[Unit]
Description=HEO Frontend
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/HEO-System
ExecStart=/usr/local/bin/streamlit run frontend/app.py --server.port 8501
Restart=always

[Install]
WantedBy=multi-user.target
```

5. Enable and start:
```bash
sudo systemctl enable heo-backend heo-frontend
sudo systemctl start heo-backend heo-frontend
```

## Database Migrations

### SQLite to PostgreSQL

1. Export data:
```bash
sqlite3 db/database.db .dump > backup.sql
```

2. Update `DATABASE_URL`:
```env
DATABASE_URL=postgresql://user:password@localhost/heodb
```

3. Modify connection in `backend/services/database.py` to use SQLAlchemy

## Monitoring

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Test authentication
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin1","password":"admin_password"}'
```

### Logs

```bash
# Backend logs
tail -f /var/log/heo-backend.log

# Frontend logs
tail -f /var/log/heo-frontend.log

# Agent logs
tail -f logs/*.json
```

## Backup

### Database Backup

```bash
# Backup
cp db/database.db db/database.db.backup.$(date +%Y%m%d)

# Restore
cp db/database.db.backup.20240101 db/database.db
```

### Full System Backup

```bash
tar -czf heo-backup-$(date +%Y%m%d).tar.gz \
  db/ \
  invoices/ \
  logs/ \
  .env
```

## Troubleshooting

### Common Issues

**1. Backend not starting**
- Check Python version: `python --version` (need 3.12+)
- Install dependencies: `pip install -r requirements.txt`
- Check logs for errors

**2. Frontend can't connect to backend**
- Verify backend is running: `curl http://localhost:8000/health`
- Check `API_BASE_URL` environment variable
- Ensure no firewall blocking port 8000

**3. Database errors**
- Initialize database: `python -c "from backend.services.database import init_db; init_db()"`
- Check file permissions on `db/` directory
- Ensure SQLite is installed

**4. AI Agents not running**
- Check GitHub Actions workflow status
- Verify Python path in workflow
- Check logs in `logs/` directory

## Security Checklist

- [ ] Change default admin password
- [ ] Use HTTPS in production
- [ ] Set up firewall rules
- [ ] Regular database backups
- [ ] Keep dependencies updated
- [ ] Monitor logs for suspicious activity
- [ ] Use environment variables for secrets
- [ ] Enable rate limiting on API

## Performance Optimization

1. **Database Indexing**:
```sql
CREATE INDEX idx_invoices_agent_id ON invoices(agent_id);
CREATE INDEX idx_invoices_client_id ON invoices(client_id);
CREATE INDEX idx_invoices_status ON invoices(status);
```

2. **Caching**:
- Add Redis for session caching
- Cache frequently accessed data
- Use Streamlit's `@st.cache_data` decorator

3. **Load Balancing**:
- Run multiple backend workers
- Use nginx for load balancing
- Consider CDN for static assets

## Support

For issues or questions:
- GitHub Issues: https://github.com/your-repo/HEO-System/issues
- Email: info@heomed.com
- Documentation: docs/ARCHITECTURE.md
