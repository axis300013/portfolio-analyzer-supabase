# Fly.io Deployment Guide - Portfolio Analyzer Backend

## Overview
Fly.io has **native IPv6 support** which will solve the Supabase connectivity issue that Railway and Render couldn't handle.

## Prerequisites
- Fly.io account (free tier: 3 VMs, 160GB bandwidth/month)
- Flyctl CLI installed
- GitHub repository

---

## Step 1: Install Flyctl CLI

### Windows (PowerShell):
```powershell
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

### After Installation:
```bash
flyctl version
```

---

## Step 2: Create Fly.io Account & Login

```bash
flyctl auth signup
# OR if you already have an account:
flyctl auth login
```

---

## Step 3: Initialize Fly App

From your project root:

```bash
cd "c:\Users\SzalmaNB1\Downloads\cabeceo\visual studio\Portfolio Analyzer"
flyctl launch --no-deploy
```

**Answer the prompts:**
- App name: `portfolio-analyzer-backend` (or auto-generate)
- Region: `fra` (Frankfurt - closest to Supabase)
- Database: **No** (we're using Supabase)
- Deploy now: **No** (we need to set environment variables first)

This creates `fly.toml` configuration file.

---

## Step 4: Set Environment Variables

```bash
flyctl secrets set DATABASE_URL="postgresql://postgres.hrlzrirsvifxsnccxvsa:Clobufclobuf01#@db.hrlzrirsvifxsnccxvsa.supabase.co:5432/postgres"

flyctl secrets set SUPABASE_URL="https://hrlzrirsvifxsnccxvsa.supabase.co"

flyctl secrets set SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhybHpyaXJzdmlmeHNuY2N4dnNhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzM5MjU3MjEsImV4cCI6MjA0OTUwMTcyMX0.XGu7Gs81fOgTcRHzSNp9u13H9_wWO3G2M02qgWbhU-A"

flyctl secrets set RAILWAY_ENVIRONMENT="production"
```

**Important:** With Fly.io secrets, use the **raw password** (with `#`), not URL-encoded. Fly handles encoding internally.

---

## Step 5: Deploy

```bash
flyctl deploy
```

This will:
- Build your application
- Push to Fly.io registry
- Deploy to your VM
- Takes 2-3 minutes first time

---

## Step 6: Get Your URL

```bash
flyctl info
```

Your app will be at: `https://portfolio-analyzer-backend.fly.dev`

Test it:
```bash
curl https://portfolio-analyzer-backend.fly.dev/
```

Should return: `{"message": "Portfolio Analyzer API", "version": "1.0"}`

---

## Step 7: Update Mobile App

**File:** `mobile/lib/services/supabase_service.dart` (line ~597)

```dart
// Change from Render URL:
final url = backendUrl ?? 'https://portfolio-analyzer-backend.onrender.com';

// To Fly.io URL:
final url = backendUrl ?? 'https://portfolio-analyzer-backend.fly.dev';
```

---

## Useful Fly.io Commands

```bash
# View logs (real-time)
flyctl logs

# Check app status
flyctl status

# Open dashboard
flyctl dashboard

# SSH into VM
flyctl ssh console

# Restart app
flyctl restart

# Scale (if needed)
flyctl scale count 1
```

---

## Free Tier Limits

- **3 shared VMs** (256MB RAM each)
- **160GB bandwidth/month**
- **3GB persistent storage**
- **IPv6 by default** (IPv4 costs $2/month extra - not needed!)

Your app will stay within free tier limits.

---

## Troubleshooting

### Issue: Build Failed
```bash
# Check build logs
flyctl logs --build

# Redeploy
flyctl deploy --no-cache
```

### Issue: Connection Timeout
```bash
# Check if app is running
flyctl status

# View health checks
flyctl checks list
```

### Issue: Database Connection Error
```bash
# Test connection from VM
flyctl ssh console
python -c "import psycopg2; conn = psycopg2.connect('$DATABASE_URL'); print('OK')"
```

---

## Why Fly.io Wins

| Feature | Railway | Render | Fly.io |
|---------|---------|--------|--------|
| IPv6 Support | ❌ No | ❌ No | ✅ Native |
| Free Tier | ❌ Paid | ✅ Yes | ✅ Yes |
| Always On | Yes | ❌ Sleeps | ✅ Yes |
| Cold Starts | None | 30-60s | None |
| Supabase IPv6 | ❌ Failed | ❌ Failed | ✅ Works |

**Verdict:** Fly.io is the ONLY free option that works with Supabase's IPv6!

---

## Next Steps

1. ✅ Install flyctl
2. ✅ Login to Fly.io
3. ✅ Run `flyctl launch --no-deploy`
4. ✅ Set environment secrets
5. ✅ Deploy with `flyctl deploy`
6. ✅ Update mobile app with Fly.io URL
7. ✅ Test "Run Daily Update" button

You're done! 🎉
