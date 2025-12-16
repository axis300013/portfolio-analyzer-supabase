# Portfolio Analyzer Mobile App - Installation Guide

**Version:** 1.0.0  
**Build Date:** December 10, 2025  
**Package:** com.example.portfolio_analyzer

---

## 📱 **Files Available**

### 1. **PortfolioAnalyzer-v1.0.0.apk** (22.6 MB)
- ✅ **Use this for direct installation on Android devices**
- Ready to install on any Android phone/tablet
- No Google Play Store needed

### 2. **PortfolioAnalyzer-v1.0.0.aab** (22.9 MB)
- For Google Play Store distribution (if needed later)
- Cannot be installed directly on devices

---

## 🚀 **Method 1: USB Cable Transfer (Recommended)**

### Step 1: Enable Developer Options on Your Phone
1. Go to **Settings** → **About Phone**
2. Tap **Build Number** 7 times until you see "You are now a developer!"
3. Go back to **Settings** → **Developer Options**
4. Enable **USB Debugging**

### Step 2: Transfer the APK
1. Connect your phone to PC via USB cable
2. Select **File Transfer** mode on your phone
3. Copy `PortfolioAnalyzer-v1.0.0.apk` to your phone's **Downloads** folder

### Step 3: Install the APK
1. On your phone, open **Files** or **My Files** app
2. Navigate to **Downloads**
3. Tap on `PortfolioAnalyzer-v1.0.0.apk`
4. If prompted, allow "Install from unknown sources" for Files app
5. Tap **Install**
6. Tap **Open** to launch the app

---

## 📧 **Method 2: Email Transfer**

1. Email the APK file to yourself
2. Open the email on your phone
3. Download the attachment
4. Open the downloaded APK file
5. Allow installation from unknown sources if prompted
6. Install and open

---

## 🌐 **Method 3: Cloud Storage (Google Drive, Dropbox, etc.)**

1. Upload `PortfolioAnalyzer-v1.0.0.apk` to Google Drive/Dropbox
2. Open the cloud storage app on your phone
3. Download the APK
4. Install as described above

---

## ⚙️ **Method 4: ADB Install (Advanced)**

If you have ADB installed:

```powershell
# Connect phone via USB with USB debugging enabled
adb devices

# Install the APK
adb install "C:\Users\SzalmaNB1\Downloads\cabeceo\visual studio\Portfolio Analyzer\mobile_builds\PortfolioAnalyzer-v1.0.0.apk"
```

---

## 🔑 **Important: Backend Configuration**

Before using the app, you need to ensure the backend is accessible:

### **Option 1: Use Supabase (Default)**
- ✅ App is configured to use Supabase backend
- No additional setup needed
- Works anywhere with internet connection

### **Option 2: Use Local Backend (Development)**
If you want to connect to your local desktop backend:

1. Make sure your phone and PC are on the **same WiFi network**
2. Find your PC's local IP address:
   ```powershell
   ipconfig | Select-String IPv4
   ```
3. Start the backend on your PC:
   ```powershell
   cd "C:\Users\SzalmaNB1\Downloads\cabeceo\visual studio\Portfolio Analyzer"
   .\START_PORTABLE.bat
   ```
4. Update the mobile app's `.env` file before building:
   ```
   SUPABASE_URL=http://YOUR_PC_IP:8000
   ```
5. Rebuild the APK

---

## 🛡️ **Security Notice**

This app is **signed with debug keys** for development purposes. For production distribution:

1. Generate a proper signing key:
   ```powershell
   keytool -genkey -v -keystore portfolio-release-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias portfolio
   ```

2. Configure signing in `android/key.properties`

3. Update `android/app/build.gradle` to use release signing config

4. Rebuild: `flutter build apk --release`

---

## 📊 **App Features**

✅ Dashboard - Net wealth overview  
✅ Portfolio - Track investments with date picker  
✅ Wealth - Manage cash, property, pensions, loans  
✅ Trends - Visual graphs (Portfolio, Net Wealth, Asset Breakdown)  
✅ Analytics - Detailed historical data tables  

---

## 🐛 **Troubleshooting**

### "App not installed" error
- Delete any previous version of the app
- Ensure enough storage space (need ~50 MB)
- Try restarting your phone

### "Install blocked" error
- Go to Settings → Security → Install unknown apps
- Allow installation for your file manager/browser

### App crashes on startup
- Check internet connection (for Supabase)
- Clear app data: Settings → Apps → Portfolio Analyzer → Clear Data
- Reinstall the app

### Cannot connect to backend
- Verify Supabase credentials in the app
- Check your internet connection
- If using local backend, ensure PC and phone are on same WiFi

---

## 📝 **Version History**

### v1.0.0 (December 10, 2025)
- ✅ Complete historical data integration (2015-2025)
- ✅ 33 snapshots spanning 10.5 years
- ✅ Net wealth tracking: 104.4M → 183.0M HUF
- ✅ All 5 screens functional
- ✅ Supabase backend integration
- ✅ Mobile CRUD operations (add/edit/delete)
- ✅ Date picker for historical data
- ✅ Analytics tables with full history

---

## 📞 **Support**

For issues or questions:
- Check the backend is running
- Verify Supabase connection
- Review app logs in Android Studio Logcat

---

**Enjoy tracking your portfolio! 📈💰**
