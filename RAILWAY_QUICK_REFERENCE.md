# 🚀 Railway Deployment - Quick Reference

## Phase 2: Account Setup (5 min)
1. Go to: https://railway.app
2. Click "Start a New Project"
3. Sign up with GitHub
4. Click "New Project" → "Deploy from GitHub repo"
5. Select: `portfolio-analyzer-supabase`
6. Click "Deploy Now"

**✅ Done when:** Service card appears in Railway dashboard

---

## Phase 3: Configure (20 min)

### Build & Start Commands
- **Build:** `pip install -r requirements-cloud.txt`
- **Start:** `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`

### Environment Variables (15 total)
Add each to Railway Variables section:

```
DATABASE_URL=postgresql://postgres:Clobufclobuf01#@db.hrlzrirsvifxsnccxvsa.supabase.co:5432/postgres
SUPABASE_URL=https://hrlzrirsvifxsnccxvsa.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhybHpyaXJzdmlmeHNuY2N4dnNhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ5NDQzMTcsImV4cCI6MjA4MDUyMDMxN30.IAhjGmpcNA9KIi6fSTIPauVVNTIRSb8jBNCJTpmHodA
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhybHpyaXJzdmlmeHNuY2N4dnNhIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDk0NDMxNywiZXhwIjoyMDgwNTIwMzE3fQ.vLI8kZmCRnSSqP-yiRYBwz5rYqhNnrGCOJYKR2BLKk4
MNB_API_URL=https://www.mnb.hu/arfolyamok.asmx
API_HOST=0.0.0.0
API_PORT=8000
HORIZONT_USERNAME=axis3000@gmail.com
HORIZONT_PASSWORD=Clobufclobuf01#
ALFA_USERNAME=12266379
ALFA_PASSWORD=Mobilemobile01
RAILWAY_ENVIRONMENT=production
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10
```

### Deploy
- Click "Trigger Deploy" button
- Wait for build to complete (3-5 min)
- Watch logs for: "Application startup complete"

### Get Public URL
- Click "Generate Domain" in Settings
- Copy the URL: `https://YOUR_URL.railway.app`
- ⭐ **SAVE THIS URL** - needed for Phase 5 & 6

**✅ Done when:** 
- Deployment shows green checkmark
- Root endpoint returns JSON: `{"message": "Portfolio Analyzer API", "version": "1.0"}`

---

## 📋 Phases 2-3 Checklist

- [ ] GitHub authorization complete
- [ ] Repository deployed to Railway
- [ ] Build command configured
- [ ] Start command configured
- [ ] 15 environment variables added
- [ ] Deployment completed successfully
- [ ] Public domain generated
- [ ] Endpoint `/` tested and working
- [ ] URL saved: `_______________________`

---

## 🔗 Full Reference
See: `RAILWAY_DEPLOYMENT_GUIDE.md` for detailed troubleshooting

---

**After Phases 2-3:** We'll verify the deployment in Phase 4
