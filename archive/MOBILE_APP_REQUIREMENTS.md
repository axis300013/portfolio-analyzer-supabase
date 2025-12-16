# Portfolio Analyzer Mobile App - Requirements & Architecture

## Overview
Flutter mobile application (iOS/Android/Web) that connects to Supabase backend to display portfolio and wealth management data.

## Completed Features (December 6, 2025)

### 1. Authentication System
- **Sign Up**: Email + password registration
- **Email Verification**: Supabase automatic verification emails
- **Login**: Secure authentication with Supabase Auth
- **Session Management**: Persistent login state across app restarts

### 2. Main Navigation (Bottom Navigation Bar)
Four main screens accessible via bottom tabs:

#### **Dashboard Screen**
- Overview of total portfolio value
- Summary of wealth categories
- Quick stats display

#### **Portfolio Screen** ⭐ PRIMARY FEATURE
- **Date Picker**: Select any historical date to view portfolio snapshot
  - Shows all available dates from Supabase `portfolio_values_daily` table
  - Currently displays: Dec 2-6, 2025 (5 dates)
  - Default selection: Most recent date
- **Holdings List**: All portfolio instruments with:
  - Instrument name and ticker
  - Quantity held
  - Current price in original currency
  - Total value in HUF
  - Currency indicator
- **Total Portfolio Value**: Sum of all holdings in HUF
- **Real-time Data**: Syncs with Supabase cloud database

#### **Wealth Screen**
- Display of all wealth categories:
  - Cash accounts
  - Property/Real Estate
  - Pension funds
  - Other assets
  - Liabilities
- Categorization by type (Asset vs Liability)
- Values displayed in HUF

#### **Trends Screen**
- Placeholder for future trend analysis
- Historical portfolio performance charts (planned)

### 3. Data Architecture

#### **Supabase Tables Used**
1. **`portfolio_values_daily`**
   - Columns: `id`, `portfolio_id`, `snapshot_date`, `instrument_id`, `quantity`, `price`, `instrument_currency`, `fx_rate`, `value_huf`, `calculated_at`
   - Primary key: `id` (auto-increment)
   - Unique constraint: `(portfolio_id, snapshot_date, instrument_id)`
   - Purpose: Daily snapshots of each portfolio instrument

2. **`instruments`**
   - Columns: `id`, `name`, `ticker`, `asset_class`, `currency`, etc.
   - Purpose: Master list of investable instruments

3. **`wealth_categories`**
   - Columns: `id`, `category_type`, `name`, `is_liability`, `sort_order`
   - Purpose: Defines wealth categories (cash, property, pension, loans, etc.)

4. **`wealth_values`**
   - Columns: `id`, `wealth_category_id`, `value_date`, `present_value`
   - Primary key: `id` (auto-increment)
   - Unique constraint: `(wealth_category_id, value_date)`
   - Purpose: Daily values for each wealth category

5. **`total_wealth_snapshots`**
   - Columns: `id`, `snapshot_date`, `portfolio_value_huf`, `other_assets_huf`, `total_liabilities_huf`, `net_wealth_huf`, `cash_huf`, `property_huf`, `pension_huf`, `other_huf`, `created_at`
   - Primary key: `id` (auto-increment)
   - Unique constraint: `snapshot_date`
   - Purpose: Aggregated daily wealth summary

#### **Row Level Security (RLS)**
- All tables have RLS policies enabled
- Public read access for authenticated users
- No write access from mobile app (read-only)

### 4. Technical Stack

#### **Frontend**
- **Framework**: Flutter 3.27.1
- **Language**: Dart
- **Platforms**: 
  - ✅ Web (Chrome) - Currently tested and working
  - 📱 Android - Not yet built
  - 🍎 iOS - Not yet built

#### **Key Dependencies** (95 total)
- `supabase_flutter: ^2.9.2` - Supabase client SDK
- `postgrest: ^2.4.2` - PostgreSQL REST API client
- `intl: ^0.19.0` - Internationalization and date formatting
- `fl_chart: ^0.70.1` - Charts for trends (future use)
- `shared_preferences: ^2.3.4` - Local storage
- `url_launcher: ^6.3.1` - External links

#### **Backend**
- **Database**: Supabase (PostgreSQL cloud)
- **Project**: `hrlzrirsvifxsnccxvsa`
- **URL**: `https://hrlzrirsvifxsnccxvsa.supabase.co`
- **Authentication**: Supabase Auth with email/password

#### **Configuration**
- `.env` file with Supabase credentials:
  - `SUPABASE_URL`
  - `SUPABASE_ANON_KEY`
- Flutter loads `.env` via `flutter_dotenv` package

### 5. Data Flow

```
Desktop App (Streamlit) 
    ↓
    [Run Daily Update Button]
    ↓
Backend API (FastAPI on port 8000)
    ↓
    [ETL Process: Fetch prices, calculate values]
    ↓
Supabase Cloud Database
    ↓
    [Real-time sync]
    ↓
Mobile App (Flutter)
    ↓
    [Display to user]
```

### 6. Key Features Implementation

#### **Date Picker Logic**
```dart
// File: mobile/lib/screens/portfolio/portfolio_screen.dart
Future<void> _loadAvailableDates() async {
  final dates = await _supabaseService.getAvailablePortfolioDates();
  setState(() {
    _availableDates = dates;
    if (dates.isNotEmpty) {
      _selectedDate = dates.first; // Most recent date
    }
  });
}
```

#### **Portfolio Data Fetch**
```dart
// File: mobile/lib/services/supabase_service.dart
Future<List<PortfolioHolding>> getPortfolioHoldings(DateTime date) async {
  final response = await _supabase
      .from('portfolio_values_daily')
      .select('*, instruments(*)')
      .eq('snapshot_date', DateFormat('yyyy-MM-dd').format(date));
  
  return (response as List).map((json) => 
    PortfolioHolding.fromJson(json)
  ).toList();
}
```

### 7. Current Limitations

1. **Data Updates**: 
   - Mobile app is read-only
   - Data must be updated via desktop app's "Run Daily Update" button
   - Manual SQL import needed if backend is offline

2. **Platform Support**:
   - Only tested on Web (Chrome)
   - Android/iOS builds not yet tested

3. **Authentication**:
   - Basic email/password only
   - No social login (Google, Apple, etc.)
   - No password reset flow

4. **Offline Support**:
   - No offline data caching
   - Requires internet connection

5. **Trends Screen**:
   - Not yet implemented
   - Placeholder only

### 8. Setup Instructions

#### **Prerequisites**
- Flutter SDK 3.27.1 installed
- VS Code with Flutter extension
- Supabase project with credentials

#### **Installation**
```bash
cd mobile
flutter pub get
```

#### **Configuration**
Create `.env` file in `mobile/` directory:
```
SUPABASE_URL=https://hrlzrirsvifxsnccxvsa.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
```

#### **Run Web Version**
```bash
cd mobile
flutter run -d chrome
```

#### **Build for Production**
```bash
# Web
flutter build web

# Android
flutter build apk

# iOS (macOS only)
flutter build ios
```

### 9. Testing Status

| Feature | Status | Notes |
|---------|--------|-------|
| Sign Up | ✅ Tested | Email verification works |
| Login | ✅ Tested | Session persists |
| Dashboard | ✅ Working | Shows summary |
| Portfolio Screen | ✅ Working | Date picker + holdings list |
| Wealth Screen | ✅ Working | All categories display |
| Trends Screen | ⚠️ Placeholder | Not implemented |
| Date Picker | ✅ Working | Shows 5 dates (Dec 2-6) |
| Data Sync | ✅ Working | Real-time from Supabase |
| Hot Reload | ✅ Working | Press 'r' in terminal |
| Web Performance | ✅ Good | Loads in <2 seconds |

### 10. Known Issues & Fixes

#### **Issue 1: Today's date not selectable** ✅ FIXED
- **Problem**: Dec 6, 2025 not appearing in date picker
- **Root Cause**: Backend wrote data to local Docker instead of Supabase
- **Solution**: Manual SQL import with sequence fix
- **Status**: Resolved - Dec 6 now selectable

#### **Issue 2: Duplicate key errors during import** ✅ FIXED
- **Problem**: SQL INSERT failed with "duplicate key value violates unique constraint"
- **Root Cause**: Auto-increment sequences out of sync
- **Solution**: Added `setval()` to reset sequences before INSERT
- **Status**: Resolved

#### **Issue 3: Wrong column names** ✅ FIXED
- **Problem**: `liquid_assets_huf` column doesn't exist
- **Root Cause**: Table schema uses `cash_huf`, `property_huf`, etc.
- **Solution**: Updated SQL with correct column names
- **Status**: Resolved

### 11. Future Enhancements

#### **Priority 1: Essential**
- [ ] Password reset flow
- [ ] User profile management
- [ ] Error handling improvements
- [ ] Loading indicators
- [ ] Empty state designs

#### **Priority 2: User Experience**
- [ ] Offline data caching
- [ ] Pull-to-refresh on all screens
- [ ] Search/filter holdings
- [ ] Export portfolio to PDF/Excel
- [ ] Push notifications for daily updates

#### **Priority 3: Analytics**
- [ ] Implement Trends screen
- [ ] Historical performance charts
- [ ] Asset allocation pie charts
- [ ] Year-over-year comparisons
- [ ] Return calculations (IRR, XIRR)

#### **Priority 4: Advanced**
- [ ] Multi-portfolio support
- [ ] Custom wealth categories
- [ ] Budget tracking
- [ ] Goal setting
- [ ] Social login (Google, Apple)

### 12. Development Guidelines

#### **Code Style**
- Follow Flutter/Dart conventions
- Use `flutter analyze` before committing
- Format code with `dart format .`

#### **State Management**
- Currently using `setState()` for local state
- Consider upgrading to Riverpod or Bloc for complex state

#### **Error Handling**
- Wrap Supabase calls in try-catch
- Display user-friendly error messages
- Log errors for debugging

#### **Testing**
- Write unit tests for services
- Add widget tests for screens
- Integration tests for critical flows

### 13. Deployment Checklist

#### **Before Production**
- [ ] Remove debug prints
- [ ] Enable production Supabase policies
- [ ] Add analytics (Firebase, Mixpanel)
- [ ] Set up crash reporting (Sentry, Firebase Crashlytics)
- [ ] Create privacy policy
- [ ] Add app icons and splash screens
- [ ] Test on physical devices (Android + iOS)
- [ ] Performance profiling
- [ ] Security audit
- [ ] App Store/Play Store metadata

### 14. Support & Documentation

#### **Mobile App Structure**
```
mobile/
├── lib/
│   ├── main.dart                 # App entry point
│   ├── screens/
│   │   ├── auth/                 # Login, signup screens
│   │   ├── dashboard/            # Dashboard screen
│   │   ├── portfolio/            # Portfolio screen with date picker
│   │   ├── wealth/               # Wealth categories screen
│   │   └── trends/               # Trends placeholder
│   ├── services/
│   │   └── supabase_service.dart # Supabase API client
│   ├── models/                   # Data models
│   └── widgets/                  # Reusable UI components
├── assets/
│   └── .env                      # Supabase credentials
├── web/                          # Web platform files
├── android/                      # Android platform files
├── ios/                          # iOS platform files
└── pubspec.yaml                  # Dependencies
```

#### **Debug Output Example**
```
🔍 Raw data from Supabase: 45 rows
🔍 First row: {snapshot_date: 2025-12-06}
🔍 Last row: {snapshot_date: 2025-12-02}
🔍 Unique dates: [2025-12-06, 2025-12-05, 2025-12-04, 2025-12-03, 2025-12-02]
📅 Available dates from Supabase: [2025-12-06, 2025-12-05, 2025-12-04, 2025-12-03, 2025-12-02]
📅 Total dates: 5
📅 Selected date: 2025-12-06
```

---

## Summary

**Mobile app is FULLY FUNCTIONAL** with:
- ✅ Authentication working
- ✅ 4 main screens implemented
- ✅ Date picker showing all available dates
- ✅ Real-time data sync with Supabase
- ✅ Web version tested and working
- ✅ Ready for Android/iOS builds

**Next Steps:**
1. Test desktop app (original portable version)
2. Fix any desktop app startup issues
3. Consider mobile app enhancements
4. Test Android/iOS builds
