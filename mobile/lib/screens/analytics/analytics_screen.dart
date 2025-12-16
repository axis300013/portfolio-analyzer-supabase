import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import '../../services/supabase_service.dart';
import '../../utils/analytics_helpers.dart';

class AnalyticsScreen extends StatefulWidget {
  const AnalyticsScreen({super.key});

  @override
  State<AnalyticsScreen> createState() => _AnalyticsScreenState();
}

class _AnalyticsScreenState extends State<AnalyticsScreen> {
  DateTime _startDate = DateTime.now().subtract(const Duration(days: 90));
  DateTime _endDate = DateTime.now();
  String _granularity = 'Daily';
  bool _isLoading = false;

  List<Map<String, dynamic>> _portfolioData = [];
  List<Map<String, dynamic>> _wealthData = [];
  List<Map<String, dynamic>> _wealthValuesData = [];
  Map<String, dynamic>? _summary;

  final dateFormatter = DateFormat('yyyy-MM-dd');
  final numberFormatter = NumberFormat('#,##0', 'hu_HU');

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);

    try {
      // Load portfolio history
      final portfolioHistory = await SupabaseService.getPortfolioHistory(
        startDate: dateFormatter.format(_startDate),
        endDate: dateFormatter.format(_endDate),
      );

      // Load wealth snapshots
      final wealthSnapshots = await SupabaseService.getWealthSnapshotsRange(
        startDate: dateFormatter.format(_startDate),
        endDate: dateFormatter.format(_endDate),
      );

      // Load wealth values history
      final wealthValuesHistory = await SupabaseService.getWealthValuesHistory(
        startDate: dateFormatter.format(_startDate),
        endDate: dateFormatter.format(_endDate),
      );

      // Calculate summary - extract instrument names from nested instruments object
      final uniqueDates =
          portfolioHistory.map((e) => e['snapshot_date']).toSet().length;
      final uniqueInstruments = portfolioHistory
          .map((e) {
            final instruments = e['instruments'];
            if (instruments is Map) {
              return instruments['name'] ?? 'Unknown';
            }
            return 'Unknown';
          })
          .toSet()
          .length;

      setState(() {
        _portfolioData = portfolioHistory;
        _wealthData = wealthSnapshots;
        _wealthValuesData = wealthValuesHistory;
        _summary = {
          'datePoints': uniqueDates,
          'instruments': uniqueInstruments,
        };
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading data: $e')),
        );
      }
    }
  }

  Future<void> _selectStartDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _startDate,
      firstDate: DateTime(2015, 7),
      lastDate: DateTime.now(),
    );

    if (picked != null) {
      setState(() => _startDate = picked);
    }
  }

  Future<void> _selectEndDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _endDate,
      firstDate: DateTime(2015, 7),
      lastDate: DateTime.now(),
    );

    if (picked != null) {
      setState(() => _endDate = picked);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('📋 Analytical Data'),
      ),
      body: Column(
        children: [
          // Compact Controls - One Line
          Card(
            margin: const EdgeInsets.all(8),
            child: Padding(
              padding: const EdgeInsets.all(8),
              child: Row(
                children: [
                  // Start Date
                  Expanded(
                    flex: 2,
                    child: InkWell(
                      onTap: _selectStartDate,
                      child: Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 8, vertical: 6),
                        decoration: BoxDecoration(
                          border: Border.all(color: Colors.grey),
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text('Start',
                                style:
                                    TextStyle(fontSize: 9, color: Colors.grey)),
                            Text(dateFormatter.format(_startDate),
                                style: const TextStyle(fontSize: 11)),
                          ],
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 4),
                  // End Date
                  Expanded(
                    flex: 2,
                    child: InkWell(
                      onTap: _selectEndDate,
                      child: Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 8, vertical: 6),
                        decoration: BoxDecoration(
                          border: Border.all(color: Colors.grey),
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text('End',
                                style:
                                    TextStyle(fontSize: 9, color: Colors.grey)),
                            Text(dateFormatter.format(_endDate),
                                style: const TextStyle(fontSize: 11)),
                          ],
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 4),
                  // Granularity Dropdown
                  Expanded(
                    flex: 2,
                    child: DropdownButtonFormField<String>(
                      value: _granularity,
                      isDense: true,
                      decoration: const InputDecoration(
                        contentPadding:
                            EdgeInsets.symmetric(horizontal: 8, vertical: 6),
                        border: OutlineInputBorder(),
                        isDense: true,
                      ),
                      style: const TextStyle(fontSize: 11),
                      items: ['Daily', 'Monthly', 'Yearly']
                          .map(
                              (g) => DropdownMenuItem(value: g, child: Text(g)))
                          .toList(),
                      onChanged: (value) {
                        setState(() => _granularity = value!);
                      },
                    ),
                  ),
                  const SizedBox(width: 4),
                  // Load Button
                  ElevatedButton(
                    onPressed: _isLoading ? null : _loadData,
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 12, vertical: 12),
                      minimumSize: const Size(50, 32),
                    ),
                    child: const Icon(Icons.refresh, size: 16),
                  ),
                ],
              ),
            ),
          ),

          // Compact Summary metrics
          if (_summary != null)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 8),
              child: Row(
                children: [
                  Expanded(
                    child: _buildMetricCard(
                      'Points',
                      '${_summary!['datePoints']}',
                      Icons.calendar_today,
                    ),
                  ),
                  const SizedBox(width: 4),
                  Expanded(
                    child: _buildMetricCard(
                      'Items',
                      '${_summary!['instruments']}',
                      Icons.business_center,
                    ),
                  ),
                  const SizedBox(width: 4),
                  Expanded(
                    child: _buildMetricCard(
                      'Gran.',
                      _granularity,
                      Icons.grid_on,
                    ),
                  ),
                ],
              ),
            ),

          const SizedBox(height: 8),

          // Data tabs
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : DefaultTabController(
                    length: 3,
                    child: Column(
                      children: [
                        const TabBar(
                          tabs: [
                            Tab(text: 'Portfolio Details'),
                            Tab(text: 'Wealth Details'),
                            Tab(text: 'Combined Summary'),
                          ],
                        ),
                        Expanded(
                          child: TabBarView(
                            children: [
                              _buildPortfolioDetails(),
                              _buildWealthDetails(),
                              _buildCombinedSummary(),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
          ),
        ],
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: 4,
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
          BottomNavigationBarItem(
            icon: Icon(Icons.table_chart),
            label: 'Analytics',
          ),
        ],
      ),
    );
  }

  void _onNavigationTap(int index) {
    switch (index) {
      case 0:
        context.go('/');
        break;
      case 1:
        context.go('/portfolio');
        break;
      case 2:
        context.go('/wealth');
        break;
      case 3:
        context.go('/trends');
        break;
      case 4:
        context.go('/analytics');
        break;
    }
  }

  Widget _buildMetricCard(String label, String value, IconData icon) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(6),
        child: Column(
          children: [
            Icon(icon, size: 14, color: Colors.blue),
            const SizedBox(height: 2),
            Text(
              value,
              style: const TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.bold,
              ),
              overflow: TextOverflow.ellipsis,
            ),
            Text(
              label,
              style: const TextStyle(
                fontSize: 9,
                color: Colors.grey,
              ),
              overflow: TextOverflow.ellipsis,
            ),
          ],
        ),
      ),
    );
  }

  // Helper to wrap DataTable with pinch-to-zoom capability
  Widget _buildZoomableTable(DataTable table) {
    return InteractiveViewer(
      constrained: true,
      scaleEnabled: true,
      panEnabled: true,
      minScale: 0.5,
      maxScale: 4.0,
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: table,
      ),
    );
  }

  Widget _buildPortfolioDetails() {
    if (_portfolioData.isEmpty) {
      return const Center(
        child: Text('No portfolio data available for this date range'),
      );
    }

    // Get unique dates (columns)
    Set<String> uniqueDates = {};
    for (var row in _portfolioData) {
      uniqueDates.add(row['snapshot_date']?.substring(0, 10) ?? '');
    }
    List<String> sortedDates = uniqueDates.toList()..sort();

    // Get unique instruments (rows) - extract from nested instruments object
    Set<String> uniqueInstruments = {};
    for (var row in _portfolioData) {
      final instruments = row['instruments'];
      String instrumentName = 'Unknown';
      if (instruments is Map && instruments['name'] != null) {
        instrumentName = instruments['name'];
      }
      uniqueInstruments.add(instrumentName);
    }
    List<String> sortedInstruments = uniqueInstruments.toList()..sort();

    // Build data map: instrument -> date -> value
    Map<String, Map<String, double>> dataMap = {};
    for (var instrument in sortedInstruments) {
      dataMap[instrument] = {};
      for (var date in sortedDates) {
        dataMap[instrument]![date] = 0;
      }
    }

    // Fill in actual values
    for (var row in _portfolioData) {
      final instruments = row['instruments'];
      String instrument = 'Unknown';
      if (instruments is Map && instruments['name'] != null) {
        instrument = instruments['name'];
      }
      String date = row['snapshot_date']?.substring(0, 10) ?? '';
      double value = (row['value_huf'] ?? 0).toDouble();

      if (dataMap.containsKey(instrument) &&
          dataMap[instrument]!.containsKey(date)) {
        dataMap[instrument]![date] = (dataMap[instrument]![date] ?? 0) + value;
      }
    }

    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Main Portfolio Detail Table
          const Padding(
            padding: EdgeInsets.all(16.0),
            child: Text(
              'Portfolio Detail by Instrument',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
          ),
          _buildZoomableTable(
            DataTable(
              columns: [
                const DataColumn(label: Text('Instrument')),
                ...sortedDates.map((date) => DataColumn(
                      label: Text(date),
                      numeric: true,
                    )),
              ],
              rows: sortedInstruments.map((instrument) {
                return DataRow(cells: [
                  DataCell(Text(instrument)),
                  ...sortedDates.map((date) {
                    double value = dataMap[instrument]![date]!;
                    return DataCell(
                      Text(value > 0 ? numberFormatter.format(value) : '-'),
                    );
                  }),
                ]);
              }).toList(),
            ),
          ),
          const SizedBox(height: 24),

          // YoY Rolling Table
          const Padding(
            padding: EdgeInsets.all(16.0),
            child: Text(
              '📈 Summary Analytics for Portfolio - Rolling 12-Month % Change',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
          ),
          const Padding(
            padding: EdgeInsets.symmetric(horizontal: 16.0),
            child: Text(
              'Year-over-Year percentage change by instrument (Dec-to-Dec)',
              style: TextStyle(fontSize: 12, color: Colors.grey),
            ),
          ),
          _buildPortfolioYoYRolling(),
          const SizedBox(height: 24),

          // YoY Baseline Table
          const Padding(
            padding: EdgeInsets.all(16.0),
            child: Text(
              '📊 Summary Analytics YoY Portfolio - Year-over-Year by Instrument',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
          ),
          const Padding(
            padding: EdgeInsets.symmetric(horizontal: 16.0),
            child: Text(
              'Each year compared to prior year\'s December baseline by instrument',
              style: TextStyle(fontSize: 12, color: Colors.grey),
            ),
          ),
          _buildPortfolioYoYBaseline(),
        ],
      ),
    );
  }

  Widget _buildCombinedSummary() {
    if (_wealthData.isEmpty && _portfolioData.isEmpty) {
      return const Center(
        child: Text('No data available for this date range'),
      );
    }

    // Group portfolio data by date
    Map<String, double> portfolioByDate = {};
    for (var row in _portfolioData) {
      String date = row['snapshot_date']?.substring(0, 10) ?? '';
      portfolioByDate[date] =
          (portfolioByDate[date] ?? 0) + ((row['value_huf'] ?? 0).toDouble());
    }

    // Get all unique dates
    Set<String> allDates = {...portfolioByDate.keys};
    for (var wealth in _wealthData) {
      allDates.add(wealth['snapshot_date']?.substring(0, 10) ?? '');
    }

    List<String> sortedDates = allDates.toList()..sort();

    // Build data map: metric -> date -> value
    Map<String, Map<String, double>> dataMap = {
      'Portfolio Total': {},
      'Cash': {},
      'Property': {},
      'Pension': {},
      'Other Assets': {},
      'Loans': {},
      'Net Wealth': {},
    };

    for (String date in sortedDates) {
      var wealthRow = _wealthData.firstWhere(
        (w) => w['snapshot_date']?.substring(0, 10) == date,
        orElse: () => {},
      );

      dataMap['Portfolio Total']![date] = portfolioByDate[date] ?? 0;
      dataMap['Cash']![date] = (wealthRow['cash_huf'] ?? 0).toDouble();
      dataMap['Property']![date] = (wealthRow['property_huf'] ?? 0).toDouble();
      dataMap['Pension']![date] = (wealthRow['pension_huf'] ?? 0).toDouble();
      dataMap['Other Assets']![date] = (wealthRow['other_huf'] ?? 0).toDouble();
      dataMap['Loans']![date] = (wealthRow['loans_huf'] ?? 0).toDouble();
      dataMap['Net Wealth']![date] =
          (wealthRow['net_wealth_huf'] ?? 0).toDouble();
    }

    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Main Combined Summary Table
          const Padding(
            padding: EdgeInsets.all(16.0),
            child: Text(
              'Portfolio Summary Over Time',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
          ),
          _buildZoomableTable(
            DataTable(
              columns: [
                const DataColumn(label: Text('Metric')),
                ...sortedDates.map((date) => DataColumn(
                      label: Text(date),
                      numeric: true,
                    )),
              ],
              rows: dataMap.entries.map((entry) {
                return DataRow(cells: [
                  DataCell(Text(entry.key)),
                  ...sortedDates.map((date) {
                    double value = entry.value[date] ?? 0;
                    return DataCell(
                      Text(value != 0 ? numberFormatter.format(value) : '-'),
                    );
                  }),
                ]);
              }).toList(),
            ),
          ),
          const SizedBox(height: 24),

          // YoY Rolling Table
          const Padding(
            padding: EdgeInsets.all(16.0),
            child: Text(
              '📈 Summary Analytics - Rolling 12-Month % Change',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
          ),
          const Padding(
            padding: EdgeInsets.symmetric(horizontal: 16.0),
            child: Text(
              'Year-over-Year percentage change (Dec-to-Dec comparison)',
              style: TextStyle(fontSize: 12, color: Colors.grey),
            ),
          ),
          _buildCombinedSummaryYoYRolling(),
          const SizedBox(height: 24),

          // YoY Baseline Table
          const Padding(
            padding: EdgeInsets.all(16.0),
            child: Text(
              '📊 Summary Analytics YoY - Year-over-Year vs Prior December',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
          ),
          const Padding(
            padding: EdgeInsets.symmetric(horizontal: 16.0),
            child: Text(
              'Each year compared to prior year\'s December baseline',
              style: TextStyle(fontSize: 12, color: Colors.grey),
            ),
          ),
          _buildCombinedSummaryYoYBaseline(),
        ],
      ),
    );
  }

  Widget _buildWealthDetails() {
    if (_wealthValuesData.isEmpty) {
      return const Center(
        child: Text('No wealth values data available for this date range'),
      );
    }

    // Get unique dates and categories
    Set<String> uniqueDates = {};
    Set<String> uniqueCategories = {};

    for (var row in _wealthValuesData) {
      uniqueDates.add(row['value_date']?.substring(0, 10) ?? '');
      final category = row['wealth_categories'];
      if (category is Map) {
        uniqueCategories.add(category['name'] ?? 'Unknown');
      }
    }

    List<String> sortedDates = uniqueDates.toList()..sort();
    List<String> sortedCategories = uniqueCategories.toList()..sort();

    // Build data map: category -> date -> value
    Map<String, Map<String, double>> dataMap = {};
    for (var category in sortedCategories) {
      dataMap[category] = {};
      for (var date in sortedDates) {
        dataMap[category]![date] = 0;
      }
    }

    // Fill in actual values
    for (var row in _wealthValuesData) {
      final category = row['wealth_categories'];
      if (category is Map) {
        String categoryName = category['name'] ?? 'Unknown';
        String date = row['value_date']?.substring(0, 10) ?? '';
        double value = (row['present_value'] ?? 0).toDouble();

        if (dataMap.containsKey(categoryName) &&
            dataMap[categoryName]!.containsKey(date)) {
          dataMap[categoryName]![date] = value;
        }
      }
    }

    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Main Wealth Detail Table
          const Padding(
            padding: EdgeInsets.all(16.0),
            child: Text(
              'Wealth Detail by Category',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
          ),
          _buildZoomableTable(
            DataTable(
              columns: [
                const DataColumn(label: Text('Category')),
                ...sortedDates.map((date) => DataColumn(
                      label: Text(date),
                      numeric: true,
                    )),
              ],
              rows: sortedCategories.map((category) {
                return DataRow(cells: [
                  DataCell(Text(category)),
                  ...sortedDates.map((date) {
                    double value = dataMap[category]![date]!;
                    return DataCell(
                      Text(value > 0 ? numberFormatter.format(value) : '-'),
                    );
                  }),
                ]);
              }).toList(),
            ),
          ),
          const SizedBox(height: 24),

          // YoY Rolling Table
          const Padding(
            padding: EdgeInsets.all(16.0),
            child: Text(
              '📈 Summary Analytics for Wealth - Rolling 12-Month % Change',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
          ),
          const Padding(
            padding: EdgeInsets.symmetric(horizontal: 16.0),
            child: Text(
              'Year-over-Year percentage change by category (Dec-to-Dec)',
              style: TextStyle(fontSize: 12, color: Colors.grey),
            ),
          ),
          _buildWealthYoYRolling(),
          const SizedBox(height: 24),

          // YoY Baseline Table
          const Padding(
            padding: EdgeInsets.all(16.0),
            child: Text(
              '📊 Summary Analytics YoY Wealth - Year-over-Year by Category',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
          ),
          const Padding(
            padding: EdgeInsets.symmetric(horizontal: 16.0),
            child: Text(
              'Each year compared to prior year\'s December baseline by category',
              style: TextStyle(fontSize: 12, color: Colors.grey),
            ),
          ),
          _buildWealthYoYBaseline(),
        ],
      ),
    );
  }

  /// Build YoY Rolling table for Combined Summary
  Widget _buildCombinedSummaryYoYRolling() {
    if (_wealthData.isEmpty && _portfolioData.isEmpty) {
      return const Center(child: Text('Insufficient data for YoY analysis'));
    }

    // Prepare data in format needed for YoY calculation
    Map<String, double> portfolioByDate = {};
    for (var row in _portfolioData) {
      String date = row['snapshot_date']?.substring(0, 10) ?? '';
      portfolioByDate[date] =
          (portfolioByDate[date] ?? 0) + ((row['value_huf'] ?? 0).toDouble());
    }

    Set<String> allDates = {...portfolioByDate.keys};
    for (var wealth in _wealthData) {
      allDates.add(wealth['snapshot_date']?.substring(0, 10) ?? '');
    }

    List<String> sortedDates = allDates.toList()..sort();

    // Build list of maps for YoY calculation
    List<Map<String, dynamic>> timeSeriesData = [];
    for (String date in sortedDates) {
      var wealthRow = _wealthData.firstWhere(
        (w) => w['snapshot_date']?.substring(0, 10) == date,
        orElse: () => {},
      );

      timeSeriesData.add({
        'date': date,
        'portfolio_total': portfolioByDate[date] ?? 0,
        'cash': (wealthRow['cash_huf'] ?? 0).toDouble(),
        'property': (wealthRow['property_huf'] ?? 0).toDouble(),
        'pension': (wealthRow['pension_huf'] ?? 0).toDouble(),
        'other': (wealthRow['other_huf'] ?? 0).toDouble(),
        'loans': (wealthRow['loans_huf'] ?? 0).toDouble(),
        'net_wealth': (wealthRow['net_wealth_huf'] ?? 0).toDouble(),
      });
    }

    // Calculate YoY
    var yoyData = AnalyticsHelpers.calculateRollingYoY(
      data: timeSeriesData,
      dateCol: 'date',
      valueCols: [
        'portfolio_total',
        'cash',
        'property',
        'pension',
        'other',
        'loans',
        'net_wealth'
      ],
    );

    if (yoyData.isEmpty) {
      return const Center(child: Text('No YoY data available'));
    }

    // Transpose: dates as columns, metrics as rows
    List<String> dates = yoyData.map((r) => r['date'] as String).toList();
    Map<String, List<String>> metricsData = {
      'Portfolio Total': [],
      'Cash': [],
      'Property': [],
      'Pension': [],
      'Other Assets': [],
      'Loans': [],
      'Net Wealth': [],
    };

    List<String> yoyKeys = [
      'portfolio_total_YoY%',
      'cash_YoY%',
      'property_YoY%',
      'pension_YoY%',
      'other_YoY%',
      'loans_YoY%',
      'net_wealth_YoY%'
    ];

    for (var row in yoyData) {
      metricsData['Portfolio Total']!
          .add(AnalyticsHelpers.formatPercent(row[yoyKeys[0]]));
      metricsData['Cash']!.add(AnalyticsHelpers.formatPercent(row[yoyKeys[1]]));
      metricsData['Property']!
          .add(AnalyticsHelpers.formatPercent(row[yoyKeys[2]]));
      metricsData['Pension']!
          .add(AnalyticsHelpers.formatPercent(row[yoyKeys[3]]));
      metricsData['Other Assets']!
          .add(AnalyticsHelpers.formatPercent(row[yoyKeys[4]]));
      metricsData['Loans']!
          .add(AnalyticsHelpers.formatPercent(row[yoyKeys[5]]));
      metricsData['Net Wealth']!
          .add(AnalyticsHelpers.formatPercent(row[yoyKeys[6]]));
    }

    return _buildZoomableTable(
      DataTable(
        columns: [
          const DataColumn(label: Text('Metric')),
          ...dates.map((date) => DataColumn(label: Text(date))),
        ],
        rows: metricsData.entries.map((entry) {
          return DataRow(cells: [
            DataCell(Text(entry.key)),
            ...entry.value.map((val) => DataCell(Text(val))),
          ]);
        }).toList(),
      ),
    );
  }

  /// Build YoY Baseline table for Combined Summary
  Widget _buildCombinedSummaryYoYBaseline() {
    if (_wealthData.isEmpty && _portfolioData.isEmpty) {
      return const Center(child: Text('Insufficient data for YoY analysis'));
    }

    // Prepare time series data (same as rolling)
    Map<String, double> portfolioByDate = {};
    for (var row in _portfolioData) {
      String date = row['snapshot_date']?.substring(0, 10) ?? '';
      portfolioByDate[date] =
          (portfolioByDate[date] ?? 0) + ((row['value_huf'] ?? 0).toDouble());
    }

    Set<String> allDates = {...portfolioByDate.keys};
    for (var wealth in _wealthData) {
      allDates.add(wealth['snapshot_date']?.substring(0, 10) ?? '');
    }

    List<String> sortedDates = allDates.toList()..sort();

    List<Map<String, dynamic>> timeSeriesData = [];
    for (String date in sortedDates) {
      var wealthRow = _wealthData.firstWhere(
        (w) => w['snapshot_date']?.substring(0, 10) == date,
        orElse: () => {},
      );

      timeSeriesData.add({
        'date': date,
        'portfolio_total': portfolioByDate[date] ?? 0,
        'cash': (wealthRow['cash_huf'] ?? 0).toDouble(),
        'property': (wealthRow['property_huf'] ?? 0).toDouble(),
        'pension': (wealthRow['pension_huf'] ?? 0).toDouble(),
        'other': (wealthRow['other_huf'] ?? 0).toDouble(),
        'loans': (wealthRow['loans_huf'] ?? 0).toDouble(),
        'net_wealth': (wealthRow['net_wealth_huf'] ?? 0).toDouble(),
      });
    }

    // Calculate baseline YoY
    var yoyData = AnalyticsHelpers.calculateYoYBaseline(
      data: timeSeriesData,
      dateCol: 'date',
      valueCols: [
        'portfolio_total',
        'cash',
        'property',
        'pension',
        'other',
        'loans',
        'net_wealth'
      ],
    );

    if (yoyData.isEmpty) {
      return const Center(child: Text('No YoY baseline data available'));
    }

    // Transpose: years as columns, metrics as rows
    List<int> years = yoyData.map((r) => r['Year'] as int).toList();
    Map<String, List<String>> metricsData = {
      'Portfolio Total': [],
      'Cash': [],
      'Property': [],
      'Pension': [],
      'Other Assets': [],
      'Loans': [],
      'Net Wealth': [],
    };

    List<String> yoyKeys = [
      'portfolio_total_YoY%',
      'cash_YoY%',
      'property_YoY%',
      'pension_YoY%',
      'other_YoY%',
      'loans_YoY%',
      'net_wealth_YoY%'
    ];

    for (var row in yoyData) {
      metricsData['Portfolio Total']!
          .add(AnalyticsHelpers.formatPercent(row[yoyKeys[0]]));
      metricsData['Cash']!.add(AnalyticsHelpers.formatPercent(row[yoyKeys[1]]));
      metricsData['Property']!
          .add(AnalyticsHelpers.formatPercent(row[yoyKeys[2]]));
      metricsData['Pension']!
          .add(AnalyticsHelpers.formatPercent(row[yoyKeys[3]]));
      metricsData['Other Assets']!
          .add(AnalyticsHelpers.formatPercent(row[yoyKeys[4]]));
      metricsData['Loans']!
          .add(AnalyticsHelpers.formatPercent(row[yoyKeys[5]]));
      metricsData['Net Wealth']!
          .add(AnalyticsHelpers.formatPercent(row[yoyKeys[6]]));
    }

    return _buildZoomableTable(
      DataTable(
        columns: [
          const DataColumn(label: Text('Metric')),
          ...years.map((year) => DataColumn(label: Text(year.toString()))),
        ],
        rows: metricsData.entries.map((entry) {
          return DataRow(cells: [
            DataCell(Text(entry.key)),
            ...entry.value.map((val) => DataCell(Text(val))),
          ]);
        }).toList(),
      ),
    );
  }

  /// Build YoY Rolling table for Portfolio Details
  Widget _buildPortfolioYoYRolling() {
    if (_portfolioData.isEmpty) {
      return const Center(child: Text('Insufficient data for portfolio YoY'));
    }

    // Get unique instruments
    Set<String> uniqueInstruments = {};
    for (var row in _portfolioData) {
      final instruments = row['instruments'];
      if (instruments is Map && instruments['name'] != null) {
        uniqueInstruments.add(instruments['name']);
      }
    }

    List<String> sortedInstruments = uniqueInstruments.toList()..sort();

    // Calculate YoY for each instrument
    Map<String, List<Map<String, dynamic>>> yoyByInstrument = {};

    for (var instrument in sortedInstruments) {
      // Get time series for this instrument
      List<Map<String, dynamic>> instrumentData = [];
      Map<String, double> valuesByDate = {};

      for (var row in _portfolioData) {
        final instruments = row['instruments'];
        if (instruments is Map && instruments['name'] == instrument) {
          String date = row['snapshot_date']?.substring(0, 10) ?? '';
          double value = (row['value_huf'] ?? 0).toDouble();
          valuesByDate[date] = (valuesByDate[date] ?? 0) + value;
        }
      }

      List<String> dates = valuesByDate.keys.toList()..sort();
      for (var date in dates) {
        instrumentData.add({
          'date': date,
          'value': valuesByDate[date],
        });
      }

      if (instrumentData.length >= 2) {
        var yoyData = AnalyticsHelpers.calculateRollingYoY(
          data: instrumentData,
          dateCol: 'date',
          valueCols: ['value'],
        );
        yoyByInstrument[instrument] = yoyData;
      }
    }

    if (yoyByInstrument.isEmpty) {
      return const Center(child: Text('Insufficient data for YoY analysis'));
    }

    // Get all unique dates from all instruments
    Set<String> allDates = {};
    for (var yoyList in yoyByInstrument.values) {
      for (var row in yoyList) {
        allDates.add(row['date'] as String);
      }
    }
    List<String> sortedDates = allDates.toList()..sort();

    return _buildZoomableTable(
      DataTable(
        columns: [
          const DataColumn(label: Text('Instrument')),
          ...sortedDates.map((date) => DataColumn(label: Text(date))),
        ],
        rows: sortedInstruments
            .where((inst) => yoyByInstrument.containsKey(inst))
            .map((instrument) {
          List<Map<String, dynamic>> yoyData = yoyByInstrument[instrument]!;
          Map<String, dynamic> yoyMap = {};
          for (var row in yoyData) {
            yoyMap[row['date']] = row['value_YoY%'];
          }

          return DataRow(cells: [
            DataCell(Text(instrument)),
            ...sortedDates.map((date) {
              return DataCell(
                  Text(AnalyticsHelpers.formatPercent(yoyMap[date])));
            }),
          ]);
        }).toList(),
      ),
    );
  }

  /// Build YoY Baseline table for Portfolio Details
  Widget _buildPortfolioYoYBaseline() {
    if (_portfolioData.isEmpty) {
      return const Center(child: Text('Insufficient data for portfolio YoY'));
    }

    // Get unique instruments
    Set<String> uniqueInstruments = {};
    for (var row in _portfolioData) {
      final instruments = row['instruments'];
      if (instruments is Map && instruments['name'] != null) {
        uniqueInstruments.add(instruments['name']);
      }
    }

    List<String> sortedInstruments = uniqueInstruments.toList()..sort();

    // Calculate YoY baseline for each instrument
    Map<String, List<Map<String, dynamic>>> yoyByInstrument = {};

    for (var instrument in sortedInstruments) {
      List<Map<String, dynamic>> instrumentData = [];
      Map<String, double> valuesByDate = {};

      for (var row in _portfolioData) {
        final instruments = row['instruments'];
        if (instruments is Map && instruments['name'] == instrument) {
          String date = row['snapshot_date']?.substring(0, 10) ?? '';
          double value = (row['value_huf'] ?? 0).toDouble();
          valuesByDate[date] = (valuesByDate[date] ?? 0) + value;
        }
      }

      List<String> dates = valuesByDate.keys.toList()..sort();
      for (var date in dates) {
        instrumentData.add({
          'date': date,
          'value': valuesByDate[date],
        });
      }

      if (instrumentData.length >= 2) {
        var yoyData = AnalyticsHelpers.calculateYoYBaseline(
          data: instrumentData,
          dateCol: 'date',
          valueCols: ['value'],
        );
        yoyByInstrument[instrument] = yoyData;
      }
    }

    if (yoyByInstrument.isEmpty) {
      return const Center(child: Text('Insufficient data for YoY baseline'));
    }

    // Get all unique years
    Set<int> allYears = {};
    for (var yoyList in yoyByInstrument.values) {
      for (var row in yoyList) {
        allYears.add(row['Year'] as int);
      }
    }
    List<int> sortedYears = allYears.toList()..sort();

    return _buildZoomableTable(
      DataTable(
        columns: [
          const DataColumn(label: Text('Instrument')),
          ...sortedYears
              .map((year) => DataColumn(label: Text(year.toString()))),
        ],
        rows: sortedInstruments
            .where((inst) => yoyByInstrument.containsKey(inst))
            .map((instrument) {
          List<Map<String, dynamic>> yoyData = yoyByInstrument[instrument]!;
          Map<int, dynamic> yoyMap = {};
          for (var row in yoyData) {
            yoyMap[row['Year']] = row['value_YoY%'];
          }

          return DataRow(cells: [
            DataCell(Text(instrument)),
            ...sortedYears.map((year) {
              return DataCell(
                  Text(AnalyticsHelpers.formatPercent(yoyMap[year])));
            }),
          ]);
        }).toList(),
      ),
    );
  }

  /// Build YoY Rolling table for Wealth Details
  Widget _buildWealthYoYRolling() {
    if (_wealthValuesData.isEmpty) {
      return const Center(child: Text('Insufficient data for wealth YoY'));
    }

    // Get unique categories
    Set<String> uniqueCategories = {};
    for (var row in _wealthValuesData) {
      final category = row['wealth_categories'];
      if (category is Map) {
        uniqueCategories.add(category['name'] ?? 'Unknown');
      }
    }

    List<String> sortedCategories = uniqueCategories.toList()..sort();

    // Calculate YoY for each category
    Map<String, List<Map<String, dynamic>>> yoyByCategory = {};

    for (var category in sortedCategories) {
      List<Map<String, dynamic>> categoryData = [];
      Map<String, double> valuesByDate = {};

      for (var row in _wealthValuesData) {
        final cat = row['wealth_categories'];
        if (cat is Map && cat['name'] == category) {
          String date = row['value_date']?.substring(0, 10) ?? '';
          double value = (row['present_value'] ?? 0).toDouble();
          valuesByDate[date] = value;
        }
      }

      List<String> dates = valuesByDate.keys.toList()..sort();
      for (var date in dates) {
        categoryData.add({
          'date': date,
          'value': valuesByDate[date],
        });
      }

      if (categoryData.length >= 2) {
        var yoyData = AnalyticsHelpers.calculateRollingYoY(
          data: categoryData,
          dateCol: 'date',
          valueCols: ['value'],
        );
        yoyByCategory[category] = yoyData;
      }
    }

    if (yoyByCategory.isEmpty) {
      return const Center(child: Text('Insufficient data for YoY analysis'));
    }

    // Get all unique dates
    Set<String> allDates = {};
    for (var yoyList in yoyByCategory.values) {
      for (var row in yoyList) {
        allDates.add(row['date'] as String);
      }
    }
    List<String> sortedDates = allDates.toList()..sort();

    return _buildZoomableTable(
      DataTable(
        columns: [
          const DataColumn(label: Text('Category')),
          ...sortedDates.map((date) => DataColumn(label: Text(date))),
        ],
        rows: sortedCategories
            .where((cat) => yoyByCategory.containsKey(cat))
            .map((category) {
          List<Map<String, dynamic>> yoyData = yoyByCategory[category]!;
          Map<String, dynamic> yoyMap = {};
          for (var row in yoyData) {
            yoyMap[row['date']] = row['value_YoY%'];
          }

          return DataRow(cells: [
            DataCell(Text(category)),
            ...sortedDates.map((date) {
              return DataCell(
                  Text(AnalyticsHelpers.formatPercent(yoyMap[date])));
            }),
          ]);
        }).toList(),
      ),
    );
  }

  /// Build YoY Baseline table for Wealth Details
  Widget _buildWealthYoYBaseline() {
    if (_wealthValuesData.isEmpty) {
      return const Center(child: Text('Insufficient data for wealth YoY'));
    }

    // Get unique categories
    Set<String> uniqueCategories = {};
    for (var row in _wealthValuesData) {
      final category = row['wealth_categories'];
      if (category is Map) {
        uniqueCategories.add(category['name'] ?? 'Unknown');
      }
    }

    List<String> sortedCategories = uniqueCategories.toList()..sort();

    // Calculate YoY baseline for each category
    Map<String, List<Map<String, dynamic>>> yoyByCategory = {};

    for (var category in sortedCategories) {
      List<Map<String, dynamic>> categoryData = [];
      Map<String, double> valuesByDate = {};

      for (var row in _wealthValuesData) {
        final cat = row['wealth_categories'];
        if (cat is Map && cat['name'] == category) {
          String date = row['value_date']?.substring(0, 10) ?? '';
          double value = (row['present_value'] ?? 0).toDouble();
          valuesByDate[date] = value;
        }
      }

      List<String> dates = valuesByDate.keys.toList()..sort();
      for (var date in dates) {
        categoryData.add({
          'date': date,
          'value': valuesByDate[date],
        });
      }

      if (categoryData.length >= 2) {
        var yoyData = AnalyticsHelpers.calculateYoYBaseline(
          data: categoryData,
          dateCol: 'date',
          valueCols: ['value'],
        );
        yoyByCategory[category] = yoyData;
      }
    }

    if (yoyByCategory.isEmpty) {
      return const Center(child: Text('Insufficient data for YoY baseline'));
    }

    // Get all unique years
    Set<int> allYears = {};
    for (var yoyList in yoyByCategory.values) {
      for (var row in yoyList) {
        allYears.add(row['Year'] as int);
      }
    }
    List<int> sortedYears = allYears.toList()..sort();

    return _buildZoomableTable(
      DataTable(
        columns: [
          const DataColumn(label: Text('Category')),
          ...sortedYears
              .map((year) => DataColumn(label: Text(year.toString()))),
        ],
        rows: sortedCategories
            .where((cat) => yoyByCategory.containsKey(cat))
            .map((category) {
          List<Map<String, dynamic>> yoyData = yoyByCategory[category]!;
          Map<int, dynamic> yoyMap = {};
          for (var row in yoyData) {
            yoyMap[row['Year']] = row['value_YoY%'];
          }

          return DataRow(cells: [
            DataCell(Text(category)),
            ...sortedYears.map((year) {
              return DataCell(
                  Text(AnalyticsHelpers.formatPercent(yoyMap[year])));
            }),
          ]);
        }).toList(),
      ),
    );
  }
}
