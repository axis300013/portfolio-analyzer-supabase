# Mobile App - 4 Critical Issues to Fix

## Issue 1: Wealth Management Edit Error
**Problem**: `updateWealthCategory` method needs the `id` parameter to be cast as int
**Location**: `wealth_management_screen.dart` line ~254
**Fix**: Cast `category['id']` to int: `id: category['id'] as int`

## Issue 2: Dashboard "Run Update" - Backend Not Available  
**Problem**: Backend URL hardcoded to localhost:8000, not accessible from mobile
**Location**: `supabase_service.dart` triggerDataUpdate()
**Fix**: Backend isn't running OR provide better error handling message

## Issue 3: Portfolio Management - Currency Not Selectable
**Problem**: Dropdown needs `onChanged` callback to update state variable
**Location**: `portfolio_management_screen.dart` line ~667
**Fix**: Add proper state management: `onChanged: (value) { setState(() => selectedCurrency = value); }`

## Issue 4: Saving Price - PostgrestException
**Problem**: Missing `currency` column in prices table insert
**Location**: `supabase_service.dart` saveManualPrice()
**Fix**: Add currency parameter or use default from instrument

Let me check the exact Supabase schema and implement fixes...
