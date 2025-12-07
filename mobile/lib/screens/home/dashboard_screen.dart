import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import '../../services/supabase_service.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  Map<String, dynamic>? _summary;
  bool _isLoading = true;
  String? _errorMessage;
  int _selectedIndex = 0;

  final currencyFormatter = NumberFormat.currency(
    locale: 'hu_HU',
    symbol: 'Ft',
    decimalDigits: 0,
  );

  @override
  void initState() {
    super.initState();
    _loadDashboardData();
  }

  Future<void> _loadDashboardData() async {
    try {
      final summary = await SupabaseService.getDashboardSummary();
      setState(() {
        _summary = summary;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _triggerDataUpdate() async {
    // Show loading dialog
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => const AlertDialog(
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            CircularProgressIndicator(),
            SizedBox(height: 16),
            Text('Updating data from backend...'),
            SizedBox(height: 8),
            Text(
              'This may take 1-2 minutes',
              style: TextStyle(fontSize: 12, color: Colors.grey),
            ),
          ],
        ),
      ),
    );

    try {
      final result = await SupabaseService.triggerDataUpdate();
      
      if (mounted) {
        Navigator.pop(context); // Close loading dialog
        
        if (result['success'] == true) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(result['message'] ?? 'Data updated successfully!'),
              backgroundColor: Colors.green,
              duration: const Duration(seconds: 3),
            ),
          );
          
          // Refresh dashboard data
          _loadDashboardData();
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(result['message'] ?? 'Update failed'),
              backgroundColor: Colors.orange,
              duration: const Duration(seconds: 5),
              action: SnackBarAction(
                label: 'Details',
                textColor: Colors.white,
                onPressed: () {
                  showDialog(
                    context: context,
                    builder: (context) => AlertDialog(
                      title: const Text('Update Info'),
                      content: SingleChildScrollView(
                        child: Text(result['error']?.toString() ?? 'No details available'),
                      ),
                      actions: [
                        TextButton(
                          onPressed: () => Navigator.pop(context),
                          child: const Text('OK'),
                        ),
                      ],
                    ),
                  );
                },
              ),
            ),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        Navigator.pop(context); // Close loading dialog
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error: $e'),
            backgroundColor: Colors.red,
            duration: const Duration(seconds: 5),
          ),
        );
      }
    }
  }

  void _onNavigationTap(int index) {
    setState(() {
      _selectedIndex = index;
    });

    switch (index) {
      case 0:
        // Already on dashboard
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Dashboard'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              setState(() {
                _isLoading = true;
                _errorMessage = null;
              });
              _loadDashboardData();
            },
          ),
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () async {
              await SupabaseService.signOut();
              if (mounted) {
                context.go('/login');
              }
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
                          'Error loading data',
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
                          onPressed: _loadDashboardData,
                          child: const Text('Retry'),
                        ),
                      ],
                    ),
                  ),
                )
              : RefreshIndicator(
                  onRefresh: _loadDashboardData,
                  child: ListView(
                    padding: const EdgeInsets.all(16),
                    children: [
                      // Data Update Button
                      Card(
                        elevation: 2,
                        child: Padding(
                          padding: const EdgeInsets.all(16.0),
                          child: Column(
                            children: [
                              Row(
                                children: [
                                  const Icon(Icons.info_outline, color: Colors.blue),
                                  const SizedBox(width: 12),
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Text(
                                          'Data Updates',
                                          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                            fontWeight: FontWeight.bold,
                                          ),
                                        ),
                                        const SizedBox(height: 4),
                                        const Text(
                                          'Use the desktop app to update prices and portfolio data. Changes sync automatically.',
                                          style: TextStyle(
                                            fontSize: 12,
                                            color: Colors.grey,
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
                      ),
                      const SizedBox(height: 16),
                      
                      _buildSummaryCard(
                        'Portfolio Value',
                        _summary!['portfolio_value'],
                        Icons.trending_up,
                        Colors.blue,
                      ),
                      const SizedBox(height: 16),
                      _buildSummaryCard(
                        'Total Assets',
                        _summary!['total_assets'],
                        Icons.account_balance,
                        Colors.green,
                      ),
                      const SizedBox(height: 16),
                      _buildSummaryCard(
                        'Total Liabilities',
                        _summary!['total_liabilities'],
                        Icons.credit_card,
                        Colors.orange,
                      ),
                      const SizedBox(height: 16),
                      _buildSummaryCard(
                        'Net Wealth',
                        _summary!['net_wealth'],
                        Icons.account_balance_wallet,
                        Colors.purple,
                      ),
                      const SizedBox(height: 24),
                      Row(
                        children: [
                          Expanded(
                            child: _buildCountCard(
                              'Instruments',
                              _summary!['instrument_count'],
                              Icons.pie_chart,
                            ),
                          ),
                          const SizedBox(width: 16),
                          Expanded(
                            child: _buildCountCard(
                              'Wealth Items',
                              _summary!['wealth_item_count'],
                              Icons.list_alt,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 24),
                      _buildQuickActionsCard(),
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

  Widget _buildSummaryCard(
    String title,
    double value,
    IconData icon,
    Color color,
  ) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: color.withOpacity(0.2),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(icon, color: color, size: 32),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: const TextStyle(
                      fontSize: 14,
                      color: Colors.grey,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    currencyFormatter.format(value),
                    style: const TextStyle(
                      fontSize: 22,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCountCard(String title, int count, IconData icon) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Icon(icon, size: 32, color: Colors.blue),
            const SizedBox(height: 8),
            Text(
              count.toString(),
              style: const TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              title,
              style: const TextStyle(
                fontSize: 12,
                color: Colors.grey,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildQuickActionsCard() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Quick Actions',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            ListTile(
              leading: const Icon(Icons.trending_up, color: Colors.blue),
              title: const Text('View Portfolio'),
              subtitle: const Text('See all your investments'),
              trailing: const Icon(Icons.arrow_forward_ios, size: 16),
              onTap: () => context.go('/portfolio'),
            ),
            const Divider(),
            ListTile(
              leading: const Icon(Icons.account_balance_wallet, color: Colors.green),
              title: const Text('Wealth Tracker'),
              subtitle: const Text('Track assets and liabilities'),
              trailing: const Icon(Icons.arrow_forward_ios, size: 16),
              onTap: () => context.go('/wealth'),
            ),
            const Divider(),
            ListTile(
              leading: const Icon(Icons.show_chart, color: Colors.purple),
              title: const Text('Trends & Analytics'),
              subtitle: const Text('View historical performance'),
              trailing: const Icon(Icons.arrow_forward_ios, size: 16),
              onTap: () => context.go('/trends'),
            ),
            const Divider(),
            ListTile(
              leading: const Icon(Icons.table_chart, color: Colors.orange),
              title: const Text('Analytical Data'),
              subtitle: const Text('Detailed time series data'),
              trailing: const Icon(Icons.arrow_forward_ios, size: 16),
              onTap: () => context.go('/analytics'),
            ),
          ],
        ),
      ),
    );
  }
}

