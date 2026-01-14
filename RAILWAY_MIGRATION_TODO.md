# Railway Backend Migration - Todo List

**Goal:** Deploy Portfolio Analyzer backend to Railway for 24/7 automatic daily updates  
**Started:** 2026-01-14  
**Status:** 🟡 Not Started

---

## 📋 Phase 1: Prepare Codebase (Estimated: 30 minutes)

### 1.1 Create Cloud Dependencies File
- [ ] Create `requirements-cloud.txt` in project root
- [ ] Copy from `requirements.txt` but exclude:
  - `selenium`
  - `webdriver-manager`
  - `streamlit`
  - `plotly`
- [ ] Final cloud requirements:
  ```
  fastapi
  uvicorn[standard]
  sqlalchemy
  psycopg2-binary
  alembic
  python-dotenv
  requests
  pandas
  pydantic
  pydantic-settings
  beautifulsoup4
  lxml
  supabase
  ```

### 1.2 Create Railway Configuration Files
- [ ] Create `Procfile` in project root:
  ```
  web: uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
  ```
- [ ] Create `runtime.txt` in project root:
  ```
  python-3.13.1
  ```
- [ ] Create `.railwayignore` in project root:
  ```
  .venv/
  ui/
  mobile/
  tests/
  archive/
  mobile_builds/
  data/
  docs/
  *.md
  *.bat
  *.ps1
  .git/
  ```

### 1.3 Modify ETL for Cloud Environment
- [ ] Open `backend/app/etl/fetch_wealth_automated.py`
- [ ] Add at top of file (after imports):
  ```python
  import os
  
  # Detect cloud environment
  IS_CLOUD = os.getenv('RAILWAY_ENVIRONMENT') == 'production'
  ```
- [ ] Modify `HorizontPensionFetcher.fetch_and_save()`:
  ```python
  def fetch_and_save(self):
      """Fetch Horizont pension balance and save to database"""
      if IS_CLOUD:
          print("  ⚠ Skipping Horizont fetch in cloud environment (Selenium not available)")
          return False
      
      if not self.username or not self.password:
          print("  ⚠ Horizont credentials not found in .env - skipping")
          return False
      # ... rest of method
  ```
- [ ] Modify `AlfaPensionFetcher.fetch_and_save()` with same IS_CLOUD check
- [ ] Save file

### 1.4 Test Cloud Mode Locally
- [ ] Open terminal with venv activated
- [ ] Run: `$env:RAILWAY_ENVIRONMENT="production" ; python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000`
- [ ] Test endpoint: `http://localhost:8000/`
- [ ] Trigger ETL: `POST http://localhost:8000/api/updates/trigger-daily-update`
- [ ] Verify ETL runs without Selenium errors
- [ ] Verify Steps 1-4 and 6 complete (Step 5 skipped gracefully)
- [ ] Stop server (Ctrl+C)

### 1.5 Commit Changes to Git
- [ ] Stage files: `git add requirements-cloud.txt Procfile runtime.txt .railwayignore backend/app/etl/fetch_wealth_automated.py`
- [ ] Commit: `git commit -m "feat: Prepare backend for Railway cloud deployment"`
- [ ] Push: `git push origin main`

---

## 🚀 Phase 2: Railway Account Setup (Estimated: 10 minutes)

### 2.1 Create Railway Account
- [ ] Go to https://railway.app
- [ ] Click "Start a New Project"
- [ ] Sign up with GitHub account
- [ ] Authorize Railway to access GitHub

### 2.2 Connect GitHub Repository
- [ ] In Railway dashboard, click "New Project"
- [ ] Select "Deploy from GitHub repo"
- [ ] Find "portfolio-analyzer-supabase" repository
- [ ] Click "Deploy Now"
- [ ] Wait for initial detection (Railway will scan for Python project)

---

## ⚙️ Phase 3: Configure Railway Project (Estimated: 15 minutes)

### 3.1 Project Settings
- [ ] In Railway dashboard, go to project settings
- [ ] Set **Project Name**: "Portfolio Analyzer Backend"
- [ ] Set **Root Directory**: Leave empty (auto-detect)
- [ ] Set **Build Command**: `pip install -r requirements-cloud.txt`
- [ ] Set **Start Command**: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`

### 3.2 Environment Variables
- [ ] Click "Variables" tab
- [ ] Add each variable one by one:

**Database & API:**
```
DATABASE_URL=postgresql://postgres:Clobufclobuf01#@db.hrlzrirsvifxsnccxvsa.supabase.co:5432/postgres
MNB_API_URL=https://www.mnb.hu/arfolyamok.asmx
API_HOST=0.0.0.0
API_PORT=8000
```

**Supabase:**
```
SUPABASE_URL=https://hrlzrirsvifxsnccxvsa.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhybHpyaXJzdmlmeHNuY2N4dnNhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ5NDQzMTcsImV4cCI6MjA4MDUyMDMxN30.IAhjGmpcNA9KIi6fSTIPauVVNTIRSb8jBNCJTpmHodA
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhybHpyaXJzdmlmeHNuY2N4dnNhIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDk0NDMxNywiZXhwIjoyMDgwNTIwMzE3fQ.vLI8kZmCRnSSqP-yiRYBwz5rYqhNnrGCOJYKR2BLKk4
```

**Credentials (Stored but unused in cloud):**
```
HORIZONT_USERNAME=axis3000@gmail.com
HORIZONT_PASSWORD=Clobufclobuf01#
ALFA_USERNAME=12266379
ALFA_PASSWORD=Mobilemobile01
```

**Cloud Environment Flag:**
```
RAILWAY_ENVIRONMENT=production
```

**Database Pool (Optional):**
```
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10
```

### 3.3 Deploy
- [ ] Click "Deploy" button
- [ ] Wait for build to complete (~3-5 minutes)
- [ ] Check logs for successful startup
- [ ] Look for: "Application startup complete"

### 3.4 Get Public URL
- [ ] In Railway dashboard, go to "Settings"
- [ ] Click "Generate Domain"
- [ ] Copy the public URL (e.g., `portfolio-analyzer-production.up.railway.app`)
- [ ] **Save this URL** - you'll need it for next steps

---

## ✅ Phase 4: Verify Deployment (Estimated: 10 minutes)

### 4.1 Test Backend Health
- [ ] Open browser to: `https://YOUR_RAILWAY_URL.railway.app/`
- [ ] Should see: `{"message": "Portfolio Analyzer API", "version": "1.0"}`
- [ ] Test status endpoint: `https://YOUR_RAILWAY_URL.railway.app/api/updates/status`
- [ ] Should see: `{"is_running": false, "last_started": null, ...}`

### 4.2 Test Manual ETL Trigger
- [ ] Use Postman or curl to test:
  ```bash
  curl -X POST https://YOUR_RAILWAY_URL.railway.app/api/updates/trigger-daily-update
  ```
- [ ] Should return: `{"status": "ETL pipeline started", "timestamp": "..."}`
- [ ] Wait 60 seconds
- [ ] Check status again: `GET https://YOUR_RAILWAY_URL.railway.app/api/updates/status`
- [ ] Should see: `"last_completed": "..."`

### 4.3 Verify Database Updates
- [ ] Open Supabase dashboard
- [ ] Go to Table Editor > `total_wealth_snapshots`
- [ ] Check latest record has today's date
- [ ] Verify `net_wealth_huf` value looks correct

### 4.4 Check Railway Logs
- [ ] In Railway dashboard, click "View Logs"
- [ ] Look for ETL execution logs:
  ```
  Step 1: Fetching FX rates...
  Step 2: Fetching instrument prices...
  Step 3: Calculating portfolio values...
  Step 4: Copying static wealth values...
  Step 5: Fetching automated wealth values...
    ⚠ Skipping Horizont fetch in cloud environment
    ⚠ Skipping Alfa fetch in cloud environment
  Step 6: Creating total wealth snapshot...
  ✅ Snapshot saved: 2026-01-14 - Net Wealth: 189,612,604 HUF
  ETL Complete!
  ```
- [ ] Verify no errors (warnings for Selenium skip are OK)

---

## 🔗 Phase 5: Update Mobile App (Estimated: 5 minutes)

### 5.1 Update Flutter App Configuration
- [ ] Open `mobile/lib/services/daily_update_service.dart`
- [ ] Update line ~16:
  ```dart
  static const String _remoteBackendUrl = "https://YOUR_RAILWAY_URL.railway.app";
  ```
- [ ] Update line ~19:
  ```dart
  static bool useRemoteBackend = true; // Changed from false
  ```
- [ ] Save file

### 5.2 Test Mobile App
- [ ] Run Flutter app: `flutter run -d chrome`
- [ ] Go to Trends screen
- [ ] Click cloud button (☁️)
- [ ] Confirm dialog
- [ ] Watch status updates appear every 5 seconds
- [ ] Wait for green success message
- [ ] Verify data refreshes automatically

### 5.3 Commit Mobile Changes
- [ ] Stage: `git add mobile/lib/services/daily_update_service.dart`
- [ ] Commit: `git commit -m "feat: Update mobile app to use Railway backend URL"`
- [ ] Push: `git push origin main`

### 5.4 Rebuild Mobile APK (Optional)
- [ ] Run: `flutter build apk --release`
- [ ] Copy APK: `Copy-Item mobile\build\app\outputs\flutter-apk\app-release.apk mobile_builds\PortfolioAnalyzer-v1.0.2-railway.apk`
- [ ] Distribute new APK to Android devices

---

## 🔄 Phase 6: Configure Automatic Updates (Estimated: 10 minutes)

### 6.1 Remove Old pg_cron Job
- [ ] Open Supabase SQL Editor
- [ ] Run:
  ```sql
  -- Remove local network job
  SELECT cron.unschedule('daily-portfolio-update-7am');
  ```

### 6.2 Create New Railway pg_cron Job
- [ ] In Supabase SQL Editor, run:
  ```sql
  SELECT cron.schedule(
    'daily-portfolio-update-railway',
    '0 7 * * *',  -- 7 AM UTC daily
    $$SELECT http.post(
      'https://YOUR_RAILWAY_URL.railway.app/api/updates/trigger-daily-update',
      '{}'::json,
      'application/json'
    ) AS request;$$
  );
  ```
- [ ] **Replace `YOUR_RAILWAY_URL`** with actual Railway URL

### 6.3 Verify Job Created
- [ ] Run in Supabase SQL Editor:
  ```sql
  SELECT jobid, schedule, command, active 
  FROM cron.job 
  WHERE command LIKE '%railway%';
  ```
- [ ] Should see 1 row with your Railway URL
- [ ] Verify `active = true`

---

## 🎯 Phase 7: Final Testing (Estimated: 15 minutes)

### 7.1 Test Complete Workflow
- [ ] Wait for next day at 7 AM UTC (or manually trigger)
- [ ] Check Railway logs at 7:05 AM UTC
- [ ] Should see ETL execution logs
- [ ] Verify Supabase database updated
- [ ] Open mobile app
- [ ] Check Trends screen shows new data

### 7.2 Monitor First Week
- [ ] Day 1: Check Railway logs after 7 AM UTC
- [ ] Day 2: Verify pg_cron triggered correctly
- [ ] Day 3: Check Railway billing (should be $0)
- [ ] Day 7: Verify 7 consecutive successful runs

### 7.3 Stress Test
- [ ] Manually trigger ETL 3 times in a row
- [ ] Verify Railway handles concurrent requests
- [ ] Check database for 3 new snapshots
- [ ] Verify mobile app shows latest data

---

## 📊 Success Criteria Checklist

- [ ] ✅ Railway backend running 24/7
- [ ] ✅ Public HTTPS URL accessible
- [ ] ✅ Mobile app connects to Railway (not local PC)
- [ ] ✅ ETL runs successfully without Selenium errors
- [ ] ✅ Step 5 (pension scraping) skipped gracefully
- [ ] ✅ Steps 1-4 and 6 complete successfully
- [ ] ✅ Supabase database updates daily
- [ ] ✅ pg_cron job triggers at 7 AM UTC
- [ ] ✅ Mobile app shows real-time status updates
- [ ] ✅ Railway cost: $0 (within free tier)
- [ ] ✅ No backend dependency on local PC
- [ ] ✅ System works when PC is off

---

## 🆘 Troubleshooting Guide

### Issue: Railway build fails
**Symptoms:** Red X in Railway dashboard, build logs show errors  
**Solutions:**
1. Check `requirements-cloud.txt` has correct package names
2. Verify `Procfile` syntax is correct (no extra spaces)
3. Check Railway build logs for specific error message
4. Ensure Python version 3.13 is specified in `runtime.txt`

### Issue: "Application startup complete" but endpoints don't work
**Symptoms:** Railway shows running, but URLs return 502/504  
**Solutions:**
1. Verify `$PORT` variable is used in start command
2. Check `API_HOST=0.0.0.0` in environment variables
3. Ensure Railway domain is generated (Settings > Generate Domain)
4. Wait 2-3 minutes after deployment for DNS propagation

### Issue: ETL crashes on Step 5
**Symptoms:** Logs show import errors or webdriver errors  
**Solutions:**
1. Verify `RAILWAY_ENVIRONMENT=production` is set
2. Check `fetch_wealth_automated.py` has IS_CLOUD checks
3. Ensure `requirements-cloud.txt` doesn't include selenium
4. Review Railway logs for exact error message

### Issue: pg_cron job not triggering
**Symptoms:** No Railway logs at 7 AM UTC  
**Solutions:**
1. Check job exists: `SELECT * FROM cron.job;`
2. Verify URL in cron command is correct
3. Check job history: `SELECT * FROM cron.job_run_details ORDER BY start_time DESC LIMIT 5;`
4. Ensure Railway URL is HTTPS (not HTTP)
5. Test manual curl to verify endpoint works

### Issue: Mobile app can't connect to Railway
**Symptoms:** "Backend not responding" error  
**Solutions:**
1. Verify `useRemoteBackend = true`
2. Check Railway URL has HTTPS
3. Test URL in browser first
4. Ensure Railway app is not sleeping (check Railway dashboard)
5. Verify no typos in URL string

### Issue: Railway app keeps sleeping
**Symptoms:** First request takes 10+ seconds  
**Solutions:**
1. This is normal on free tier (sleeps after 1 hour inactivity)
2. Upgrade to Hobby plan ($5/month) for always-on
3. Set up a keep-alive ping every 30 minutes (optional)

---

## 💰 Cost Tracking

**Railway Free Tier:**
- $5 credit per month (auto-renews)
- Sufficient for daily ETL + mobile app requests
- Estimated usage: ~$1-2/month

**Current Status:**
- [ ] Week 1: $_____ used
- [ ] Week 2: $_____ used
- [ ] Week 3: $_____ used
- [ ] Week 4: $_____ used
- [ ] **Total Month 1**: $_____ (Target: < $5)

**If exceeding free tier:**
- [ ] Consider Hobby plan: $5/month for 8GB RAM, no sleep
- [ ] Or optimize: reduce ETL frequency, batch requests

---

## 📝 Post-Deployment Notes

### What Works in Cloud:
✅ All API endpoints  
✅ Portfolio calculations  
✅ FX rate fetching (MNB API)  
✅ Manual price overrides  
✅ Wealth snapshot generation  
✅ Static wealth value copying  
✅ Daily automatic updates via pg_cron  
✅ Mobile app remote access  

### What Requires Local PC:
❌ Horizont pension scraping (Selenium)  
❌ Alfa pension scraping (Selenium)  

**Workaround:**
- Keep desktop app for monthly pension updates
- Run "Daily Update" button in Streamlit UI
- Desktop app has full Selenium support

### Maintenance Schedule:
- **Daily:** Railway auto-updates at 7 AM UTC (no action needed)
- **Weekly:** Check Railway logs for errors
- **Monthly:** Run desktop app for pension scraping
- **Quarterly:** Review Railway billing

---

## 🎉 Completion Checklist

- [ ] All Phase 1-7 tasks completed
- [ ] Railway backend deployed and stable
- [ ] Mobile app using Railway URL
- [ ] pg_cron scheduling working
- [ ] First week of automated updates successful
- [ ] Cost within free tier ($0-$5)
- [ ] Documentation updated
- [ ] Team notified of new architecture

**Date Completed:** _______________  
**Railway URL:** _______________  
**Total Time:** _____ hours  

---

**Next Steps After Completion:**
1. Monitor daily for first month
2. Consider Hobby plan if needed ($5/month)
3. Optional: Set up monitoring/alerting
4. Optional: Deploy frontend to Vercel/Netlify
5. Optional: Add Chrome buildpack for full Selenium support

---

**Created:** 2026-01-14  
**Last Updated:** 2026-01-14  
**Status:** 🟡 Ready to Start
