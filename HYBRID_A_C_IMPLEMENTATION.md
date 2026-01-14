# Hybrid A+C Implementation Guide
**Date**: January 14, 2026  
**Status**: Ready to implement

---

## What's Been Created

### 1. ✅ Backend HTTP Endpoint (Option A - Manual Trigger)
**File**: `backend/app/daily_update_endpoint.py`

- `/api/updates/trigger-daily-update` → POST endpoint to start ETL
- `/api/updates/status` → GET endpoint to check current update status
- `/api/updates/schedule-daily` → POST to configure schedule

**Features**:
- Returns immediately while ETL runs in background
- Prevents simultaneous updates
- Tracks current step/progress
- Stores last error message

### 2. ✅ Mobile Service (Option A - Client)
**File**: `mobile/lib/services/daily_update_service.dart`

```dart
// Usage examples:
await DailyUpdateService.triggerDailyUpdate();
final status = await DailyUpdateService.getUpdateStatus();
```

**Features**:
- Configurable local/remote backend URLs
- 30-second timeout with proper error handling
- Support for ngrok remote URLs
- JSON response parsing

### 3. ✅ Mobile UI Button
**File**: `mobile/lib/screens/trends/trends_screen.dart` (updated)

- Cloud upload icon button in app bar
- Shows confirmation dialog before triggering
- Displays update status with spinner
- Auto-refreshes trends data after 2 minutes
- Shows success/error notifications

### 4. ✅ Database Scheduler (Option C - Automatic Daily)
**File**: `sql/supabase_daily_update_scheduler.sql`

- Uses PostgreSQL `pg_cron` extension (built-in to Supabase)
- Automatically triggers daily at 7:00 AM UTC
- Includes alternative schedules (6 AM, 7 PM, business hours, etc.)
- Monitoring queries to check execution history
- Full documentation for configuration

---

## Implementation Steps

### Step 1: Integrate Backend Endpoint

**Add to your `backend/app/main.py`**:

```python
from app.daily_update_endpoint import router as daily_update_router

app = FastAPI()

# Include the daily update router
app.include_router(daily_update_router)

# Other routes...
```

**Test locally**:
```bash
cd backend
python -m uvicorn app.main:app --reload
# Visit: http://localhost:8000/api/updates/status
```

---

### Step 2: Update Mobile pubspec.yaml

Ensure the `http` package is included:

```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^1.1.0
  # ... other dependencies
```

Run `flutter pub get` if needed.

---

### Step 3: Configure Backend URL for Mobile

**Edit `mobile/lib/services/daily_update_service.dart`**:

```dart
// For LOCAL NETWORK (when PC on same WiFi):
static const String _localBackendUrl = "http://192.168.1.100:8000";
static bool useRemoteBackend = false;

// For REMOTE ACCESS (ngrok):
static const String _remoteBackendUrl = "https://your-ngrok-url.ngrok.io";
static bool useRemoteBackend = true;
```

**Get your local IP**:
```bash
# Windows (PowerShell)
ipconfig | findstr "IPv4"

# Mac/Linux
ifconfig | grep "inet"
```

**Set up ngrok** (for remote access):
```bash
# Download from https://ngrok.com
ngrok http 8000
# You'll get a public URL like: https://abc123.ngrok.io
```

---

### Step 4: Enable Automatic Daily Updates (Option C)

**In Supabase Dashboard**:

1. Go to **SQL Editor**
2. Create new query
3. Paste entire contents of `sql/supabase_daily_update_scheduler.sql`
4. Click **Run** to execute

**Verify installation**:
```sql
SELECT * FROM cron.job WHERE jobname LIKE '%portfolio-update%';
```

**Monitor execution**:
```sql
SELECT 
  jobname, 
  start_time, 
  succeeded, 
  return_message
FROM cron.job_run_details
WHERE jobname LIKE '%portfolio-update%'
ORDER BY start_time DESC
LIMIT 5;
```

---

## Testing

### Test Option A (Manual Trigger)

**1. From Terminal** (local testing):
```bash
curl -X POST http://localhost:8000/api/updates/trigger-daily-update

# Response:
# {
#   "status": "ETL pipeline started",
#   "timestamp": "2026-01-14T10:30:00.123456"
# }
```

**2. From Mobile App**:
- Open Trends & Analytics tab
- Tap cloud upload icon (⬆️) in app bar
- Confirm update in dialog
- Watch spinner and status
- Auto-refresh happens in 2 minutes

**3. Check Status**:
```bash
curl http://localhost:8000/api/updates/status
```

### Test Option C (Automatic Daily)

**Monitor from Supabase**:
```sql
-- Check if job is running
SELECT * FROM cron.job WHERE jobname = 'daily-portfolio-update-7am';

-- View recent executions
SELECT * FROM cron.job_run_details 
WHERE jobname = 'daily-portfolio-update-7am'
ORDER BY start_time DESC LIMIT 5;
```

---

## Network Configuration

### Local Network Setup (Simplest)

**Requirements**:
- PC and phone on same WiFi
- No firewall blocking port 8000
- PC IP doesn't change

**Setup**:
```
PC (192.168.1.100:8000)
    ↓ WiFi
Phone (same network)
```

**In daily_update_service.dart**:
```dart
static const String _localBackendUrl = "http://192.168.1.100:8000";
static bool useRemoteBackend = false;  // ← Use local
```

### Remote Access with ngrok (Works Anywhere)

**Free tier includes**:
- 2.5 GB/month bandwidth
- Sessions timeout after 1 hour inactivity
- Perfect for daily trigger (minimal usage)

**Setup**:
```bash
# 1. Download ngrok: https://ngrok.com
# 2. Run in portfolio analyzer directory
ngrok http 8000

# You'll see:
# Forwarding    https://abc123.ngrok.io -> http://localhost:8000

# 3. Update in daily_update_service.dart:
static const String _remoteBackendUrl = "https://abc123.ngrok.io";
static bool useRemoteBackend = true;  // ← Use remote

# 4. Mobile will now work from anywhere
```

### Always-On Solution (Production)

For always-on automatic daily updates:
- Keep ngrok running: `ngrok http 8000` (background)
- Or use paid ngrok tier (~$7/month)
- Or implement Option C (pg_cron on Supabase)

---

## Monitoring & Logs

### Backend Logs (Python)
```bash
# Run with verbose output
python -m uvicorn app.main:app --reload --log-level debug

# Watch for messages:
# INFO: Started server process
# 2026-01-14 10:30:00 - Initializing ETL pipeline...
# 2026-01-14 10:35:00 - Completed successfully
```

### Mobile Logs (Flutter)
```bash
# Run with logging enabled
cd mobile
flutter run -d chrome -v

# Check for:
# DailyUpdateService: Update triggered
# DailyUpdateService: Response received
# DailyUpdateService: Update status updated
```

### Database Logs (Supabase)
```sql
-- View cron job history
SELECT jobname, start_time, end_time, succeeded, return_message
FROM cron.job_run_details
WHERE jobname = 'daily-portfolio-update-7am'
ORDER BY start_time DESC;
```

---

## Troubleshooting

### "Connection refused" on Mobile

**Cause**: Backend not running or wrong IP

**Fix**:
```bash
# 1. Ensure backend is running
cd backend
python -m uvicorn app.main:app --reload

# 2. Check local IP
ipconfig | findstr "IPv4"

# 3. Update daily_update_service.dart with correct IP

# 4. Verify port 8000 is open
netstat -ano | findstr ":8000"
```

### "ngrok connection timeout"

**Cause**: Session expired after 1 hour

**Fix**:
```bash
# Restart ngrok (it will show new URL)
ngrok http 8000

# Update daily_update_service.dart with new URL
```

### "http 403 / 500 error"

**Cause**: Backend endpoint not properly integrated

**Fix**:
```bash
# Test directly:
curl -X POST http://localhost:8000/api/updates/trigger-daily-update

# If fails, check main.py includes:
from app.daily_update_endpoint import router as daily_update_router
app.include_router(daily_update_router)
```

### "ETL pipeline timeout"

**Cause**: Update takes longer than 10 minutes

**Fix** in `backend/app/daily_update_endpoint.py`:
```python
timeout=600,  # 10 minutes - increase if needed
```

### Supabase cron job not running

**Check status**:
```sql
SELECT active FROM cron.job WHERE jobname = 'daily-portfolio-update-7am';
-- Should return: true

SELECT * FROM cron.job_run_details 
WHERE jobname = 'daily-portfolio-update-7am' 
LIMIT 1;
-- Check if it ran at expected time
```

**Fix**:
```sql
-- Re-create the job
SELECT cron.unschedule('daily-portfolio-update-7am');

-- Then run sql/supabase_daily_update_scheduler.sql again
```

---

## Architecture Summary

```
┌─────────────────────────────────────────────────────────┐
│                    Mobile App (Flutter)                  │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  Trends Screen                                       │ │
│  │  • Cloud Upload Button (Manual Trigger - Option A)   │ │
│  │  • Status Indicator                                  │ │
│  └─────────────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────────────┘
                       │
                       │ HTTP POST (Option A)
                       │ /api/updates/trigger-daily-update
                       ▼
    ┌──────────────────────────────────────┐
    │  Desktop Backend (Python + FastAPI)   │
    │  ┌────────────────────────────────┐   │
    │  │ daily_update_endpoint.py        │   │
    │  │ • Receives trigger request      │   │
    │  │ • Starts ETL in background      │   │
    │  │ • Returns status                │   │
    │  └────────────────────────────────┘   │
    └──────────┬─────────────────────────────┘
               │
               │ Subprocess call
               ▼
    ┌──────────────────────────────────────┐
    │  ETL Pipeline (Python)                │
    │  • Fetch FX rates (MNB API)           │
    │  • Fetch prices (Selenium)            │
    │  • Fetch pensions (Selenium)          │
    │  • Calculate net wealth               │
    │  • Update database                    │
    └──────┬───────────────────────────────┘
           │
           ▼
    ┌──────────────────────────────────────┐
    │  Supabase PostgreSQL                  │
    │  • Updated snapshots                  │
    │  • New wealth values                  │
    │  • New portfolio values               │
    └──────────────────────────────────────┘

OPTION C: Automatic Daily (Supabase pg_cron)
    ┌──────────────────────────────────────┐
    │  Supabase pg_cron (7 AM UTC)          │
    │  • Scheduled job runs daily           │
    │  • HTTP POST to backend endpoint      │
    │  • Triggers same ETL pipeline         │
    │  • No user action needed              │
    └──────────────────────────────────────┘
```

---

## Cost Analysis

| Component | Option | Cost | Notes |
|-----------|--------|------|-------|
| **Backend Endpoint** | A | FREE | Python/FastAPI (already using) |
| **Mobile HTTP Client** | A | FREE | Dart http package (built-in) |
| **Database Scheduler** | C | FREE | Supabase pg_cron (included) |
| **Network Access** | ngrok | FREE | 2.5 GB/mo bandwidth (sufficient) |
| **Total Monthly** | A+C | **FREE** | No additional costs |

---

## Next Steps

1. ✅ Copy `backend/app/daily_update_endpoint.py` to your project
2. ✅ Integrate endpoint in `backend/app/main.py`
3. ✅ Update mobile URL in `daily_update_service.dart`
4. ✅ Test Option A (manual trigger from mobile)
5. ✅ Run Supabase SQL to enable Option C (automatic daily)
6. ✅ Verify both work (manual button + automatic 7 AM)
7. ✅ Monitor with provided queries
8. ✅ (Optional) Build APK and deploy

---

## Files Ready for Use

| File | Purpose | Status |
|------|---------|--------|
| `backend/app/daily_update_endpoint.py` | HTTP endpoint for manual trigger | ✅ Ready |
| `mobile/lib/services/daily_update_service.dart` | Mobile HTTP client | ✅ Ready |
| `mobile/lib/screens/trends/trends_screen.dart` | UI with update button | ✅ Updated |
| `sql/supabase_daily_update_scheduler.sql` | Automatic daily schedule | ✅ Ready |

---

## Quick Start

```bash
# 1. Add endpoint to backend
cp backend/app/daily_update_endpoint.py backend/app/

# 2. Update main.py (1 line)
# Add: from app.daily_update_endpoint import router
# Add: app.include_router(router)

# 3. Update mobile config (change IPs)
nano mobile/lib/services/daily_update_service.dart

# 4. Test locally
python -m uvicorn backend.app.main:app --reload

# 5. Test from mobile (curl or app button)
curl -X POST http://localhost:8000/api/updates/trigger-daily-update

# 6. Enable automatic daily (copy-paste SQL to Supabase)
# Open sql/supabase_daily_update_scheduler.sql
# Copy entire file → Supabase SQL Editor → Run

# 7. Done! Both manual (A) and automatic (C) are now active
```

Enjoy! 🚀
