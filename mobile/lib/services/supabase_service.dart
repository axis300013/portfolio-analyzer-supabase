import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class SupabaseService {
  static final SupabaseClient client = Supabase.instance.client;

  // Auth Methods
  static Future<AuthResponse> signUp(String email, String password) async {
    return await client.auth.signUp(
      email: email,
      password: password,
    );
  }

  static Future<AuthResponse> signIn(String email, String password) async {
    return await client.auth.signInWithPassword(
      email: email,
      password: password,
    );
  }

  static Future<void> signOut() async {
    await client.auth.signOut();
  }

  static User? get currentUser => client.auth.currentUser;

  // Portfolio Data Methods
  static Future<List<Map<String, dynamic>>> getPortfolioSnapshots({
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    final data = await client
        .from('portfolio_values_daily')
        .select()
        .order('snapshot_date', ascending: false);

    // Filter in Dart since the old API doesn't support gte/lte easily
    if (startDate != null || endDate != null) {
      return data.where((item) {
        final date = DateTime.parse(item['snapshot_date'] as String);
        if (startDate != null && date.isBefore(startDate)) return false;
        if (endDate != null && date.isAfter(endDate)) return false;
        return true;
      }).toList();
    }

    return data;
  }

  static Future<List<Map<String, dynamic>>> getPortfolioInstruments() async {
    return await client.from('instruments').select().order('name');
  }

  static Future<List<Map<String, dynamic>>> getLatestPortfolioValues() async {
    // Get the latest snapshot date first
    final latestSnapshot = await client
        .from('portfolio_values_daily')
        .select('snapshot_date')
        .order('snapshot_date', ascending: false)
        .limit(1)
        .single();

    final latestDate = latestSnapshot['snapshot_date'];

    // Get all values for that date
    final data = await client.from('portfolio_values_daily').select('''
          *,
          instruments(name, instrument_type, currency)
        ''').order('instrument_id');

    return data.where((item) => item['snapshot_date'] == latestDate).toList();
  }

  static Future<List<Map<String, dynamic>>> getPortfolioValuesByDate(
      String date) async {
    final data = await client.from('portfolio_values_daily').select('''
          *,
          instruments(name, instrument_type, currency)
        ''').order('instrument_id');

    return data.where((item) => item['snapshot_date'] == date).toList();
  }

  static Future<List<String>> getAvailablePortfolioDates() async {
    final data = await client
        .from('portfolio_values_daily')
        .select('snapshot_date')
        .order('snapshot_date', ascending: false);

    print('🔍 Raw data from Supabase: ${data.length} rows');
    if (data.isNotEmpty) {
      print('🔍 First row: ${data.first}');
      print('🔍 Last row: ${data.last}');
    }

    // Get unique dates
    final dates =
        data.map((item) => item['snapshot_date'] as String).toSet().toList();

    print('🔍 Unique dates: $dates');
    return dates;
  }

  // Wealth Data Methods
  static Future<List<Map<String, dynamic>>> getWealthSnapshots({
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    final data = await client
        .from('total_wealth_snapshots')
        .select()
        .order('snapshot_date', ascending: false);

    // Filter in Dart since the old API doesn't support gte/lte easily
    if (startDate != null || endDate != null) {
      return data.where((item) {
        final date = DateTime.parse(item['snapshot_date'] as String);
        if (startDate != null && date.isBefore(startDate)) return false;
        if (endDate != null && date.isAfter(endDate)) return false;
        return true;
      }).toList();
    }

    return data;
  }

  static Future<List<Map<String, dynamic>>> getWealthItems() async {
    return await client
        .from('wealth_categories')
        .select()
        .order('category_type, name');
  }

  static Future<List<Map<String, dynamic>>> getLatestWealthValues() async {
    // Get the latest snapshot date
    final latestSnapshot = await client
        .from('wealth_values')
        .select('value_date')
        .order('value_date', ascending: false)
        .limit(1)
        .single();

    final latestDate = latestSnapshot['value_date'];

    // Get all values for that date
    final data = await client.from('wealth_values').select('''
          *,
          wealth_categories(name, category_type, is_liability)
        ''').order('wealth_category_id');

    return data.where((item) => item['value_date'] == latestDate).toList();
  }

  // Analytics Methods
  static Future<Map<String, dynamic>> getDashboardSummary() async {
    try {
      // Get latest portfolio value from portfolio_values_daily
      final portfolioData = await getLatestPortfolioValues();
      final portfolioTotal = portfolioData.fold<double>(
        0.0,
        (sum, item) => sum + ((item['value_huf'] ?? 0) as num).toDouble(),
      );

      // Get latest wealth values
      final wealthData = await getLatestWealthValues();
      final assets = wealthData.where((item) {
        final category = item['wealth_categories'];
        return category != null &&
            (category['is_liability'] == false ||
                category['is_liability'] == null);
      }).fold<double>(
        0.0,
        (sum, item) => sum + ((item['present_value'] ?? 0) as num).toDouble(),
      );

      final liabilities = wealthData.where((item) {
        final category = item['wealth_categories'];
        return category != null && category['is_liability'] == true;
      }).fold<double>(
        0.0,
        (sum, item) => sum + ((item['present_value'] ?? 0) as num).toDouble(),
      );

      // Net wealth = portfolio + other assets - liabilities
      final netWealth = portfolioTotal + assets - liabilities;

      // Get counts
      final instrumentCount = (await getPortfolioInstruments()).length;
      final wealthItemCount = (await getWealthItems()).length;

      return {
        'portfolio_value': portfolioTotal,
        'total_assets': assets,
        'total_liabilities': liabilities,
        'net_wealth': netWealth,
        'instrument_count': instrumentCount,
        'wealth_item_count': wealthItemCount,
      };
    } catch (e) {
      rethrow;
    }
  }

  // Transaction Methods
  static Future<List<Map<String, dynamic>>> getTransactions({
    DateTime? startDate,
    DateTime? endDate,
    int? instrumentId,
  }) async {
    final data = await client.from('transactions').select('''
          *,
          instruments(name)
        ''').order('transaction_date', ascending: false);

    // Filter in Dart
    return data.where((item) {
      if (instrumentId != null && item['instrument_id'] != instrumentId)
        return false;
      if (startDate != null || endDate != null) {
        final date = DateTime.parse(item['transaction_date'] as String);
        if (startDate != null && date.isBefore(startDate)) return false;
        if (endDate != null && date.isAfter(endDate)) return false;
      }
      return true;
    }).toList();
  }

  // Portfolio Management - Manual Price Updates
  static Future<void> saveManualPrice({
    required int instrumentId,
    required double price,
    required String priceDate,
    required String currency,
  }) async {
    try {
      final data = {
        'instrument_id': instrumentId,
        'price': price,
        'price_date': priceDate,
        'currency': currency,
        'source': 'manual',
      };

      print('🔍 Attempting to save price with data: $data');

      // Use upsert to update if exists, insert if not
      await client
          .from('prices')
          .upsert(data, onConflict: 'instrument_id,price_date,source');

      print('✅ Price saved successfully');
    } catch (e) {
      print('❌ Error saving price: $e');
      rethrow;
    }
  }

  // Portfolio Management - Transaction Recording
  static Future<void> saveTransaction({
    required int instrumentId,
    required String transactionType,
    required double quantity,
    required double price,
    required String transactionDate,
  }) async {
    await client.from('transactions').insert({
      'portfolio_id': 1, // Default portfolio
      'instrument_id': instrumentId,
      'transaction_type': transactionType,
      'quantity': quantity,
      'price': price,
      'transaction_date': transactionDate,
      'currency': 'HUF', // Default currency
    });
  }

  // Portfolio Management - Instrument CRUD
  static Future<void> addInstrument({
    required String name,
    String? isin,
    String? ticker,
    required String instrumentType,
    required String currency,
  }) async {
    await client.from('instruments').insert({
      'name': name,
      'isin': isin,
      'ticker': ticker,
      'instrument_type': instrumentType,
      'currency': currency,
      'is_active': true,
    });
  }

  static Future<void> updateInstrument({
    required int id,
    String? name,
    String? isin,
    String? ticker,
    String? instrumentType,
    String? currency,
    bool? isActive,
  }) async {
    final updates = <String, dynamic>{};
    if (name != null) updates['name'] = name;
    if (isin != null) updates['isin'] = isin;
    if (ticker != null) updates['ticker'] = ticker;
    if (instrumentType != null) updates['instrument_type'] = instrumentType;
    if (currency != null) updates['currency'] = currency;
    if (isActive != null) updates['is_active'] = isActive;

    if (updates.isNotEmpty) {
      updates['updated_at'] = DateTime.now().toIso8601String();
      await client.from('instruments').update(updates).eq('id', id);
    }
  }

  static Future<void> deleteInstrument(int id) async {
    // Soft delete by setting is_active to false
    await client.from('instruments').update({
      'is_active': false,
      'updated_at': DateTime.now().toIso8601String(),
    }).eq('id', id);
  }

  // Wealth Management - Category CRUD
  static Future<void> addWealthCategory({
    required String name,
    required String categoryType,
    required bool isLiability,
    String? description,
  }) async {
    await client.from('wealth_categories').insert({
      'name': name,
      'category_type': categoryType,
      'is_liability': isLiability,
      'description': description,
    });
  }

  static Future<void> updateWealthCategory({
    required int id,
    String? name,
    String? categoryType,
    bool? isLiability,
    String? description,
  }) async {
    final updates = <String, dynamic>{};
    if (name != null) updates['name'] = name;
    if (categoryType != null) updates['category_type'] = categoryType;
    if (isLiability != null) updates['is_liability'] = isLiability;
    if (description != null) updates['description'] = description;

    if (updates.isNotEmpty) {
      updates['updated_at'] = DateTime.now().toIso8601String();
      await client.from('wealth_categories').update(updates).eq('id', id);
    }
  }

  static Future<void> deleteWealthCategory(int id) async {
    await client.from('wealth_categories').delete().eq('id', id);
  }

  // Wealth Management - Value Updates
  static Future<void> saveWealthValue({
    required int categoryId,
    required double presentValue,
    required String valueDate,
    String? note,
  }) async {
    // Check if a record already exists for this category and date
    final existing = await client
        .from('wealth_values')
        .select('id')
        .eq('wealth_category_id', categoryId)
        .eq('value_date', valueDate)
        .maybeSingle();

    if (existing != null) {
      // Update existing record
      await client
          .from('wealth_values')
          .update({
            'present_value': presentValue,
            'note': note,
          })
          .eq('wealth_category_id', categoryId)
          .eq('value_date', valueDate);
    } else {
      // Insert new record
      await client.from('wealth_values').insert({
        'wealth_category_id': categoryId,
        'present_value': presentValue,
        'value_date': valueDate,
        'note': note,
      });
    }
  }

  // ETL Trigger - Refresh Data from Backend
  static Future<Map<String, dynamic>> triggerDataUpdate({
    String? backendUrl,
  }) async {
    // Default to localhost for development
    final url = backendUrl ?? 'http://localhost:8000';

    try {
      final response = await http.post(
        Uri.parse('$url/etl/run-daily-update'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(const Duration(seconds: 180));

      if (response.statusCode == 200) {
        final result = json.decode(response.body);
        return {
          'success': true,
          'message': result['message'] ?? 'Data update completed successfully',
          'timestamp': result['timestamp'] ?? DateTime.now().toIso8601String(),
        };
      } else {
        return {
          'success': false,
          'message': 'Server returned status ${response.statusCode}',
          'error': response.body,
        };
      }
    } catch (e) {
      // Backend not available or error occurred
      return {
        'success': false,
        'message': 'Backend not available. Use desktop app to update data.',
        'error': e.toString(),
      };
    }
  }

  // Simple data refresh - just reload from Supabase (no backend ETL)
  static Future<void> refreshFromSupabase() async {
    // This is just a marker method - screens should call their specific load methods
    // The actual refresh happens when screens reload their data
    await Future.delayed(const Duration(milliseconds: 500));
  }

  // Analytics - Portfolio History
  static Future<List<Map<String, dynamic>>> getPortfolioHistory({
    required String startDate,
    required String endDate,
  }) async {
    final response = await client
        .from('portfolio_values_daily')
        .select('*, instruments(name, instrument_type)')
        .gte('snapshot_date', startDate)
        .lte('snapshot_date', endDate)
        .order('snapshot_date', ascending: true);

    return List<Map<String, dynamic>>.from(response as List);
  }

  // Analytics - Wealth Snapshots (with date range)
  static Future<List<Map<String, dynamic>>> getWealthSnapshotsRange({
    required String startDate,
    required String endDate,
  }) async {
    final response = await client
        .from('total_wealth_snapshots')
        .select('*')
        .gte('snapshot_date', startDate)
        .lte('snapshot_date', endDate)
        .order('snapshot_date', ascending: true);

    return List<Map<String, dynamic>>.from(response as List);
  }

  // Analytics - Wealth Values History (with categories)
  static Future<List<Map<String, dynamic>>> getWealthValuesHistory({
    required String startDate,
    required String endDate,
  }) async {
    final response = await client
        .from('wealth_values')
        .select('''
          *,
          wealth_categories(name, category_type, is_liability)
        ''')
        .gte('value_date', startDate)
        .lte('value_date', endDate)
        .order('value_date', ascending: true);

    return List<Map<String, dynamic>>.from(response as List);
  }
}
