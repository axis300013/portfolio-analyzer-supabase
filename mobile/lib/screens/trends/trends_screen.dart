import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:intl/intl.dart';
import '../../services/supabase_service.dart';
import '../../services/daily_update_service.dart';
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
  bool _isUpdating = false;
  String? _updateStatus;

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

  Future<void> _triggerDailyUpdate() async {
    if (_isUpdating) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Update already in progress')),
      );
      return;
    }

    setState(() {
      _isUpdating = true;
      _updateStatus = 'Initializing update...';
    });

    try {
      // Show update confirmation dialog
      if (!mounted) return;

      final shouldContinue = await showDialog<bool>(
        context: context,
        builder: (ctx) => AlertDialog(
          title: const Text('Run Daily Update?'),
          content: const Text(
            'This will fetch latest FX rates, instrument prices, and pension values. '
            'Update typically takes 2-5 minutes.',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx, false),
              child: const Text('Cancel'),
            ),
            FilledButton(
              onPressed: () => Navigator.pop(ctx, true),
              child: const Text('Update'),
            ),
          ],
        ),
      );

      if (shouldContinue != true) {
        setState(() {
          _isUpdating = false;
          _updateStatus = null;
        });
        return;
      }

      // Trigger the update
      setState(() {
        _updateStatus = 'Sending update request to backend...';
      });

      final result = await DailyUpdateService.triggerDailyUpdate();

      if (mounted) {
        if (result['success'] == true) {
          setState(() {
            _updateStatus = 'Update started! Running ETL pipeline...';
          });

          // Show success notification
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Daily update triggered - please wait...'),
                duration: Duration(seconds: 2),
              ),
            );
          }

          // Poll status every 5 seconds until completion
          bool isComplete = false;
          int pollCount = 0;
          const maxPolls = 24; // 2 minutes max (24 * 5 seconds)

          while (!isComplete && pollCount < maxPolls && mounted) {
            await Future.delayed(const Duration(seconds: 5));
            pollCount++;

            final status = await DailyUpdateService.getUpdateStatus();

            if (mounted) {
              if (status['is_running'] == false) {
                isComplete = true;

                if (status['last_error'] != null) {
                  setState(() {
                    _updateStatus = 'Update failed: ${status['last_error']}';
                  });

                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text('ETL failed: ${status['last_error']}'),
                      backgroundColor: Colors.red,
                      duration: Duration(seconds: 5),
                    ),
                  );
                } else {
                  setState(() {
                    _updateStatus = 'Update completed successfully!';
                  });

                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content:
                          Text('✅ Daily update completed! Refreshing data...'),
                      backgroundColor: Colors.green,
                      duration: Duration(seconds: 3),
                    ),
                  );

                  // Refresh data immediately
                  setState(() {
                    _isLoading = true;
                  });
                  await _loadTrendsData();
                }
              } else {
                // Still running - update status message
                final step = status['current_step'] ?? 'Processing...';
                setState(() {
                  _updateStatus = 'Running: $step';
                });
              }
            }
          }

          if (!isComplete && mounted) {
            setState(() {
              _updateStatus = 'Update timed out - check backend logs';
            });
          }
        } else {
          setState(() {
            _updateStatus = 'Error: ${result['error']}';
          });

          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('Update failed: ${result['error']}'),
                backgroundColor: Colors.red,
              ),
            );
          }
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _updateStatus = 'Exception: ${e.toString()}';
        });

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Update error: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isUpdating = false;
        });
        // Clear status message after 5 seconds
        Future.delayed(const Duration(seconds: 5), () {
          if (mounted) {
            setState(() {
              _updateStatus = null;
            });
          }
        });
      }
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
          if (_updateStatus != null)
            Tooltip(
              message: _updateStatus,
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Center(
                  child: _isUpdating
                      ? const SizedBox(
                          width: 24,
                          height: 24,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Icon(Icons.check_circle, color: Colors.green),
                ),
              ),
            ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              setState(() {
                _isLoading = true;
                _errorMessage = null;
              });
              _loadTrendsData();
            },
            tooltip: 'Refresh trends data',
          ),
          IconButton(
            icon: _isUpdating
                ? const SizedBox(
                    width: 24,
                    height: 24,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Icon(Icons.cloud_upload),
            onPressed: _isUpdating ? null : _triggerDailyUpdate,
            tooltip: 'Run daily update',
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
                      _buildOverallStatistics(),
                      const SizedBox(height: 24),
                      _buildStatisticsCards(),
                      const SizedBox(height: 24),
                      const Text(
                        '1. Net Wealth Over Time',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 16),
                      _buildWealthChart(),
                      const SizedBox(height: 8),
                      _buildWealthDetailTable(),
                      const SizedBox(height: 32),
                      const Text(
                        '2. Portfolio Value Over Time',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 16),
                      _buildPortfolioChart(),
                      const SizedBox(height: 8),
                      _buildPortfolioDetailTable(),
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

    // Calculate Y-axis range with 5% margin
    final values = dateValues.values.toList();
    final minValue = values.reduce((a, b) => a < b ? a : b);
    final maxValue = values.reduce((a, b) => a > b ? a : b);
    final margin = (maxValue - minValue) * 0.05;
    final double yMin =
        ((minValue - margin).clamp(0.0, double.infinity)).toDouble();
    final double yMax = (maxValue + margin).toDouble();

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
                        return Transform.rotate(
                          angle: -1.5708, // -90 degrees in radians
                          child: Text(
                            DateFormat('MM.dd').format(date),
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

    // Calculate Y-axis range with 5% margin
    final values = dateValues.values.toList();
    final minValue = values.reduce((a, b) => a < b ? a : b);
    final maxValue = values.reduce((a, b) => a > b ? a : b);
    final margin = (maxValue - minValue) * 0.05;
    final double yMin =
        ((minValue - margin).clamp(0.0, double.infinity)).toDouble();
    final double yMax = (maxValue + margin).toDouble();

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
                        return Transform.rotate(
                          angle: -1.5708, // -90 degrees in radians
                          child: Text(
                            DateFormat('MM.dd').format(date),
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
                        // Get the date for this year from portfolio snapshots
                        final snapshot = _portfolioSnapshots.firstWhere(
                          (s) =>
                              DateTime.parse(s['snapshot_date'] as String)
                                  .year ==
                              year,
                          orElse: () => _portfolioSnapshots.first,
                        );
                        final date =
                            DateTime.parse(snapshot['snapshot_date'] as String);
                        return Transform.rotate(
                          angle: -1.5708,
                          child: Text(
                            DateFormat('MM.dd').format(date),
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
                        // Get the date for this year from wealth snapshots
                        final snapshot = _wealthSnapshots.firstWhere(
                          (s) =>
                              DateTime.parse(s['snapshot_date'] as String)
                                  .year ==
                              year,
                          orElse: () => _wealthSnapshots.first,
                        );
                        final date =
                            DateTime.parse(snapshot['snapshot_date'] as String);
                        return Transform.rotate(
                          angle: -1.5708,
                          child: Text(
                            DateFormat('MM.dd').format(date),
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

  Widget _buildOverallStatistics() {
    if (_portfolioSnapshots.isEmpty || _wealthSnapshots.isEmpty) {
      return const SizedBox.shrink();
    }

    // Filter by selected period
    final startDate = _getStartDate(_selectedPeriod);

    // Aggregate portfolio values by date (filtered)
    final Map<String, double> portfolioByDate = {};
    for (final snapshot in _portfolioSnapshots) {
      final dateStr = snapshot['snapshot_date'] as String;
      final date = DateTime.parse(dateStr);
      if (date.isBefore(startDate)) continue;

      final value = ((snapshot['value_huf'] ?? 0) as num).toDouble();
      portfolioByDate[dateStr] = (portfolioByDate[dateStr] ?? 0) + value;
    }

    // Aggregate wealth values by date (filtered)
    final Map<String, double> wealthByDate = {};
    for (final snapshot in _wealthSnapshots) {
      final dateStr = snapshot['snapshot_date'] as String;
      final date = DateTime.parse(dateStr);
      if (date.isBefore(startDate)) continue;

      final value = ((snapshot['net_wealth_huf'] ?? 0) as num).toDouble();
      wealthByDate[dateStr] = (wealthByDate[dateStr] ?? 0) + value;
    }

    if (portfolioByDate.isEmpty || wealthByDate.isEmpty) {
      return const SizedBox.shrink();
    }

    // Get first and last values for the selected period
    final portfolioDates = portfolioByDate.keys.toList()..sort();
    final wealthDates = wealthByDate.keys.toList()..sort();

    final firstPortfolioValue = portfolioByDate[portfolioDates.first] ?? 0.0;
    final lastPortfolioValue = portfolioByDate[portfolioDates.last] ?? 0.0;
    final firstWealthValue = wealthByDate[wealthDates.first] ?? 0.0;
    final lastWealthValue = wealthByDate[wealthDates.last] ?? 0.0;

    if (firstPortfolioValue == 0.0 ||
        lastPortfolioValue == 0.0 ||
        firstWealthValue == 0.0 ||
        lastWealthValue == 0.0) {
      return const SizedBox.shrink();
    }

    final totalPortfolioChange = lastPortfolioValue - firstPortfolioValue;
    final totalPortfolioChangePct =
        (totalPortfolioChange / firstPortfolioValue) * 100;
    final totalWealthChange = lastWealthValue - firstWealthValue;
    final totalWealthChangePct = (totalWealthChange / firstWealthValue) * 100;

    return Card(
      elevation: 4,
      color: Colors.blue[900]?.withOpacity(0.3),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Overall Statistics ($_selectedPeriod)',
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Net Wealth',
                        style: TextStyle(
                          fontSize: 13,
                          color: Colors.white70,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        NumberFormat.currency(
                                locale: 'en_US',
                                symbol: 'Ft ',
                                decimalDigits: 0)
                            .format(lastWealthValue),
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '${totalWealthChangePct >= 0 ? '+' : ''}${totalWealthChangePct.toStringAsFixed(1)}% total',
                        style: TextStyle(
                          fontSize: 12,
                          color: totalWealthChangePct >= 0
                              ? Colors.greenAccent
                              : Colors.redAccent,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ),
                ),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Portfolio Value',
                        style: TextStyle(
                          fontSize: 13,
                          color: Colors.white70,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        NumberFormat.currency(
                                locale: 'en_US',
                                symbol: 'Ft ',
                                decimalDigits: 0)
                            .format(lastPortfolioValue),
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '${totalPortfolioChangePct >= 0 ? '+' : ''}${totalPortfolioChangePct.toStringAsFixed(1)}% total',
                        style: TextStyle(
                          fontSize: 12,
                          color: totalPortfolioChangePct >= 0
                              ? Colors.greenAccent
                              : Colors.redAccent,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Data Points',
                        style: TextStyle(
                          fontSize: 13,
                          color: Colors.white70,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '${wealthDates.length} snapshots',
                        style: const TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                    ],
                  ),
                ),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Portfolio/Wealth',
                        style: TextStyle(
                          fontSize: 13,
                          color: Colors.white70,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '${(lastPortfolioValue / lastWealthValue * 100).toStringAsFixed(1)}%',
                        style: const TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatisticsCards() {
    // Filter data based on selected period
    final startDate = _getStartDate(_selectedPeriod);
    final filteredPortfolio = _portfolioSnapshots.where((item) {
      final date = DateTime.parse(item['snapshot_date'] as String);
      return date.isAfter(startDate);
    }).toList();
    final filteredWealth = _wealthSnapshots.where((item) {
      final date = DateTime.parse(item['snapshot_date'] as String);
      return date.isAfter(startDate);
    }).toList();

    if (filteredPortfolio.isEmpty || filteredWealth.isEmpty) {
      return const SizedBox.shrink();
    }

    final firstPortfolio = filteredPortfolio.first;
    final lastPortfolio = filteredPortfolio.last;
    final firstWealth = filteredWealth.first;
    final lastWealth = filteredWealth.last;

    // Safely extract values with null checks
    final firstPortfolioValue =
        (firstPortfolio['portfolio_value'] as num?)?.toDouble() ?? 0.0;
    final lastPortfolioValue =
        (lastPortfolio['portfolio_value'] as num?)?.toDouble() ?? 0.0;
    final firstWealthValue =
        (firstWealth['net_wealth'] as num?)?.toDouble() ?? 0.0;
    final lastWealthValue =
        (lastWealth['net_wealth'] as num?)?.toDouble() ?? 0.0;

    // Return empty if we don't have valid data
    if (firstPortfolioValue == 0.0 ||
        lastPortfolioValue == 0.0 ||
        firstWealthValue == 0.0 ||
        lastWealthValue == 0.0) {
      return const SizedBox.shrink();
    }

    final portfolioChange = lastPortfolioValue - firstPortfolioValue;
    final portfolioChangePct = (portfolioChange / firstPortfolioValue) * 100;

    final wealthChange = lastWealthValue - firstWealthValue;
    final wealthChangePct = (wealthChange / firstWealthValue) * 100;

    final portfolioOfWealth = (lastPortfolioValue / lastWealthValue) * 100;

    return Column(
      children: [
        // Net Wealth Metrics Card
        Card(
          elevation: 2,
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Net Wealth Analytics',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 12),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Expanded(
                      child: _buildMetricItem(
                        'Current Value',
                        NumberFormat.currency(
                                locale: 'en_US', symbol: '', decimalDigits: 0)
                            .format(lastWealthValue),
                        wealthChangePct >= 0 ? Colors.green : Colors.red,
                        '${wealthChangePct >= 0 ? '+' : ''}${wealthChangePct.toStringAsFixed(1)}%',
                      ),
                    ),
                    Expanded(
                      child: _buildMetricItem(
                        'Period Change',
                        NumberFormat.currency(
                                locale: 'en_US', symbol: '', decimalDigits: 0)
                            .format(wealthChange),
                        wealthChangePct >= 0 ? Colors.green : Colors.red,
                        null,
                      ),
                    ),
                    Expanded(
                      child: _buildMetricItem(
                        'Data Points',
                        '${filteredWealth.length}',
                        Colors.blue,
                        null,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 12),
        // Portfolio Metrics Card
        Card(
          elevation: 2,
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Portfolio Analytics',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 12),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Expanded(
                      child: _buildMetricItem(
                        'Current Value',
                        NumberFormat.currency(
                                locale: 'en_US', symbol: '', decimalDigits: 0)
                            .format(lastPortfolioValue),
                        portfolioChangePct >= 0 ? Colors.green : Colors.red,
                        '${portfolioChangePct >= 0 ? '+' : ''}${portfolioChangePct.toStringAsFixed(1)}%',
                      ),
                    ),
                    Expanded(
                      child: _buildMetricItem(
                        'Period Change',
                        NumberFormat.currency(
                                locale: 'en_US', symbol: '', decimalDigits: 0)
                            .format(portfolioChange),
                        portfolioChangePct >= 0 ? Colors.green : Colors.red,
                        null,
                      ),
                    ),
                    Expanded(
                      child: _buildMetricItem(
                        '% of Net Wealth',
                        '${portfolioOfWealth.toStringAsFixed(1)}%',
                        Colors.blue,
                        null,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildMetricItem(
      String label, String value, Color valueColor, String? subtitle) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(
            fontSize: 11,
            color: Colors.grey,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.bold,
            color: valueColor,
          ),
        ),
        if (subtitle != null) ...[
          const SizedBox(height: 2),
          Text(
            subtitle,
            style: TextStyle(
              fontSize: 11,
              color: valueColor,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ],
    );
  }

  Widget _buildWealthDetailTable() {
    // Filter data based on selected period
    final startDate = _getStartDate(_selectedPeriod);
    final filteredWealth = _wealthSnapshots.where((item) {
      final date = DateTime.parse(item['snapshot_date'] as String);
      return date.isAfter(startDate);
    }).toList();

    if (filteredWealth.isEmpty) {
      return const SizedBox.shrink();
    }

    return ExpansionTile(
      title: const Text(
        'Show Detailed Data',
        style: TextStyle(fontSize: 14, fontWeight: FontWeight.w500),
      ),
      children: [
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: DataTable(
            columnSpacing: 20,
            horizontalMargin: 16,
            columns: const [
              DataColumn(
                  label: Text('Date',
                      style: TextStyle(fontWeight: FontWeight.bold))),
              DataColumn(
                  label: Text('Net Wealth',
                      style: TextStyle(fontWeight: FontWeight.bold)),
                  numeric: true),
              DataColumn(
                  label: Text('Change',
                      style: TextStyle(fontWeight: FontWeight.bold)),
                  numeric: true),
              DataColumn(
                  label: Text('% Change',
                      style: TextStyle(fontWeight: FontWeight.bold)),
                  numeric: true),
            ],
            rows: List.generate(filteredWealth.length, (index) {
              final item = filteredWealth[index];
              final currentValue =
                  (item['net_wealth'] as num?)?.toDouble() ?? 0.0;
              final prevValue = index > 0
                  ? ((filteredWealth[index - 1]['net_wealth'] as num?)
                          ?.toDouble() ??
                      0.0)
                  : currentValue;
              final change = currentValue - prevValue;
              final changePct =
                  prevValue != 0 ? (change / prevValue) * 100 : 0.0;

              return DataRow(
                cells: [
                  DataCell(Text(
                    DateFormat('yyyy-MM-dd').format(
                        DateTime.parse(item['snapshot_date'] as String)),
                    style: const TextStyle(fontSize: 12),
                  )),
                  DataCell(Text(
                    NumberFormat.currency(
                            locale: 'en_US', symbol: '', decimalDigits: 0)
                        .format(currentValue),
                    style: const TextStyle(fontSize: 12),
                  )),
                  DataCell(Text(
                    NumberFormat.currency(
                            locale: 'en_US', symbol: '', decimalDigits: 0)
                        .format(change),
                    style: TextStyle(
                      fontSize: 12,
                      color: change >= 0 ? Colors.green : Colors.red,
                    ),
                  )),
                  DataCell(Text(
                    '${changePct >= 0 ? '+' : ''}${changePct.toStringAsFixed(2)}%',
                    style: TextStyle(
                      fontSize: 12,
                      color: changePct >= 0 ? Colors.green : Colors.red,
                    ),
                  )),
                ],
              );
            }),
          ),
        ),
      ],
    );
  }

  Widget _buildPortfolioDetailTable() {
    // Filter data based on selected period
    final startDate = _getStartDate(_selectedPeriod);
    final filteredPortfolio = _portfolioSnapshots.where((item) {
      final date = DateTime.parse(item['snapshot_date'] as String);
      return date.isAfter(startDate);
    }).toList();

    if (filteredPortfolio.isEmpty) {
      return const SizedBox.shrink();
    }

    return ExpansionTile(
      title: const Text(
        'Show Detailed Data',
        style: TextStyle(fontSize: 14, fontWeight: FontWeight.w500),
      ),
      children: [
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: DataTable(
            columnSpacing: 20,
            horizontalMargin: 16,
            columns: const [
              DataColumn(
                  label: Text('Date',
                      style: TextStyle(fontWeight: FontWeight.bold))),
              DataColumn(
                  label: Text('Portfolio Value',
                      style: TextStyle(fontWeight: FontWeight.bold)),
                  numeric: true),
              DataColumn(
                  label: Text('Change',
                      style: TextStyle(fontWeight: FontWeight.bold)),
                  numeric: true),
              DataColumn(
                  label: Text('% Change',
                      style: TextStyle(fontWeight: FontWeight.bold)),
                  numeric: true),
            ],
            rows: List.generate(filteredPortfolio.length, (index) {
              final item = filteredPortfolio[index];
              final currentValue =
                  (item['portfolio_value'] as num?)?.toDouble() ?? 0.0;
              final prevValue = index > 0
                  ? ((filteredPortfolio[index - 1]['portfolio_value'] as num?)
                          ?.toDouble() ??
                      0.0)
                  : currentValue;
              final change = currentValue - prevValue;
              final changePct =
                  prevValue != 0 ? (change / prevValue) * 100 : 0.0;

              return DataRow(
                cells: [
                  DataCell(Text(
                    DateFormat('yyyy-MM-dd').format(
                        DateTime.parse(item['snapshot_date'] as String)),
                    style: const TextStyle(fontSize: 12),
                  )),
                  DataCell(Text(
                    NumberFormat.currency(
                            locale: 'en_US', symbol: '', decimalDigits: 0)
                        .format(currentValue),
                    style: const TextStyle(fontSize: 12),
                  )),
                  DataCell(Text(
                    NumberFormat.currency(
                            locale: 'en_US', symbol: '', decimalDigits: 0)
                        .format(change),
                    style: TextStyle(
                      fontSize: 12,
                      color: change >= 0 ? Colors.green : Colors.red,
                    ),
                  )),
                  DataCell(Text(
                    '${changePct >= 0 ? '+' : ''}${changePct.toStringAsFixed(2)}%',
                    style: TextStyle(
                      fontSize: 12,
                      color: changePct >= 0 ? Colors.green : Colors.red,
                    ),
                  )),
                ],
              );
            }),
          ),
        ),
      ],
    );
  }
}
