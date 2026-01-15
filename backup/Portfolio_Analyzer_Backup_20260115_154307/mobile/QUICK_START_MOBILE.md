# Portfolio Analyzer - Mobile App Quick Start

## 🚀 Quick Setup (3 Steps)

### 1️⃣ Get Your Supabase API Key

Go to: https://supabase.com/dashboard/project/hrlzrirsvifxsnccxvsa/settings/api

Copy your **anon public** key (starts with `eyJ...`)

### 2️⃣ Configure the App

```powershell
# Navigate to mobile directory
cd "c:\Users\SzalmaNB1\Downloads\cabeceo\visual studio\Portfolio Analyzer\mobile"

# Create .env file
Copy-Item .env.example .env

# Edit .env and add your Supabase anon key
notepad .env
```

Paste your key:
```
SUPABASE_URL=https://hrlzrirsvifxsnccxvsa.supabase.co
SUPABASE_ANON_KEY=your_key_here
```

### 3️⃣ Install & Run

```powershell
# Install dependencies
flutter pub get

# Run on Android emulator or device
flutter run
```

## 📱 First Time Use

1. App opens → Click **"Sign Up"**
2. Enter email + password
3. Check email for confirmation link
4. Return to app → Log in
5. View your portfolio data!

## 🔑 Enable Database Access

Run this in Supabase SQL Editor to allow authenticated users to read your data:

```sql
-- Enable Row Level Security
ALTER TABLE portfolio_instruments ENABLE ROW LEVEL SECURITY;
ALTER TABLE portfolio_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE wealth_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE wealth_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;

-- Allow reads for authenticated users
CREATE POLICY "Allow authenticated reads" ON portfolio_instruments FOR SELECT TO authenticated USING (true);
CREATE POLICY "Allow authenticated reads" ON portfolio_snapshots FOR SELECT TO authenticated USING (true);
CREATE POLICY "Allow authenticated reads" ON wealth_items FOR SELECT TO authenticated USING (true);
CREATE POLICY "Allow authenticated reads" ON wealth_snapshots FOR SELECT TO authenticated USING (true);
CREATE POLICY "Allow authenticated reads" ON transactions FOR SELECT TO authenticated USING (true);
```

## 📦 Build APK for Android

```powershell
flutter build apk --release
```

APK location: `build\app\outputs\flutter-apk\app-release.apk`

Transfer this file to your Android phone and install!

## 📄 Full Documentation

See `MOBILE_APP_SETUP.md` for detailed instructions, troubleshooting, and customization options.

---

**Need Help?** Check the full setup guide for detailed explanations and common issues.
