# 🆘 Railway Deployment Crash - Troubleshooting

**Symptom:** Deployment says "Successful" but then service crashes/restarts

---

## Most Common Causes & Fixes

### Issue #1: Database Connection Failing
**Error logs will show:**
```
ERROR: could not translate host name "db.hrlzrirsvifxsnccxvsa.supabase.co" to address
or
could not connect to server: Connection timed out
```

**Fix:**
- ✅ Verify DATABASE_URL is EXACT (check for typos, spaces)
- ✅ Verify Supabase project is active (check Supabase dashboard)
- ✅ Verify port 5432 is accessible from Railway IPs
- Try: Add variable `DATABASE_ECHO=false` to reduce noise

### Issue #2: Missing Environment Variables
**Error logs will show:**
```
KeyError: 'DATABASE_URL'
or
'NoneType' object has no attribute...
```

**Fix:**
- ✅ Check Railway "Variables" tab - all 14 variables must be there
- ✅ No variable should be empty
- ✅ Go back to `RAILWAY_VARIABLES_HELPER.md` and verify each one
- ✅ After adding missing variables: **Redeploy** (Trigger Deploy button)

### Issue #3: Import/Syntax Errors
**Error logs will show:**
```
ModuleNotFoundError: No module named 'xyz'
or
SyntaxError: invalid syntax
```

**Fix:**
- ✅ Check requirements-cloud.txt has all needed packages
- ✅ Verify Procfile syntax is correct: `web: uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
- ✅ Clear build cache: Railway Settings > "Clear Build Cache" > Redeploy

### Issue #4: Startup Event Failing
**Error logs will show:**
```
ℹ Loan reductions: Loan reductions already applied this month
ERROR during startup...
or
Application startup failed
```

**Fix:**
- This might be the loan reduction check
- The code might be trying to query database before it's connected
- Check if Supabase connection test is working first

---

## Step-by-Step Investigation

### 1. Check the Logs
**In Railway Dashboard:**
1. Click your service card
2. Click "Deployments" tab
3. Find your latest deployment
4. Click "View Logs"
5. Scroll to the bottom - look for error messages
6. **Screenshot or copy the error** and share it

### 2. Check Variables
**In Railway Dashboard:**
1. Click your service
2. Go to "Variables" tab
3. Verify you see 14 variables (count them)
4. Make sure none are empty
5. Check critical ones:
   - `DATABASE_URL` - should be long string
   - `RAILWAY_ENVIRONMENT` - should be `production`
   - `SUPABASE_URL` - should start with `https://`

### 3. Test Database Connection Locally
**On your PC, open PowerShell:**
```powershell
cd "c:\Users\SzalmaNB1\Downloads\cabeceo\visual studio\Portfolio Analyzer"
.\.venv\Scripts\Activate.ps1
python -c "from sqlalchemy import create_engine, text; import os; from dotenv import load_dotenv; load_dotenv(); engine = create_engine(os.getenv('DATABASE_URL')); conn = engine.connect(); result = conn.execute(text('SELECT 1')); print('✓ Database connected!')"
```

If this works locally, it means:
- DATABASE_URL is correct
- Supabase is reachable
- Issue is in Railway config

### 4. Common Quick Fixes
```
Try these in order:
1. Redeploy (click "Trigger Deploy")
2. Clear build cache + Redeploy
3. Check all 14 variables are present
4. Verify DATABASE_URL has no spaces before/after
5. Restart service: Settings > "Restart" button
```

---

## What to Share

**Please provide:**
1. Last 20 lines of Railway logs (copy/paste or screenshot)
2. Count of variables in "Variables" tab
3. Whether it crashes immediately or after 5+ seconds

**Then I can give you exact fix!**

---

## If Still Stuck

**Option A: Rollback and Fix Code**
- I can disable the startup event check
- Redeploy simpler version
- Get it stable first, then add features back

**Option B: Deploy Directly from Here**
- You provide Railway token
- I can deploy using CLI (automated)

---

**Next Steps:**
1. Check Railway logs
2. Share the error message
3. I'll give you exact fix
