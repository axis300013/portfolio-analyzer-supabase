# Portfolio Analyzer Mobile - Quick Installation Guide

**⚡ Get started in 5 minutes!**

---

## 📱 For Mobile Users (Android)

### Option 1: Web Version (Recommended - No Installation!)

**Access the app directly in your browser:**

1. Open Chrome or any modern browser on your phone
2. Go to: `http://localhost:8501` (when desktop app is running)
3. Tap the menu (⋮) → "Add to Home Screen"
4. The app will appear like a native app on your phone!

**Advantages:**
- ✅ Works immediately
- ✅ No APK installation needed
- ✅ Automatic updates
- ✅ Same features as native app

### Option 2: Direct APK Installation

**When Android SDK is available:**

1. **Download APK** from GitHub Releases:
   ```
   https://github.com/axis300013/portfolio-analyzer-supabase/releases/latest
   ```

2. **Enable Unknown Sources:**
   - Settings → Security → Enable "Install from Unknown Sources"

3. **Install:**
   - Open the downloaded APK file
   - Tap "Install"
   - Tap "Open" when done

4. **Login:**
   - Use your email and password
   - Verify email if first time

---

## 🖥️ For Desktop Users

### Current Setup (Already Working!)

**You already have everything running!**

1. **Start the app:**
   ```powershell
   .\start_portfolio_supabase.ps1
   ```

2. **Access UI:**
   - Open browser: `http://localhost:8501`
   - Desktop Streamlit app with full features

3. **Mobile access:**
   - On same WiFi network
   - Open phone browser: `http://[your-pc-ip]:8501`
   - Find your PC IP: `ipconfig` (look for IPv4)

---

## 🚀 Building Your Own APK

**If you want to build the APK yourself:**

### Prerequisites

1. **Install Android Studio:**
   - Download: https://developer.android.com/studio
   - Install with default settings

2. **Set Environment Variable:**
   ```powershell
   $env:ANDROID_HOME = "C:\Users\$env:USERNAME\AppData\Local\Android\Sdk"
   [Environment]::SetEnvironmentVariable("ANDROID_HOME", $env:ANDROID_HOME, "User")
   ```

3. **Verify Setup:**
   ```bash
   flutter doctor
   ```

### Build Command

```powershell
cd "c:\Users\SzalmaNB1\Downloads\cabeceo\visual studio\Portfolio Analyzer\mobile"
flutter build apk --release
```

**Output location:**
```
build/app/outputs/flutter-apk/app-release.apk
```

**File size:** ~30 MB

---

## 📊 Feature Comparison

| Feature | Web Version | Native APK |
|---------|------------|------------|
| Installation | None needed | APK install |
| Updates | Automatic | Manual |
| Performance | Good | Excellent |
| Offline Mode | No | Limited |
| Storage | Browser cache | App storage |
| Permissions | Minimal | Standard Android |

---

## 🔧 Troubleshooting

### "Android SDK not found"

**Quick fix:**
```powershell
# Install via Android Studio:
# Tools → SDK Manager → Install Android SDK Platform 34
```

### "APK won't install"

1. Check Android version (need 5.0+)
2. Free up storage space (need 100 MB)
3. Uninstall old version first
4. Re-download APK

### "App crashes on launch"

1. Check internet connection
2. Clear app cache: Settings → Apps → Portfolio Analyzer → Storage → Clear Cache
3. Reinstall the app

---

## 💡 Recommended Approach

**For now, use the Web Version:**

1. Desktop app is already running perfectly
2. Access from phone browser on same WiFi
3. Add to home screen for app-like experience
4. Build APK later when Android SDK is set up

**Benefits:**
- ✅ Zero setup time
- ✅ Works immediately
- ✅ No troubleshooting needed
- ✅ Full functionality

---

## 📚 Next Steps

1. **Use Web Version:**
   - Access `http://[your-pc-ip]:8501` from phone
   - Add to home screen
   - Start managing portfolio!

2. **Setup Android SDK (Optional):**
   - Follow detailed guide: `docs/APK_BUILD_AND_DISTRIBUTION_GUIDE.md`
   - Build APK for offline use
   - Distribute to family/friends

3. **Explore Features:**
   - Dashboard: Overview
   - Portfolio: Manage instruments
   - Wealth: Track assets/liabilities
   - Trends: Historical charts
   - Analytics: Detailed data

---

## ✨ Tips for Best Experience

### On Mobile Web:

1. **Add to Home Screen:**
   - Chrome menu → "Add to Home Screen"
   - Creates app icon on phone

2. **Enable Desktop Site (if needed):**
   - Chrome menu → "Desktop site"
   - For full-width tables

3. **Bookmark for Quick Access:**
   - Chrome menu → ⭐ Bookmark
   - Save to bookmarks bar

### Performance:

- Use WiFi (faster than mobile data)
- Close other browser tabs
- Clear browser cache if slow
- Refresh page if data doesn't load

---

## 🎯 Summary

**Current Status:**
- ✅ Desktop app: Fully functional
- ✅ Web access: Working on localhost
- ✅ Mobile features: All screens implemented
- ⏳ APK: Requires Android SDK setup

**Recommended Action:**
1. Use web version now (immediate access)
2. Set up Android SDK later (for APK)
3. Enjoy portfolio management today!

---

**Questions?** Check `docs/APK_BUILD_AND_DISTRIBUTION_GUIDE.md` for detailed instructions.

**Last Updated:** 2025-12-07
