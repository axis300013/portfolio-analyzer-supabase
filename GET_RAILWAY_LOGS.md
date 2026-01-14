# 🔍 Collecting Crash Logs

## Get the Error Message

1. **In Railway Dashboard**, click your service
2. Click **"Deployments"** tab
3. Find your latest deployment (top of list)
4. Click **"View Logs"** button
5. **Scroll to the bottom** to find the error
6. Look for red text or "ERROR" messages
7. **Copy the last 30-50 lines** and paste here

---

## What to Look For

The error will likely be one of:

❌ **Database connection error:**
```
ERROR: could not translate host name
ERROR: connection refused
```

❌ **Environment variable missing:**
```
KeyError: 'DATABASE_URL'
KeyError: 'SUPABASE_URL'
```

❌ **Import error:**
```
ModuleNotFoundError:
ImportError:
```

❌ **Startup event crash:**
```
ERROR during startup
```

---

## Steps to Share Logs

1. Open Railway Deployments view
2. Find the RED/FAILED deployment
3. Click "View Logs"
4. Select all text (Ctrl+A)
5. Copy (Ctrl+C)
6. Paste into chat

---

**Please share the crash logs so I can fix it!**
