import 'package:supabase_flutter/supabase_flutter.dart';

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
    // Get all wealth categories
    final categories = await client.from('wealth_categories').select('id');
    final categoryIds =
        (categories as List).map((c) => c['id'] as int).toList();

    print('[Wealth] Total categories: ${categoryIds.length}');

    // For each category, get the latest value
    final latest = <Map<String, dynamic>>[];
    for (final categoryId in categoryIds) {
      final result = await client
          .from('wealth_values')
          .select('*, wealth_categories(name, category_type, is_liability)')
          .eq('wealth_category_id', categoryId)
          .order('value_date', ascending: false)
          .limit(1);

      if (result != null && (result as List).isNotEmpty) {
        latest.add((result as List)[0] as Map<String, dynamic>);
      }
    }

    print('[Wealth] Fetched latest for ${latest.length} categories');

    // Drop historic records (before 2026-01-01)
    final cutoff = DateTime(2026, 1, 1);
    final filtered = latest.where((item) {
      final dateStr = item['value_date'] as String?;
      if (dateStr == null) return false;
      final valueDate = DateTime.parse(dateStr);
      return !valueDate.isBefore(cutoff);
    }).toList();

    // Debug: post-cutoff distribution
    final typeCounts = <String, int>{};
    for (final item in filtered) {
      final cat = item['wealth_categories'] ?? {};
      final isLiability = cat['is_liability'] == true;
      final rawType = cat['category_type']?.toString() ?? '';
      final normalized =
          isLiability ? 'LIABILITIES' : rawType.toUpperCase().trim();
      typeCounts[normalized] = (typeCounts[normalized] ?? 0) + 1;
    }
    print('[Wealth] Post-cutoff type distribution: $typeCounts');

    return filtered;
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
          portfolio_instruments(instrument_name)
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
}
