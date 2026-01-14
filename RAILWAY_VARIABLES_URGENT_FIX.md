# URGENT FIX: Railway Variables Not Saved

**Error:** `DATABASE_URL` field required - variables not in Railway environment

---

## Quick Fix (2 minutes)

1. **Open Railway Dashboard**: https://railway.app
2. **Click your project → Your service**
3. **Click "Variables" tab**
4. **Check if DATABASE_URL is there:**
   - If YES and visible → Keep it
   - If NO or empty → **Add it now**

---

## Add DATABASE_URL (Copy & Paste)

1. Click **"Add Variable"** button
2. In the **Key** field, paste: `DATABASE_URL`
3. In the **Value** field, paste:
   ```
   postgresql://postgres:Clobufclobuf01#@db.hrlzrirsvifxsnccxvsa.supabase.co:5432/postgres
   ```
4. Click **Save**
5. Click **"Trigger Deploy"** button

---

## Critical: Add ALL Variables Again

Go through this checklist and add EACH one:

```
☐ DATABASE_URL = postgresql://postgres:Clobufclobuf01#@db.hrlzrirsvifxsnccxvsa.supabase.co:5432/postgres
☐ SUPABASE_URL = https://hrlzrirsvifxsnccxvsa.supabase.co
☐ SUPABASE_ANON_KEY = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhybHpyaXJzdmlmeHNuY2N4dnNhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ5NDQzMTcsImV4cCI6MjA4MDUyMDMxN30.IAhjGmpcNA9KIi6fSTIPauVVNTIRSb8jBNCJTpmHodA
☐ SUPABASE_SERVICE_KEY = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhybHpyaXJzdmlmeHNuY2N4dnNhIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDk0NDMxNywiZXhwIjoyMDgwNTIwMzE3fQ.vLI8kZmCRnSSqP-yiRYBwz5rYqhNnrGCOJYKR2BLKk4
☐ MNB_API_URL = https://www.mnb.hu/arfolyamok.asmx
☐ API_HOST = 0.0.0.0
☐ API_PORT = 8000
☐ HORIZONT_USERNAME = axis3000@gmail.com
☐ HORIZONT_PASSWORD = Clobufclobuf01#
☐ ALFA_USERNAME = 12266379
☐ ALFA_PASSWORD = Mobilemobile01
☐ RAILWAY_ENVIRONMENT = production
☐ DATABASE_POOL_SIZE = 5
☐ DATABASE_MAX_OVERFLOW = 10
```

---

## After Adding Variables

1. Click **"Trigger Deploy"** button
2. Wait 3-5 minutes for build
3. Should now show "online" and stay online
4. Check logs - should show no DATABASE_URL error

---

## If Still Crashing

Share screenshot of:
1. Railway Variables tab (all variables visible)
2. Railway Deployments logs

---

**Do this now and let me know when done!**
