# Fly.io Quick Setup - Portfolio Analyzer

## 🚀 5-Minute Setup

### 1️⃣ Install Flyctl CLI
```powershell
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

Close and reopen PowerShell, then verify:
```bash
flyctl version
```

### 2️⃣ Login
```bash
flyctl auth signup
# OR
flyctl auth login
```

### 3️⃣ Initialize App (Don't Deploy Yet)
```bash
cd "c:\Users\SzalmaNB1\Downloads\cabeceo\visual studio\Portfolio Analyzer"
flyctl launch --no-deploy
```

**Prompts:**
- App name: `portfolio-analyzer-backend`
- Region: `fra` (Frankfurt)
- Database: **No**
- Deploy now: **No**

### 4️⃣ Set Secrets (Use Raw Password with #)
```bash
flyctl secrets set DATABASE_URL="postgresql://postgres.hrlzrirsvifxsnccxvsa:Clobufclobuf01#@db.hrlzrirsvifxsnccxvsa.supabase.co:5432/postgres"

flyctl secrets set SUPABASE_URL="https://hrlzrirsvifxsnccxvsa.supabase.co"

flyctl secrets set SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhybHpyaXJzdmlmeHNuY2N4dnNhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzM5MjU3MjEsImV4cCI6MjA0OTUwMTcyMX0.XGu7Gs81fOgTcRHzSNp9u13H9_wWO3G2M02qgWbhU-A"

flyctl secrets set RAILWAY_ENVIRONMENT="production"
```

### 5️⃣ Deploy
```bash
flyctl deploy
```

Wait 2-3 minutes...

### 6️⃣ Get Your URL
```bash
flyctl info
```

URL: `https://portfolio-analyzer-backend.fly.dev`

### 7️⃣ Test
```bash
curl https://portfolio-analyzer-backend.fly.dev/
```

Should return: `{"message": "Portfolio Analyzer API", "version": "1.0"}`

### 8️⃣ Update Mobile App
**File:** `mobile/lib/services/supabase_service.dart` (line 597)

```dart
final url = backendUrl ?? 'https://portfolio-analyzer-backend.fly.dev';
```

Commit, restart Flutter app, test "Run Daily Update" button!

---

## ✅ Done!

**Fly.io advantages:**
- ✅ Native IPv6 (works with Supabase)
- ✅ Free tier (no cold starts)
- ✅ Always on
- ✅ No authentication issues

**Cleanup:**
- Delete Railway service (save $5/month)
- Delete Render service (if created)
