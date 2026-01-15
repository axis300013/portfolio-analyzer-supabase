# Mobile Trends Screen Enhancement Plan
**Date**: 2026-01-14

## Overview
Enhance the mobile app Trends screen to match the desktop app's new features:
1. Add statistics metrics at the top
2. Add expandable detail tables below charts
3. Add portfolio.jpg as app icon and splash screen
4. Build APK

---

## Phase 1: Add Statistics Metrics

### Net Wealth Metrics Card
```dart
- Current Net Wealth: Latest value with % change indicator
- Net Wealth Period Change: Absolute + percentage
- Data Points: Count of data points
```

### Portfolio Metrics Card
```dart
- Current Portfolio Value: Latest value with % change indicator
- Portfolio Period Change: Absolute + percentage  
- Portfolio vs Net Wealth: Portfolio as % of total wealth
```

---

## Phase 2: Add Detail Tables

### Table 1: Net Wealth Details (Below Chart 1)
- Expandable ExpansionTile widget
- Shows Date, Net Wealth, Portfolio, Cash, Property, Pension, Liabilities (if available)
- Formatted with NumberFormat
- Scrollable DataTable

### Table 2: Portfolio Details (Below Chart 2)
- Expandable ExpansionTile widget
- Shows Date, Portfolio Value
- Formatted with NumberFormat
- Scrollable DataTable

---

## Phase 3: Icon & Splash Screen

### App Icon Setup
1. Copy portfolio.jpg to mobile/assets/images/
2. Update android/app/src/main/res/mipmap-xxx/ folders
3. Use flutter_launcher_icons package

### Splash Screen Setup
1. Update android/app/src/main/res/drawable/launch_background.xml
2. Add portfolio.jpg as splash image
3. Configure native splash screen

---

## Phase 4: Build APK

```bash
cd mobile
flutter clean
flutter pub get
flutter build apk --release
```

Output: `mobile/build/app/outputs/flutter-apk/app-release.apk`

---

## Implementation Status
- [ ] Statistics metrics
- [ ] Detail tables
- [ ] App icon
- [ ] Splash screen
- [ ] Build APK
