# Railway Deployment Guide - Phases 2-3

**Current Status:** Codebase ready for Railway (Phase 1 ✅ complete)  
**Next Step:** Manual Railway setup required  
**Estimated Time:** 35 minutes for Phases 2-3

---

## 📋 Phase 2: Railway Account Setup (10 minutes)

### Step 1: Create Railway Account
1. Open browser: **https://railway.app**
2. Click "Start a New Project" button (top right)
3. Click "GitHub" to sign up with GitHub account
4. Authorize Railway to access your GitHub repos
5. ✅ Account created - you're now logged into Railway dashboard

### Step 2: Import Your Repository
1. In Railway dashboard, click **"New Project"** button
2. Select **"Deploy from GitHub repo"**
3. Search for: **`portfolio-analyzer-supabase`**
4. Click on your repository when it appears
5. Click **"Deploy Now"**
6. Wait 30 seconds - Railway will scan your project
7. ✅ Railway detected Python project and created the service

---

## ⚙️ Phase 3: Configure Railway Project (25 minutes)

### Step 3.1: Configure Build & Start Commands

1. **In Railway Dashboard:**
   - You should see a card showing "Service" with your repo name
   - Click on the service card to enter the settings

2. **Set Build Command:**
   - Look for "Build Command" field
   - Enter: `pip install -r requirements-cloud.txt`
   - Press Enter/Save

3. **Set Start Command:**
   - Look for "Start Command" field  
   - Enter: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
   - Press Enter/Save

4. **Python Version (Optional):**
   - Railway should auto-detect `runtime.txt`
   - It will use Python 3.13.1
   - You can verify in build logs later

### Step 3.2: Add Environment Variables

⚠️ **IMPORTANT:** Railway has a UI for variables. Do this carefully:

1. **In the service card, find "Variables" section**
2. **Click "Add Variable"** and enter each pair:

#### Database Configuration:
```
DATABASE_URL = postgresql://postgres:Clobufclobuf01#@db.hrlzrirsvifxsnccxvsa.supabase.co:5432/postgres
```

#### Supabase Configuration:
```
SUPABASE_URL = https://hrlzrirsvifxsnccxvsa.supabase.co
SUPABASE_ANON_KEY = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhybHpyaXJzdmlmeHNuY2N4dnNhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ5NDQzMTcsImV4cCI6MjA4MDUyMDMxN30.IAhjGmpcNA9KIi6fSTIPauVVNTIRSb8jBNCJTpmHodA
SUPABASE_SERVICE_KEY = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhybHpyaXJzdmlmeHNuY2N4dnNhIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDk0NDMxNywiZXhwIjoyMDgwNTIwMzE3fQ.vLI8kZmCRnSSqP-yiRYBwz5rYqhNnrGCOJYKR2BLKk4
```

#### API Configuration:
```
MNB_API_URL = https://www.mnb.hu/arfolyamok.asmx
API_HOST = 0.0.0.0
API_PORT = 8000
```

#### Credentials (Stored in cloud, unused):
```
HORIZONT_USERNAME = axis3000@gmail.com
HORIZONT_PASSWORD = Clobufclobuf01#
ALFA_USERNAME = 12266379
ALFA_PASSWORD = Mobilemobile01
```

#### Cloud Environment Flag:
```
RAILWAY_ENVIRONMENT = production
```

#### Optional Database Pool:
```
DATABASE_POOL_SIZE = 5
DATABASE_MAX_OVERFLOW = 10
```

**Total: 15 variables added**

### Step 3.3: Deploy

1. **After all variables are set:**
   - Look for a **"Deploy"** button (usually appears automatically)
   - OR click the service and look for a **"Trigger Deploy"** button
   - Click it to start deployment

2. **Monitor the build:**
   - You should see build logs appearing
   - Watch for:
     ```
     ✓ Building Docker image
     ✓ Dependencies installed from requirements-cloud.txt
     ✓ Application starting...
     INFO: Application startup complete
     ```
   - ⏱️ Build takes 3-5 minutes

3. **Check for errors:**
   - If build fails, click "View Logs" to see why
   - Common issues:
     - Typo in variable name
     - Missing DATABASE_URL
     - Invalid Python syntax

### Step 3.4: Generate Public URL

1. **After deployment completes:**
   - In the service card, look for "Settings" or "Domain" section
   - Click **"Generate Domain"** button
   - Railway will create a public URL like:
     ```
     portfolio-analyzer-xxxxxx.railway.app
     ```

2. **⭐ Save this URL - you'll need it for:**
   - Phase 4: Verification
   - Phase 5: Mobile app configuration
   - Phase 6: pg_cron setup

3. **Verify the domain:**
   - Copy the URL
   - Open in browser: `https://YOUR_RAILWAY_URL.railway.app/`
   - Should see: `{"message": "Portfolio Analyzer API", "version": "1.0"}`

---

## ✅ Phases 2-3 Completion Checklist

Before moving to Phase 4, verify:

- [ ] Railway account created and logged in
- [ ] GitHub repository connected to Railway
- [ ] Service card visible in Railway dashboard
- [ ] Build command set: `pip install -r requirements-cloud.txt`
- [ ] Start command set: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
- [ ] All 15 environment variables added
- [ ] Deployment triggered and completed (green checkmark)
- [ ] Public domain generated
- [ ] Root endpoint `/` returns JSON response
- [ ] **Railway URL saved:** `___________________________`

---

## 🆘 Troubleshooting Phases 2-3

### Build Fails: "pip install failed"
**Solution:**
- Check requirements-cloud.txt has all packages
- Verify no typos in variable names
- Clear Railway cache: Settings > Clear Build Cache > Rebuild

### Build Succeeds but Service Won't Start
**Solution:**
- Check Start Command syntax exactly matches: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
- Verify DATABASE_URL is complete (includes password and path)
- Check logs for import errors

### "Domain generation failed"
**Solution:**
- Wait 1-2 minutes after deployment completes
- Try generating domain again
- If still fails, restart the service

### Service crashes on startup
**Solution:**
- In Railway dashboard, click "View Logs"
- Look for error messages
- Most common: missing DATABASE_URL or SUPABASE_URL
- Add missing variable and re-deploy

---

## 📝 Next Steps After Phase 3

Once Phases 2-3 are complete:

1. **Move to Phase 4:** Verify deployment endpoints
2. **Move to Phase 5:** Update mobile app URL
3. **Move to Phase 6:** Set up pg_cron for automatic daily updates
4. **Move to Phase 7:** Final testing

---

**Status:** Awaiting Railway deployment  
**Last Updated:** 2026-01-14
