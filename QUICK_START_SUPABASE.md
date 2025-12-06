# 🚀 Quick Start - Supabase Edition

## Switch from Local Docker to Cloud Supabase in 3 Steps!

### **Step 1: Export Your Data (5 minutes)**
```powershell
# Run the export script
.\export_for_supabase.ps1
```
This creates `exports/portfolio_export_for_supabase_TIMESTAMP_cleaned.sql`

---

### **Step 2: Set Up Supabase (10 minutes)**

1. **Create Account**: Go to https://supabase.com and sign up (free)

2. **Create Project**:
   - Click "New Project"
   - Name: `portfolio-analyzer`
   - Generate strong password (SAVE IT!)
   - Region: Choose closest to you
   - Wait 2-3 minutes

3. **Import Your Data**:
   - Click "SQL Editor" in left sidebar
   - Click "New query"
   - Open `exports/portfolio_export_for_supabase_*_cleaned.sql`
   - Copy entire contents
   - Paste into SQL Editor
   - Click "Run"
   - Wait for "Success" message

4. **Get Connection String**:
   - Click "Settings" → "Database"
   - Find "Connection string" section
   - Select "URI"
   - Click "Copy"
   - You'll get something like:
     ```
     postgresql://postgres.abcd1234:PASSWORD@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
     ```

---

### **Step 3: Configure & Run (2 minutes)**

1. **Create .env file**:
   ```powershell
   # Copy template
   Copy-Item .env.example .env
   
   # Edit .env in Notepad
   notepad .env
   ```

2. **Add your Supabase connection**:
   ```env
   DATABASE_URL=postgresql://postgres.YOUR_PROJECT:YOUR_PASSWORD@YOUR_HOST:6543/postgres
   ```
   (Paste the connection string from Step 2.4)

3. **Start the app**:
   ```powershell
   .\start_portfolio_supabase.ps1
   ```

That's it! 🎉

---

## What You Get

✅ **Cloud Database** - Access from anywhere
✅ **No Docker** - Simpler setup
✅ **Auto Backups** - Supabase backs up daily
✅ **Free Forever** - 500MB database on free tier
✅ **Same Features** - Everything works exactly the same

---

## Daily Usage

### Start the App:
```powershell
.\start_portfolio_supabase.ps1
```

Browser opens automatically to: http://localhost:8501

### Backup Your Data (Optional):
```powershell
.\backup_supabase.ps1
```

Creates timestamped backup in `backups/` folder

---

## Access From Another Computer

1. Copy these files to new computer:
   - `.env` (your connection settings)
   - `start_portfolio_supabase.ps1`
   - `ui/` folder
   - `backend/` folder

2. Install Python 3.13

3. Install dependencies:
   ```powershell
   cd backend
   pip install -r requirements.txt
   
   cd ../ui
   pip install -r requirements.txt
   ```

4. Run:
   ```powershell
   .\start_portfolio_supabase.ps1
   ```

Your data is in the cloud, so it's the same everywhere!

---

## Troubleshooting

### "Cannot connect to database"
- Check internet connection
- Verify DATABASE_URL in .env is correct
- Ensure Supabase project is active (not paused)

### "Module not found" errors
```powershell
cd backend
pip install -r requirements.txt

cd ../ui
pip install -r requirements.txt
```

### "Port already in use"
Another instance is running. Close it first, or restart your computer.

### Need more help?
See `SUPABASE_SETUP_GUIDE.md` for detailed instructions.

---

## What Happened to Docker?

You don't need Docker Desktop anymore! 🎉

Your database is now in Supabase cloud, so:
- ❌ No more `docker-compose up`
- ❌ No more Docker Desktop
- ❌ No more local database
- ✅ Just double-click `start_portfolio_supabase.ps1`

Your old `start_portfolio_analyzer.ps1` won't be needed anymore.

---

## Free Tier Limits

Supabase Free Tier includes:
- 💾 500MB database storage
- 📊 2GB bandwidth/month
- 🔄 7 days of backups
- 🔒 SSL encryption
- ⚡ Connection pooling

This is more than enough for personal portfolio tracking!

If you need more, Pro tier is $25/month with unlimited everything.

---

## Next Steps

Once you're comfortable:
1. Set up weekly backups (Task Scheduler)
2. Add authentication for remote access
3. Access from mobile devices
4. Share with family (create separate portfolios)

Enjoy your cloud-connected Portfolio Analyzer! 💰✨
