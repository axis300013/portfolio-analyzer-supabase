# Hybrid A+C Implementation Checklist
**Date**: January 14, 2026  
**Target**: Enable both manual & automatic daily updates

---

## ✅ What's Ready

- [x] **Backend HTTP Endpoint** (`backend/app/daily_update_endpoint.py`)
  - POST `/api/updates/trigger-daily-update` - Start ETL
  - GET `/api/updates/status` - Check progress
  - POST `/api/updates/schedule-daily` - Configure schedule

- [x] **Mobile HTTP Client** (`mobile/lib/services/daily_update_service.dart`)
  - `triggerDailyUpdate()` - Send update request
  - `getUpdateStatus()` - Monitor progress
  - Local IP or ngrok URL support

- [x] **Mobile UI Button** (`mobile/lib/screens/trends/trends_screen.dart`)
  - Cloud upload icon in app bar
  - Confirmation dialog
  - Status spinner & notifications
  - Auto-refresh after 2 min

- [x] **Automatic Scheduler** (`sql/supabase_daily_update_scheduler.sql`)
  - pg_cron job - Daily 7 AM UTC
  - Alternative schedules included
  - Monitoring queries provided

---

## 📋 Implementation Checklist

### Phase 1: Backend Integration (15 min)

- [ ] Copy `backend/app/daily_update_endpoint.py` to your backend/app folder
- [ ] Edit `backend/app/main.py` and add:
  ```python
  from app.daily_update_endpoint import router as daily_update_router
  app.include_router(daily_update_router)
  ```
- [ ] Test endpoint:
  ```bash
  curl -X POST http://localhost:8000/api/updates/trigger-daily-update
  ```

### Phase 2: Mobile Configuration (10 min)

- [ ] Edit `mobile/lib/services/daily_update_service.dart`
  - Get your local PC IP: `ipconfig | findstr IPv4`
  - Update `_localBackendUrl` with correct IP
  - Set `useRemoteBackend = false` for local network
  
- [ ] If using ngrok:
  - [ ] Download from https://ngrok.com
  - [ ] Run: `ngrok http 8000`
  - [ ] Copy ngrok URL to `_remoteBackendUrl`
  - [ ] Set `useRemoteBackend = true`

- [ ] Run `flutter pub get` in mobile folder

### Phase 3: Test Manual Trigger (10 min)

- [ ] Start backend: `python -m uvicorn backend.app.main:app --reload`
- [ ] Run mobile app: `flutter run -d chrome`
- [ ] Open Trends & Analytics tab
- [ ] Click cloud upload icon (⬆️) in app bar
- [ ] Confirm update in dialog
- [ ] Watch spinner (should complete in 2-5 min)
- [ ] Trends data auto-refreshes

### Phase 4: Enable Automatic Daily (5 min)

- [ ] Open Supabase dashboard
- [ ] Go to SQL Editor
- [ ] Create new query
- [ ] Copy entire `sql/supabase_daily_update_scheduler.sql`
- [ ] Click Run
- [ ] Verify with:
  ```sql
  SELECT * FROM cron.job WHERE jobname LIKE '%portfolio%';
  ```

### Phase 5: Test Automatic Scheduler (5 min)

- [ ] Check job runs every day at 7 AM UTC
  ```sql
  SELECT jobname, start_time, succeeded 
  FROM cron.job_run_details 
  WHERE jobname = 'daily-portfolio-update-7am' 
  ORDER BY start_time DESC LIMIT 5;
  ```
- [ ] Verify ETL completed successfully
- [ ] Check Supabase data was updated

### Phase 6: Final Testing (10 min)

- [ ] [ ] Manual trigger works from mobile
- [ ] [ ] Auto-refresh happens after 2 min
- [ ] [ ] Error notifications work
- [ ] [ ] Automatic daily job shows in cron history
- [ ] [ ] Updated data appears in dashboard

---

## 🚀 Quick Start Commands

```bash
# 1. Backend setup (from root)
# Add to backend/app/main.py:
# from app.daily_update_endpoint import router
# app.include_router(router)

# 2. Test backend
python -m uvicorn backend.app.main:app --reload

# 3. Configure mobile (edit one file)
nano mobile/lib/services/daily_update_service.dart
# Change IP to your PC's local IP (e.g., 192.168.1.100)

# 4. Test from another terminal
curl -X POST http://localhost:8000/api/updates/trigger-daily-update

# 5. Enable automatic (in Supabase SQL Editor)
# Copy & paste entire sql/supabase_daily_update_scheduler.sql
```

---

## 📊 What You Get

### Option A: Manual Trigger (Mobile Button)
- ✅ Button in Trends tab app bar
- ✅ Click to run update immediately
- ✅ Works from anywhere (with ngrok)
- ✅ Perfect for "run now" scenarios

### Option C: Automatic Daily (pg_cron)
- ✅ Runs automatically every day at 7 AM UTC
- ✅ No user action needed
- ✅ Runs even when phone is off
- ✅ Perfect for "set and forget"

### Combined (Hybrid)
- ✅ **Best of both worlds**
- ✅ Automatic baseline (7 AM)
- ✅ Manual override when needed
- ✅ Zero additional cost

---

## 🔧 Configuration Options

### Change Update Time (Option C)
Edit in `sql/supabase_daily_update_scheduler.sql`:
```sql
-- Current: 7 AM UTC
'0 7 * * *'

-- Change to 6 AM
'0 6 * * *'

-- Change to 7 PM
'0 19 * * *'

-- Business hours (9 AM, 12 PM, 3 PM weekdays)
'0 9 * * 1-5'
'0 12 * * 1-5'
'0 15 * * 1-5'
```

### Change Backend URL (Option A)
Edit `mobile/lib/services/daily_update_service.dart`:
```dart
// Local network
static const String _localBackendUrl = "http://192.168.X.X:8000";

// Remote (ngrok)
static const String _remoteBackendUrl = "https://YOUR_NGROK_URL";

// Toggle
static bool useRemoteBackend = false; // local = false, remote = true
```

### Change ETL Timeout
Edit `backend/app/daily_update_endpoint.py`:
```python
timeout=600,  # Current: 10 minutes
# Change to 900 for 15 minutes if ETL takes longer
```

---

## ❓ Troubleshooting

| Issue | Solution |
|-------|----------|
| **Connection refused** | Check backend running + IP correct |
| **Mobile can't find backend** | Verify PC IP with `ipconfig` |
| **ngrok keeps timing out** | Restart ngrok (shows new URL) |
| **Cron job not running** | Check Supabase SQL for errors |
| **Update takes >10 min** | Increase timeout in endpoint.py |
| **No data updated** | Check ETL script (run manually first) |

---

## 📈 Monitoring

### Manual Trigger Status
```bash
curl http://localhost:8000/api/updates/status
# Returns: {"is_running": false, "last_completed": "...", ...}
```

### Automatic Daily Execution
```sql
SELECT start_time, succeeded, return_message
FROM cron.job_run_details
WHERE jobname = 'daily-portfolio-update-7am'
ORDER BY start_time DESC
LIMIT 10;
```

### Mobile Logs
```bash
flutter run -d chrome -v
# Look for: "DailyUpdateService: Update..."
```

---

## ✨ Success Criteria

- [ ] Backend endpoint responds to HTTP requests
- [ ] Mobile app can reach backend (local or ngrok)
- [ ] Clicking mobile button triggers ETL successfully
- [ ] Trends data auto-refreshes after 2 minutes
- [ ] Supabase cron job created and showing in `cron.job`
- [ ] Automatic daily update runs at scheduled time
- [ ] No manual intervention needed (both working)

---

## 📞 Support

If you encounter issues:

1. **Check logs**: Backend terminal + Supabase SQL logs + mobile console
2. **Test independently**: `curl` for backend, SQL for cron
3. **Verify config**: IPs match, firewall open, backend running
4. **Review docs**: `HYBRID_A_C_IMPLEMENTATION.md` for detailed guide

---

## Timeline

- **Phase 1**: 15 min (backend setup)
- **Phase 2**: 10 min (mobile config)
- **Phase 3**: 10 min (test manual)
- **Phase 4**: 5 min (enable cron)
- **Phase 5**: 5 min (test auto)
- **Phase 6**: 10 min (final test)

**Total: ~55 minutes for full setup**

---

Ready? Start with Phase 1! 🚀
