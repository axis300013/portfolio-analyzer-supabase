# Portfolio Analyzer Mobile - Step-by-Step Installation Guide

**Visual Guide with Screenshots** 📱  
**Date:** 2025-12-07  
**Time Required:** 5-10 minutes

---

## 🎯 Choose Your Installation Method

| Method | Time | Difficulty | Best For |
|--------|------|------------|----------|
| **Web Version** | 2 min | ⭐ Easy | Immediate use |
| **APK Install** | 5 min | ⭐⭐ Medium | Offline access |
| **Build Your Own** | 30 min | ⭐⭐⭐ Advanced | Developers |

---

## 📱 METHOD 1: Web Version (Recommended!)

### ✅ EASIEST - Works in 2 minutes!

This method requires NO installation and works immediately.

---

### **STEP 1: Start Desktop App**

**On Your Computer:**

```powershell
# Open PowerShell in project directory
cd "c:\Users\SzalmaNB1\Downloads\cabeceo\visual studio\Portfolio Analyzer"

# Run startup script
.\start_portfolio_supabase.ps1
```

**What You'll See:**
```
================================
 Portfolio Analyzer - Supabase
================================

✓ Found .env configuration
✓ Connected to Supabase successfully!
✓ Starting FastAPI backend...
✓ Starting Streamlit UI...
✓ Opening browser...

UI:  http://localhost:8501
API: http://localhost:8000/docs
```

**Status:** ✅ Desktop app is running!

---

### **STEP 2: Find Your Computer's IP Address**

**On Your Computer (PowerShell):**

```powershell
ipconfig
```

**Look for this section:**
```
Wireless LAN adapter Wi-Fi:

   Connection-specific DNS Suffix  . :
   IPv4 Address. . . . . . . . . . . : 192.168.1.105  ← YOUR IP ADDRESS
   Subnet Mask . . . . . . . . . . . : 255.255.255.0
   Default Gateway . . . . . . . . . : 192.168.1.1
```

**Write down your IPv4 Address:** `192.168.1.105` (yours will be different)

**Status:** ✅ You have your IP address!

---

### **STEP 3: Open on Your Phone**

**On Your Phone:**

1. **Make sure phone is on same WiFi network as computer**
   - Settings → WiFi → Connected to same network

2. **Open Chrome browser on your phone**

3. **Type in address bar:**
   ```
   http://192.168.1.105:8501
   ```
   (Use YOUR IP address from Step 2)

4. **Press Enter/Go**

**What You'll See:**
```
┌─────────────────────────────────┐
│  Portfolio Analyzer             │
│  🏠 Dashboard                    │
│  ─────────────────────────────  │
│  Total Portfolio Value          │
│  15,234,567 Ft                  │
│  ─────────────────────────────  │
│  Total Net Wealth               │
│  28,456,789 Ft                  │
│  ─────────────────────────────  │
│  [📊 Portfolio] [💰 Wealth]     │
│  [📈 Trends] [📋 Analytics]     │
└─────────────────────────────────┘
```

**Status:** ✅ App is working on your phone!

---

### **STEP 4: Add to Home Screen (Optional but Recommended)**

**On Your Phone (Chrome):**

1. **Tap the menu icon** (three dots ⋮ in top right)

2. **Select "Add to Home Screen"**

3. **Edit name if desired:**
   - Default: "Portfolio Analyzer"
   - Tap "Add"

4. **Confirm:**
   - Tap "Add" or "Add to Home screen"

**What Happens:**
- Icon appears on your phone's home screen
- Looks like a native app
- One tap to open
- No browser bars when opened

**Icon Preview:**
```
┌───────┐
│  📊   │  ← Portfolio
│       │     Analyzer
└───────┘
```

**Status:** ✅ App installed like a native app!

---

### **STEP 5: Test the App**

**On Your Phone:**

1. **Tap the app icon** on home screen

2. **Navigate through screens:**
   - Bottom navigation bar has 5 buttons
   - Dashboard → Portfolio → Wealth → Trends → Analytics

3. **Try some features:**
   - View portfolio holdings
   - Check wealth categories
   - See historical trends
   - Browse analytics tables

**Expected Behavior:**
- ✅ All screens load quickly
- ✅ Data appears correctly
- ✅ Charts render properly
- ✅ Navigation is smooth

**Status:** ✅ Everything works!

---

## 💡 Troubleshooting Web Version

### Problem: "This site can't be reached"

**Solution 1: Check WiFi**
```
1. Phone Settings → WiFi
2. Verify connected to SAME network as computer
3. Network name should match exactly
```

**Solution 2: Check Desktop App**
```powershell
# On computer, verify app is running:
# Look for these windows:
# - PowerShell window showing "Streamlit UI on http://localhost:8501"
# - Browser tab open to localhost:8501
```

**Solution 3: Verify IP Address**
```powershell
# On computer, run again:
ipconfig

# Use the CORRECT IPv4 address
# Try: http://[your-ip]:8501
```

### Problem: "Connection timed out"

**Solution: Check Firewall**
```
1. Windows Security → Firewall & network protection
2. Allow an app through firewall
3. Find "Python" and check both Private and Public
4. Or temporarily disable firewall to test
```

### Problem: Page loads but no data appears

**Solution: Run Daily Update**
```
1. On desktop browser (localhost:8501)
2. Click "Run Daily Update" button in sidebar
3. Wait for "Update completed successfully!"
4. Refresh mobile browser
```

---

## 📦 METHOD 2: APK Installation

### ⚠️ REQUIRES: Android SDK installed (see Method 3 first)

---

### **STEP 1: Build the APK**

**On Your Computer:**

```powershell
# Navigate to mobile directory
cd "c:\Users\SzalmaNB1\Downloads\cabeceo\visual studio\Portfolio Analyzer\mobile"

# Build release APK
flutter build apk --release
```

**Expected Output:**
```
Building with sound null safety
Running Gradle task 'assembleRelease'...
✓ Built build\app\outputs\flutter-apk\app-release.apk (28.5MB)
```

**APK Location:**
```
C:\Users\SzalmaNB1\Downloads\cabeceo\visual studio\Portfolio Analyzer\mobile\build\app\outputs\flutter-apk\app-release.apk
```

**Status:** ✅ APK file created!

---

### **STEP 2: Transfer APK to Phone**

**Choose ONE method:**

#### Option A: USB Cable (Fastest)

1. **Connect phone to computer via USB**
2. **On phone: Tap notification "USB charging this device"**
3. **Select "File Transfer" or "Transfer files"**
4. **On computer: Open File Explorer**
5. **Navigate to your phone** (appears as a device)
6. **Copy APK to Downloads folder on phone:**
   ```
   From: C:\Users\...\app-release.apk
   To:   Phone\Internal Storage\Download\
   ```

#### Option B: Email (Easy)

1. **Attach APK to email**
2. **Send to yourself**
3. **Open email on phone**
4. **Download attachment**

#### Option C: Cloud Storage (Reliable)

1. **Upload APK to Google Drive/Dropbox/OneDrive**
2. **Share link**
3. **Open link on phone**
4. **Download file**

**Status:** ✅ APK is on your phone!

---

### **STEP 3: Enable Unknown Sources**

**On Your Phone:**

#### For Android 8.0+ (Most Common)

1. **Open Settings**
2. **Go to Apps & notifications**
3. **Advanced → Special app access**
4. **Install unknown apps**
5. **Select your browser or file manager** (e.g., Chrome, Files)
6. **Toggle "Allow from this source" ON**

#### For Older Android (before 8.0)

1. **Open Settings**
2. **Go to Security**
3. **Toggle "Unknown sources" ON**
4. **Tap OK on warning**

**What You'll See:**
```
┌─────────────────────────────────┐
│  ⚠️ Security Warning            │
│                                 │
│  Your phone and personal data   │
│  are more vulnerable to attack  │
│  by apps from unknown sources.  │
│                                 │
│  [Cancel]  [OK]                 │
└─────────────────────────────────┘
```

**Tap OK** - This is normal and safe for your own APK.

**Status:** ✅ Ready to install apps!

---

### **STEP 4: Install the APK**

**On Your Phone:**

1. **Open Files app or Downloads**
2. **Navigate to Download folder**
3. **Tap on "app-release.apk"**

**Installation Screen:**
```
┌─────────────────────────────────┐
│  Do you want to install this    │
│  application?                   │
│                                 │
│  Portfolio Analyzer             │
│  📊                             │
│                                 │
│  • Internet access              │
│  • View network connections     │
│                                 │
│  [Cancel]        [Install]      │
└─────────────────────────────────┘
```

4. **Tap "Install"**
5. **Wait for installation** (5-10 seconds)

**Success Screen:**
```
┌─────────────────────────────────┐
│  ✅ App installed                │
│                                 │
│  Portfolio Analyzer has been    │
│  installed successfully         │
│                                 │
│  [Done]          [Open]         │
└─────────────────────────────────┘
```

6. **Tap "Open"**

**Status:** ✅ App installed and launching!

---

### **STEP 5: First Time Setup**

**On Your Phone:**

#### Login Screen Appears:
```
┌─────────────────────────────────┐
│  Portfolio Analyzer             │
│  📊                             │
│                                 │
│  Email:                         │
│  [____________________]         │
│                                 │
│  Password:                      │
│  [____________________]         │
│                                 │
│  [        Login       ]         │
│                                 │
│  Don't have an account?         │
│  Sign Up                        │
└─────────────────────────────────┘
```

#### If New User:

1. **Tap "Sign Up"**
2. **Enter email address**
3. **Create password** (min 6 characters)
4. **Tap "Sign Up"**
5. **Check your email**
6. **Click confirmation link**
7. **Return to app**
8. **Login with email and password**

#### If Existing User:

1. **Enter email**
2. **Enter password**
3. **Tap "Login"**

**Status:** ✅ Logged in successfully!

---

### **STEP 6: Explore the App**

**On Your Phone:**

#### Bottom Navigation (5 Buttons):
```
[🏠 Dashboard] [📈 Portfolio] [💰 Wealth] [📊 Trends] [📋 Analytics]
```

1. **Dashboard:**
   - Total portfolio value
   - Total net wealth
   - Quick metrics
   - Date selector

2. **Portfolio:**
   - View holdings
   - Manage instruments
   - Update prices
   - Record transactions

3. **Wealth:**
   - Manage categories
   - Update values
   - View current wealth

4. **Trends:**
   - Historical charts
   - YoY comparison
   - Portfolio growth
   - Wealth growth

5. **Analytics:**
   - Detailed data tables
   - Portfolio details
   - Combined summary
   - Wealth details

**Status:** ✅ Ready to manage your portfolio!

---

## 🛠️ METHOD 3: Build APK Yourself (Advanced)

### Prerequisites Setup

---

### **STEP 1: Install Android Studio**

1. **Download Android Studio:**
   ```
   https://developer.android.com/studio
   ```

2. **Run installer:**
   - File: `android-studio-2024.2.1.11-windows.exe`
   - Accept defaults
   - Choose "Standard" installation

3. **Wait for downloads:**
   - Android SDK Platform
   - Android SDK Build-Tools
   - Android Emulator
   - Takes 10-20 minutes

**Status:** ✅ Android Studio installed!

---

### **STEP 2: Configure Android SDK**

**In Android Studio:**

1. **Open Android Studio** (even if you don't have a project)
2. **Click "More Actions" → "SDK Manager"**

**Or from menu:**
- **File → Settings → Appearance & Behavior → System Settings → Android SDK**

3. **SDK Platforms tab:**
   - ☑️ Check "Android 14.0 (UpsideDownCake)" (API 34)
   - ☑️ Check "Show Package Details"
   - ☑️ Check "Android SDK Platform 34"

4. **SDK Tools tab:**
   - ☑️ Check "Android SDK Build-Tools 34.0.0"
   - ☑️ Check "Android SDK Command-line Tools"
   - ☑️ Check "Android Emulator"
   - ☑️ Check "Android SDK Platform-Tools"

5. **Click "Apply"**
6. **Accept licenses**
7. **Click "OK"** - Downloads start (5-10 minutes)

**Status:** ✅ Android SDK configured!

---

### **STEP 3: Set Environment Variables**

**On Your Computer (PowerShell as Administrator):**

```powershell
# Set ANDROID_HOME
$androidHome = "C:\Users\$env:USERNAME\AppData\Local\Android\Sdk"
[Environment]::SetEnvironmentVariable("ANDROID_HOME", $androidHome, "User")

# Add to PATH
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
$newPath = "$currentPath;$androidHome\platform-tools;$androidHome\tools;$androidHome\tools\bin"
[Environment]::SetEnvironmentVariable("Path", $newPath, "User")

# Verify
Write-Host "ANDROID_HOME set to: $androidHome"
Write-Host "Restart PowerShell for changes to take effect"
```

**Close and reopen PowerShell, then verify:**

```powershell
# Check environment variable
$env:ANDROID_HOME

# Should output:
# C:\Users\SzalmaNB1\AppData\Local\Android\Sdk
```

**Status:** ✅ Environment variables set!

---

### **STEP 4: Verify Flutter Configuration**

```powershell
cd "c:\Users\SzalmaNB1\Downloads\cabeceo\visual studio\Portfolio Analyzer\mobile"
flutter doctor
```

**Expected Output:**
```
Doctor summary (to see all details, run flutter doctor -v):
[✓] Flutter (Channel stable, 3.27.1, on Microsoft Windows 10)
[✓] Windows Version (Installed version of Windows is 10 or higher)
[✓] Android toolchain - develop for Android devices (Android SDK version 34.0.0)
[✓] Chrome - develop for the web
[✓] Visual Studio - develop Windows apps (Visual Studio Community 2022 17.11.5)
[✓] Android Studio (version 2024.2)
[✓] Connected device (2 available)
[✓] Network resources

• No issues found!
```

**If you see ❌ next to Android toolchain:**
```powershell
# Accept Android licenses
flutter doctor --android-licenses

# Type 'y' to accept each license
```

**Status:** ✅ Flutter ready to build!

---

### **STEP 5: Build the APK**

```powershell
# Clean previous builds
flutter clean

# Get dependencies
flutter pub get

# Build release APK
flutter build apk --release
```

**Build Process (takes 2-5 minutes):**
```
Running Gradle task 'assembleRelease'...
[========================================] 100%

✓ Built build\app\outputs\flutter-apk\app-release.apk (28.5MB).
```

**APK Location:**
```
mobile\build\app\outputs\flutter-apk\app-release.apk
```

**Status:** ✅ APK built successfully!

---

### **STEP 6: Test the APK**

**Option A: Physical Device (Recommended)**

1. **Enable Developer Options on phone:**
   - Settings → About phone
   - Tap "Build number" 7 times
   - "You are now a developer!"

2. **Enable USB Debugging:**
   - Settings → Developer options
   - Toggle "USB debugging" ON

3. **Connect phone via USB**

4. **On phone: Accept USB debugging**
   ```
   Allow USB debugging?
   [Always allow from this computer]
   [Cancel] [OK]
   ```

5. **Install APK:**
   ```powershell
   adb devices  # Verify phone is connected
   adb install build\app\outputs\flutter-apk\app-release.apk
   ```

**Option B: Android Emulator**

1. **In Android Studio:**
   - Tools → Device Manager
   - Click "Create Device"
   - Select phone (e.g., Pixel 7)
   - Select system image (API 34)
   - Finish

2. **Start emulator:**
   - Click ▶️ play button

3. **Install APK:**
   ```powershell
   flutter install --release
   ```

**Status:** ✅ APK tested and working!

---

## 📊 Feature Testing Checklist

After installation, verify these features work:

### Dashboard Screen
- [ ] Total portfolio value displays
- [ ] Total net wealth displays
- [ ] Date selector works
- [ ] Metrics update when date changes

### Portfolio Screen
- [ ] Holdings list appears
- [ ] Date picker works
- [ ] Historical data loads
- [ ] Manage button opens management screen

### Portfolio Management
- [ ] Manual price update form works
- [ ] Currency dropdown selectable
- [ ] Price saves successfully
- [ ] Transaction recording works
- [ ] Instrument CRUD operations work

### Wealth Screen
- [ ] Categories list appears
- [ ] Current values display
- [ ] Manage button opens management screen

### Wealth Management
- [ ] Category CRUD operations work
- [ ] Value update form works
- [ ] Currency shows from category
- [ ] Values save successfully

### Trends Screen
- [ ] Portfolio chart renders
- [ ] Wealth chart renders
- [ ] Combined chart renders
- [ ] YoY metrics calculate

### Analytics Screen
- [ ] Portfolio Details tab loads
- [ ] Combined Summary tab loads
- [ ] Wealth Details tab loads
- [ ] Date range selector works
- [ ] Data tables render correctly

### Navigation
- [ ] Bottom nav bar on all screens
- [ ] All 5 buttons work
- [ ] Screen transitions smooth
- [ ] Back button works correctly

---

## 🔧 Common Issues & Solutions

### Build Issues

#### "Android SDK not found"
```powershell
# Solution: Set ANDROID_HOME
$env:ANDROID_HOME = "C:\Users\$env:USERNAME\AppData\Local\Android\Sdk"
flutter doctor
```

#### "Gradle build failed"
```powershell
# Solution: Clean and rebuild
cd android
./gradlew clean
cd ..
flutter clean
flutter pub get
flutter build apk --release
```

#### "Unable to locate Android SDK"
```
Solution:
1. Open Android Studio
2. Tools → SDK Manager
3. Note the "Android SDK Location" path
4. Use that path in ANDROID_HOME
```

### Installation Issues

#### "App not installed"
```
Causes:
1. Insufficient storage → Free up space
2. Conflicting version → Uninstall old version
3. Corrupted APK → Re-download

Solution: Check available storage, uninstall any existing version
```

#### "Parse error: There is a problem parsing the package"
```
Causes:
1. APK corrupted during transfer
2. Android version too old (need 5.0+)
3. Architecture mismatch

Solution:
1. Re-transfer APK file
2. Check Android version (Settings → About)
3. Build with --split-per-abi flag
```

### Runtime Issues

#### App crashes immediately on launch
```
Solutions:
1. Clear app cache:
   Settings → Apps → Portfolio Analyzer → Storage → Clear Cache

2. Check internet connection (app requires Supabase)

3. Reinstall app:
   Settings → Apps → Portfolio Analyzer → Uninstall
   Then reinstall APK
```

#### "Connection failed" errors
```
Solution:
1. Check internet connection
2. Verify Supabase is accessible
3. Check .env configuration in mobile app
4. Try toggling WiFi off/on
```

#### Data not loading
```
Solutions:
1. Check if desktop Daily Update has been run
2. Verify Supabase credentials
3. Check RLS policies in Supabase
4. Logout and login again
```

---

## 📱 Distribution to Other Users

### Option 1: Direct APK Share

1. **Share APK file via:**
   - Email attachment
   - WhatsApp/Telegram
   - Google Drive/Dropbox link
   - USB transfer

2. **Provide instructions:**
   - "Enable Unknown Sources"
   - "Install APK"
   - "Login with your credentials"

### Option 2: GitHub Releases

1. **Create release on GitHub:**
   ```
   https://github.com/axis300013/portfolio-analyzer-supabase/releases
   ```

2. **Upload APK as release asset**

3. **Share download link:**
   ```
   https://github.com/axis300013/portfolio-analyzer-supabase/releases/latest
   ```

### Option 3: Google Play Store (Future)

**Requirements:**
- Google Play Developer account ($25 one-time fee)
- App signing key
- App bundle (AAB format)
- Store listing (screenshots, description)
- Privacy policy
- Content rating

**Build app bundle:**
```powershell
flutter build appbundle --release
```

**Steps:**
1. Create developer account
2. Create app in Play Console
3. Upload AAB file
4. Complete store listing
5. Submit for review

---

## 🎯 Quick Reference

### Start Desktop App
```powershell
.\start_portfolio_supabase.ps1
```

### Find Your IP
```powershell
ipconfig
# Look for IPv4 Address
```

### Access from Phone
```
http://[your-ip]:8501
```

### Build APK
```powershell
cd mobile
flutter build apk --release
```

### Install on Phone
```powershell
adb install build\app\outputs\flutter-apk\app-release.apk
```

---

## 📚 Additional Resources

**Documentation:**
- Full docs: `docs/MOBILE_APP_COMPLETE_DOCUMENTATION.md`
- APK guide: `docs/APK_BUILD_AND_DISTRIBUTION_GUIDE.md`
- Quick start: `docs/QUICK_START_MOBILE_INSTALLATION.md`

**Support:**
- GitHub Issues: https://github.com/axis300013/portfolio-analyzer-supabase/issues
- Project backup: `Portfolio_Analyzer_Backup_20251207_171220`

---

## ✅ Installation Complete!

**What You Should Have:**
- ✅ Mobile app running on your phone
- ✅ Desktop app running on your computer
- ✅ Both connected to Supabase
- ✅ All features working

**Next Steps:**
1. Explore all 5 screens
2. Try updating some data
3. Run Daily Update from desktop
4. View trends and analytics

**Enjoy managing your portfolio! 📊💰📈**

---

**Last Updated:** 2025-12-07  
**Guide Version:** 1.0  
**App Version:** 1.0.0
