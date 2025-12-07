import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import '../../services/supabase_service.dart';

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
      firstDate: DateTime(2020),
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
      firstDate: DateTime(2020),
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
          // Controls
          Card(
            margin: const EdgeInsets.all(16),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: InkWell(
                          onTap: _selectStartDate,
                          child: InputDecorator(
                            decoration: const InputDecoration(
                              labelText: 'Start Date',
                              border: OutlineInputBorder(),
                            ),
                            child: Text(dateFormatter.format(_startDate)),
                          ),
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: InkWell(
                          onTap: _selectEndDate,
                          child: InputDecorator(
                            decoration: const InputDecoration(
                              labelText: 'End Date',
                              border: OutlineInputBorder(),
                            ),
                            child: Text(dateFormatter.format(_endDate)),
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Expanded(
                        child: DropdownButtonFormField<String>(
                          value: _granularity,
                          decoration: const InputDecoration(
                            labelText: 'Granularity',
                            border: OutlineInputBorder(),
                          ),
                          items: ['Daily', 'Monthly']
                              .map((g) =>
                                  DropdownMenuItem(value: g, child: Text(g)))
                              .toList(),
                          onChanged: (value) {
                            setState(() => _granularity = value!);
                          },
                        ),
                      ),
                      const SizedBox(width: 16),
                      ElevatedButton.icon(
                        onPressed: _isLoading ? null : _loadData,
                        icon: const Icon(Icons.refresh),
                        label: const Text('Load Data'),
                        style: ElevatedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 24, vertical: 16),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),

          // Summary metrics
          if (_summary != null)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Row(
                children: [
                  Expanded(
                    child: _buildMetricCard(
                      'Date Points',
                      '${_summary!['datePoints']}',
                      Icons.calendar_today,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: _buildMetricCard(
                      'Instruments',
                      '${_summary!['instruments']}',
                      Icons.business_center,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: _buildMetricCard(
                      'Granularity',
                      _granularity,
                      Icons.grid_on,
                    ),
                  ),
                ],
              ),
            ),

          const SizedBox(height: 16),

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
                            Tab(text: 'Combined Summary'),
                            Tab(text: 'Wealth Details'),
                          ],
                        ),
                        Expanded(
                          child: TabBarView(
                            children: [
                              _buildPortfolioDetails(),
                              _buildCombinedSummary(),
                              _buildWealthDetails(),
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
        padding: const EdgeInsets.all(12),
        child: Column(
          children: [
            Icon(icon, size: 24, color: Colors.blue),
            const SizedBox(height: 8),
            Text(
              value,
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            Text(
              label,
              style: const TextStyle(
                fontSize: 12,
                color: Colors.grey,
              ),
            ),
          ],
        ),
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
      scrollDirection: Axis.horizontal,
      child: SingleChildScrollView(
        child: DataTable(
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
      scrollDirection: Axis.horizontal,
      child: SingleChildScrollView(
        child: DataTable(
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
      scrollDirection: Axis.horizontal,
      child: SingleChildScrollView(
        child: DataTable(
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
    );
  }
}
