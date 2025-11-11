# Streamlit Cloud Deployment Guide

## Overview

This guide provides step-by-step instructions to deploy the HEO System on Streamlit Cloud.

## Prerequisites

1. GitHub account with the HEO-System repository
2. Streamlit Cloud account (sign up at https://streamlit.io/cloud)
3. Repository must be public or you need Streamlit Cloud Pro for private repos

## Deployment Steps

### 1. Prepare Your Repository

Ensure these files are in your repository:
- ✅ `requirements.txt` - All Python dependencies
- ✅ `unified_app.py` - Main application entry point
- ✅ `.streamlit/config.toml` - Streamlit configuration (optional)
- ✅ All necessary folders: `backend/`, `frontend/`, `assets/`, `fonts/`, `locales/`

### 2. Sign In to Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Sign in with your GitHub account
3. Authorize Streamlit Cloud to access your repositories

### 3. Deploy the App

1. Click "New app" button
2. Select your repository: `MohamedMedhat18/HEO-System`
3. Select branch: `main` (or your preferred branch)
4. Set Main file path: `unified_app.py`
5. (Optional) Set App URL: Choose a custom subdomain

### 4. Configure Advanced Settings

Click "Advanced settings" before deploying:

#### Python Version
- Select: **Python 3.12** (or 3.11 if 3.12 not available)

#### Environment Variables

Add the following secrets (click "Add" for each):

```
DATABASE_URL=sqlite:///db/database.db
ADMIN_PASSWORD=your_secure_password_here
API_BASE_URL=http://localhost:8000
```

**Important**: Change `your_secure_password_here` to a strong password!

Additional optional variables:
```
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_SERVER_ENABLE_CORS=false
```

### 5. Deploy

1. Click "Deploy!" button
2. Wait for the app to build (2-5 minutes)
3. Once deployed, you'll get a URL like: `https://your-app-name.streamlit.app`

## Post-Deployment Configuration

### Default Credentials

After first deployment, you can log in with:
- **Username**: `admin1`
- **Password**: The value you set in `ADMIN_PASSWORD` env variable (default: `admin_password`)

**⚠️ Important**: Change the default password immediately in production!

### Database Initialization

The app automatically:
1. Creates the SQLite database on first run
2. Creates required tables
3. Sets up the default admin user
4. Creates necessary directories (`db/`, `invoices/`, `logs/`)

### Verify Deployment

1. Open your app URL
2. Check that the login page appears
3. Log in with default credentials
4. Test creating a quotation request
5. Test PDF generation (both English and Arabic)
6. Verify that the backend API is responding (the app starts it automatically)

## App Architecture on Streamlit Cloud

### How It Works

The `unified_app.py` does the following:

1. **Starts Backend API**: Automatically starts FastAPI backend on port 8000 in a background thread
2. **Waits for Backend**: Ensures backend is ready before showing UI
3. **Runs Frontend**: Shows the Streamlit UI which communicates with the backend
4. **All-in-One**: No need to deploy backend separately

### File Structure

```
HEO-System/
├── unified_app.py          # ⭐ Main entry point (Streamlit + Backend)
├── app.py                  # Alternative standalone app
├── requirements.txt        # Python dependencies
├── .streamlit/
│   └── config.toml        # Streamlit configuration
├── backend/
│   ├── api/
│   │   └── main.py        # FastAPI application
│   ├── models/            # Pydantic models
│   └── services/          # Business logic
├── frontend/
│   ├── app.py            # Modular frontend (alternative)
│   ├── pages/            # Page modules
│   └── utils/            # Helper functions
├── assets/
│   ├── logo.png          # Company logo
│   └── fonts/            # Font files (Roboto, Tajawal)
├── fonts/                # Additional fonts
├── locales/              # Translations (en.json, ar.json)
├── agents/               # AI agents
├── db/                   # SQLite database (created at runtime)
└── invoices/             # Generated PDF files (created at runtime)
```

## Configuration Files

### requirements.txt

Ensure all dependencies are listed with versions:

```txt
streamlit>=1.28.0
bcrypt>=4.0.1
plotly>=5.17.0
reportlab>=4.0.0
arabic-reshaper>=3.0.0
python-bidi>=0.4.2
pandas>=2.0.0
openpyxl>=3.1.0
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic[email]>=2.0.0
requests>=2.31.0
python-multipart>=0.0.6
email-validator>=2.0.0
httpx>=0.25.0
pillow>=10.0.0
qrcode>=7.4.2
```

### .streamlit/config.toml (Optional)

```toml
[theme]
primaryColor = "#3880fa"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#f5f7fa"
textColor = "#183475"
font = "sans serif"

[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false
```

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | No | `sqlite:///db/database.db` | Database connection string |
| `ADMIN_PASSWORD` | No | `admin_password` | Default admin password |
| `API_BASE_URL` | No | `http://localhost:8000` | Backend API URL |
| `STREAMLIT_SERVER_PORT` | No | `8501` | Frontend port |

## Troubleshooting

### Issue: App Not Loading

**Symptoms**: Spinning wheel, blank screen
**Solutions**:
1. Check Streamlit Cloud logs (click "Manage app" → "Logs")
2. Verify all files are committed to GitHub
3. Check for import errors in logs
4. Ensure `requirements.txt` has all dependencies

### Issue: Backend Not Starting

**Symptoms**: "Backend Offline" indicator, API errors
**Solutions**:
1. Check that `uvicorn` is in `requirements.txt`
2. Verify port 8000 is not being used elsewhere (unlikely on Streamlit Cloud)
3. Check backend logs in the Streamlit Cloud console
4. Increase backend startup timeout in `unified_app.py` if needed

### Issue: Missing Fonts or Images

**Symptoms**: Broken images, PDF generation errors
**Solutions**:
1. Verify `assets/` and `fonts/` folders are in repository
2. Check file paths are relative, not absolute
3. Ensure logo files are committed (not in .gitignore)
4. Font files should be in `fonts/` directory

### Issue: Database Errors

**Symptoms**: "Table doesn't exist", database locked errors
**Solutions**:
1. Delete `db/database.db` and restart (Cloud will recreate it)
2. Ensure `db/` directory exists
3. Check write permissions (Streamlit Cloud may have restrictions)
4. Consider using a remote database for production (PostgreSQL)

### Issue: Arabic Text Not Displaying Correctly

**Symptoms**: Arabic text shows as broken characters or reversed
**Solutions**:
1. Verify `arabic-reshaper` and `python-bidi` are installed
2. Check that Tajawal font is available in `fonts/` directory
3. Ensure PDF generation uses `get_display()` and `reshape()` for Arabic
4. Test with the sample PDF generation in Settings page

### Issue: Authentication Not Working

**Symptoms**: Can't log in, invalid credentials error
**Solutions**:
1. Check `ADMIN_PASSWORD` environment variable is set correctly
2. Database might not be initialized - restart the app
3. Try default credentials: `admin1` / `admin_password`
4. Check backend health: `https://your-app.streamlit.app/health` (if accessible)

## Performance Optimization

### Tips for Better Performance

1. **Use Caching**: Streamlit's `@st.cache_data` is already used for data loading
2. **Minimize API Calls**: Frontend batches requests where possible
3. **Optimize Images**: Compress logo and assets before committing
4. **Database Indexing**: Indexes are auto-created on common query fields
5. **Lazy Loading**: Only load data when pages are accessed

### Resource Limits

Streamlit Cloud Community (Free) tier limits:
- **Memory**: 1 GB RAM
- **CPU**: Shared CPU
- **Storage**: Limited (ephemeral)
- **Sleep**: Apps sleep after 7 days of inactivity

For production with higher traffic, consider:
- Streamlit Cloud Pro/Teams
- Self-hosting on AWS/Azure/GCP
- Using external database (PostgreSQL, MongoDB)

## Updating Your Deployment

### To Update the App:

1. Make changes to your code locally
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Update: description of changes"
   git push origin main
   ```
3. Streamlit Cloud will auto-detect changes and redeploy (takes 2-5 minutes)
4. Alternatively, click "Reboot app" in Streamlit Cloud dashboard for immediate restart

### To Update Environment Variables:

1. Go to Streamlit Cloud dashboard
2. Click "..." next to your app → "Settings"
3. Update variables under "Secrets"
4. Click "Save"
5. Reboot the app for changes to take effect

## Security Best Practices

✅ **Do's:**
- Use strong passwords for admin accounts
- Set `ADMIN_PASSWORD` via environment variables
- Keep dependencies updated
- Use HTTPS (Streamlit Cloud provides this automatically)
- Regularly backup database
- Monitor logs for suspicious activity

❌ **Don'ts:**
- Don't commit passwords or secrets to Git
- Don't use default credentials in production
- Don't expose backend port 8000 publicly (unified_app handles this)
- Don't store sensitive data in SQLite for high-value applications

## Support and Resources

- **Streamlit Docs**: https://docs.streamlit.io/
- **Streamlit Cloud Docs**: https://docs.streamlit.io/streamlit-community-cloud
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Project Issues**: https://github.com/MohamedMedhat18/HEO-System/issues
- **HEO Contact**: info@heomed.com

## Migration to Production Database

For production use, consider migrating from SQLite to PostgreSQL:

### 1. Set Up PostgreSQL (e.g., on Heroku, Railway, or Supabase)

```bash
# Example with Heroku Postgres
heroku addons:create heroku-postgresql:mini
heroku config:get DATABASE_URL
```

### 2. Update DATABASE_URL in Streamlit Secrets

```
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

### 3. Update Database Connection Code

Modify `backend/services/database.py` to use SQLAlchemy with PostgreSQL adapter.

### 4. Run Migration

Export data from SQLite and import into PostgreSQL using standard database tools.

## Conclusion

Your HEO System should now be live on Streamlit Cloud! 🎉

Access your app at: `https://your-app-name.streamlit.app`

For any issues, check the troubleshooting section above or contact support.

---

**Last Updated**: November 2024  
**Version**: 2.0.0  
**Maintained By**: HEO Medical Systems
