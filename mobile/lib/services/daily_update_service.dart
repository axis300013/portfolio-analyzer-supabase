import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:async';

/// Service for triggering daily ETL updates from mobile app
///
/// Usage:
///   // Trigger manually
///   await DailyUpdateService.triggerDailyUpdate();
///
///   // Or get status
///   final status = await DailyUpdateService.getUpdateStatus();
///
/// Supports both local network (192.168.X.X:8000) and remote access (ngrok)

class DailyUpdateService {
  // Configuration - Update these based on your network setup
  static const String _localBackendUrl = "http://192.168.0.19:8000"; // Local IP
  static const String _remoteBackendUrl =
      "https://abc123.ngrok.io"; // ngrok URL

  // Use remote by default; set to false for local network
  static bool useRemoteBackend = false;

  static String get _baseUrl =>
      useRemoteBackend ? _remoteBackendUrl : _localBackendUrl;

  /// Trigger daily ETL update
  ///
  /// Returns success status and timestamp if update started
  /// Throws exception if network error or backend unreachable
  static Future<Map<String, dynamic>> triggerDailyUpdate() async {
    try {
      final uri = Uri.parse("$_baseUrl/api/updates/trigger-daily-update");

      final response = await http.post(
        uri,
        headers: {
          "Content-Type": "application/json",
          "User-Agent": "PortfolioAnalyzer-Mobile/1.0",
        },
      ).timeout(
        const Duration(seconds: 30),
        onTimeout: () => throw TimeoutException("Backend not responding"),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        return {
          "success": true,
          "status": data["status"],
          "timestamp": data["timestamp"],
        };
      } else {
        throw Exception("Backend error: ${response.statusCode}");
      }
    } catch (e) {
      return {
        "success": false,
        "error": e.toString(),
      };
    }
  }

  /// Get current status of ETL pipeline
  ///
  /// Returns:
  ///   {
  ///     "is_running": bool,
  ///     "last_started": "2026-01-14T10:30:00",
  ///     "last_completed": "2026-01-14T10:35:00",
  ///     "last_error": null,
  ///     "current_step": "Completed successfully"
  ///   }
  static Future<Map<String, dynamic>> getUpdateStatus() async {
    try {
      final uri = Uri.parse("$_baseUrl/api/updates/status");

      final response = await http.get(uri).timeout(
            const Duration(seconds: 10),
            onTimeout: () => throw TimeoutException("Backend not responding"),
          );

      if (response.statusCode == 200) {
        return jsonDecode(response.body) as Map<String, dynamic>;
      } else {
        throw Exception("Failed to get status: ${response.statusCode}");
      }
    } catch (e) {
      return {
        "error": e.toString(),
      };
    }
  }

  /// Configure automatic daily update schedule
  ///
  /// Parameters:
  ///   hour: Hour of day (0-23, default 7 = 7 AM)
  ///   minute: Minute (0-59, default 0)
  static Future<Map<String, dynamic>> scheduleDaily({
    int hour = 7,
    int minute = 0,
  }) async {
    try {
      final uri = Uri.parse(
          "$_baseUrl/api/updates/schedule-daily?hour=$hour&minute=$minute");

      final response = await http.post(uri).timeout(
            const Duration(seconds: 10),
            onTimeout: () => throw TimeoutException("Backend not responding"),
          );

      if (response.statusCode == 200) {
        return jsonDecode(response.body) as Map<String, dynamic>;
      } else {
        throw Exception("Failed to schedule: ${response.statusCode}");
      }
    } catch (e) {
      return {
        "error": e.toString(),
      };
    }
  }
}
