# Portfolio Analyzer Mobile App - Complete Documentation
**Version:** 1.0.0  
**Last Updated:** December 7, 2025  
**Platform:** Flutter (iOS, Android, Web)

---

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Features](#features)
4. [Technical Stack](#technical-stack)
5. [Database Schema](#database-schema)
6. [Setup & Installation](#setup--installation)
7. [User Guide](#user-guide)
8. [Development History](#development-history)
9. [Known Issues & Solutions](#known-issues--solutions)
10. [Future Enhancements](#future-enhancements)

---

## Overview

The Portfolio Analyzer Mobile App is a comprehensive financial management tool that allows users to track investments, wealth, and financial trends on the go. It connects to a Supabase backend and provides real-time access to portfolio data.

### Key Objectives
- **Mobile-First Design**: View and manage financial data from any device
- **Read & Edit Capability**: Update prices and wealth values directly from mobile
- **Real-Time Sync**: Automatic synchronization with Supabase cloud database
- **Desktop Integration**: Works alongside desktop Streamlit app for data updates

---

## Architecture

### System Components
```
┌─────────────────────┐
│   Mobile App        │
│   (Flutter)         │
└──────────┬──────────┘
           │
           │ REST API
           ↓
┌─────────────────────┐
│   Supabase          │
│   (PostgreSQL)      │
└──────────┬──────────┘
           │
           │
           ↓
┌─────────────────────┐
│   Desktop App       │
│   (Streamlit)       │
└─────────────────────┘
```

### Data Flow
1. **Mobile App** → Reads from Supabase directly
2. **Mobile App** → Writes prices & wealth values to Supabase
3. **Desktop App** → Runs ETL pipeline to fetch external data
4. **Desktop App** → Updates calculated fields in Supabase
5. **Mobile App** → Auto-refreshes to show updated calculations

---

## Features

### 1. Dashboard
- **Portfolio Summary**: Total value, instrument count
- **Wealth Overview**: Net wealth, assets, liabilities
- **Quick Actions**: Navigate to key functions
- **5-Button Navigation**: Access all screens quickly

### 2. Portfolio Management
**Screens:**
- **Portfolio Overview**: Current holdings by date
- **Manual Prices**: Update instrument prices
- **Instruments**: Add/edit investment instruments
- **Transactions**: Record buys/sells

**Capabilities:**
- View portfolio snapshots by date
- Update prices in original currency (USD, EUR, HUF, etc.)
- Add new instruments with ISIN, ticker
- Record transactions with date and quantity

**Key Fix (Dec 7, 2025):**
- ✅ Currency dropdown now functional (was stuck on USD)
- ✅ Upsert logic prevents duplicate key errors
- ✅ Info dialog explains need for Daily Update after price changes

### 3. Wealth Management
**Screens:**
- **Wealth Overview**: Current wealth by category
- **Categories**: Asset/liability categories
- **Values**: Update wealth item values

**Capabilities:**
- Track cash, property, pension, other assets
- Record liabilities (loans, mortgages)
- Update values in original currency
- Add notes to value entries

**Key Fix (Dec 7, 2025):**
- ✅ Currency displayed from category (not editable)
- ✅ Values entered in original currency
- ✅ Fixed 400 error (notes → note field)
- ✅ Fixed 403 error (check-then-update approach)

### 4. Trends
- **Portfolio Trends**: Value over time
- **Wealth Trends**: Net wealth progression
- **Period Selection**: 1M, 3M, 6M, 1Y, ALL
- **Charts**: Line charts with date ranges

### 5. Analytical Data ⭐ NEW
**3 Tabs:**

**Portfolio Details**
- Rows: Instruments (stocks, bonds, etc.)
- Columns: Dates
- Values: Portfolio value by instrument per date
- Transposed table format matching desktop

**Combined Summary**
- Rows: 7 metrics
  1. Portfolio Total
  2. Cash
  3. Property
  4. Pension ⭐ (Added Dec 7)
  5. Other Assets ⭐ (Added Dec 7)
  6. Loans
  7. Net Wealth
- Columns: Dates
- Shows comprehensive wealth breakdown over time

**Wealth Details** ⭐ NEW (Dec 7)
- Rows: Individual wealth categories (bank accounts, properties, etc.)
- Columns: Dates
- Values: Value of each category per date
- Detailed breakdown of wealth composition

---

## Technical Stack

### Frontend
- **Framework**: Flutter 3.27.1
- **Language**: Dart
- **State Management**: StatefulWidget with setState
- **Routing**: go_router ^14.7.3
- **HTTP Client**: http ^1.2.2

### Backend
- **Database**: Supabase (PostgreSQL)
- **Authentication**: Supabase Auth
- **Real-time**: Supabase Realtime subscriptions
- **Storage**: Supabase Storage (for future use)

### Key Dependencies
```yaml
dependencies:
  flutter: sdk: flutter
  supabase_flutter: ^2.10.3
  go_router: ^14.7.3
  intl: ^0.19.0
  http: ^1.2.2
  flutter_dotenv: ^5.2.1
```

---

## Database Schema

### Core Tables

#### instruments
- `id` (PK): Integer
- `name`: String(200)
- `currency`: String(3) - USD, EUR, HUF, etc.
- `isin`: String(12) - International identifier
- `ticker`: String(20)
- `instrument_type`: String(50) - stock, bond, etf, etc.
- `is_active`: Boolean
- `created_at`, `updated_at`: Timestamps

#### prices
- `instrument_id` (FK): → instruments.id
- `price`: Numeric(20,4)
- `price_date`: Date
- `currency`: String(3)
- `source`: String(50) - yahoo, manual, bloomberg
- **Unique**: (instrument_id, price_date, source)

#### portfolio_values_daily
- `snapshot_date`: Date
- `instrument_id` (FK): → instruments.id
- `quantity`: Numeric(20,4)
- `price`: Numeric(20,4)
- `value_huf`: Numeric(20,2)
- **Calculated by desktop ETL**

#### wealth_categories
- `id` (PK): Integer
- `name`: String(200) - "Erste Savings", "Budapest Apartment"
- `currency`: String(3)
- `category_type`: String(50) - cash, property, pension, etc.
- `is_liability`: Boolean
- **Unique**: (category_type, name)

#### wealth_values
- `wealth_category_id` (FK): → wealth_categories.id
- `value_date`: Date
- `present_value`: Numeric(20,2) - In original currency
- `note`: Text (optional)
- **Unique**: (wealth_category_id, value_date)

#### total_wealth_snapshots
- `snapshot_date`: Date (PK)
- `portfolio_value_huf`: Numeric(20,2)
- `cash_huf`: Numeric(20,2)
- `property_huf`: Numeric(20,2)
- `pension_huf`: Numeric(20,2)
- `other_huf`: Numeric(20,2)
- `loans_huf`: Numeric(20,2)
- `net_wealth_huf`: Numeric(20,2)
- **Calculated by desktop ETL**

### Relationships
```
instruments (1) ─── (N) prices
instruments (1) ─── (N) portfolio_values_daily
wealth_categories (1) ─── (N) wealth_values
```

---

## Setup & Installation

### Prerequisites
1. **Flutter SDK**: 3.27.1 or later
2. **Dart SDK**: Included with Flutter
3. **Supabase Account**: Free tier available
4. **Chrome** (for web testing)

### Initial Setup

#### 1. Clone Repository
```bash
cd "C:\Users\SzalmaNB1\Downloads\cabeceo\visual studio\Portfolio Analyzer\mobile"
```

#### 2. Install Dependencies
```bash
flutter pub get
```

#### 3. Configure Supabase
Create `.env` file in mobile directory:
```env
SUPABASE_URL=https://hrlzrirsvifxsnccxvsa.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
```

#### 4. Run on Web
```bash
flutter run -d chrome
```

#### 5. Run on Android (requires setup)
```bash
flutter run -d android
```

### Directory Structure
```
mobile/
├── lib/
│   ├── main.dart                 # App entry point
│   ├── models/                   # Data models
│   │   └── portfolio_snapshot.dart
│   ├── screens/                  # UI screens
│   │   ├── auth/                 # Login, signup
│   │   ├── home/                 # Dashboard
│   │   ├── portfolio/            # Portfolio management
│   │   ├── wealth/               # Wealth management
│   │   ├── trends/               # Trend charts
│   │   └── analytics/            # Analytical data ⭐ NEW
│   └── services/                 # Backend services
│       └── supabase_service.dart # All Supabase queries
├── pubspec.yaml                  # Dependencies
├── .env                          # Supabase credentials
└── README.md
```

---

## User Guide

### First Time Setup
1. **Sign Up**: Create account with email/password
2. **Verify Email**: Check inbox for verification link
3. **Login**: Use credentials to access app
4. **Dashboard**: View summary of portfolio and wealth

### Daily Usage

#### Updating Instrument Prices
1. Go to **Portfolio** → **Management** → **Manual Prices**
2. Select instrument from dropdown
3. Enter new price (in instrument's currency)
4. Select currency (USD, EUR, HUF, etc.)
5. Choose date (defaults to today)
6. Click **Save Price**
7. ✅ See confirmation: "Price saved successfully"
8. ℹ️ Info dialog: "Run Daily Update from desktop to see recalculated values"

**Important**: Manual price updates don't immediately affect portfolio values. Run Daily Update from desktop app to recalculate.

#### Updating Wealth Values
1. Go to **Wealth** → **Management** → **Values**
2. Select category (e.g., "Erste Savings")
3. Notice currency changes to category's currency
4. Enter new value (in original currency - USD, not HUF)
5. Select date
6. Add optional notes
7. Click **Save Wealth Value**
8. ✅ Confirmation shows immediately

**Note**: Wealth values are stored in original currency for accuracy.

#### Viewing Analytics
1. Go to **Analytics** tab (bottom navigation or dashboard)
2. Select date range (Start Date, End Date)
3. Choose granularity (Daily/Monthly)
4. View 3 tabs:
   - **Portfolio Details**: See each instrument's value over time
   - **Combined Summary**: 7-metric wealth overview
   - **Wealth Details**: Individual category breakdown

### Navigation
- **Bottom Bar**: 5 buttons (Dashboard, Portfolio, Wealth, Trends, Analytics)
- **Consistent**: Same navigation on all screens
- **Quick Jump**: Tap any button to switch screens instantly

---

## Development History

### Phase 1: Initial Setup (Dec 4-5, 2025)
- ✅ Flutter project created
- ✅ Supabase integration
- ✅ Authentication (sign up, email verification, login)
- ✅ 4 main screens: Dashboard, Portfolio, Wealth, Trends

### Phase 2: CRUD Operations (Dec 6, 2025)
- ✅ Portfolio management (instruments, transactions, prices)
- ✅ Wealth management (categories, values)
- ✅ Row Level Security policies
- ✅ Read/write operations to Supabase

### Phase 3: Bug Fixes (Dec 7, 2025 - Morning)
**Issue 1**: Wealth category edit error
- **Problem**: Type mismatch on category ID
- **Solution**: Added `as int` cast

**Issue 2**: Currency dropdown not working
- **Problem**: No StatefulBuilder wrapper
- **Solution**: Wrapped dialog in StatefulBuilder

**Issue 3**: Manual price save error
- **Problem**: Missing currency parameter, `created_at` field issue
- **Solution**: Added currency with fallback, removed `created_at`

**Issue 4**: Dashboard "Backend not available"
- **Problem**: User confusion about mobile/desktop architecture
- **Solution**: Removed button, added informational message

**Issue 5**: Systematic `created_at` errors
- **Problem**: Supabase auto-generates timestamps
- **Solution**: Removed `created_at` from all 5 insert operations

**Issue 6**: Dropdown value mismatch
- **Problem**: Database has lowercase 'cash', UI had 'Cash'
- **Solution**: Values lowercase, display capitalized

### Phase 4: Analytics Feature (Dec 7, 2025 - Afternoon)
- ✅ New Analytics screen with 3 tabs
- ✅ Portfolio Details table (instruments × dates)
- ✅ Combined Summary with 7 metrics (added Pension, Other Assets)
- ✅ Wealth Details table (categories × dates) ⭐ NEW
- ✅ Transposed table format matching desktop
- ✅ Date range and granularity selectors

### Phase 5: Navigation Enhancement (Dec 7, 2025 - Late Afternoon)
- ✅ Unified 5-button bottom navigation
- ✅ Analytics accessible from all screens
- ✅ Consistent UI/UX across entire app

### Phase 6: Final Fixes (Dec 7, 2025 - Evening)
**Price Update Issues:**
- ✅ Duplicate key error → Changed to upsert
- ✅ Currency dropdown stuck on USD → Added selectable dropdown
- ✅ Added info dialog about Daily Update requirement

**Wealth Update Issues:**
- ✅ 400 error → Fixed `notes` vs `note` field name
- ✅ 403 error → Changed upsert to check-then-update/insert
- ✅ Currency display → Shows category currency (not editable)
- ✅ Value input → In original currency, not HUF

---

## Known Issues & Solutions

### Issue: Portfolio values don't update after manual price change
**Root Cause**: `portfolio_values_daily` table is calculated by desktop ETL pipeline, not automatically recalculated on price update.

**Solution**: Run "Daily Update" from desktop app after changing prices.

**Why**: Mobile app writes to `prices` table. Desktop ETL reads prices, applies forex, calculates portfolio values, and writes to `portfolio_values_daily`.

**Workflow**:
1. Mobile: Update price → `prices` table
2. Desktop: Run Daily Update → ETL calculates → `portfolio_values_daily`
3. Mobile: Refresh → See updated values

### Issue: Can't change wealth category currency
**Expected Behavior**: Currency is fixed per category and should not be editable when updating values.

**Solution**: Working as designed. Currency is displayed from the category definition.

**Why**: Each wealth item (e.g., "US Bank Account") has a fixed currency (USD). Values should be entered in that original currency for accuracy.

### Issue: Flutter web assertion errors in console
**Symptom**: DartError assertions in Chrome console about input elements.

**Impact**: None - these are harmless Flutter web engine warnings.

**Status**: Ignored - does not affect functionality.

---

## Future Enhancements

### Short Term (Next Release)
- [ ] Export analytics data to CSV
- [ ] Charts in Analytics screen
- [ ] Filtering by instrument type
- [ ] Search functionality in dropdowns

### Medium Term
- [ ] Push notifications for price alerts
- [ ] Offline mode with local caching
- [ ] Biometric authentication (fingerprint/face)
- [ ] Dark/light theme toggle

### Long Term
- [ ] Real-time price updates
- [ ] Portfolio rebalancing suggestions
- [ ] Tax reporting features
- [ ] Multi-user support with sharing

---

## API Reference

### SupabaseService Methods

#### Portfolio Operations
```dart
// Get portfolio instruments
static Future<List<Map<String, dynamic>>> getPortfolioInstruments()

// Get portfolio values by date
static Future<List<Map<String, dynamic>>> getPortfolioValuesByDate(String date)

// Save manual price
static Future<void> saveManualPrice({
  required int instrumentId,
  required double price,
  required String priceDate,
  required String currency,
})

// Add instrument
static Future<void> addInstrument({
  required String name,
  String? isin,
  String? ticker,
  required String instrumentType,
  required String currency,
})

// Save transaction
static Future<void> saveTransaction({
  required int portfolioId,
  required int instrumentId,
  required String transactionType,
  required double quantity,
  required double price,
  required String transactionDate,
})
```

#### Wealth Operations
```dart
// Get wealth items (categories)
static Future<List<Map<String, dynamic>>> getWealthItems()

// Get latest wealth values
static Future<List<Map<String, dynamic>>> getLatestWealthValues()

// Save wealth value
static Future<void> saveWealthValue({
  required int categoryId,
  required double presentValue,
  required String valueDate,
  String? note,
})

// Add wealth category
static Future<void> addWealthCategory({
  required String name,
  required String categoryType,
  required String currency,
  required bool isLiability,
  String? description,
})
```

#### Analytics Operations
```dart
// Get portfolio history (date range)
static Future<List<Map<String, dynamic>>> getPortfolioHistory({
  required String startDate,
  required String endDate,
})

// Get wealth snapshots (date range)
static Future<List<Map<String, dynamic>>> getWealthSnapshotsRange({
  required String startDate,
  required String endDate,
})

// Get wealth values history (date range)
static Future<List<Map<String, dynamic>>> getWealthValuesHistory({
  required String startDate,
  required String endDate,
})
```

---

## Troubleshooting

### App won't start
**Check**:
1. Flutter version: `flutter --version` (should be 3.27.1+)
2. Dependencies installed: `flutter pub get`
3. `.env` file exists with correct Supabase credentials

### Can't login
**Check**:
1. Email verified (check inbox/spam)
2. Correct credentials
3. Supabase project active
4. Row Level Security policies enabled

### Data not showing
**Check**:
1. Desktop app has run Daily Update recently
2. Date selector shows a date with data
3. Network connection active
4. Supabase project not paused

### Price update fails
**Check**:
1. Instrument selected
2. Price is a valid number
3. Currency selected
4. Date not in future
5. Network connection stable

---

## Support & Contact

### Resources
- **GitHub**: https://github.com/axis300013/portfolio-analyzer-supabase
- **Supabase Dashboard**: https://supabase.com/dashboard
- **Flutter Docs**: https://docs.flutter.dev

### Getting Help
1. Check this documentation first
2. Review error messages carefully
3. Check Supabase dashboard for data issues
4. Run Daily Update from desktop if values seem wrong

---

## Appendix

### A. Environment Variables
```env
# Required in mobile/.env
SUPABASE_URL=https://hrlzrirsvifxsnccxvsa.supabase.co
SUPABASE_ANON_KEY=your_key_here
```

### B. Supported Currencies
- USD (US Dollar)
- EUR (Euro)
- HUF (Hungarian Forint)
- GBP (British Pound)
- CHF (Swiss Franc)
- JPY (Japanese Yen)
- CNY (Chinese Yuan)
- AUD (Australian Dollar)
- CAD (Canadian Dollar)

### C. Date Format
All dates use ISO 8601 format: `YYYY-MM-DD` (e.g., 2025-12-07)

### D. Number Formatting
- Portfolio values: Hungarian locale with thousand separators (e.g., 1,234,567 Ft)
- Prices: Up to 4 decimal places (e.g., 1234.5678)
- Wealth values: Up to 2 decimal places (e.g., 12345.67)

---

**Document Version**: 1.0.0  
**Last Updated**: December 7, 2025  
**Maintained By**: Portfolio Analyzer Development Team
