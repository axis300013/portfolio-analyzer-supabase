# Mobile Daily Update - Implementation Task List
**Approach:** Hybrid (Backend API + Mobile Trigger)  
**Estimated Time:** 1-2 weeks (30-44 hours)  
**App Size Increase:** +5-7 MB

---

## Prerequisites

- [ ] Review analysis document: `MOBILE_DAILY_UPDATE_ANALYSIS.md`
- [ ] Decide on backend hosting (Railway, VPS, or local for testing)
- [ ] Ensure Supabase database is accessible from backend
- [ ] Have mobile development environment set up

---

## Phase 1: Backend API Layer (Week 1, Days 1-3)

### Task 1.1: Create ETL API Endpoints (8-12 hours)

#### Subtasks:
- [ ] **1.1.1** Create new file: `backend/app/routers/etl.py`
  - Import existing ETL functions
  - Add FastAPI router boilerplate
  - Add authentication middleware
  
- [ ] **1.1.2** Implement `/api/etl/run-daily-update` endpoint
  ```python
  @router.post("/run-daily-update")
  async def run_daily_update(background_tasks: BackgroundTasks):
      # Trigger all ETL steps asynchronously
      # Return job_id for status tracking
  ```
  
- [ ] **1.1.3** Implement individual step endpoints:
  - [ ] `POST /api/etl/fetch-fx-rates`
  - [ ] `POST /api/etl/fetch-prices`
  - [ ] `POST /api/etl/calculate-portfolio`
  - [ ] `POST /api/etl/copy-wealth-values`
  - [ ] `POST /api/etl/fetch-pensions`
  
- [ ] **1.1.4** Implement status tracking endpoint
  ```python
  @router.get("/status/{job_id}")
  async def get_job_status(job_id: str):
      # Return current status, progress, errors
  ```
  
- [ ] **1.1.5** Add job status storage (Redis or database table)
  - Create `etl_jobs` table
  - Fields: id, status, started_at, completed_at, error_message, steps_completed
  
- [ ] **1.1.6** Implement error handling and logging
  - Catch exceptions in ETL functions
  - Store error details in job status
  - Add comprehensive logging

#### Files to Create/Modify:
- `backend/app/routers/etl.py` (NEW)
- `backend/app/main.py` (add router)
- `backend/app/models.py` (add ETL job models)
- `sql/create_etl_jobs_table.sql` (NEW)

#### Testing Checklist:
- [ ] Test each endpoint with Postman/curl
- [ ] Verify job status updates correctly
- [ ] Test error handling (invalid inputs, network failures)
- [ ] Check response times (should be < 500ms for trigger, background for execution)

---

### Task 1.2: Add API Authentication (4-6 hours)

#### Subtasks:
- [ ] **1.2.1** Choose authentication method:
  - Option A: Simple API key (fast, less secure)
  - Option B: JWT tokens (more secure, recommended)
  
- [ ] **1.2.2** Implement authentication middleware
  - Create `backend/app/auth.py`
  - Add token validation
  - Add rate limiting (prevent abuse)
  
- [ ] **1.2.3** Create API key management
  - Store keys in database
  - Add key generation endpoint (admin only)
  - Add key revocation
  
- [ ] **1.2.4** Update mobile app to include API key
  - Add API_KEY to `.env` file
  - Add to Supabase dashboard as environment variable

#### Files to Create/Modify:
- `backend/app/auth.py` (NEW)
- `backend/app/routers/etl.py` (add authentication decorator)
- `.env.example` (add API_KEY)

#### Testing Checklist:
- [ ] Test authenticated requests work
- [ ] Test unauthenticated requests are rejected (401)
- [ ] Test invalid API keys are rejected
- [ ] Test rate limiting works

---

### Task 1.3: Deploy Backend API (2-4 hours)

#### Subtasks:
- [ ] **1.3.1** Choose hosting platform:
  - Railway (recommended, easy deployment)
  - Heroku (easy but paid)
  - VPS (DigitalOcean, Linode)
  - Local (for testing only)
  
- [ ] **1.3.2** Prepare deployment:
  - Update `requirements.txt`
  - Create `Procfile` or `railway.toml`
  - Set environment variables on platform
  
- [ ] **1.3.3** Deploy and test:
  - Deploy backend
  - Test endpoints from public URL
  - Verify scheduled tasks work (if applicable)

#### Files to Create/Modify:
- `Procfile` or `railway.toml` (NEW)
- `README.md` (add deployment instructions)
- `.env.production` (NEW, for production settings)

#### Testing Checklist:
- [ ] Backend is accessible from public URL
- [ ] All endpoints return expected responses
- [ ] Database connection works from deployed instance
- [ ] Environment variables are correctly loaded

---

## Phase 2: Mobile UI Integration (Week 1-2, Days 4-6)

### Task 2.1: Create Daily Update Service (4-6 hours)

#### Subtasks:
- [ ] **2.1.1** Create service file: `mobile/lib/services/daily_update_service.dart`
  - Add method to trigger full update
  - Add method to get update status
  - Add method to fetch individual steps
  
- [ ] **2.1.2** Implement API calls:
  ```dart
  class DailyUpdateService {
    Future<String> runDailyUpdate() async {
      // POST to /api/etl/run-daily-update
      // Return job_id
    }
    
    Future<UpdateStatus> getStatus(String jobId) async {
      // GET /api/etl/status/{job_id}
      // Return status object
    }
  }
  ```
  
- [ ] **2.1.3** Add error handling and retry logic
  - Network timeout handling
  - Retry failed requests (exponential backoff)
  - Parse and display error messages

#### Files to Create/Modify:
- `mobile/lib/services/daily_update_service.dart` (NEW)
- `mobile/lib/models/update_status.dart` (NEW)
- `mobile/lib/utils/api_client.dart` (add base URL config)

#### Testing Checklist:
- [ ] Service successfully triggers backend update
- [ ] Status polling works correctly
- [ ] Errors are properly caught and handled
- [ ] Retry logic works as expected

---

### Task 2.2: Create Daily Update Screen (6-8 hours)

#### Subtasks:
- [ ] **2.2.1** Create UI file: `mobile/lib/screens/daily_update_screen.dart`
  - Add "Run Update" button
  - Add progress indicator
  - Add step-by-step status list
  - Add last update timestamp
  
- [ ] **2.2.2** Implement state management:
  - Use Provider or Riverpod for state
  - Track update progress
  - Handle loading/success/error states
  
- [ ] **2.2.3** Design UI layout:
  ```
  ┌─────────────────────────────────┐
  │ Daily Update                    │
  ├─────────────────────────────────┤
  │ Last Update: Jan 13, 9:30 AM   │
  │                                 │
  │ [Run Daily Update]              │
  │                                 │
  │ ✓ Fetch FX Rates (Complete)    │
  │ ↻ Fetch Prices (In Progress)   │
  │ ○ Calculate Portfolio           │
  │ ○ Copy Wealth Values            │
  │ ○ Fetch Pensions                │
  │                                 │
  │ [View Logs]                     │
  └─────────────────────────────────┘
  ```
  
- [ ] **2.2.4** Add animations and loading indicators
  - Spinning loader during update
  - Check marks for completed steps
  - Error icons for failed steps
  
- [ ] **2.2.5** Add navigation integration
  - Add to main navigation menu
  - Or add to settings screen
  - Or add as floating action button on dashboard

#### Files to Create/Modify:
- `mobile/lib/screens/daily_update_screen.dart` (NEW)
- `mobile/lib/providers/update_provider.dart` (NEW)
- `mobile/lib/main.dart` (add route)
- `mobile/lib/widgets/update_step_item.dart` (NEW, reusable widget)

#### Testing Checklist:
- [ ] Screen loads without errors
- [ ] Update button triggers backend correctly
- [ ] Progress updates display in real-time
- [ ] Success state shows check marks
- [ ] Error state shows error messages
- [ ] Last update timestamp persists after app restart

---

### Task 2.3: Add Manual Refresh to Existing Screens (2-4 hours)

#### Subtasks:
- [ ] **2.3.1** Add pull-to-refresh on Dashboard
  - Trigger daily update on pull down
  - Show loading indicator
  - Reload data after completion
  
- [ ] **2.3.2** Add refresh button on Portfolio screen
  - Add FloatingActionButton with refresh icon
  - Trigger portfolio calculation
  - Reload portfolio data
  
- [ ] **2.3.3** Add refresh button on Wealth screen
  - Trigger wealth value copy
  - Reload wealth data

#### Files to Modify:
- `mobile/lib/screens/dashboard_screen.dart`
- `mobile/lib/screens/portfolio_screen.dart`
- `mobile/lib/screens/wealth_screen.dart`

#### Testing Checklist:
- [ ] Pull-to-refresh works smoothly
- [ ] Data refreshes after update completes
- [ ] Loading indicators appear correctly
- [ ] Error messages display if update fails

---

## Phase 3: Background Scheduling (Week 2, Days 7-9)

### Task 3.1: Implement Android Background Tasks (6-8 hours)

#### Subtasks:
- [ ] **3.1.1** Add `workmanager` package to `pubspec.yaml`
  ```yaml
  dependencies:
    workmanager: ^0.5.2
  ```
  
- [ ] **3.1.2** Configure WorkManager in `MainActivity.kt`
  ```kotlin
  // Add WorkManager initialization
  ```
  
- [ ] **3.1.3** Create background task handler
  ```dart
  void callbackDispatcher() {
    Workmanager().executeTask((task, inputData) async {
      // Trigger daily update
      await DailyUpdateService().runDailyUpdate();
      return Future.value(true);
    });
  }
  ```
  
- [ ] **3.1.4** Schedule periodic task:
  ```dart
  Workmanager().registerPeriodicTask(
    "daily-update",
    "dailyUpdate",
    frequency: Duration(hours: 24),
    initialDelay: Duration(hours: 9), // 9 AM
    constraints: Constraints(
      networkType: NetworkType.connected,
    ),
  );
  ```
  
- [ ] **3.1.5** Add battery optimization exemption request
  - Show dialog explaining why background tasks are needed
  - Request to disable battery optimization for app

#### Files to Create/Modify:
- `mobile/android/app/src/main/kotlin/MainActivity.kt`
- `mobile/lib/services/background_service.dart` (NEW)
- `mobile/pubspec.yaml`

#### Testing Checklist:
- [ ] Background task registers successfully
- [ ] Task executes at scheduled time (test with 15-min interval first)
- [ ] Task runs even when app is closed
- [ ] Task respects network constraints
- [ ] Battery optimization doesn't kill task

---

### Task 3.2: Implement iOS Background Refresh (4-6 hours)

#### Subtasks:
- [ ] **3.2.1** Add `background_fetch` package to `pubspec.yaml`
  ```yaml
  dependencies:
    background_fetch: ^1.2.0
  ```
  
- [ ] **3.2.2** Configure background modes in `Info.plist`
  ```xml
  <key>UIBackgroundModes</key>
  <array>
    <string>fetch</string>
    <string>processing</string>
  </array>
  ```
  
- [ ] **3.2.3** Register background fetch task
  ```dart
  BackgroundFetch.configure(
    BackgroundFetchConfig(
      minimumFetchInterval: 15, // iOS minimum
      stopOnTerminate: false,
      startOnBoot: true,
      enableHeadless: true,
    ),
    (String taskId) async {
      // Trigger daily update
      await DailyUpdateService().runDailyUpdate();
      BackgroundFetch.finish(taskId);
    },
  );
  ```
  
- [ ] **3.2.4** Handle iOS limitations:
  - iOS decides when to run background tasks
  - Can't guarantee exact time
  - Show user notification when update completes (optional)

#### Files to Create/Modify:
- `mobile/ios/Runner/Info.plist`
- `mobile/lib/services/background_service.dart`
- `mobile/pubspec.yaml`

#### Testing Checklist:
- [ ] Background fetch registers successfully on iOS
- [ ] Task runs when iOS schedules it (test by using app regularly)
- [ ] Task respects iOS restrictions
- [ ] App doesn't crash when background task runs
- [ ] Notification appears after successful update (if implemented)

---

### Task 3.3: Add Scheduling Preferences (2-4 hours)

#### Subtasks:
- [ ] **3.3.1** Create settings screen section
  - Toggle for auto-update (on/off)
  - Time picker for preferred update time
  - Network preference (WiFi only / Any network)
  
- [ ] **3.3.2** Implement settings persistence
  - Use SharedPreferences or Hive
  - Store user preferences
  - Apply preferences when scheduling tasks
  
- [ ] **3.3.3** Update background service to respect preferences
  - Check if auto-update is enabled
  - Reschedule task when time preference changes
  - Check network type before running

#### Files to Create/Modify:
- `mobile/lib/screens/settings_screen.dart` (add section)
- `mobile/lib/services/preferences_service.dart` (NEW)
- `mobile/lib/services/background_service.dart` (check preferences)

#### Testing Checklist:
- [ ] Settings persist after app restart
- [ ] Toggling auto-update enables/disables background task
- [ ] Changing time reschedules task correctly
- [ ] Network preference is respected

---

## Phase 4: Optimization & Polish (Week 2, Days 10-12)

### Task 4.1: Implement Smart Updates (4-6 hours)

#### Subtasks:
- [ ] **4.1.1** Add "last update" tracking
  - Store timestamp of last successful update
  - Display on UI
  - Skip update if already run today
  
- [ ] **4.1.2** Implement conditional updates:
  ```dart
  // Only fetch prices on trading days (Mon-Fri)
  if (DateTime.now().weekday <= 5) {
    await fetchPrices();
  }
  
  // Only fetch pensions on specific days (e.g., after market close)
  if (DateTime.now().hour >= 18) {
    await fetchPensions();
  }
  ```
  
- [ ] **4.1.3** Add quick refresh option
  - Skip expensive operations (pension scraping)
  - Only update FX rates and portfolio calculations
  - Complete in < 10 seconds

#### Files to Create/Modify:
- `mobile/lib/services/daily_update_service.dart`
- `mobile/lib/screens/daily_update_screen.dart`

#### Testing Checklist:
- [ ] Duplicate updates on same day are prevented
- [ ] Weekday logic works correctly
- [ ] Quick refresh completes fast
- [ ] Full refresh still available when needed

---

### Task 4.2: Add Offline Mode Handling (2-4 hours)

#### Subtasks:
- [ ] **4.2.1** Add connectivity check
  ```dart
  final connectivity = await Connectivity().checkConnectivity();
  if (connectivity == ConnectivityResult.none) {
    // Show offline message
    return;
  }
  ```
  
- [ ] **4.2.2** Handle offline gracefully:
  - Show "No internet" message
  - Don't trigger update
  - Queue update for when online
  
- [ ] **4.2.3** Add retry on connection restore:
  - Listen to connectivity changes
  - Auto-retry failed updates when online

#### Files to Create/Modify:
- `mobile/lib/services/daily_update_service.dart`
- `mobile/lib/utils/connectivity_helper.dart` (NEW)
- `mobile/pubspec.yaml` (add connectivity_plus)

#### Testing Checklist:
- [ ] Offline state is detected correctly
- [ ] Appropriate message is shown when offline
- [ ] Update retries when connection restored
- [ ] No crashes when going offline mid-update

---

### Task 4.3: Add Error Reporting & Logging (2-4 hours)

#### Subtasks:
- [ ] **4.3.1** Implement local logging
  - Log all update attempts
  - Log errors with stack traces
  - Store last 100 log entries
  
- [ ] **4.3.2** Add logs viewer in app
  - Create logs screen
  - Display recent updates and errors
  - Add export/share logs button
  
- [ ] **4.3.3** Implement analytics (optional)
  - Track update success rate
  - Track average update duration
  - Track most common errors

#### Files to Create/Modify:
- `mobile/lib/services/log_service.dart` (NEW)
- `mobile/lib/screens/logs_screen.dart` (NEW)
- `mobile/lib/models/log_entry.dart` (NEW)

#### Testing Checklist:
- [ ] Logs are recorded correctly
- [ ] Logs screen displays entries
- [ ] Export logs works
- [ ] Old logs are cleaned up (don't grow indefinitely)

---

### Task 4.4: Performance Optimization (2-4 hours)

#### Subtasks:
- [ ] **4.4.1** Implement caching
  - Cache FX rates for 24 hours
  - Cache last successful update result
  - Don't re-fetch if fresh data exists
  
- [ ] **4.4.2** Optimize API calls
  - Batch requests where possible
  - Use compression for large responses
  - Implement request timeout (30s)
  
- [ ] **4.4.3** Reduce memory usage
  - Stream large responses instead of loading all at once
  - Clear caches after update completes
  - Dispose resources properly

#### Files to Modify:
- `mobile/lib/services/daily_update_service.dart`
- `mobile/lib/utils/cache_manager.dart` (NEW)

#### Testing Checklist:
- [ ] Cached data is used when available
- [ ] Cache expires correctly
- [ ] Memory usage is reasonable (< 100 MB during update)
- [ ] No memory leaks after multiple updates

---

### Task 4.5: UI Polish & User Experience (4-6 hours)

#### Subtasks:
- [ ] **4.5.1** Add animations
  - Smooth transitions between states
  - Loading animation
  - Success/error animations
  
- [ ] **4.5.2** Improve visual feedback
  - Progress bar with percentage
  - Estimated time remaining
  - Color-coded status (green/yellow/red)
  
- [ ] **4.5.3** Add helpful messages
  - Explain what each step does
  - Show why update failed
  - Provide troubleshooting tips
  
- [ ] **4.5.4** Implement notifications (optional)
  - Notify when update completes
  - Notify on error (if critical)
  - Allow user to disable notifications

#### Files to Modify:
- `mobile/lib/screens/daily_update_screen.dart`
- `mobile/lib/widgets/update_step_item.dart`
- `mobile/lib/services/notification_service.dart` (NEW, if implementing notifications)

#### Testing Checklist:
- [ ] Animations are smooth (60fps)
- [ ] Progress updates are accurate
- [ ] Messages are helpful and clear
- [ ] Notifications work (if implemented)
- [ ] UI looks good on small screens

---

## Testing & Quality Assurance (Week 2, Days 13-14)

### Task 5.1: Unit Testing (4-6 hours)

#### Test Coverage:
- [ ] Test `DailyUpdateService` API calls
- [ ] Test `BackgroundService` scheduling logic
- [ ] Test error handling in all services
- [ ] Test state management (UpdateProvider)
- [ ] Target: 80%+ code coverage

#### Files to Create:
- `mobile/test/services/daily_update_service_test.dart`
- `mobile/test/services/background_service_test.dart`
- `mobile/test/providers/update_provider_test.dart`

---

### Task 5.2: Integration Testing (4-6 hours)

#### Test Scenarios:
- [ ] Full update flow (trigger → progress → completion)
- [ ] Error scenarios (network failure, API error, timeout)
- [ ] Background task execution
- [ ] Offline mode handling
- [ ] Settings changes affecting behavior

#### Files to Create:
- `mobile/integration_test/daily_update_flow_test.dart`
- `mobile/integration_test/background_task_test.dart`

---

### Task 5.3: Manual Testing Checklist (2-4 hours)

#### Android Testing:
- [ ] Test on Android 10, 11, 12, 13, 14
- [ ] Test with different network conditions (WiFi, 4G, offline)
- [ ] Test battery optimization scenarios
- [ ] Test after device reboot
- [ ] Test in foreground and background

#### iOS Testing:
- [ ] Test on iOS 14, 15, 16, 17
- [ ] Test with different network conditions
- [ ] Test background refresh scenarios
- [ ] Test after app force-quit
- [ ] Test in low power mode

#### Common Tests:
- [ ] App size is acceptable (< 70 MB)
- [ ] Battery usage is minimal (< 2% per update)
- [ ] Network usage is reasonable
- [ ] No crashes during update
- [ ] UI remains responsive

---

## Deployment & Release (Week 2, Days 15-16)

### Task 6.1: Build & Test Release Versions (2-3 hours)

#### Subtasks:
- [ ] Build Android APK/AAB
- [ ] Build iOS IPA
- [ ] Test release builds on real devices
- [ ] Verify ProGuard/R8 doesn't break functionality
- [ ] Check app size of release builds

---

### Task 6.2: Update Documentation (1-2 hours)

#### Documents to Update:
- [ ] `README.md` - Add daily update feature
- [ ] `MOBILE_APP_SETUP.md` - Add backend setup instructions
- [ ] `USER_GUIDE.md` - Document how to use daily update
- [ ] `CHANGELOG.md` - Add version notes

---

### Task 6.3: Deploy to Stores (2-4 hours)

#### App Store:
- [ ] Update app description
- [ ] Add screenshots of new feature
- [ ] Submit for review
- [ ] Monitor review status

#### Google Play:
- [ ] Update app description
- [ ] Add screenshots
- [ ] Submit release
- [ ] Monitor rollout

---

## Post-Launch Tasks

### Monitoring (Ongoing)
- [ ] Monitor backend API usage
- [ ] Track update success rate
- [ ] Watch for crash reports
- [ ] Collect user feedback

### Iteration (As needed)
- [ ] Fix bugs reported by users
- [ ] Optimize performance based on metrics
- [ ] Add requested features
- [ ] Improve error messages based on feedback

---

## Rollback Plan

If major issues occur:

1. **Disable background updates** via server flag
2. **Remove from app stores** if critical bug
3. **Deploy hotfix** with feature flag to disable
4. **Communicate** with users about issue

---

## Success Criteria

### Functionality:
- ✅ Daily update successfully updates all data
- ✅ Background tasks work reliably on both platforms
- ✅ Error handling prevents crashes
- ✅ UI clearly communicates status

### Performance:
- ✅ App size increase < 10 MB
- ✅ Update completes in < 60 seconds
- ✅ Battery usage < 2% per day
- ✅ Network usage < 5 MB per update

### Quality:
- ✅ No crashes during normal operation
- ✅ 80%+ test coverage
- ✅ Positive user feedback (> 4.5 stars maintained)
- ✅ < 1% error rate in production

---

## Estimated Total Time

| Phase | Hours | Days |
|-------|-------|------|
| Backend API | 12-18h | 2-3 days |
| Mobile UI | 12-18h | 2-3 days |
| Background Tasks | 12-18h | 2-3 days |
| Optimization | 10-16h | 2-3 days |
| Testing | 10-16h | 2-3 days |
| Deployment | 5-9h | 1-2 days |
| **TOTAL** | **61-95h** | **11-17 days** |

**Realistic estimate with buffer:** 2-3 weeks

---

## Notes

- This task list assumes hybrid approach (recommended)
- Times are estimates for experienced developer
- Add 30-50% time if learning new technologies
- Can be parallelized if multiple developers
- Backend and mobile work can be done simultaneously

---

## Dependencies Between Tasks

```
Backend API (1.1) → Mobile Service (2.1) → Mobile UI (2.2)
                                           ↓
                         Background Tasks (3.1, 3.2)
                                           ↓
                          Optimization (4.1-4.5)
                                           ↓
                            Testing (5.1-5.3)
                                           ↓
                          Deployment (6.1-6.3)
```

**Critical path:** Backend API → Mobile Service → Mobile UI → Testing → Deployment
**Minimum time:** ~2 weeks following critical path

---

*Last Updated: 2026-01-13*
