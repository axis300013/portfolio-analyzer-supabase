import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import '../../services/supabase_service.dart';
import '../../models/wealth_snapshot.dart';

class WealthScreen extends StatefulWidget {
  const WealthScreen({super.key});

  @override
  State<WealthScreen> createState() => _WealthScreenState();
}

class _WealthScreenState extends State<WealthScreen> {
  List<Map<String, dynamic>> _wealthData = [];
  Map<String, dynamic>? _dashboardSummary;
  DateTime? _snapshotDate;
  bool _isLoading = true;
  String? _errorMessage;
  int _selectedIndex = 2;

  final currencyFormatter = NumberFormat.currency(
    locale: 'hu_HU',
    symbol: 'Ft',
    decimalDigits: 0,
  );

  @override
  void initState() {
    super.initState();
    _loadWealthData();
  }

  Future<void> _loadWealthData() async {
    try {
      // Load both dashboard summary (for total assets) and wealth details
      final summary = await SupabaseService.getDashboardSummary();
      final data = await SupabaseService.getLatestWealthValues();

      // Extract snapshot date from the data
      DateTime? snapshotDate;
      if (data.isNotEmpty && data[0]['value_date'] != null) {
        snapshotDate = DateTime.parse(data[0]['value_date'] as String);
      }

      // Debug: Print first item to see structure
      if (data.isNotEmpty) {
        print('Sample wealth item: ${data[0]}');
        print('Wealth categories: ${data[0]['wealth_categories']}');
      }

      setState(() {
        _dashboardSummary = summary;
        // Filter to show only non-zero values
        _wealthData = data.where((item) {
          final value = (item['present_value'] ?? 0) as num;
          return value != 0;
        }).toList();
        _snapshotDate = snapshotDate;
        _isLoading = false;

        // Debug: Print categorization
        print('Total items loaded: ${_wealthData.length}');
        print('CASH items: ${_getItemsByCategory('CASH').length}');
        print('PROPERTY items: ${_getItemsByCategory('PROPERTY').length}');
        print('PENSION items: ${_getItemsByCategory('PENSION').length}');
        print(
            'LIABILITIES items: ${_getItemsByCategory('LIABILITIES').length}');

        // Debug: show category types to detect trailing spaces/variants
        final typeCounts = <String, int>{};
        for (final item in _wealthData) {
          final normalized = _normalizedCategoryType(item);
          typeCounts[normalized] = (typeCounts[normalized] ?? 0) + 1;
        }
        print('Category type distribution (normalized): $typeCounts');

        // Debug: list CASH items with names/values to find filtered entries
        final cashItems = _getItemsByCategory('CASH');
        for (final item in cashItems) {
          final name = item['wealth_categories']?['name'];
          final value = item['present_value'];
          final rawType = item['wealth_categories']?['category_type'];
          print('CASH item -> name: $name | value: $value | rawType: $rawType');
        }
      });
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
        _isLoading = false;
      });
    }
  }

  void _onNavigationTap(int index) {
    setState(() {
      _selectedIndex = index;
    });

    switch (index) {
      case 0:
        context.go('/');
        break;
      case 1:
        context.go('/portfolio');
        break;
      case 2:
        // Already on wealth
        break;
      case 3:
        context.go('/trends');
        break;
    }
  }

  List<Map<String, dynamic>> _getItemsByCategory(String categoryType) {
    final target = categoryType.toUpperCase();
    return _wealthData
        .where((item) => _normalizedCategoryType(item) == target)
        .toList();
  }

  String _normalizedCategoryType(Map<String, dynamic> item) {
    final wealthCategory = item['wealth_categories'];
    final isLiability = wealthCategory?['is_liability'] == true;
    if (isLiability) return 'LIABILITIES';

    final rawType = wealthCategory?['category_type']?.toString() ?? '';
    final normalized = rawType.toUpperCase().trim();
    return normalized.isEmpty ? 'UNKNOWN' : normalized;
  }

  double _getCategoryTotal(String categoryType) {
    return _getItemsByCategory(categoryType).fold<double>(
      0.0,
      (sum, item) => sum + ((item['present_value'] ?? 0) as num).toDouble(),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Wealth Tracker'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.go('/'),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              setState(() {
                _isLoading = true;
                _errorMessage = null;
              });
              _loadWealthData();
            },
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _errorMessage != null
              ? Center(
                  child: Padding(
                    padding: const EdgeInsets.all(24.0),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(
                          Icons.error_outline,
                          size: 64,
                          color: Colors.red,
                        ),
                        const SizedBox(height: 16),
                        Text(
                          'Error loading wealth data',
                          style: Theme.of(context).textTheme.headlineSmall,
                        ),
                        const SizedBox(height: 8),
                        Text(
                          _errorMessage!,
                          textAlign: TextAlign.center,
                          style: const TextStyle(color: Colors.grey),
                        ),
                        const SizedBox(height: 24),
                        ElevatedButton(
                          onPressed: _loadWealthData,
                          child: const Text('Retry'),
                        ),
                      ],
                    ),
                  ),
                )
              : _wealthData.isEmpty
                  ? const Center(
                      child: Text('No wealth data available'),
                    )
                  : RefreshIndicator(
                      onRefresh: _loadWealthData,
                      child: Column(
                        children: [
                          _buildSummaryHeader(),
                          Expanded(
                            child: ListView(
                              padding: const EdgeInsets.all(16),
                              children: [
                                if (_snapshotDate != null)
                                  Padding(
                                    padding: const EdgeInsets.only(bottom: 16),
                                    child: Text(
                                      'Snapshot Date: ${DateFormat('yyyy-MM-dd').format(_snapshotDate!)}',
                                      style: const TextStyle(
                                        fontSize: 12,
                                        color: Colors.grey,
                                      ),
                                    ),
                                  ),
                                ..._getDisplayCategories()
                                    .map((category) => Padding(
                                          padding:
                                              const EdgeInsets.only(bottom: 16),
                                          child: _buildCategorySection(
                                            category,
                                            _getCategoryColor(category),
                                            _getCategoryIcon(category),
                                          ),
                                        )),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _selectedIndex,
        onTap: _onNavigationTap,
        type: BottomNavigationBarType.fixed,
        backgroundColor: Colors.grey[900],
        selectedItemColor: Colors.blue,
        unselectedItemColor: Colors.grey,
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.dashboard),
            label: 'Dashboard',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.trending_up),
            label: 'Portfolio',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.account_balance_wallet),
            label: 'Wealth',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.show_chart),
            label: 'Trends',
          ),
        ],
      ),
    );
  }

  Widget _buildSummaryHeader() {
    if (_dashboardSummary == null) {
      return const SizedBox.shrink();
    }

    final totalAssets = (_dashboardSummary!['total_assets'] ?? 0) as num;
    final liabilities = (_dashboardSummary!['total_liabilities'] ?? 0) as num;
    final netWealth = totalAssets - liabilities;

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [Colors.green[700]!, Colors.green[900]!],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
      ),
      child: Column(
        children: [
          const Text(
            'Total Assets (Wealth)',
            style: TextStyle(
              fontSize: 16,
              color: Colors.white70,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            currencyFormatter.format(totalAssets.toDouble()),
            style: const TextStyle(
              fontSize: 32,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              Column(
                children: [
                  const Text(
                    'Assets',
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.white70,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    currencyFormatter.format(totalAssets.toDouble()),
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                ],
              ),
              Column(
                children: [
                  const Text(
                    'Liabilities',
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.white70,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    currencyFormatter.format(liabilities.toDouble()),
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ],
      ),
    );
  }

  List<String> _getDisplayCategories() {
    // Return fixed categories in order
    final categories = ['CASH', 'PROPERTY', 'PENSION', 'LIABILITIES'];
    // Only return categories that have items
    return categories
        .where((cat) => _getItemsByCategory(cat).isNotEmpty)
        .toList();
  }

  Color _getCategoryColor(String categoryType) {
    switch (categoryType) {
      case 'CASH':
        return Colors.green;
      case 'PROPERTY':
        return Colors.blue;
      case 'PENSION':
        return Colors.orange;
      case 'LIABILITIES':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  IconData _getCategoryIcon(String categoryType) {
    switch (categoryType) {
      case 'CASH':
        return Icons.attach_money;
      case 'PROPERTY':
        return Icons.home;
      case 'PENSION':
        return Icons.account_balance;
      case 'LIABILITIES':
        return Icons.credit_card;
      default:
        return Icons.account_balance_wallet;
    }
  }

  Widget _buildCategorySection(
      String categoryType, Color color, IconData icon) {
    final items = _getItemsByCategory(categoryType);
    if (items.isEmpty) return const SizedBox.shrink();

    final total = _getCategoryTotal(categoryType);

    return Card(
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(12),
                topRight: Radius.circular(12),
              ),
            ),
            child: Row(
              children: [
                Icon(icon, color: color),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    categoryType,
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: color,
                    ),
                  ),
                ),
                Text(
                  currencyFormatter.format(total),
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: color,
                  ),
                ),
              ],
            ),
          ),
          ...items.map((item) => _buildWealthItem(item)),
        ],
      ),
    );
  }

  Widget _buildWealthItem(Map<String, dynamic> item) {
    final rawName = item['wealth_categories']?['name'] ?? 'Unknown';
    final categoryName = _normalizeName(rawName);
    final value = (item['present_value'] ?? 0) as num;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: const BoxDecoration(
        border: Border(
          top: BorderSide(color: Colors.grey, width: 0.5),
        ),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  categoryName,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Present Value',
                  style: const TextStyle(
                    fontSize: 12,
                    color: Colors.grey,
                  ),
                ),
              ],
            ),
          ),
          Text(
            currencyFormatter.format(value.toDouble()),
            style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  String _normalizeName(String rawName) {
    final cleaned =
        rawName.replaceAll(RegExp(r'[^\x20-\x7E]'), '').toLowerCase();
    if (cleaned.contains('szep') ||
        cleaned.contains('szp') ||
        cleaned.contains('szepkartya') ||
        cleaned.contains('szpkartya')) {
      // Normalize corrupted SZEP kartya variants to a single readable label
      return 'SZEP Kartya';
    }
    return rawName;
  }
}
