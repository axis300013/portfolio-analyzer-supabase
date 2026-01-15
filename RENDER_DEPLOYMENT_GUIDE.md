# Render.com Deployment Guide - Portfolio Analyzer Backend

## Overview
This guide will help you deploy the FastAPI backend to Render.com's free tier to solve Railway's IPv6 connectivity issue.

## Prerequisites
- GitHub account (code must be in a repository)
- Render.com account (free tier)
- Supabase database credentials

---

## Step 1: Prepare Repository

### 1.1 Create render.yaml (Build Configuration)
Already exists at root of project - Render will auto-detect it.

### 1.2 Verify requirements.txt
File exists with all dependencies.

### 1.3 Commit and Push to GitHub
```bash
git add .
git commit -m "Prepare for Render.com deployment"
git push origin main
```

---

## Step 2: Create Render Account & Connect GitHub

1. Go to https://render.com
2. Click **"Get Started for Free"**
3. Sign up with GitHub (easier integration)
4. Authorize Render to access your GitHub repositories

---

## Step 3: Create New Web Service

1. From Render Dashboard, click **"New +"** → **"Web Service"**
2. Connect your GitHub repository:
   - If first time: Click "Connect GitHub" and authorize
   - Search for: `Portfolio Analyzer` repository
   - Click **"Connect"**

---

## Step 4: Configure Web Service

### Basic Settings:
- **Name:** `portfolio-analyzer-backend` (or any name you prefer)
- **Region:** `Frankfurt (EU Central)` (closest to your Supabase)
- **Branch:** `main`
- **Root Directory:** Leave empty (root of repo)
- **Runtime:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`

### Instance Type:
- **Free** (select free tier)

---

## Step 5: Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"** for each:

```
DATABASE_URL=postgresql://postgres.hrlzrirsvifxsnccxvsa:Clobufclobuf01%2523@db.hrlzrirsvifxsnccxvsa.supabase.co:5432/postgres

SUPABASE_URL=https://hrlzrirsvifxsnccxvsa.supabase.co

SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhybHpyaXJzdmlmeHNuY2N4dnNhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzM5MjU3MjEsImV4cCI6MjA0OTUwMTcyMX0.XGu7Gs81fOgTcRHzSNp9u13H9_wWO3G2M02qgWbhU-A

RAILWAY_ENVIRONMENT=production

PORT=10000
```

**Note:** Render automatically sets `PORT` variable, but we include it for clarity.

---

## Step 6: Deploy

1. Click **"Create Web Service"**
2. Render will:
   - Clone your repository
   - Install dependencies (takes 2-3 minutes first time)
   - Start your application
3. Monitor deployment in the **Logs** tab

### Expected Output:
```
==> Building...
==> Installing dependencies
==> Starting application
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:10000
```

---

## Step 7: Test Deployment

### 7.1 Check Service URL
- Your service will be at: `https://portfolio-analyzer-backend.onrender.com`
- Test endpoint: `https://portfolio-analyzer-backend.onrender.com/`
- Should return: `{"message": "Portfolio Analyzer API", "version": "1.0"}`

### 7.2 Test Database Connection
- Open the URL in browser
- If it loads successfully, database connection works!

---

## Step 8: Update Mobile App

Update the Railway backend URL to Render URL in the mobile app:

**File:** `mobile/lib/services/supabase_service.dart`

Change line ~597 from:
```dart
final url = backendUrl ?? 'https://web-production-07ca1a.up.railway.app';
```

To:
```dart
final url = backendUrl ?? 'https://portfolio-analyzer-backend.onrender.com';
```

Then commit and test!

---

## Free Tier Limitations

⚠️ **Important Free Tier Restrictions:**
- **Spins down after 15 minutes of inactivity**
- **Cold start takes 30-60 seconds** on first request after sleep
- 750 hours/month free (plenty for personal use)
- No custom domain on free tier

### Cold Start Solution:
When you click "Run Daily Update" in mobile app:
- First request: May take 60 seconds (waking up server)
- Subsequent requests: Fast (< 1 second)
- Loading dialog already shows "This may take 1-2 minutes"

---

## Troubleshooting

### Issue: Build Failed
- Check Render logs for Python/dependency errors
- Verify `requirements.txt` has all packages
- Check Python version (Render uses 3.11 by default)

### Issue: App Crashes on Start
- Check environment variables are set correctly
- Verify DATABASE_URL password encoding (%2523)
- Check Render logs for specific error

### Issue: Database Connection Failed
- Verify Supabase credentials
- Check if Supabase is online
- Test connection from local machine first

### Issue: Cold Start Too Slow
- Upgrade to paid tier ($7/month) for always-on instance
- Or use a cron job / uptime monitor to ping every 10 minutes

---

## Monitoring & Maintenance

### View Logs:
- Render Dashboard → Your Service → **Logs** tab
- Real-time log streaming available

### Manual Redeploy:
- Click **"Manual Deploy"** → **"Deploy latest commit"**

### Check Health:
- Visit: `https://your-service.onrender.com/`
- Should return API info JSON

---

## Cost Comparison

| Feature | Railway (Crashed) | Render Free | Render Paid |
|---------|------------------|-------------|-------------|
| Price | $5/month | FREE | $7/month |
| Always On | Yes | No (sleeps) | Yes |
| IPv6 Support | No | Yes | Yes |
| Build Minutes | 500/month | 500/month | Unlimited |
| Cold Start | N/A | 30-60s | None |

---

## Next Steps After Deployment

1. ✅ Test mobile app "Run Daily Update" button
2. ✅ Verify data loads correctly
3. ✅ Update documentation with new URL
4. ✅ Disable/delete Railway service (save $5/month)
5. ✅ Consider paid Render tier if cold starts are annoying

---

## Support

- **Render Docs:** https://render.com/docs
- **Render Status:** https://status.render.com
- **Community:** https://community.render.com

Let me know if you encounter any issues during deployment!
