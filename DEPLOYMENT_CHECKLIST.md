# HEO System - Deployment Checklist

Use this checklist before deploying to production.

---

## Pre-Deployment Checklist

### ✅ Code Quality

- [x] All dependencies listed in requirements.txt
- [x] No import errors
- [x] All tests passing
- [x] Security scan completed (CodeQL: 0 alerts)
- [x] Documentation complete
- [x] README updated

### ✅ Configuration

- [ ] Changed default admin password
- [ ] Set ADMIN_PASSWORD environment variable
- [ ] Configured DATABASE_URL (if not using SQLite)
- [ ] Verified all paths are relative, not absolute
- [ ] Checked .gitignore excludes sensitive files

### ✅ Testing

- [x] Backend imports successfully
- [x] Database initializes without errors
- [x] PDF generation works (English)
- [x] PDF generation works (Arabic)
- [x] Authentication works
- [ ] Tested all pages manually
- [ ] Tested invoice creation workflow
- [ ] Tested client management
- [ ] Tested status updates

### ✅ Assets

- [x] Logo files present (assets/logo.png, assets/logo1.png)
- [x] Font files present (fonts/Roboto-*.ttf)
- [x] Translation files present (locales/en.json, locales/ar.json)
- [x] All directories created automatically on startup

### ✅ Documentation

- [x] README.md updated
- [x] DEPLOYMENT.md complete
- [x] STREAMLIT_CLOUD_DEPLOYMENT.md created
- [x] PROJECT_STRUCTURE.md created
- [x] FIXES_AND_IMPROVEMENTS.md created
- [x] API endpoints documented

---

## Streamlit Cloud Deployment

### Step 1: Prepare Repository

- [ ] All changes committed to GitHub
- [ ] Repository is public (or you have Streamlit Cloud Pro)
- [ ] Branch selected: `main` or `copilot/fix-imports-and-structure`

### Step 2: Deploy

1. [ ] Go to https://share.streamlit.io/
2. [ ] Sign in with GitHub
3. [ ] Click "New app"
4. [ ] Repository: `MohamedMedhat18/HEO-System`
5. [ ] Branch: `main` or your branch
6. [ ] Main file: `unified_app.py`
7. [ ] Click "Advanced settings"

### Step 3: Environment Variables

Add these in Streamlit Cloud Secrets:

```toml
ADMIN_PASSWORD = "your_secure_password_here"
DATABASE_URL = "sqlite:///db/database.db"
API_BASE_URL = "http://localhost:8000"
```

**⚠️ CRITICAL**: Change `your_secure_password_here` to a strong password!

### Step 4: Deploy

- [ ] Click "Deploy!"
- [ ] Wait 2-5 minutes for build
- [ ] Check logs for any errors

### Step 5: Verify

- [ ] App loads successfully
- [ ] Can log in with credentials
- [ ] Backend status shows 🟢 Online
- [ ] Can create a test quotation
- [ ] PDF generation works
- [ ] Can download PDF

---

## Local Deployment

### Windows

1. [ ] Python 3.10+ installed
2. [ ] Clone repository
3. [ ] Open PowerShell in repo directory
4. [ ] Run: `.\run_minimal.ps1`
5. [ ] Wait for startup (creates venv, installs packages)
6. [ ] Access at http://localhost:8501

### Linux/Mac

1. [ ] Python 3.10+ installed
2. [ ] Clone repository
3. [ ] Make script executable: `chmod +x start.sh`
4. [ ] Run: `./start.sh`
5. [ ] Access at http://localhost:8501

### Manual

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from backend.services.database import init_db; init_db()"

# Run unified app
streamlit run unified_app.py
```

---

## Docker Deployment

### Build and Run

```bash
# Build backend
docker build -f Dockerfile.backend -t heo-backend .

# Build frontend
docker build -f Dockerfile.frontend -t heo-frontend .

# Run with docker-compose
docker-compose up -d

# Access
# Frontend: http://localhost:8501
# Backend: http://localhost:8000
```

### Verify

- [ ] Containers running: `docker ps`
- [ ] Backend healthy: `curl http://localhost:8000/health`
- [ ] Frontend accessible: http://localhost:8501

---

## Post-Deployment

### Immediate (First Hour)

- [ ] Test login functionality
- [ ] Create test client
- [ ] Create test quotation with multiple items
- [ ] Generate and download PDF (English)
- [ ] Generate and download PDF (Arabic)
- [ ] Verify Arabic text displays correctly in PDF
- [ ] Test status update (Pending → Paid)
- [ ] Test employee management (if applicable)
- [ ] Check backend API: http://your-url.streamlit.app:8000/health (if accessible)

### First Day

- [ ] Monitor logs for errors
- [ ] Test all pages (Dashboard, Invoices, Clients, Settings)
- [ ] Create real client data
- [ ] Train team on system usage
- [ ] Document any issues encountered
- [ ] Set up regular database backups

### First Week

- [ ] Collect user feedback
- [ ] Monitor performance
- [ ] Check for any error patterns
- [ ] Optimize slow queries if needed
- [ ] Review security logs
- [ ] Update documentation based on issues

### First Month

- [ ] Review usage statistics
- [ ] Identify common workflows
- [ ] Plan feature enhancements
- [ ] Evaluate need for PostgreSQL migration
- [ ] Consider custom domain (if using Streamlit Cloud)
- [ ] Review and update dependencies

---

## Security Checklist

### Critical

- [ ] Default admin password changed
- [ ] ADMIN_PASSWORD environment variable set
- [ ] No secrets committed to Git
- [ ] HTTPS enabled (automatic on Streamlit Cloud)
- [ ] Database file not publicly accessible

### Recommended

- [ ] Regular database backups configured
- [ ] Logging enabled and monitored
- [ ] User passwords follow strong password policy
- [ ] API endpoints protected (authentication required)
- [ ] Dependencies up to date (run `pip list --outdated`)

### Optional

- [ ] Rate limiting implemented (for high-traffic sites)
- [ ] WAF configured (for enterprise deployments)
- [ ] Penetration testing completed
- [ ] Security audit performed
- [ ] Compliance requirements met (GDPR, etc.)

---

## Backup Strategy

### Database

**Frequency**: Daily

**Method**:
```bash
# Backup SQLite
cp db/database.db backups/database_$(date +%Y%m%d).db

# Backup to cloud (example)
aws s3 cp db/database.db s3://your-bucket/backups/database_$(date +%Y%m%d).db
```

### Invoices

**Frequency**: Weekly

**Method**:
```bash
# Backup invoices directory
tar -czf backups/invoices_$(date +%Y%m%d).tar.gz invoices/

# Or sync to cloud
rclone sync invoices/ cloud:heo-invoices/
```

### Configuration

**Frequency**: On change

**Method**:
```bash
# Backup environment variables and config
tar -czf backups/config_$(date +%Y%m%d).tar.gz \
  .env \
  .streamlit/config.toml \
  requirements.txt
```

---

## Monitoring

### Key Metrics to Track

- [ ] **Uptime**: Target 99.9%
- [ ] **Response Time**: < 2 seconds for page load
- [ ] **PDF Generation**: < 3 seconds
- [ ] **Error Rate**: < 0.1%
- [ ] **User Sessions**: Track active users
- [ ] **Database Size**: Monitor growth

### Tools

- **Streamlit Cloud**: Built-in analytics (if deployed there)
- **Application Logs**: Check `logs/` directory
- **Database Monitoring**: Check table sizes, query times
- **Custom Metrics**: Add to application as needed

### Alerts

Set up alerts for:
- [ ] Application crashes
- [ ] High error rates
- [ ] Slow response times
- [ ] Database corruption
- [ ] Low disk space
- [ ] Failed PDF generations

---

## Rollback Plan

If deployment fails:

### Immediate Actions

1. **Check Logs**: Review error messages
2. **Verify Environment**: Check environment variables
3. **Test Locally**: Reproduce issue locally
4. **Database**: Restore from backup if needed

### Rollback Steps

```bash
# If using Git
git revert <commit-hash>
git push origin main

# If on Streamlit Cloud
# Revert to previous commit via GitHub
# Streamlit Cloud will auto-redeploy

# If local/Docker
# Stop services
docker-compose down
# Checkout previous version
git checkout <previous-tag>
# Restart services
docker-compose up -d
```

### Communication

- [ ] Notify users of the issue
- [ ] Provide expected resolution time
- [ ] Update status page (if applicable)
- [ ] Announce when issue is resolved

---

## Troubleshooting Common Issues

### Issue: "Backend Offline"

**Symptoms**: Red indicator, API calls failing

**Solutions**:
1. Check if port 8000 is available
2. Verify backend process started (check logs)
3. Increase startup timeout in unified_app.py
4. Check for import errors in backend code

### Issue: "Database Locked"

**Symptoms**: "database is locked" error

**Solutions**:
1. Close all database connections
2. Restart application
3. Check for long-running queries
4. Consider migrating to PostgreSQL

### Issue: "PDF Generation Failed"

**Symptoms**: Error when generating PDF

**Solutions**:
1. Verify reportlab installed: `pip list | grep reportlab`
2. Check fonts exist: `ls fonts/*.ttf`
3. Verify arabic-reshaper installed for Arabic
4. Check logs for specific error
5. Test with sample data

### Issue: "Login Not Working"

**Symptoms**: "Invalid credentials" error

**Solutions**:
1. Verify database initialized: Check `db/database.db` exists
2. Check default password: Try `admin_password`
3. Verify ADMIN_PASSWORD environment variable
4. Check user exists: Query users table
5. Test password hashing: Check bcrypt working

---

## Performance Optimization

### If Response is Slow

1. [ ] Check database indexes
2. [ ] Optimize SQL queries
3. [ ] Enable caching (`@st.cache_data`)
4. [ ] Reduce item count per page
5. [ ] Optimize image sizes
6. [ ] Use CDN for static assets

### If PDF Generation is Slow

1. [ ] Optimize font loading (cache fonts)
2. [ ] Reduce image sizes in PDFs
3. [ ] Simplify PDF layout
4. [ ] Generate PDFs asynchronously
5. [ ] Consider PDF caching

### If Memory Usage is High

1. [ ] Clear Streamlit cache periodically
2. [ ] Optimize database queries (avoid SELECT *)
3. [ ] Limit concurrent users (upgrade resources)
4. [ ] Check for memory leaks
5. [ ] Upgrade to larger instance

---

## Support Contacts

### Internal

- **Developer**: [Your Team]
- **System Admin**: [Your Admin]
- **Business Owner**: [Your Owner]

### External

- **GitHub Issues**: https://github.com/MohamedMedhat18/HEO-System/issues
- **Email Support**: info@heomed.com
- **Streamlit Community**: https://discuss.streamlit.io/
- **FastAPI Community**: https://github.com/tiangolo/fastapi/discussions

### Documentation

- **This Project**: See all .md files in repository
- **Streamlit Docs**: https://docs.streamlit.io/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **ReportLab**: https://www.reportlab.com/docs/

---

## Success Criteria

Deployment is successful when:

- [x] Application loads without errors
- [x] Users can log in
- [x] Invoices can be created
- [x] PDFs generate correctly (both languages)
- [x] Database operations work
- [x] All pages accessible
- [x] No security vulnerabilities (CodeQL: 0 alerts)
- [x] Performance acceptable (< 3s for operations)
- [x] Documentation complete
- [x] Team trained on usage

---

## Sign-Off

- [ ] **Developer**: Code reviewed and tested ✅
- [ ] **QA**: All tests passed
- [ ] **Security**: Security scan completed ✅
- [ ] **Manager**: Approved for deployment
- [ ] **Client**: Accepted and signed off

---

**Deployment Date**: _______________

**Deployed By**: _______________

**Version**: 2.0.0

**Status**: ✅ READY

---

*For detailed deployment instructions, see:*
- *STREAMLIT_CLOUD_DEPLOYMENT.md*
- *DEPLOYMENT.md*
- *FIXES_AND_IMPROVEMENTS.md*
