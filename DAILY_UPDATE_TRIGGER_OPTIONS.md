# Daily Update Trigger Implementation Options
**Analysis Date**: January 14, 2026  
**Goal**: Allow users to trigger daily ETL updates remotely from mobile phone  
**Constraint**: Cost-free solutions only

---

## Architecture Overview

Currently, daily updates run via scheduled backend (Supabase or local database):
- **FX rates**: MNB API (Hungarian National Bank) 
- **Instrument prices**: Web scraping via Selenium
- **Pension values**: Automated Selenium scraping (Horizont & Alfa portals)
- **Wealth calculations**: Aggregation from raw data

---

## Option A: Remote Trigger via Desktop Backend (Recommended for most users)

### Architecture
```
Mobile App (Flutter)
    ↓ HTTP POST (IP:PORT or ngrok)
Desktop Backend (Python FastAPI)
    ↓ Triggers ETL pipeline
Supabase PostgreSQL (Updates data)
    ↓ Auto-sync
Mobile App (Reads updated data)
```

### Implementation Steps

#### 1. Add HTTP Endpoint to Desktop Backend (`backend/app/main.py`)
```python
from fastapi import FastAPI, BackgroundTasks
import uvicorn

app = FastAPI()

@app.post("/api/trigger-daily-update")
async def trigger_daily_update(background_tasks: BackgroundTasks):
    """Trigger full ETL pipeline from remote request"""
    background_tasks.add_task(run_etl_pipeline)
    return {"status": "ETL pipeline started", "timestamp": datetime.now()}

async def run_etl_pipeline():
    from etl.run_daily_etl import main
    await main()
```

#### 2. Mobile App HTTP Client
```dart
// lib/services/daily_update_service.dart
class DailyUpdateService {
  static const String backendUrl = "http://192.168.X.X:8000"; // Local network
  // OR use ngrok for remote access: "https://abc123.ngrok.io"
  
  static Future<void> triggerDailyUpdate() async {
    try {
      final response = await http.post(
        Uri.parse("$backendUrl/api/trigger-daily-update"),
        headers: {"Content-Type": "application/json"},
        timeout: const Duration(minutes: 10),
      );
      
      if (response.statusCode == 200) {
        // Show success notification
      }
    } catch (e) {
      print("Update trigger failed: $e");
    }
  }
}
```

#### 3. Network Configuration
- **Local Network**: Use device IP (192.168.X.X:8000) when home
- **Remote Access**: Use **ngrok** (free tier = 2.5 GB/month transfer)
  ```bash
  ngrok http 8000
  # Provides public URL: https://abc123.ngrok.io
  ```

#### 4. UI Button in Mobile App
```dart
// Add to dashboard screen
FloatingActionButton(
  onPressed: () async {
    showDialog(context: context, builder: (ctx) {
      return AlertDialog(
        title: Text("Run Daily Update?"),
        actions: [
          TextButton(
            onPressed: () async {
              await DailyUpdateService.triggerDailyUpdate();
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text("Update started..."))
              );
            },
            child: Text("Update"),
          ),
        ],
      );
    });
  },
  child: Icon(Icons.refresh),
  label: Text("Daily Update"),
)
```

### Pros ✅
- **Minimal changes** to existing backend
- **Full control** over ETL (all 5 steps working as designed)
- **Selenium web scraping** for pension portals continues to work
- **Cost-free** (ngrok has free tier for home use)
- **Low latency** when on same local network
- **Familiar architecture** (no new tech stack)
- **Easy to monitor** (logs on desktop PC)
- **Database isolation** (Supabase stays private, no direct mobile access)

### Cons ❌
- **Network dependency**: Requires WiFi or ngrok connection
- **PC must be on**: Desktop backend needs to be running
- **ngrok limitations**: 2.5 GB/month free, connections timeout after 1 hour inactivity
- **IP address issues**: Local IP might change (use hostname or static IP)
- **Firewall configuration**: May need router port forwarding
- **No offline triggers**: Can't trigger updates when PC is offline

### Cost Analysis
- **Backend hosting**: €0 (PC already running)
- **ngrok**: €0 (free tier sufficient for daily trigger)
- **Mobile changes**: €0 (Flutter built-in HTTP)
- **Total**: **FREE**

---

## Option B: Embedded Backend in Mobile App

### Architecture
```
Mobile App (Flutter + Python via Kivy/PyCall)
    ↓ Direct integration
SQLite / Local Database
    ↓ On-device processing
Supabase PostgreSQL (Sync when online)
    ↓ Auto-sync
All other devices (Read-only via Supabase)
```

### Implementation Steps

#### 1. Add Python to Flutter via Python Integration Library
- Use **`python_anywhere`** or **`flutterpy`** (cross-platform Python embedding)
- Include Python scripts: fx_fetch.py, price_fetch.py, wealth_calculations.py

#### 2. Mobile App Trigger Handler
```dart
// lib/services/embedded_etl_service.dart
class EmbeddedETLService {
  static Future<void> runLocalETL() async {
    try {
      // Call embedded Python ETL
      final result = await MethodChannel('com.example.etl')
          .invokeMethod('runETL', {"mode": "full"});
      
      if (result["status"] == "success") {
        // Sync results to Supabase
        await SupabaseService.syncLocalData();
      }
    } catch (e) {
      print("Local ETL failed: $e");
    }
  }
}
```

#### 3. Android Native Code (Kotlin)
```kotlin
// android/app/src/main/kotlin/MainActivity.kt
MethodChannel(flutterEngine?.dartExecutor?.binaryMessenger!!, 
  "com.example.etl")
  .setMethodCallHandler { call, result ->
    when (call.method) {
      "runETL" -> {
        // Launch Python subprocess running ETL
        val process = Runtime.getRuntime().exec(arrayOf(
          "python3", 
          "/data/data/com.example.app/etl/run_etl.py"
        ))
        result.success(mapOf("status" to "success"))
      }
    }
  }
```

### Pros ✅
- **Completely offline**: No network dependency
- **Phone can be anywhere**: No PC required
- **Instant updates**: No latency waiting for remote backend
- **Privacy**: All data stays on device until manually synced
- **Always available**: Works 24/7 on phone
- **No cost**: Single-app deployment

### Cons ❌
- **Phone resource intensive**: Runs heavy Selenium scraping on mobile (slow, drains battery)
- **Requires Python shipping**: ~50-100 MB app size increase
- **Complex build process**: Python compilation for Android/iOS platforms
- **Dependency hell**: Managing Python packages on mobile is difficult
- **Selenium limitations**: Browser automation on mobile very limited/unstable
- **Storage constraints**: Mobile storage may overflow with historical data
- **FX API calls**: Rate-limited differently on mobile IP
- **Maintenance burden**: Python version updates, library compatibility
- **Testing complexity**: Hard to test all ETL scenarios on different devices
- **No background execution**: iOS limits background processes to ~30 seconds
- **Sync conflicts**: Complex logic when data out of sync across devices

### Cost Analysis
- **Python embedding**: €0 (open source)
- **App hosting**: €0 (Play Store/App Store free)
- **Mobile data**: Variable (FX/price requests, Selenium scraping = ~10-50 MB per update)
- **Storage**: ~100-200 MB additional app size
- **Total**: **FREE (but with high phone resource cost)**

---

## Option C: Cloud Scheduler + Mobile Trigger

### Architecture
```
Mobile App (Button to enable)
    ↓ Set cron in cloud
Cloud Scheduler (Cloud Run / Supabase cron)
    ↓ Runs ETL daily
Desktop Backend (Python)
    ↓ Executes locally when triggered
Supabase (Updates)
```

### Implementation
- Use **Supabase Cron Extension** (PostgreSQL `pg_cron` built-in, free tier)
- Or **Firebase Cloud Scheduler** (free tier: 3 jobs)
- Mobile app manages schedule preferences

### Pros ✅
- **Always runs on schedule**: No need to remember to trigger
- **Automatic execution**: Works while phone is offline
- **Scalable**: Cloud handles orchestration

### Cons ❌
- **Less flexible**: Fixed daily schedule (can't do ad-hoc updates)
- **Cloud dependency**: Internet required
- **Selenium still on PC**: Same backend requirement as Option A
- **Not really a "mobile trigger"**: More of an automated schedule

### Cost Analysis
- **Cloud Scheduler**: €0 (3 free jobs in Firebase)
- **Supabase cron**: €0 (included in free tier)
- **Total**: **FREE**

---

## Comparison Matrix

| Feature | Option A (Desktop + HTTP) | Option B (Embedded) | Option C (Cloud) |
|---------|--------------------------|-------------------|------------------|
| **Network Required** | Yes (trigger only) | No | Yes (auto) |
| **PC Required** | Yes | No | No |
| **Offline Capable** | No | Yes | No |
| **Ad-hoc Triggers** | ✅ Yes | ✅ Yes | ❌ No |
| **App Size** | <1 MB increase | +50-100 MB | <1 MB |
| **Phone Battery** | Minimal | High drain | Minimal |
| **Implementation** | 1-2 days | 5-7 days | 2-3 days |
| **Reliability** | High (proven setup) | Medium (untested) | High (cloud) |
| **Cost** | **FREE** | **FREE** | **FREE** |
| **Complexity** | Low | Very High | Medium |

---

## Recommendation: **Option A + Option C Hybrid**

### Suggested Implementation
1. **Option A** for manual ad-hoc updates
   - Add "Run Daily Update Now" button in mobile dashboard
   - Show status/logs of current update
   
2. **Option C** for automated daily schedule
   - Use Supabase `pg_cron` for daily 7 AM trigger
   - Mobile can override/disable schedule

### Benefits
- ✅ **Automatic daily updates** (Option C)
- ✅ **Manual triggers** when needed (Option A)
- ✅ **Always free** (both options)
- ✅ **Minimal complexity** (reuse existing backend)
- ✅ **Flexible & reliable** (best of both worlds)

### Implementation Timeline
- **Week 1**: Add HTTP endpoint to backend (Option A) + mobile button
- **Week 2**: Add Supabase pg_cron schedule (Option C) + UI for schedule management
- **Week 3**: Testing on all devices + documentation

---

## Quick Start: Option A Implementation

```bash
# 1. Install FastAPI (if not already in requirements.txt)
pip install fastapi uvicorn

# 2. Add to backend/app/main.py
# (See code example above)

# 3. Install ngrok for remote access (optional)
# https://ngrok.com/download

# 4. Run backend with ngrok
ngrok http 8000 &
python -m uvicorn backend.app.main:app --reload

# 5. Share ngrok URL with mobile app config
# Mobile will call: https://abc123.ngrok.io/api/trigger-daily-update

# 6. Test with curl
curl -X POST http://localhost:8000/api/trigger-daily-update
```

---

## Questions for Refinement

1. **Offline updates needed?** (→ favors Option B, but complex)
2. **Always-on PC available?** (→ Option A simpler)
3. **Prefer automatic or manual?** (→ Hybrid A+C best)
4. **How often trigger needed?** (→ If daily: use Option C)
5. **Network reliability?** (→ Poor → need offline Option B)

---

## Next Steps

1. **Confirm requirements** with user
2. **Implement Option A** HTTP endpoint (1-2 days)
3. **Add mobile UI button** for trigger (1 day)
4. **Test with ngrok** for remote access (1 day)
5. **Add Option C schedule** if automatic daily needed (1-2 days)

