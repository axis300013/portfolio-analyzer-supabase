# 🚀 Supabase Setup Guide for Portfolio Analyzer

## Step 1: Create Supabase Account (5 minutes)

### 1.1 Sign Up
1. Go to: https://supabase.com
2. Click **"Start your project"**
3. Sign in with GitHub (recommended) or email
4. Confirm your email address

### 1.2 Create New Project
1. Click **"New Project"**
2. Fill in details:
   - **Name**: `portfolio-analyzer`
   - **Database Password**: Generate a strong password (SAVE THIS!)
   - **Region**: Choose closest to you (e.g., Europe - Frankfurt, US East, etc.)
   - **Pricing Plan**: **Free** (500MB database, 500MB file storage)
3. Click **"Create new project"**
4. Wait 2-3 minutes for database provisioning

### 1.3 Get Connection Details
1. In your project dashboard, click **"Settings"** (gear icon) in left sidebar
2. Click **"Database"** under Settings
3. Scroll to **"Connection string"** section
4. Under **"Connection string"**, select **"URI"**
5. Click **"Copy"** - You'll see something like:
   ```
   postgresql://postgres.xxxxxxxxxxxxx:YOUR_PASSWORD@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
   ```
   """postgresql://postgres:[YOUR_PASSWORD]@db.hrlzrirsvifxsnccxvsa.supabase.co:5432/postgres"""
6. **SAVE THIS CONNECTION STRING** - you'll need it!

### 1.4 Connection Parameters (Alternative)
If you prefer individual parameters, note these from the same page:
- **Host**: `aws-0-eu-central-1.pooler.supabase.com`
- **Database name**: `postgres`
- **Port**: `6543` (for pooler connection) or `5432` (for direct)
- **User**: `postgres.xxxxxxxxxxxxx`
- **Password**: Your password from step 1.2

---

## Step 2: Migrate Your Database to Supabase (10 minutes)

### 2.1 Export Current PostgreSQL Data
Run this in your PowerShell:

```powershell
# Navigate to your project folder
cd "C:\Users\SzalmaNB1\Downloads\cabeceo\visual studio\Portfolio Analyzer"

# Export your current database (make sure Docker is running)
docker exec -t portfolio_db pg_dump -U portfolio_user -d portfolio_db --clean --if-exists > backup_before_supabase.sql

# This creates backup_before_supabase.sql with all your data
```

### 2.2 Clean Up Export for Supabase
Open `backup_before_supabase.sql` and:
1. Remove any lines starting with `DROP DATABASE` or `CREATE DATABASE`
2. Remove any `ALTER DATABASE` commands
3. Save the file

### 2.3 Import to Supabase

**Option A: Using Supabase Dashboard (Easy)**
1. Go to your Supabase project
2. Click **"SQL Editor"** in left sidebar
3. Click **"New query"**
4. Copy contents of `backup_before_supabase.sql`
5. Paste into the editor
6. Click **"Run"**

**Option B: Using psql Command (Advanced)**
```powershell
# Install psql if not already (or use Docker)
# Replace with YOUR connection string
$env:PGPASSWORD="YOUR_PASSWORD"
psql "postgresql://postgres.xxxxxxxxxxxxx:YOUR_PASSWORD@aws-0-eu-central-1.pooler.supabase.com:6543/postgres" -f backup_before_supabase.sql
```

### 2.4 Verify Data Import
1. In Supabase dashboard, click **"Table Editor"**
2. You should see all your tables:
   - `portfolios`
   - `instruments`
   - `prices`
   - `portfolio_values_daily`
   - `wealth_categories`
   - `wealth_values`
   - `total_wealth_snapshots`
   - etc.
3. Click on each table to verify data is there

---

## Step 3: Update Your Application Configuration (5 minutes)

### 3.1 Create Environment File
I'll create a `.env` file with your Supabase connection details.

**File: `.env`** (in project root)
```env
# Supabase Database Connection
DATABASE_URL=postgresql://postgres.xxxxxxxxxxxxx:YOUR_PASSWORD@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
DATABASE_HOST=aws-0-eu-central-1.pooler.supabase.com
DATABASE_PORT=6543
DATABASE_NAME=postgres
DATABASE_USER=postgres.xxxxxxxxxxxxx
DATABASE_PASSWORD=YOUR_PASSWORD

# Application Settings
API_HOST=0.0.0.0
API_PORT=8000
UI_PORT=8501
```

### 3.2 Update Backend Configuration
The backend code will automatically read from `.env` file (no changes needed if you use `python-dotenv`).

### 3.3 Test Connection
Run this test script to verify connection:

```powershell
# Test connection
python -c "
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    result = conn.execute(text('SELECT version()'))
    print('✅ Connected to Supabase!')
    print(result.fetchone()[0])
"
```

---

## Step 4: Create Portable Launcher (10 minutes)

### 4.1 Install Dependencies
```powershell
# Install python-dotenv for reading .env files
cd backend
pip install python-dotenv
pip freeze > requirements.txt

cd ../ui
pip install python-dotenv
pip freeze > requirements.txt
```

### 4.2 Create Launcher Script
I'll create a `start_portfolio_supabase.ps1` launcher that:
- Loads environment variables
- Starts FastAPI backend
- Starts Streamlit UI
- Opens browser automatically

---

## Step 5: Security Best Practices

### 5.1 Protect Your .env File
**IMPORTANT:** Never commit `.env` to GitHub!

Add to `.gitignore`:
```
.env
*.env
.env.local
```

### 5.2 Create .env.example Template
Create `.env.example` (safe to commit):
```env
# Supabase Database Connection
DATABASE_URL=postgresql://postgres.PROJECT_REF:YOUR_PASSWORD@HOST:PORT/postgres
DATABASE_HOST=your-project.supabase.com
DATABASE_PORT=6543
DATABASE_NAME=postgres
DATABASE_USER=postgres.PROJECT_REF
DATABASE_PASSWORD=your_password_here

# Application Settings
API_HOST=0.0.0.0
API_PORT=8000
UI_PORT=8501
```

### 5.3 Database Security (Supabase Dashboard)
1. Go to **Settings → Database**
2. Under **"Connection pooling"**, ensure **"Connection pooler"** is enabled
3. Under **"SSL enforcement"**, keep **"Require SSL"** enabled
4. Consider enabling **Row Level Security (RLS)** for production

---

## Step 6: Access From Multiple Devices

### 6.1 Same Connection String
On any device:
1. Copy your project folder (or just the `.env` file)
2. Install Python dependencies
3. Run the launcher
4. Everything connects to the same Supabase database

### 6.2 Cloud Sync (Optional)
To sync your configuration:
1. Copy `.env.example` to OneDrive/PortfolioAnalyzer/
2. Rename to `.env`
3. Reference this file in your launcher

---

## Step 7: Backup Strategy

### 7.1 Automatic Supabase Backups
- **Free tier**: Daily backups (kept for 7 days)
- **Pro tier** ($25/mo): Point-in-time recovery

### 7.2 Manual Backup Script
Create `backup_to_local.ps1`:
```powershell
$env:PGPASSWORD="YOUR_PASSWORD"
$date = Get-Date -Format "yyyy-MM-dd"
$backupFile = "backup_$date.sql"

pg_dump "postgresql://postgres.xxxxx:PASSWORD@HOST:PORT/postgres" > $backupFile

Write-Host "✅ Backup saved to: $backupFile"
```

### 7.3 Schedule Weekly Backups
Use Windows Task Scheduler to run backup script weekly.

---

## Step 8: Monitor Usage (Free Tier Limits)

### 8.1 Check Your Usage
In Supabase dashboard:
1. Go to **Settings → Billing**
2. View **Database Size** (limit: 500MB)
3. View **Bandwidth** (limit: 2GB/month)

### 8.2 Optimize Database Size
If you approach limits:
```sql
-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Archive old data if needed
-- Delete old price history (keep last 2 years)
DELETE FROM prices WHERE date < NOW() - INTERVAL '2 years';
```

---

## Troubleshooting

### Issue: "Connection timeout"
**Solution:** 
- Check your internet connection
- Verify connection string is correct
- Try using direct connection (port 5432) instead of pooler (port 6543)

### Issue: "SSL required"
**Solution:**
Add `?sslmode=require` to connection string:
```
postgresql://user:pass@host:port/db?sslmode=require
```

### Issue: "Too many connections"
**Solution:**
- Use connection pooler (port 6543) instead of direct connection
- Close unused database connections in your code

### Issue: "Permission denied"
**Solution:**
- Verify your password is correct
- Check if user has proper permissions in Supabase dashboard

---

## Next Steps

✅ Supabase database created and configured
✅ Data migrated from local PostgreSQL
✅ Application updated to use Supabase
✅ Portable launcher created
✅ Security configured

**You can now:**
1. Access your portfolio from any device
2. No need for Docker Desktop
3. Automatic cloud backups
4. Free forever (within limits)

**Want to go further?**
- Set up authentication (Supabase Auth)
- Add email notifications
- Create mobile app
- Enable real-time subscriptions

---

## Support & Resources

- **Supabase Docs**: https://supabase.com/docs
- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **Project Issues**: Contact your developer

**Need Help?** 
Check the troubleshooting section or review Supabase community forums.
