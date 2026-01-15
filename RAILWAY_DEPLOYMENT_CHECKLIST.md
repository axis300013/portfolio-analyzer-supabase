# Railway Deployment Checklist - Portfolio Analyzer Backend

## ⚠️ CRITICAL BLOCKERS IDENTIFIED

### 🚫 **Selenium/Chrome Dependency Issue**
Your ETL pipeline uses **Selenium with Chrome** for web scraping (Horizont & Alfa pension portals). This is a **major blocker** for Railway:

**Problem:**
- Railway containers don't have Chrome browser installed by default
- Selenium requires Chrome + ChromeDriver to work
- Headless Chrome is resource-intensive in cloud environments

**Impact:**
- ETL Step 5 (Fetch automated wealth values) will **FAIL** in Railway
- Pension data won't update automatically

**Solutions:**

#### Option A: Remove Selenium Dependencies (Recommended for Railway)
- Skip automated pension fetching in cloud
- Continue manual trigger from local PC when needed
- Update ETL to gracefully skip pension steps in cloud

#### Option B: Use Railway with Chrome Buildpack (Complex)
- Requires custom Dockerfile with Chrome installation
- ~500MB additional container size
- Possible but adds complexity and cost

#### Option C: Split Architecture (Hybrid)
- Deploy API/database logic to Railway
- Keep Selenium scraping on local PC
- Railway backend calls local endpoint for pension data

---

## 📋 PRE-DEPLOYMENT CHECKLIST

### 1. **Dependencies Analysis** ✅

**Current requirements.txt:**
```
fastapi ✅ (Railway compatible)
uvicorn[standard] ✅ (Railway compatible)
sqlalchemy ✅ (Railway compatible)
psycopg2-binary ✅ (Railway compatible)
alembic ✅ (Railway compatible)
python-dotenv ✅ (Railway compatible)
requests ✅ (Railway compatible)
pandas ✅ (Railway compatible)
pydantic ✅ (Railway compatible)
pydantic-settings ✅ (Railway compatible)
beautifulsoup4 ✅ (Railway compatible)
lxml ✅ (Railway compatible)
selenium ❌ (REQUIRES CHROME - NOT AVAILABLE)
webdriver-manager ❌ (REQUIRES CHROME - NOT AVAILABLE)
supabase ✅ (Railway compatible)
streamlit ❌ (NOT NEEDED - Only for desktop UI)
plotly ❌ (NOT NEEDED - Only for desktop UI)
```

**Action Required:**
- [ ] Create `requirements-cloud.txt` without Selenium/Streamlit
- [ ] Modify ETL to gracefully skip Selenium steps in cloud

---

### 2. **Environment Variables Required** 📝

**Must be set in Railway dashboard:**

```bash
# Database (Already using Supabase - OK)
DATABASE_URL=postgresql://postgres:PASSWORD@db.hrlzrirsvifxsnccxvsa.supabase.co:5432/postgres

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# MNB API (Exchange rates)
MNB_API_URL=https://www.mnb.hu/arfolyamok.asmx

# Supabase Configuration
SUPABASE_URL=https://hrlzrirsvifxsnccxvsa.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# ⚠️ SENSITIVE - Do NOT commit to git
HORIZONT_USERNAME=axis3000@gmail.com
HORIZONT_PASSWORD=Clobufclobuf01#
ALFA_USERNAME=12266379
ALFA_PASSWORD=Mobilemobile01

# Pool settings (Optional - defaults OK)
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10
```

**⚠️ Security Note:**
- Railway environment variables are encrypted
- Your .env file should be in `.gitignore` (already is)
- Never commit credentials to GitHub

---

### 3. **Files to Create for Railway**

#### A. `Procfile` (Railway startup command)
```yaml
web: uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
```

#### B. `runtime.txt` (Python version)
```
python-3.13.1
```

#### C. `requirements-cloud.txt` (Cloud dependencies)
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

#### D. `.railwayignore` (Exclude unnecessary files)
```
.venv/
ui/
mobile/
tests/
*.md
*.bat
*.ps1
.git/
archive/
mobile_builds/
data/
docs/
```

---

## 🚀 RAILWAY DEPLOYMENT STEPS

### Phase 1: Prepare Codebase

- [ ] **1.1** Create `requirements-cloud.txt` (without Selenium)
- [ ] **1.2** Create `Procfile` with Railway startup command
- [ ] **1.3** Create `runtime.txt` with Python 3.13
- [ ] **1.4** Create `.railwayignore` to exclude UI/mobile files
- [ ] **1.5** Modify `backend/app/etl/fetch_wealth_automated.py`:
  - Add environment check: `IS_CLOUD = os.getenv('RAILWAY_ENVIRONMENT') == 'production'`
  - Skip Selenium fetchers if `IS_CLOUD == True`
  - Return gracefully without error
- [ ] **1.6** Test backend locally with `IS_CLOUD=True` to ensure no crashes
- [ ] **1.7** Update pg_cron SQL script with Railway URL (after deployment)

---

### Phase 2: Railway Account Setup

- [ ] **2.1** Go to [railway.app](https://railway.app) and sign up
- [ ] **2.2** Choose "Start a New Project"
- [ ] **2.3** Select "Deploy from GitHub repo"
- [ ] **2.4** Connect GitHub account and authorize Railway
- [ ] **2.5** Select "Portfolio Analyzer" repository

---

### Phase 3: Configure Railway Project

- [ ] **3.1** Railway will auto-detect Python project
- [ ] **3.2** Set **Root Directory**: Leave empty (Railway scans for Procfile)
- [ ] **3.3** Set **Start Command**: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
- [ ] **3.4** Set **Install Command**: `pip install -r requirements-cloud.txt`
- [ ] **3.5** Click "Variables" tab
- [ ] **3.6** Add all environment variables from `.env`:
  ```
  DATABASE_URL=postgresql://postgres:...
  SUPABASE_URL=https://hrlzrirsvifxsnccxvsa.supabase.co
  SUPABASE_ANON_KEY=eyJhbGci...
  SUPABASE_SERVICE_KEY=eyJhbGci...
  MNB_API_URL=https://www.mnb.hu/arfolyamok.asmx
  HORIZONT_USERNAME=axis3000@gmail.com
  HORIZONT_PASSWORD=Clobufclobuf01#
  ALFA_USERNAME=12266379
  ALFA_PASSWORD=Mobilemobile01
  RAILWAY_ENVIRONMENT=production
  ```
- [ ] **3.7** Click "Deploy"

---

### Phase 4: Post-Deployment Configuration

- [ ] **4.1** Wait for Railway deployment to complete (~5 minutes)
- [ ] **4.2** Copy Railway public URL (e.g., `https://portfolio-analyzer-production.up.railway.app`)
- [ ] **4.3** Test backend health:
  ```bash
  curl https://YOUR_RAILWAY_URL.railway.app/
  ```
  Should return: `{"message": "Portfolio Analyzer API", "version": "1.0"}`

- [ ] **4.4** Update Supabase pg_cron job:
  ```sql
  -- Remove old local job
  SELECT cron.unschedule('daily-portfolio-update-7am');
  
  -- Add new Railway job
  SELECT cron.schedule(
    'daily-portfolio-update-railway',
    '0 7 * * *',
    $$SELECT http.post(
      'https://YOUR_RAILWAY_URL.railway.app/api/updates/trigger-daily-update',
      '{}'::json,
      'application/json'
    ) AS request;$$
  );
  ```

- [ ] **4.5** Update mobile app `daily_update_service.dart`:
  ```dart
  static const String _remoteBackendUrl = "https://YOUR_RAILWAY_URL.railway.app";
  static bool useRemoteBackend = true; // Changed from false
  ```

- [ ] **4.6** Test manual trigger from mobile app
- [ ] **4.7** Verify pg_cron executes successfully tomorrow at 7 AM UTC
- [ ] **4.8** Monitor Railway logs for first automated run

---

## 🔍 TESTING CHECKLIST

### Local Testing (Before Railway)

- [ ] Run backend with `IS_CLOUD=True` environment variable
- [ ] Verify ETL skips Selenium steps gracefully
- [ ] Check all 6 ETL steps complete (except automated pension fetch)
- [ ] Test `/api/updates/trigger-daily-update` endpoint
- [ ] Test `/api/updates/status` endpoint
- [ ] Verify snapshot creation in Step 6

### Railway Testing (After Deployment)

- [ ] Verify Railway deployment succeeded (check build logs)
- [ ] Test root endpoint: `GET https://YOUR_URL.railway.app/`
- [ ] Test health check: `GET https://YOUR_URL.railway.app/api/updates/status`
- [ ] Test manual trigger: `POST https://YOUR_URL.railway.app/api/updates/trigger-daily-update`
- [ ] Check Railway logs for ETL execution (~60 seconds runtime)
- [ ] Verify Supabase database updated after ETL run
- [ ] Test mobile app with Railway URL (useRemoteBackend=true)

---

## 📊 COST ESTIMATE

**Railway Free Tier:**
- ✅ $5 free credit per month
- ✅ Unlimited projects
- ✅ 512 MB RAM
- ✅ 1 GB disk
- ✅ Automatic SSL/HTTPS
- ⚠️ Sleeps after 1 hour inactivity (startup delay)

**Expected Usage:**
- Daily ETL run: ~60 seconds/day = ~30 minutes/month
- Mobile app requests: Minimal (few KB per request)
- **Estimated cost: FREE** (well within $5 credit)

**Paid Tier (if needed):**
- $5/month Hobby plan
- No sleep (always-on)
- 8 GB RAM
- 100 GB disk

---

## ⚠️ KNOWN LIMITATIONS IN CLOUD

### What WILL Work:
✅ Manual trigger from mobile app  
✅ Automatic pg_cron scheduling  
✅ Portfolio calculations (Step 3)  
✅ FX rate fetching (Step 1)  
✅ Manual price overrides  
✅ Wealth snapshot generation (Step 6)  
✅ Static wealth value copying (Step 4)  

### What WON'T Work (Selenium Required):
❌ Automated Horizont pension fetching  
❌ Automated Alfa pension fetching  
❌ Any web scraping with Selenium  

**Workaround:**
- Keep desktop app running on PC for Selenium scraping
- Use "Daily Update" button in desktop app weekly/monthly
- Railway handles everything else automatically

---

## 🆘 TROUBLESHOOTING

### Issue: Railway deployment fails
**Solution:** Check Railway build logs for Python errors

### Issue: "Module not found" errors
**Solution:** Verify `requirements-cloud.txt` includes all imports

### Issue: Database connection fails
**Solution:** Check `DATABASE_URL` environment variable in Railway

### Issue: ETL crashes on Selenium step
**Solution:** Ensure `IS_CLOUD` check properly skips Selenium code

### Issue: pg_cron job not triggering
**Solution:** 
- Verify job exists: `SELECT * FROM cron.job;`
- Check execution history: `SELECT * FROM cron.job_run_details;`
- Ensure Railway URL is correct in cron command

### Issue: Mobile app can't reach Railway
**Solution:**
- Verify `useRemoteBackend = true`
- Check Railway URL has HTTPS (not HTTP)
- Test URL in browser first

---

## 🎯 SUCCESS CRITERIA

✅ Railway backend running and accessible  
✅ Mobile app can trigger ETL remotely  
✅ Supabase pg_cron runs daily at 7 AM UTC  
✅ ETL completes 5/6 steps (Selenium skipped gracefully)  
✅ Portfolio snapshots update automatically  
✅ Total cost: $0 (within free tier)  

---

## 📞 NEXT STEPS

**Ready to deploy?**

1. Start with Phase 1 (Prepare Codebase)
2. Commit code changes to GitHub
3. Follow Railway deployment steps
4. Test thoroughly before relying on automation

**Questions to answer before proceeding:**
- Do you want to deploy with Selenium disabled? (Recommended)
- Or attempt Chrome buildpack installation? (Complex)
- Keep desktop app for weekly Selenium updates? (Hybrid approach)

---

**Estimated Time:** 2-3 hours for full setup  
**Difficulty:** Medium (requires GitHub + Railway account)  
**Risk Level:** Low (can always rollback to local-only)  

---

## 📝 ADDITIONAL NOTES

- Railway provides automatic HTTPS certificates
- Deployments are automatic on git push (CI/CD)
- Railway dashboard shows real-time logs
- Environment variables can be changed without redeployment
- Railway has excellent Python support (no custom Dockerfile needed for basic FastAPI)

**Author:** AI Assistant  
**Created:** 2026-01-14  
**Status:** Ready for implementation
