import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:intl/intl.dart';
import '../../services/supabase_service.dart';
import '../../utils/analytics_helpers.dart';

class TrendsScreen extends StatefulWidget {
  const TrendsScreen({super.key});

  @override
  State<TrendsScreen> createState() => _TrendsScreenState();
}

class _TrendsScreenState extends State<TrendsScreen> {
  List<Map<String, dynamic>> _portfolioSnapshots = [];
  List<Map<String, dynamic>> _wealthSnapshots = [];
  bool _isLoading = true;
  String? _errorMessage;
  int _selectedIndex = 3;
  String _selectedPeriod = 'ALL';

  final currencyFormatter = NumberFormat.currency(
    locale: 'hu_HU',
    symbol: 'Ft',
    decimalDigits: 0,
  );

  @override
  void initState() {
    super.initState();
    _loadTrendsData();
  }

  Future<void> _loadTrendsData() async {
    try {
      final DateTime endDate = DateTime.now();
      // Always load ALL data from 2015 for YoY calculations
      // Period filtering will be applied in chart builders
      final DateTime startDate = DateTime(2015, 7);

      final portfolioData = await SupabaseService.getPortfolioSnapshots(
        startDate: startDate,
        endDate: endDate,
      );

      final wealthData = await SupabaseService.getWealthSnapshots(
        startDate: startDate,
        endDate: endDate,
      );

      setState(() {
        _portfolioSnapshots = portfolioData;
        _wealthSnapshots = wealthData;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
        _isLoading = false;
      });
    }
  }

  DateTime _getStartDate(String period) {
    final now = DateTime.now();
    switch (period) {
      case '1M':
        return now.subtract(const Duration(days: 30));
      case '3M':
        return now.subtract(const Duration(days: 90));
      case '6M':
        return now.subtract(const Duration(days: 180));
      case '1Y':
        return now.subtract(const Duration(days: 365));
      case 'ALL':
        return DateTime(2000);
      default:
        return now.subtract(const Duration(days: 180));
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
        context.go('/wealth');
        break;
      case 3:
        // Already on trends
        break;
      case 4:
        context.go('/analytics');
        break;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Trends & Analytics'),
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
              _loadTrendsData();
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
                          'Error loading trends',
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
                          onPressed: _loadTrendsData,
                          child: const Text('Retry'),
                        ),
                      ],
                    ),
                  ),
                )
              : RefreshIndicator(
                  onRefresh: _loadTrendsData,
                  child: ListView(
                    padding: const EdgeInsets.all(16),
                    children: [
                      _buildPeriodSelector(),
                      const SizedBox(height: 16),
                      const Text(
                        'Portfolio Value Over Time',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 16),
                      _buildPortfolioChart(),
                      const SizedBox(height: 32),
                      const Text(
                        'Net Wealth Over Time',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 16),
                      _buildWealthChart(),
                      const SizedBox(height: 32),
                      const Text(
                        'Portfolio YoY % Change',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 8),
                      const Text(
                        'Year-over-year percentage change (Dec-to-Dec)',
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.grey,
                        ),
                      ),
                      const SizedBox(height: 16),
                      _buildPortfolioYoYChart(),
                      const SizedBox(height: 32),
                      const Text(
                        'Net Wealth YoY % Change',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 8),
                      const Text(
                        'Year-over-year percentage change (Dec-to-Dec)',
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.grey,
                        ),
                      ),
                      const SizedBox(height: 16),
                      _buildWealthYoYChart(),
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
          BottomNavigationBarItem(
            icon: Icon(Icons.table_chart),
            label: 'Analytics',
          ),
        ],
      ),
    );
  }

  Widget _buildPeriodSelector() {
    final periods = ['1M', '3M', '6M', '1Y', 'ALL'];

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(8),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: periods.map((period) {
            final isSelected = _selectedPeriod == period;
            return Expanded(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 4),
                child: ElevatedButton(
                  onPressed: () {
                    setState(() {
                      _selectedPeriod = period;
                    });
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor:
                        isSelected ? Colors.blue : Colors.grey[800],
                    foregroundColor:
                        isSelected ? Colors.white : Colors.grey[400],
                    padding: const EdgeInsets.symmetric(vertical: 12),
                  ),
                  child: Text(period),
                ),
              ),
            );
          }).toList(),
        ),
      ),
    );
  }

  Widget _buildPortfolioChart() {
    if (_portfolioSnapshots.isEmpty) {
      return const Card(
        child: Padding(
          padding: EdgeInsets.all(32),
          child: Center(
            child: Text('No portfolio data available for this period'),
          ),
        ),
      );
    }

    // Group by date and sum values
    final Map<DateTime, double> dateValues = {};
    final filterStartDate = _getStartDate(_selectedPeriod);

    for (final snapshot in _portfolioSnapshots) {
      final date = DateTime.parse(snapshot['snapshot_date'] as String);
      // Apply period filter for absolute value charts
      if (date.isBefore(filterStartDate)) continue;

      final value = ((snapshot['value_huf'] ?? 0) as num).toDouble();
      dateValues[date] = (dateValues[date] ?? 0) + value;
    }

    final sortedDates = dateValues.keys.toList()..sort();
    final spots = sortedDates.asMap().entries.map((entry) {
      return FlSpot(entry.key.toDouble(), dateValues[entry.value]!);
    }).toList();

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: SizedBox(
          height: 250,
          child: LineChart(
            LineChartData(
              minY: 0,
              gridData: const FlGridData(show: true),
              titlesData: FlTitlesData(
                leftTitles: AxisTitles(
                  sideTitles: SideTitles(
                    showTitles: true,
                    reservedSize: 60,
                    getTitlesWidget: (value, meta) {
                      return Text(
                        '${(value / 1000000).toStringAsFixed(0)}M',
                        style: const TextStyle(fontSize: 10),
                      );
                    },
                  ),
                ),
                bottomTitles: AxisTitles(
                  sideTitles: SideTitles(
                    showTitles: true,
                    reservedSize: 50,
                    interval: sortedDates.length > 20
                        ? (sortedDates.length / 10).ceilToDouble()
                        : 1,
                    getTitlesWidget: (value, meta) {
                      if (value.toInt() >= 0 &&
                          value.toInt() < sortedDates.length) {
                        final date = sortedDates[value.toInt()];
                        // Show year on first occurrence or January
                        bool showYear = value.toInt() == 0 ||
                            (value.toInt() > 0 &&
                                sortedDates[value.toInt()].year !=
                                    sortedDates[value.toInt() - 1].year);
                        return Transform.rotate(
                          angle: -1.5708, // -90 degrees in radians
                          child: Text(
                            showYear
                                ? '${date.year}\n${DateFormat('MMM').format(date)}'
                                : DateFormat('MMM').format(date),
                            style: const TextStyle(fontSize: 9),
                            textAlign: TextAlign.center,
                          ),
                        );
                      }
                      return const Text('');
                    },
                  ),
                ),
                rightTitles: const AxisTitles(
                  sideTitles: SideTitles(showTitles: false),
                ),
                topTitles: const AxisTitles(
                  sideTitles: SideTitles(showTitles: false),
                ),
              ),
              borderData: FlBorderData(show: true),
              lineBarsData: [
                LineChartBarData(
                  spots: spots,
                  isCurved: true,
                  color: Colors.blue,
                  barWidth: 3,
                  dotData: const FlDotData(show: false),
                  belowBarData: BarAreaData(
                    show: true,
                    color: Colors.blue.withOpacity(0.2),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildWealthChart() {
    if (_wealthSnapshots.isEmpty) {
      return const Card(
        child: Padding(
          padding: EdgeInsets.all(32),
          child: Center(
            child: Text('No wealth data available for this period'),
          ),
        ),
      );
    }

    // Group by date and sum values
    final Map<DateTime, double> dateValues = {};
    final filterStartDate = _getStartDate(_selectedPeriod);

    for (final snapshot in _wealthSnapshots) {
      final date = DateTime.parse(snapshot['snapshot_date'] as String);
      // Apply period filter for absolute value charts
      if (date.isBefore(filterStartDate)) continue;

      final value = ((snapshot['net_wealth_huf'] ?? 0) as num).toDouble();
      dateValues[date] = (dateValues[date] ?? 0) + value;
    }

    final sortedDates = dateValues.keys.toList()..sort();
    final spots = sortedDates.asMap().entries.map((entry) {
      return FlSpot(entry.key.toDouble(), dateValues[entry.value]!);
    }).toList();

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: SizedBox(
          height: 250,
          child: LineChart(
            LineChartData(
              minY: 0,
              gridData: const FlGridData(show: true),
              titlesData: FlTitlesData(
                leftTitles: AxisTitles(
                  sideTitles: SideTitles(
                    showTitles: true,
                    reservedSize: 60,
                    getTitlesWidget: (value, meta) {
                      return Text(
                        '${(value / 1000000).toStringAsFixed(0)}M',
                        style: const TextStyle(fontSize: 10),
                      );
                    },
                  ),
                ),
                bottomTitles: AxisTitles(
                  sideTitles: SideTitles(
                    showTitles: true,
                    reservedSize: 50,
                    interval: sortedDates.length > 20
                        ? (sortedDates.length / 10).ceilToDouble()
                        : 1,
                    getTitlesWidget: (value, meta) {
                      if (value.toInt() >= 0 &&
                          value.toInt() < sortedDates.length) {
                        final date = sortedDates[value.toInt()];
                        // Show year on first occurrence or year change
                        bool showYear = value.toInt() == 0 ||
                            (value.toInt() > 0 &&
                                sortedDates[value.toInt()].year !=
                                    sortedDates[value.toInt() - 1].year);
                        return Transform.rotate(
                          angle: -1.5708, // -90 degrees in radians
                          child: Text(
                            showYear
                                ? '${date.year}\n${DateFormat('MMM').format(date)}'
                                : DateFormat('MMM').format(date),
                            style: const TextStyle(fontSize: 9),
                            textAlign: TextAlign.center,
                          ),
                        );
                      }
                      return const Text('');
                    },
                  ),
                ),
                rightTitles: const AxisTitles(
                  sideTitles: SideTitles(showTitles: false),
                ),
                topTitles: const AxisTitles(
                  sideTitles: SideTitles(showTitles: false),
                ),
              ),
              borderData: FlBorderData(show: true),
              lineBarsData: [
                LineChartBarData(
                  spots: spots,
                  isCurved: true,
                  color: Colors.green,
                  barWidth: 3,
                  dotData: const FlDotData(show: false),
                  belowBarData: BarAreaData(
                    show: true,
                    color: Colors.green.withOpacity(0.2),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildPortfolioYoYChart() {
    if (_portfolioSnapshots.isEmpty) {
      return const Card(
        child: Padding(
          padding: EdgeInsets.all(32),
          child: Center(
            child: Text('No portfolio data available for this period'),
          ),
        ),
      );
    }

    // Prepare data for YoY calculation (December-to-December)
    List<Map<String, dynamic>> timeSeriesData = [];
    for (final snapshot in _portfolioSnapshots) {
      timeSeriesData.add({
        'date': snapshot['snapshot_date'],
        'value': ((snapshot['value_huf'] ?? 0) as num).toDouble(),
      });
    }

    // Sort by date chronologically (oldest first)
    timeSeriesData
        .sort((a, b) => (a['date'] as String).compareTo(b['date'] as String));

    // Calculate YoY using December baselines (Dec-to-Dec comparison)
    final yoyData = AnalyticsHelpers.calculateYoYBaseline(
      data: timeSeriesData,
      dateCol: 'date',
      valueCols: ['value'],
    );

    if (yoyData.isEmpty) {
      return const Card(
        child: Padding(
          padding: EdgeInsets.all(32),
          child: Center(
            child:
                Text('Insufficient data for YoY calculation (need 12+ months)'),
          ),
        ),
      );
    }

    // Filter out null YoY values and prepare chart data
    final validData =
        yoyData.where((row) => row['value_YoY%'] != null).toList();
    if (validData.isEmpty) {
      return const Card(
        child: Padding(
          padding: EdgeInsets.all(32),
          child: Center(
            child: Text('No YoY data available'),
          ),
        ),
      );
    }

    // Sort by date chronologically (already sorted from timeSeriesData)
    // Data already sorted by Year from calculateYoYBaseline

    final years = validData.map((row) => (row['Year'] as int)).toList();
    final spots = validData.asMap().entries.map((entry) {
      final yoyPercent = (entry.value['value_YoY%'] as num).toDouble();
      return FlSpot(entry.key.toDouble(), yoyPercent);
    }).toList();

    // Find min/max for better scaling
    final yoyValues = spots.map((s) => s.y).toList();
    final minY = yoyValues.reduce((a, b) => a < b ? a : b);
    final maxY = yoyValues.reduce((a, b) => a > b ? a : b);
    final yRange = maxY - minY;
    final yMin = minY - (yRange * 0.1); // Add 10% padding
    final yMax = maxY + (yRange * 0.1);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: SizedBox(
          height: 250,
          child: LineChart(
            LineChartData(
              minY: yMin,
              maxY: yMax,
              gridData: const FlGridData(show: true),
              titlesData: FlTitlesData(
                leftTitles: AxisTitles(
                  sideTitles: SideTitles(
                    showTitles: true,
                    reservedSize: 60,
                    getTitlesWidget: (value, meta) {
                      return Text(
                        '${value.toStringAsFixed(2)}%',
                        style: const TextStyle(fontSize: 10),
                      );
                    },
                  ),
                ),
                bottomTitles: AxisTitles(
                  sideTitles: SideTitles(
                    showTitles: true,
                    reservedSize: 50,
                    interval: years.length > 15 ? 2 : 1,
                    getTitlesWidget: (value, meta) {
                      if (value.toInt() >= 0 && value.toInt() < years.length) {
                        final year = years[value.toInt()];
                        return Transform.rotate(
                          angle: -1.5708,
                          child: Text(
                            year.toString(),
                            style: const TextStyle(
                                fontSize: 9, color: Colors.grey),
                            textAlign: TextAlign.center,
                          ),
                        );
                      }
                      return const Text('');
                    },
                  ),
                ),
                rightTitles: const AxisTitles(
                  sideTitles: SideTitles(showTitles: false),
                ),
                topTitles: const AxisTitles(
                  sideTitles: SideTitles(showTitles: false),
                ),
              ),
              borderData: FlBorderData(show: true),
              lineBarsData: [
                LineChartBarData(
                  spots: spots,
                  isCurved: true,
                  color: Colors.orange,
                  barWidth: 3,
                  dotData: const FlDotData(show: false),
                  belowBarData: BarAreaData(
                    show: true,
                    color: Colors.orange.withOpacity(0.2),
                  ),
                ),
              ],
              // Add horizontal line at 0%
              extraLinesData: ExtraLinesData(
                horizontalLines: [
                  HorizontalLine(
                    y: 0,
                    color: Colors.grey,
                    strokeWidth: 1,
                    dashArray: [5, 5],
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildWealthYoYChart() {
    if (_wealthSnapshots.isEmpty) {
      return const Card(
        child: Padding(
          padding: EdgeInsets.all(32),
          child: Center(
            child: Text('No wealth data available for this period'),
          ),
        ),
      );
    }

    // Prepare data for YoY calculation
    List<Map<String, dynamic>> timeSeriesData = [];
    final Map<DateTime, double> dateValues = {};
    for (final snapshot in _wealthSnapshots) {
      final date = DateTime.parse(snapshot['snapshot_date'] as String);
      final value = ((snapshot['net_wealth_huf'] ?? 0) as num).toDouble();
      dateValues[date] = (dateValues[date] ?? 0) + value;
    }

    for (final entry in dateValues.entries) {
      timeSeriesData.add({
        'date': entry.key.toIso8601String().substring(0, 10),
        'value': entry.value,
      });
    }

    // Sort by date chronologically (oldest first)
    timeSeriesData
        .sort((a, b) => (a['date'] as String).compareTo(b['date'] as String));

    // Calculate YoY using analytics helpers
    final yoyData = AnalyticsHelpers.calculateYoYBaseline(
      data: timeSeriesData,
      dateCol: 'date',
      valueCols: ['value'],
    );

    if (yoyData.isEmpty) {
      return const Card(
        child: Padding(
          padding: EdgeInsets.all(32),
          child: Center(
            child:
                Text('Insufficient data for YoY calculation (need 12+ months)'),
          ),
        ),
      );
    }

    // Filter out null YoY values and prepare chart data
    final validData =
        yoyData.where((row) => row['value_YoY%'] != null).toList();
    if (validData.isEmpty) {
      return const Card(
        child: Padding(
          padding: EdgeInsets.all(32),
          child: Center(
            child: Text('No YoY data available'),
          ),
        ),
      );
    }

    // Sort by date chronologically (already sorted from timeSeriesData)
    // Data already sorted by Year from calculateYoYBaseline

    final years = validData.map((row) => (row['Year'] as int)).toList();
    final spots = validData.asMap().entries.map((entry) {
      final yoyPercent = (entry.value['value_YoY%'] as num).toDouble();
      return FlSpot(entry.key.toDouble(), yoyPercent);
    }).toList();

    // Find min/max for better scaling
    final yoyValues = spots.map((s) => s.y).toList();
    final minY = yoyValues.reduce((a, b) => a < b ? a : b);
    final maxY = yoyValues.reduce((a, b) => a > b ? a : b);
    final yRange = maxY - minY;
    final yMin = minY - (yRange * 0.1); // Add 10% padding
    final yMax = maxY + (yRange * 0.1);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: SizedBox(
          height: 250,
          child: LineChart(
            LineChartData(
              minY: yMin,
              maxY: yMax,
              gridData: const FlGridData(show: true),
              titlesData: FlTitlesData(
                leftTitles: AxisTitles(
                  sideTitles: SideTitles(
                    showTitles: true,
                    reservedSize: 60,
                    getTitlesWidget: (value, meta) {
                      return Text(
                        '${value.toStringAsFixed(2)}%',
                        style: const TextStyle(fontSize: 10),
                      );
                    },
                  ),
                ),
                bottomTitles: AxisTitles(
                  sideTitles: SideTitles(
                    showTitles: true,
                    reservedSize: 50,
                    interval: years.length > 15 ? 2 : 1,
                    getTitlesWidget: (value, meta) {
                      if (value.toInt() >= 0 && value.toInt() < years.length) {
                        final year = years[value.toInt()];
                        return Transform.rotate(
                          angle: -1.5708,
                          child: Text(
                            year.toString(),
                            style: const TextStyle(
                                fontSize: 9, color: Colors.grey),
                            textAlign: TextAlign.center,
                          ),
                        );
                      }
                      return const Text('');
                    },
                  ),
                ),
                rightTitles: const AxisTitles(
                  sideTitles: SideTitles(showTitles: false),
                ),
                topTitles: const AxisTitles(
                  sideTitles: SideTitles(showTitles: false),
                ),
              ),
              borderData: FlBorderData(show: true),
              lineBarsData: [
                LineChartBarData(
                  spots: spots,
                  isCurved: true,
                  color: Colors.purple,
                  barWidth: 3,
                  dotData: const FlDotData(show: false),
                  belowBarData: BarAreaData(
                    show: true,
                    color: Colors.purple.withOpacity(0.2),
                  ),
                ),
              ],
              // Add horizontal line at 0%
              extraLinesData: ExtraLinesData(
                horizontalLines: [
                  HorizontalLine(
                    y: 0,
                    color: Colors.grey,
                    strokeWidth: 1,
                    dashArray: [5, 5],
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
