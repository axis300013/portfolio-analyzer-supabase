# Portfolio Analyzer Mobile - APK Build & Distribution Guide

**Date:** 2025-12-07  
**Mobile App Version:** 1.0.0  
**Author:** Portfolio Analyzer Team

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Android SDK Setup](#android-sdk-setup)
3. [Building the APK](#building-the-apk)
4. [APK Distribution Options](#apk-distribution-options)
5. [Installation Instructions for Users](#installation-instructions-for-users)
6. [Troubleshooting](#troubleshooting)
7. [Alternative Distribution Methods](#alternative-distribution-methods)

---

## Prerequisites

### Required Software

1. **Flutter SDK** (already installed: 3.27.1)
2. **Android SDK** (needs installation)
3. **Java Development Kit (JDK)** 17 or higher
4. **Android Studio** (recommended) OR Command Line Tools

### System Requirements

- **OS:** Windows 10/11, macOS, or Linux
- **RAM:** 8 GB minimum (16 GB recommended)
- **Storage:** 10 GB free space for Android SDK
- **Internet:** Required for downloading SDK components

---

## Android SDK Setup

### Option 1: Install Android Studio (Recommended)

1. **Download Android Studio**
   ```
   https://developer.android.com/studio
   ```

2. **Install Android Studio**
   - Run the installer
   - Choose "Standard" installation
   - Let it download required SDK components

3. **Configure SDK**
   - Open Android Studio
   - Go to: File → Settings → Appearance & Behavior → System Settings → Android SDK
   - Check boxes for:
     - Android SDK Platform 34 (Android 14)
     - Android SDK Build-Tools 34.0.0
     - Android SDK Command-line Tools
     - Android Emulator
   - Click "Apply" to download

4. **Set Environment Variables**

   **Windows:**
   ```powershell
   # Add to System Environment Variables
   ANDROID_HOME = C:\Users\<YourUsername>\AppData\Local\Android\Sdk
   
   # Add to PATH:
   %ANDROID_HOME%\platform-tools
   %ANDROID_HOME%\tools
   %ANDROID_HOME%\tools\bin
   ```

   **macOS/Linux:**
   ```bash
   # Add to ~/.bashrc or ~/.zshrc
   export ANDROID_HOME=$HOME/Library/Android/sdk
   export PATH=$PATH:$ANDROID_HOME/platform-tools
   export PATH=$PATH:$ANDROID_HOME/tools
   export PATH=$PATH:$ANDROID_HOME/tools/bin
   ```

5. **Verify Installation**
   ```bash
   flutter doctor
   ```
   Should show: `[✓] Android toolchain - develop for Android devices`

### Option 2: Command Line Tools Only

If you don't want Android Studio:

1. **Download Command Line Tools**
   ```
   https://developer.android.com/studio#command-tools
   ```

2. **Extract to a folder** (e.g., `C:\Android\sdk`)

3. **Set ANDROID_HOME** environment variable

4. **Install Required Components**
   ```bash
   sdkmanager "platform-tools" "platforms;android-34" "build-tools;34.0.0"
   ```

---

## Building the APK

### Step 1: Verify Flutter Configuration

```bash
cd "c:\Users\SzalmaNB1\Downloads\cabeceo\visual studio\Portfolio Analyzer\mobile"
flutter doctor
```

**Expected output:**
```
Doctor summary (to see all details, run flutter doctor -v):
[✓] Flutter (Channel stable, 3.27.1, on Microsoft Windows)
[✓] Android toolchain - develop for Android devices (Android SDK version 34.0.0)
[✓] Chrome - develop for the web
[✓] Visual Studio - develop Windows apps
[✓] Connected device (2 available)
[✓] Network resources
```

### Step 2: Clean Build Artifacts

```bash
flutter clean
flutter pub get
```

### Step 3: Update App Configuration

**File:** `android/app/build.gradle`

Update version information:
```gradle
android {
    defaultConfig {
        applicationId "com.portfolio.analyzer"
        minSdkVersion 21
        targetSdkVersion 34
        versionCode 1
        versionName "1.0.0"
    }
}
```

### Step 4: Build Release APK

**Standard APK (Universal):**
```bash
flutter build apk --release
```

**Split APKs (Smaller file sizes):**
```bash
flutter build apk --split-per-abi --release
```

This creates 3 separate APKs:
- `app-armeabi-v7a-release.apk` (32-bit ARM)
- `app-arm64-v8a-release.apk` (64-bit ARM)
- `app-x86_64-release.apk` (64-bit Intel/AMD)

**Output Location:**
```
build/app/outputs/flutter-apk/app-release.apk
```

### Step 5: Test APK

**On Physical Device:**
```bash
# Connect Android device via USB (enable USB Debugging)
adb install build/app/outputs/flutter-apk/app-release.apk
```

**On Emulator:**
```bash
# Start emulator from Android Studio
flutter install --release
```

---

## APK Distribution Options

### Option 1: Direct APK Distribution

**Pros:**
- ✅ Fastest method
- ✅ No account needed
- ✅ No app store approval process

**Cons:**
- ❌ Users must enable "Unknown Sources"
- ❌ No automatic updates
- ❌ Less trust from users

**How to Share:**
1. Upload APK to cloud storage (Google Drive, Dropbox, OneDrive)
2. Share download link with users
3. Provide installation instructions (see below)

### Option 2: Google Play Store

**Pros:**
- ✅ Trusted source
- ✅ Automatic updates
- ✅ Wider reach

**Cons:**
- ❌ $25 one-time developer fee
- ❌ App review process (1-7 days)
- ❌ Must follow Play Store policies

**Steps:**
1. Create Google Play Console account
2. Create app listing
3. Upload APK (or AAB - recommended)
4. Complete store listing (screenshots, description)
5. Submit for review

**Build AAB (App Bundle) for Play Store:**
```bash
flutter build appbundle --release
```

### Option 3: Firebase App Distribution

**Pros:**
- ✅ Free for small teams
- ✅ Easy beta testing
- ✅ Distribution to testers via email

**Cons:**
- ❌ Not public distribution
- ❌ Requires Firebase setup

**Setup:**
1. Create Firebase project
2. Add Firebase to Flutter app
3. Install Firebase CLI
4. Upload APK:
   ```bash
   firebase appdistribution:distribute build/app/outputs/flutter-apk/app-release.apk \
     --app YOUR_APP_ID \
     --groups "testers" \
     --release-notes "Initial release with portfolio and wealth management"
   ```

### Option 4: GitHub Releases

**Pros:**
- ✅ Free
- ✅ Version control
- ✅ Public distribution

**Steps:**
1. Go to your GitHub repository
2. Click "Releases" → "Create a new release"
3. Tag version (e.g., `v1.0.0`)
4. Upload APK file
5. Write release notes
6. Publish release

Users can then download directly from:
```
https://github.com/axis300013/portfolio-analyzer-supabase/releases/latest
```

---

## Installation Instructions for Users

### Prerequisites

- Android device running Android 5.0 (Lollipop) or higher
- Minimum 100 MB free storage
- Internet connection (for Supabase access)

### Installation Steps

#### Step 1: Download the APK

**Option A: From GitHub Releases**
1. Open this link on your Android device:
   ```
   https://github.com/axis300013/portfolio-analyzer-supabase/releases/latest
   ```
2. Tap on `app-release.apk` to download

**Option B: From Shared Link**
1. Open the link provided to you
2. Download the APK file

#### Step 2: Enable Unknown Sources

1. Open **Settings** on your Android device
2. Go to **Security** or **Privacy**
3. Enable **Install from Unknown Sources** or **Allow from this source**
   - On newer Android versions (8.0+), you'll be prompted to allow the specific app (Chrome, Downloads, etc.)

#### Step 3: Install the APK

1. Open your device's **Downloads** folder
2. Tap on the downloaded APK file (`app-release.apk`)
3. Tap **Install**
4. Wait for installation to complete
5. Tap **Open** to launch the app

#### Step 4: First-Time Setup

1. **Sign Up / Login**
   - Tap "Sign Up" if you're a new user
   - Enter your email and password
   - Verify your email (check spam folder if needed)

2. **Grant Permissions** (if prompted)
   - Storage: For potential data export
   - Internet: For Supabase connection

3. **Explore the App**
   - Dashboard: Overview of portfolio and wealth
   - Portfolio: Manage instruments, prices, transactions
   - Wealth: Track categories and values
   - Trends: View historical charts
   - Analytics: Detailed data tables

### Uninstallation

1. Go to **Settings** → **Apps**
2. Find **Portfolio Analyzer**
3. Tap **Uninstall**

---

## Troubleshooting

### Build Issues

#### Issue: "Android SDK not found"

**Solution:**
```powershell
# Set environment variable
$env:ANDROID_HOME = "C:\Users\<YourUsername>\AppData\Local\Android\Sdk"

# Verify
flutter doctor
```

#### Issue: "sdkmanager not found"

**Solution:**
Install Android SDK Command-line Tools from Android Studio SDK Manager.

#### Issue: "Gradle build failed"

**Solution:**
```bash
# Clean and rebuild
cd android
./gradlew clean
cd ..
flutter clean
flutter pub get
flutter build apk --release
```

### Installation Issues

#### Issue: "App not installed"

**Possible Causes:**
1. **Insufficient storage** - Free up space
2. **Conflicting package** - Uninstall any existing version first
3. **Corrupted APK** - Re-download the APK file

#### Issue: "Parse error"

**Causes:**
- APK file is corrupted during download
- Incompatible Android version (need 5.0+)

**Solution:**
- Download APK again
- Check Android version in Settings → About Phone

#### Issue: "App keeps crashing"

**Solutions:**
1. **Clear app cache:**
   - Settings → Apps → Portfolio Analyzer → Storage → Clear Cache
2. **Check internet connection** (app requires Supabase access)
3. **Reinstall the app**

---

## Alternative Distribution Methods

### 1. Progressive Web App (PWA)

Since the app is built with Flutter Web support, you can deploy it as a PWA:

**Advantages:**
- No installation needed
- Works on all platforms (Android, iOS, Desktop)
- Automatic updates

**Steps:**
1. Build web version:
   ```bash
   flutter build web --release
   ```
2. Deploy to hosting service:
   - **Netlify** (easiest)
   - **Vercel**
   - **Firebase Hosting**
   - **GitHub Pages**

3. Users access via browser:
   ```
   https://your-domain.com
   ```

### 2. Windows Desktop App

Build Windows executable:
```bash
flutter build windows --release
```

Output: `build/windows/x64/runner/Release/`

Package with Inno Setup or create ZIP for distribution.

### 3. iOS App (Requires Mac)

If you have a Mac:
```bash
flutter build ios --release
```

Then use Xcode to:
- Create IPA file
- Upload to App Store
- Or distribute via TestFlight

---

## Security Considerations

### Code Signing (for Play Store)

1. **Generate Keystore:**
   ```bash
   keytool -genkey -v -keystore ~/portfolio-analyzer-key.jks \
     -keyalg RSA -keysize 2048 -validity 10000 \
     -alias portfolio
   ```

2. **Create `android/key.properties`:**
   ```properties
   storePassword=<your-password>
   keyPassword=<your-password>
   keyAlias=portfolio
   storeFile=<path-to-keystore>
   ```

3. **Update `android/app/build.gradle`:**
   ```gradle
   signingConfigs {
       release {
           keyAlias keystoreProperties['keyAlias']
           keyPassword keystoreProperties['keyPassword']
           storeFile keystoreProperties['storeFile'] ? file(keystoreProperties['storeFile']) : null
           storePassword keystoreProperties['storePassword']
       }
   }
   ```

### ProGuard/R8 (Code Obfuscation)

Add to `android/app/build.gradle`:
```gradle
buildTypes {
    release {
        shrinkResources true
        minifyEnabled true
        proguardFiles getDefaultProguardFile('proguard-android.txt'), 'proguard-rules.pro'
    }
}
```

---

## Maintenance & Updates

### Version Numbering

Follow semantic versioning:
- **1.0.0** → Initial release
- **1.0.1** → Bug fixes
- **1.1.0** → New features
- **2.0.0** → Breaking changes

### Update Process

1. **Update version** in `pubspec.yaml`:
   ```yaml
   version: 1.1.0+2
   ```
   (Format: `major.minor.patch+build`)

2. **Build new APK**
   ```bash
   flutter build apk --release
   ```

3. **Distribute** via chosen method (GitHub Releases, Play Store, etc.)

4. **Notify users** of new version

---

## Contact & Support

For issues or questions:
- **GitHub Issues:** https://github.com/axis300013/portfolio-analyzer-supabase/issues
- **Email:** [Your contact email]
- **Documentation:** See `docs/MOBILE_APP_COMPLETE_DOCUMENTATION.md`

---

## Summary Checklist

### For Building APK:
- [ ] Install Android SDK
- [ ] Set ANDROID_HOME environment variable
- [ ] Run `flutter doctor` (all checks green)
- [ ] Run `flutter clean && flutter pub get`
- [ ] Run `flutter build apk --release`
- [ ] Test APK on device/emulator

### For Distribution:
- [ ] Choose distribution method (Direct/Play Store/Firebase/GitHub)
- [ ] Create installation instructions for users
- [ ] Test installation process
- [ ] Monitor for crashes/issues
- [ ] Plan update strategy

---

**Last Updated:** 2025-12-07  
**Document Version:** 1.0  
**App Version:** 1.0.0
