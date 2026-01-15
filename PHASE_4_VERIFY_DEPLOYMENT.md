# Phase 4: Verify Deployment - Step by Step

## ✅ Your App is Online!

Great news - Railway shows "online", which means deployment succeeded!

---

## Step 1: Get Your Railway URL

1. **In Railway Dashboard**, go to your service
2. Look for the **Domain** section (usually under "Settings" or shown on main card)
3. You should see something like: `https://portfolio-analyzer-xxxxxx.up.railway.app`
4. **Copy this URL** and paste it below:

```
Your Railway URL: ___________________________________
```

---

## Step 2: Test Endpoint #1 - Health Check

**Open a browser and go to:**
```
https://YOUR_RAILWAY_URL/
```

**Expected Response:**
```json
{
  "message": "Portfolio Analyzer API",
  "version": "1.0"
}
```

✅ **If you see this JSON, move to Step 3!**  
❌ **If you see error or nothing, check your URL**

---

## Step 3: Test Endpoint #2 - Status Check

**Open a browser and go to:**
```
https://YOUR_RAILWAY_URL/api/updates/status
```

**Expected Response:**
```json
{
  "is_running": false,
  "last_started": null,
  "last_completed": null,
  "current_step": "idle",
  "status": "Ready for manual trigger"
}
```

✅ **If you see this, your API is fully working!**

---

## Step 4: Test Endpoint #3 - Manual ETL Trigger

This is optional but good to test:

**Using PowerShell:**
```powershell
$url = "https://YOUR_RAILWAY_URL/api/updates/trigger-daily-update"
$response = Invoke-WebRequest -Uri $url -Method POST -ContentType "application/json" -Body "{}"
$response.Content | ConvertFrom-Json | Format-List
```

**Expected Response:**
```json
{
  "status": "ETL pipeline started",
  "timestamp": "2026-01-14T...",
  "message": "Daily update initiated"
}
```

✅ **If you see this, ETL triggers work!**

Then wait 60 seconds and check status:
```
https://YOUR_RAILWAY_URL/api/updates/status
```

Should now show: `"last_completed": "2026-01-14T..."`

---

## Phase 4 Verification Checklist

- [ ] Railway service shows "online"
- [ ] Root endpoint `/` returns JSON message
- [ ] Status endpoint `/api/updates/status` returns status object
- [ ] (Optional) Manual trigger works
- [ ] **Railway URL saved:** ___________________________________

---

## 📋 Troubleshooting

### Issue: "Cannot reach server" or "Connection timeout"
- Verify the URL has `https://` (not `http://`)
- Check URL matches exactly what's in Railway
- Wait 2 minutes - DNS might be propagating
- Check Railway logs for startup errors

### Issue: 404 Not Found
- Verify the endpoint path is spelled correctly
- Check URL ends with `/` for root
- Verify Railway service is still "online"

### Issue: 502 Bad Gateway
- Check Railway logs in Deployments tab
- Might still be starting up - wait 30 seconds
- Try refreshing

---

## Next Steps

Once all endpoints work:
→ **Phase 5:** Update Mobile App URL  
→ **Phase 6:** Set up pg_cron for auto updates  
→ **Phase 7:** Final testing  

---

**Ready? Share your Railway URL and I'll help verify!**
