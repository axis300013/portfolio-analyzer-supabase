# Portfolio Analyzer Mobile App - Setup Guide

## 📱 Overview

This Flutter mobile app provides iOS and Android access to your Portfolio Analyzer data stored in Supabase. The app connects directly to your cloud database, allowing you to monitor your portfolio and wealth from anywhere.

## ✨ Features

- **📊 Dashboard**: Real-time overview of portfolio value, wealth, assets, and liabilities
- **💼 Portfolio Tracker**: View all investments with detailed breakdowns by instrument type
- **💰 Wealth Tracker**: Monitor cash, property, pension, and liabilities
- **📈 Trends & Analytics**: Interactive charts showing historical performance
- **🔐 Authentication**: Secure login with Supabase Auth
- **🌙 Dark Theme**: Beautiful dark UI optimized for mobile
- **📴 Offline Support**: View cached data when offline (coming soon)

## 🛠️ Prerequisites

Before you begin, ensure you have:

1. **Flutter SDK** (Latest stable version)
   - Download from: https://flutter.dev/docs/get-started/install
   - Verify: `flutter --version`

2. **Android Studio** (for Android development)
   - Download from: https://developer.android.com/studio
   - Install Android SDK and emulator

3. **Xcode** (for iOS development - Mac only)
   - Download from Mac App Store
   - Install iOS Simulator

4. **Supabase Account** (You already have this!)
   - Project: portfolio-analyzer
   - Database: PostgreSQL with your portfolio data

## 📋 Step-by-Step Setup

### Step 1: Get Your Supabase API Keys

1. Go to your Supabase dashboard: https://supabase.com/dashboard/project/hrlzrirsvifxsnccxvsa
2. Click on **Settings** (gear icon) in the left sidebar
3. Click on **API** in the settings menu
4. Copy these values:
   - **Project URL**: `https://hrlzrirsvifxsnccxvsa.supabase.co`
   - **anon public key**: This is your API key (starts with `eyJ...`)

### Step 2: Configure Environment Variables

1. Navigate to the mobile app directory:
   ```powershell
   cd "c:\Users\SzalmaNB1\Downloads\cabeceo\visual studio\Portfolio Analyzer\mobile"
   ```

2. Copy the example environment file:
   ```powershell
   Copy-Item .env.example .env
   ```

3. Edit the `.env` file with your Supabase credentials:
   ```
   SUPABASE_URL=https://hrlzrirsvifxsnccxvsa.supabase.co
   SUPABASE_ANON_KEY=your_anon_key_here
   ```

### Step 3: Install Flutter Dependencies

Run this command in the mobile directory:

```powershell
flutter pub get
```

This will install all required packages:
- `supabase_flutter` - Supabase client for Flutter
- `flutter_riverpod` - State management
- `go_router` - Navigation
- `fl_chart` - Charts and graphs
- `intl` - Number/date formatting

### Step 4: Enable Supabase Authentication

1. Go to your Supabase dashboard: https://supabase.com/dashboard/project/hrlzrirsvifxsnccxvsa
2. Click on **Authentication** in the left sidebar
3. Click on **Providers** tab
4. Enable **Email** provider (it should be enabled by default)
5. Under **Auth URL Configuration**, add your mobile app URL (optional for development)

### Step 5: Set Up Row Level Security (RLS) Policies

Since you'll be using authentication, you need to set up access policies:

1. Go to **SQL Editor** in Supabase
2. Run this SQL to allow authenticated users to read data:

```sql
-- Enable RLS on all tables
ALTER TABLE portfolio_instruments ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolio_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE wealth_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE wealth_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;

-- Allow authenticated users to read all data
CREATE POLICY "Allow authenticated users to read portfolio_instruments"
ON portfolio_instruments FOR SELECT
TO authenticated
USING (true);

CREATE POLICY "Allow authenticated users to read portfolio_snapshots"
ON portfolio_snapshots FOR SELECT
TO authenticated
USING (true);

CREATE POLICY "Allow authenticated users to read wealth_items"
ON wealth_items FOR SELECT
TO authenticated
USING (true);

CREATE POLICY "Allow authenticated users to read wealth_snapshots"
ON wealth_snapshots FOR SELECT
TO authenticated
USING (true);

CREATE POLICY "Allow authenticated users to read transactions"
ON transactions FOR SELECT
TO authenticated
USING (true);
```

**Note**: This allows any authenticated user to read your data. For production, you may want to add user_id columns and restrict access to specific users.

### Step 6: Run on Android

1. Start an Android emulator or connect a physical device:
   ```powershell
   flutter devices
   ```

2. Run the app:
   ```powershell
   flutter run
   ```

3. The app will compile and launch on your Android device/emulator

### Step 7: Run on iOS (Mac only)

1. Open iOS Simulator from Xcode
2. Run the app:
   ```bash
   flutter run
   ```

3. The app will compile and launch on the iOS simulator

### Step 8: Create Your First Account

1. When the app launches, you'll see the Login screen
2. Click **"Don't have an account? Sign Up"**
3. Enter your email and password (minimum 6 characters)
4. Click **Sign Up**
5. Check your email for a confirmation link from Supabase
6. Click the confirmation link to verify your account
7. Return to the app and log in

## 🚀 Building Release Versions

### Android APK

Build a release APK for distribution:

```powershell
flutter build apk --release
```

The APK will be located at:
`build\app\outputs\flutter-apk\app-release.apk`

You can copy this file to your Android phone and install it.

### Android App Bundle (for Google Play)

```powershell
flutter build appbundle --release
```

### iOS App (Mac only)

```bash
flutter build ios --release
```

Then open `ios/Runner.xcworkspace` in Xcode to archive and distribute.

## 📁 Project Structure

```
mobile/
├── lib/
│   ├── main.dart                      # App entry point with routing
│   ├── models/
│   │   ├── portfolio_snapshot.dart    # Portfolio data model
│   │   └── wealth_snapshot.dart       # Wealth data model
│   ├── screens/
│   │   ├── auth/
│   │   │   ├── login_screen.dart      # Login page
│   │   │   └── signup_screen.dart     # Sign up page
│   │   ├── home/
│   │   │   └── dashboard_screen.dart  # Main dashboard
│   │   ├── portfolio/
│   │   │   └── portfolio_screen.dart  # Portfolio details
│   │   ├── wealth/
│   │   │   └── wealth_screen.dart     # Wealth tracking
│   │   └── trends/
│   │       └── trends_screen.dart     # Charts & analytics
│   └── services/
│       └── supabase_service.dart      # Database client
├── pubspec.yaml                       # Dependencies
├── .env                               # Your Supabase credentials (DO NOT COMMIT!)
└── .env.example                       # Environment template

```

## 🔧 Common Issues & Solutions

### Issue: "No Firebase App '[DEFAULT]' has been created"
**Solution**: This error shouldn't appear since we're using Supabase, not Firebase. If you see it, make sure you've run `flutter pub get` and all dependencies are installed.

### Issue: "Unable to connect to database"
**Solution**: 
- Check your `.env` file has the correct `SUPABASE_URL` and `SUPABASE_ANON_KEY`
- Verify your internet connection
- Check that your Supabase project is active

### Issue: "Authentication failed"
**Solution**:
- Verify your email has been confirmed (check your inbox)
- Make sure Email authentication is enabled in Supabase dashboard
- Try resetting your password

### Issue: "No data showing on Dashboard"
**Solution**:
- Verify you have data in your Supabase database
- Check the RLS policies are set up correctly
- Try refreshing the page (pull down on the screen)

### Issue: "Build failed on iOS"
**Solution**:
- Run `pod install` in the `ios/` directory
- Make sure you have the latest Xcode version
- Check that your Mac meets iOS development requirements

## 📊 Database Schema

The app expects these tables in Supabase:

- `portfolio_instruments` - List of investment instruments
- `portfolio_snapshots` - Historical portfolio values
- `wealth_items` - List of wealth items (cash, property, etc.)
- `wealth_snapshots` - Historical wealth values
- `transactions` - Investment transactions

These tables were already created when you migrated from Docker PostgreSQL.

## 🔐 Security Notes

1. **Never commit your `.env` file** - It contains sensitive API keys
2. **Use Row Level Security (RLS)** - Protect your data from unauthorized access
3. **Enable email confirmation** - Verify users before they can access data
4. **Consider adding user_id columns** - For multi-user support
5. **Use HTTPS only** - Supabase uses HTTPS by default

## 🎨 Customization

### Change App Theme

Edit `lib/main.dart` and modify the `ThemeData`:

```dart
theme: ThemeData(
  colorScheme: ColorScheme.fromSeed(
    seedColor: Colors.purple,  // Change to your preferred color
    brightness: Brightness.dark,
  ),
  useMaterial3: true,
),
```

### Change App Name

Edit `pubspec.yaml`:

```yaml
name: my_portfolio_app
description: My Custom Portfolio App
```

### Add App Icon

1. Add your icon image to `assets/icon.png`
2. Add `flutter_launcher_icons` dependency
3. Run `flutter pub run flutter_launcher_icons`

## 📱 Next Steps

1. **Test the app thoroughly** on both Android and iOS
2. **Add offline support** using local caching
3. **Enable push notifications** for portfolio alerts
4. **Add biometric authentication** (fingerprint/face ID)
5. **Implement data editing** (add transactions, update values)
6. **Add export features** (PDF reports, CSV exports)
7. **Publish to app stores** (Google Play, Apple App Store)

## 🆘 Need Help?

- **Flutter Documentation**: https://flutter.dev/docs
- **Supabase Documentation**: https://supabase.com/docs
- **Flutter Supabase Package**: https://pub.dev/packages/supabase_flutter

## 📄 License

This mobile app is part of your Portfolio Analyzer project.

---

**Created**: December 5, 2025  
**Version**: 1.0.0  
**Platform**: Flutter 3.x with Supabase Backend
