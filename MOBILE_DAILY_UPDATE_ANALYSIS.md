# Mobile Daily Update Implementation Analysis
**Date:** 2026-01-13  
**Project:** Portfolio Analyzer Mobile App

---

## Executive Summary

### Current Daily Update Components
The desktop daily update performs 5 main operations:
1. **FX Rate Fetch** - From MNB (Hungarian National Bank) API
2. **Instrument Price Fetch** - Web scraping from Erste Market, BSE, Yahoo Finance
3. **Portfolio Value Calculation** - Database aggregation and calculations
4. **Wealth Value Copy** - Copy static values from previous day
5. **Automated Wealth Fetch** - Selenium-based web scraping (Horizont & Alfa pension portals)

### Key Findings

| Metric | Value |
|--------|-------|
| Current ETL Python Code | 63.87 KB (12 files) |
| Python Dependencies | 17 packages (Selenium, pandas, etc.) |
| Most Complex Component | Selenium web scraping (~40% of code) |
| Network Operations | 5-10 HTTP requests per run |
| Execution Time | 30-60 seconds (including web scraping) |

---

## Technical Analysis

### 1. Component Breakdown

#### ✅ **Easy to Implement on Mobile**

**A) FX Rate Fetch**
- **Current:** Python `requests` to MNB API
- **Mobile:** Flutter `http` package (already available)
- **Complexity:** LOW
- **Size Impact:** None (using existing packages)
- **Estimated Implementation:** 2-4 hours

**B) Wealth Value Copy**
- **Current:** SQL queries via SQLAlchemy
- **Mobile:** Supabase client (already integrated)
- **Complexity:** LOW
- **Size Impact:** None
- **Estimated Implementation:** 1-2 hours

**C) Portfolio Value Calculation**
- **Current:** Database aggregation queries
- **Mobile:** Supabase queries + Dart calculations
- **Complexity:** MEDIUM
- **Size Impact:** +2-3 KB Dart code
- **Estimated Implementation:** 4-6 hours

#### ⚠️ **Challenging for Mobile**

**D) Instrument Price Fetch**
- **Current:** BeautifulSoup web scraping (Erste Market, BSE)
- **Mobile Options:**
  1. Port to Flutter web scraping (`html` package)
  2. Use backend API endpoint
  3. Skip scraping, use last known prices
- **Complexity:** MEDIUM-HIGH
- **Size Impact:** +5-10 KB if ported
- **Estimated Implementation:** 8-12 hours (porting) OR 2-4 hours (API call)

#### 🚫 **Not Suitable for Mobile**

**E) Automated Pension Scraping (Selenium)**
- **Current:** Selenium WebDriver with Chrome
- **Mobile Issues:**
  - Selenium requires browser drivers (Chrome/Firefox) - NOT available on mobile
  - Would require ~50-100 MB of additional app size
  - Browser automation is restricted on iOS
  - High battery consumption
  - Unreliable on mobile networks
- **Complexity:** IMPOSSIBLE without complete rewrite
- **Alternative:** Backend API/cloud function approach ONLY

---

## Implementation Approaches

### **Approach 1: Hybrid (RECOMMENDED)**
**Mobile handles simple operations, backend handles complex ones**

**Mobile Responsibilities:**
- Trigger daily update via API call
- Display progress and results
- Handle simple operations locally (FX rates, calculations)
- Copy wealth values

**Backend/Cloud Responsibilities:**
- Web scraping (Erste Market, pension portals)
- Heavy calculations
- Complex data transformations

**Pros:**
- ✅ Minimal app size increase (+5-10 MB)
- ✅ Fast implementation (2-3 weeks)
- ✅ Battery efficient
- ✅ Reliable execution
- ✅ Easy to maintain

**Cons:**
- ❌ Requires backend service to be running
- ❌ Network dependency

**Estimated App Size:** **60-65 MB** (current ~55 MB)

---

### **Approach 2: Partial Mobile Implementation**
**Some features in mobile, trigger backend for complex ones**

**Mobile Implementation:**
- FX rate fetching (MNB API)
- Portfolio value calculation
- Wealth value copying
- Display last known prices if fetching fails

**Backend API Endpoints:**
- `/api/etl/fetch-prices` - Trigger price scraping
- `/api/etl/fetch-pensions` - Trigger pension scraping
- `/api/etl/run-full-update` - Run complete update

**Pros:**
- ✅ More autonomy for mobile
- ✅ Moderate app size (+10-15 MB)
- ✅ Works offline for some features

**Cons:**
- ❌ More complex to maintain
- ❌ Duplicate logic between mobile/backend

**Estimated App Size:** **65-70 MB**

---

### **Approach 3: Cloud Function Architecture**
**Deploy ETL as serverless functions, mobile triggers them**

**Architecture:**
```
Mobile App → Supabase Edge Functions → Scraping/ETL → Database
```

**Components:**
- Supabase Edge Functions (Deno/TypeScript)
- Scheduled functions for automatic updates
- Mobile app just triggers and monitors

**Pros:**
- ✅ Minimal app size (no change)
- ✅ Serverless scaling
- ✅ Automatic scheduling possible
- ✅ Better security (credentials on server)

**Cons:**
- ❌ Requires Supabase Pro plan ($25/month)
- ❌ Learning curve for Edge Functions
- ❌ Limited to TypeScript/Deno ecosystem

**Estimated App Size:** **55 MB** (no change)

---

### **Approach 4: Full Mobile Implementation (NOT RECOMMENDED)**
**Port everything to Flutter/Dart**

**Requirements:**
- Replace Selenium with alternatives (WebView automation or API scraping)
- Port BeautifulSoup scraping to Flutter `html` package
- Implement complex parsing logic in Dart

**Pros:**
- ✅ Full autonomy
- ✅ No backend dependency

**Cons:**
- ❌ Large app size increase (+30-50 MB)
- ❌ Pension portal scraping nearly impossible without WebView hacks
- ❌ High maintenance burden
- ❌ Battery drain issues
- ❌ iOS restrictions on background automation
- ❌ 4-6 weeks development time

**Estimated App Size:** **85-105 MB**

---

## Recommended Implementation: Hybrid Approach

### Phase 1: Backend API Layer (Week 1)
Create FastAPI endpoints for daily update operations:

```python
# New endpoints:
POST /api/etl/run-daily-update
POST /api/etl/fetch-fx-rates
POST /api/etl/fetch-prices
POST /api/etl/fetch-pensions
POST /api/etl/calculate-portfolio
GET  /api/etl/status/{job_id}
```

### Phase 2: Mobile UI Integration (Week 2)
Add daily update screen in mobile app:
- Button to trigger update
- Progress indicator
- Step-by-step status display
- Error handling and retry logic

### Phase 3: Background Scheduling (Week 3)
- Android: WorkManager for background tasks
- iOS: Background App Refresh
- Trigger backend API at scheduled times

### Phase 4: Optimization (Week 4)
- Cache results
- Smart update (only fetch what's needed)
- Offline mode handling

---

## App Size Estimates

### Current Mobile App
- **Base APK/IPA:** ~55 MB
- **With assets:** ~58 MB

### After Implementation

| Approach | APK Size | IPA Size | Additional |
|----------|----------|----------|------------|
| Hybrid (Recommended) | 60-62 MB | 62-65 MB | +5-7 MB |
| Partial Mobile | 65-68 MB | 68-72 MB | +10-14 MB |
| Cloud Functions | 55-58 MB | 58-60 MB | +0-2 MB |
| Full Implementation | 85-95 MB | 90-105 MB | +30-47 MB |

**Primary size increases come from:**
- HTTP client improvements (~1 MB)
- Background task libraries (~3-5 MB)
- Additional UI components (~1-2 MB)
- Calculation/parsing libraries (~2-4 MB if porting)

---

## Package Requirements

### Hybrid Approach (Minimal)
```yaml
# Add to pubspec.yaml
dependencies:
  http: ^1.1.0              # Already included
  workmanager: ^0.5.2       # Background tasks (Android)
  background_fetch: ^1.2.0  # Background tasks (iOS)
  connectivity_plus: ^5.0.0 # Network status
```

**Additional Size:** ~5 MB

### Partial Mobile Approach
```yaml
dependencies:
  http: ^1.1.0
  html: ^0.15.4             # Web scraping
  xml: ^6.4.0               # XML parsing
  workmanager: ^0.5.2
  background_fetch: ^1.2.0
  connectivity_plus: ^5.0.0
```

**Additional Size:** ~12 MB

---

## Battery Impact Analysis

### Hybrid Approach
- **Network calls:** 2-5 API requests
- **Background execution:** 5-15 seconds
- **Battery impact:** MINIMAL (< 1% per day)

### Full Mobile Approach
- **Network calls:** 15-30 HTTP requests + scraping
- **Background execution:** 60-180 seconds
- **Web parsing:** CPU intensive
- **Battery impact:** MODERATE (2-5% per day)

---

## Security Considerations

### Backend API Approach ✅
- Credentials stored on server (environment variables)
- Mobile app only needs API key
- HTTPS encryption for all communication
- Rate limiting and authentication

### Full Mobile Approach ⚠️
- Pension portal credentials on device (encrypted storage)
- Vulnerable to reverse engineering
- Compliance issues with storing passwords locally

---

## Development Time Estimates

### Hybrid Approach (RECOMMENDED)
| Task | Hours | Complexity |
|------|-------|------------|
| Backend API endpoints | 8-12h | Medium |
| Mobile trigger UI | 4-6h | Low |
| Background scheduling | 6-8h | Medium |
| Error handling | 4-6h | Low |
| Testing | 8-12h | Medium |
| **TOTAL** | **30-44h** | **(1-2 weeks)** |

### Partial Mobile Approach
| Task | Hours | Complexity |
|------|-------|------------|
| Backend API endpoints | 6-8h | Medium |
| Port FX rate fetch | 2-4h | Low |
| Port price scraping | 10-15h | High |
| Mobile calculations | 6-8h | Medium |
| Background scheduling | 8-12h | Medium-High |
| Testing | 12-16h | High |
| **TOTAL** | **44-63h** | **(2-3 weeks)** |

### Cloud Functions Approach
| Task | Hours | Complexity |
|------|-------|------------|
| Learn Supabase Edge Functions | 8-12h | Medium-High |
| Port Python → TypeScript | 20-30h | High |
| Setup deployment pipeline | 4-6h | Medium |
| Mobile integration | 4-6h | Low |
| Testing | 8-12h | Medium |
| **TOTAL** | **44-66h** | **(2-3 weeks)** |

---

## Maintenance Considerations

### Hybrid Approach ✅
- **Backend:** Existing Python code, minimal changes
- **Mobile:** Simple API calls, easy to maintain
- **Updates:** Backend changes don't require app updates

### Full Mobile Approach ⚠️
- **Mobile:** Complex scraping logic to maintain
- **Updates:** Every website change requires app update
- **Platform differences:** iOS/Android specific issues

---

## Final Recommendation

### **🏆 HYBRID APPROACH - Backend API + Mobile Trigger**

**Reasoning:**
1. **Optimal app size:** Only +5-7 MB increase
2. **Fast development:** 1-2 weeks vs 4-6 weeks
3. **Maintainable:** Separation of concerns
4. **Battery efficient:** Minimal mobile processing
5. **Secure:** Credentials stay on server
6. **Reliable:** Server has more resources and stability

**Trade-off:**
- Requires backend service (can be hosted on free tier VPS or Railway)
- Network dependency (acceptable for financial data updates)

---

## Alternative: If No Backend Available

If maintaining a backend is not an option:

### **🥈 CLOUD FUNCTIONS (Supabase Edge Functions)**

**Benefits:**
- No backend server to maintain
- Automatic scaling
- Integrated with existing Supabase setup
- No app size increase

**Costs:**
- Requires Supabase Pro: $25/month
- Or implement on free tier with limitations (2M Edge Function invocations/month)

---

## Next Steps

See companion file: **`MOBILE_DAILY_UPDATE_TASKLIST.md`**
