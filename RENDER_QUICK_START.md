# Render.com Quick Setup - Portfolio Analyzer

## 🚀 Fast Track Deployment (5 minutes)

### 1️⃣ Push to GitHub
```bash
git add .
git commit -m "Add Render.com deployment config"
git push origin main
```

### 2️⃣ Create Render Account
- Go to: https://render.com
- Sign up with GitHub

### 3️⃣ Deploy
1. Click **"New +"** → **"Web Service"**
2. Connect repository: `Portfolio Analyzer`
3. Render auto-detects `render.yaml` ✅
4. Add environment variables (copy from Railway):
   - `DATABASE_URL` → `postgresql://postgres.hrlzrirsvifxsnccxvsa:Clobufclobuf01%2523@db.hrlzrirsvifxsnccxvsa.supabase.co:5432/postgres`
   - `SUPABASE_URL` → `https://hrlzrirsvifxsnccxvsa.supabase.co`
   - `SUPABASE_KEY` → `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhybHpyaXJzdmlmeHNuY2N4dnNhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzM5MjU3MjEsImV4cCI6MjA0OTUwMTcyMX0.XGu7Gs81fOgTcRHzSNp9u13H9_wWO3G2M02qgWbhU-A`
5. Click **"Create Web Service"**

### 4️⃣ Get Your URL
- Service URL: `https://portfolio-analyzer-backend.onrender.com`
- Test: Open URL in browser → Should see API info

### 5️⃣ Update Mobile App
**File:** `mobile/lib/services/supabase_service.dart` (line ~597)

```dart
// Change from Railway URL:
final url = backendUrl ?? 'https://web-production-07ca1a.up.railway.app';

// To Render URL:
final url = backendUrl ?? 'https://portfolio-analyzer-backend.onrender.com';
```

### 6️⃣ Test
- Restart mobile app in Chrome
- Click **"Run Daily Update"** button on Dashboard
- Wait 60 seconds (first cold start)
- Success! ✅

---

## ⚠️ Free Tier Notes

**Cold Start:** Server sleeps after 15 minutes idle
- First request: 30-60 seconds to wake up
- Solution: Loading dialog already says "may take 1-2 minutes"

**Upgrade to Paid ($7/month):** Always-on, no cold starts

---

## 🔄 Environment Variables to Copy

```
DATABASE_URL=postgresql://postgres.hrlzrirsvifxsnccxvsa:Clobufclobuf01%2523@db.hrlzrirsvifxsnccxvsa.supabase.co:5432/postgres

SUPABASE_URL=https://hrlzrirsvifxsnccxvsa.supabase.co

SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhybHpyaXJzdmlmeHNuY2N4dnNhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzM5MjU3MjEsImV4cCI6MjA0OTUwMTcyMX0.XGu7Gs81fOgTcRHzSNp9u13H9_wWO3G2M02qgWbhU-A

RAILWAY_ENVIRONMENT=production
```

---

## 🎯 Why Render vs Railway?

| Feature | Railway | Render |
|---------|---------|--------|
| IPv6 Support | ❌ No | ✅ Yes |
| Free Tier | ❌ Paid only | ✅ Yes |
| Supabase Compatible | ❌ Failed | ✅ Works |
| Cold Starts | None | 30-60s |
| Always On | Yes | Paid only |

**Verdict:** Render free tier solves the IPv6 issue!
