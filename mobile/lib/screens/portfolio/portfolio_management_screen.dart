import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import '../../services/supabase_service.dart';

class PortfolioManagementScreen extends StatefulWidget {
  const PortfolioManagementScreen({super.key});

  @override
  State<PortfolioManagementScreen> createState() =>
      _PortfolioManagementScreenState();
}

class _PortfolioManagementScreenState extends State<PortfolioManagementScreen> {
  int _selectedTab = 0;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Portfolio Management'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.go('/portfolio'),
        ),
      ),
      body: Column(
        children: [
          // Tab Bar
          Container(
            decoration: BoxDecoration(
              color: Colors.grey[200],
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.1),
                  blurRadius: 4,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: Row(
              children: [
                Expanded(
                  child: _buildTabButton(
                    'Manual Prices',
                    Icons.edit,
                    0,
                  ),
                ),
                Expanded(
                  child: _buildTabButton(
                    'Transactions',
                    Icons.receipt_long,
                    1,
                  ),
                ),
                Expanded(
                  child: _buildTabButton(
                    'Instruments',
                    Icons.business_center,
                    2,
                  ),
                ),
              ],
            ),
          ),
          // Content
          Expanded(
            child: IndexedStack(
              index: _selectedTab,
              children: const [
                ManualPricesTab(),
                TransactionsTab(),
                InstrumentsTab(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTabButton(String label, IconData icon, int index) {
    final isSelected = _selectedTab == index;
    return InkWell(
      onTap: () => setState(() => _selectedTab = index),
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 16),
        decoration: BoxDecoration(
          color: isSelected ? Colors.blue : Colors.transparent,
          border: Border(
            bottom: BorderSide(
              color: isSelected ? Colors.blue : Colors.transparent,
              width: 3,
            ),
          ),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              icon,
              color: isSelected ? Colors.white : Colors.grey[700],
              size: 24,
            ),
            const SizedBox(height: 4),
            Text(
              label,
              style: TextStyle(
                color: isSelected ? Colors.white : Colors.grey[700],
                fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                fontSize: 12,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// Tab 1: Manual Prices
class ManualPricesTab extends StatefulWidget {
  const ManualPricesTab({super.key});

  @override
  State<ManualPricesTab> createState() => _ManualPricesTabState();
}

class _ManualPricesTabState extends State<ManualPricesTab> {
  List<Map<String, dynamic>> _instruments = [];
  bool _isLoading = true;
  String? _selectedInstrumentId;
  String _selectedCurrency = 'USD';
  final _priceController = TextEditingController();
  final _dateController = TextEditingController();

  final currencyFormatter = NumberFormat.currency(
    locale: 'hu_HU',
    symbol: '',
    decimalDigits: 4,
  );

  @override
  void initState() {
    super.initState();
    _loadInstruments();
    _dateController.text = DateFormat('yyyy-MM-dd').format(DateTime.now());
  }

  @override
  void dispose() {
    _priceController.dispose();
    _dateController.dispose();
    super.dispose();
  }

  Future<void> _loadInstruments() async {
    try {
      final data = await SupabaseService.getPortfolioInstruments();
      setState(() {
        _instruments = data;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading instruments: $e')),
        );
      }
    }
  }

  Future<void> _savePrice() async {
    if (_selectedInstrumentId == null || _priceController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
            content: Text('Please select instrument and enter price')),
      );
      return;
    }

    try {
      final price = double.parse(_priceController.text);
      final date = _dateController.text;

      await SupabaseService.saveManualPrice(
        instrumentId: int.parse(_selectedInstrumentId!),
        price: price,
        priceDate: date,
        currency: _selectedCurrency,
      );

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('✅ Price saved successfully!'),
            backgroundColor: Colors.green,
            duration: Duration(seconds: 3),
          ),
        );

        // Show info dialog about needing to run daily update
        showDialog(
          context: context,
          builder: (context) => AlertDialog(
            title: const Row(
              children: [
                Icon(Icons.info_outline, color: Colors.blue),
                SizedBox(width: 8),
                Text('Price Update Saved'),
              ],
            ),
            content: const Text(
              'The price has been saved to the database.\n\n'
              'To see the updated portfolio values, please run the Daily Update from the desktop app. '
              'This will recalculate all portfolio values using the new price.',
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: const Text('Got it'),
              ),
            ],
          ),
        );

        _priceController.clear();
        setState(() => _selectedInstrumentId = null);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('❌ Error saving price: $e')),
        );
      }
    }
  }

  Future<void> _selectDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: DateTime.now(),
      firstDate: DateTime(2020),
      lastDate: DateTime.now(),
    );
    if (picked != null) {
      setState(() {
        _dateController.text = DateFormat('yyyy-MM-dd').format(picked);
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Card(
        elevation: 4,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                'Update Instrument Price',
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const SizedBox(height: 24),

              // Instrument Dropdown
              DropdownButtonFormField<String>(
                value: _selectedInstrumentId,
                decoration: const InputDecoration(
                  labelText: 'Select Instrument',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.business_center),
                ),
                items: _instruments.map((instrument) {
                  return DropdownMenuItem(
                    value: instrument['id'].toString(),
                    child: Text(
                        '${instrument['name']} (${instrument['instrument_type']})'),
                  );
                }).toList(),
                onChanged: (value) {
                  setState(() => _selectedInstrumentId = value);
                },
              ),
              const SizedBox(height: 16),

              // Price Input
              TextFormField(
                controller: _priceController,
                decoration: const InputDecoration(
                  labelText: 'Price',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.attach_money),
                  hintText: 'Enter price (e.g., 1234.56)',
                ),
                keyboardType:
                    const TextInputType.numberWithOptions(decimal: true),
              ),
              const SizedBox(height: 16),

              // Currency Dropdown
              DropdownButtonFormField<String>(
                value: _selectedCurrency,
                decoration: const InputDecoration(
                  labelText: 'Currency',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.money),
                ),
                items: [
                  'USD',
                  'EUR',
                  'HUF',
                  'GBP',
                  'CHF',
                  'JPY',
                  'CNY',
                  'AUD',
                  'CAD'
                ]
                    .map((currency) => DropdownMenuItem(
                          value: currency,
                          child: Text(currency),
                        ))
                    .toList(),
                onChanged: (value) {
                  setState(() => _selectedCurrency = value!);
                },
              ),
              const SizedBox(height: 16),

              // Date Input
              TextFormField(
                controller: _dateController,
                decoration: const InputDecoration(
                  labelText: 'Date',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.calendar_today),
                ),
                readOnly: true,
                onTap: _selectDate,
              ),
              const SizedBox(height: 24),

              // Save Button
              ElevatedButton.icon(
                onPressed: _savePrice,
                icon: const Icon(Icons.save),
                label: const Text('Save Price'),
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  backgroundColor: Colors.blue,
                  foregroundColor: Colors.white,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// Tab 2: Transactions
class TransactionsTab extends StatefulWidget {
  const TransactionsTab({super.key});

  @override
  State<TransactionsTab> createState() => _TransactionsTabState();
}

class _TransactionsTabState extends State<TransactionsTab> {
  List<Map<String, dynamic>> _instruments = [];
  List<Map<String, dynamic>> _transactions = [];
  bool _isLoading = true;
  String? _selectedInstrumentId;
  String _transactionType = 'buy';
  final _quantityController = TextEditingController();
  final _priceController = TextEditingController();
  final _dateController = TextEditingController();

  final currencyFormatter = NumberFormat.currency(
    locale: 'hu_HU',
    symbol: 'Ft',
    decimalDigits: 2,
  );

  @override
  void initState() {
    super.initState();
    _loadData();
    _dateController.text = DateFormat('yyyy-MM-dd').format(DateTime.now());
  }

  @override
  void dispose() {
    _quantityController.dispose();
    _priceController.dispose();
    _dateController.dispose();
    super.dispose();
  }

  Future<void> _loadData() async {
    try {
      final instruments = await SupabaseService.getPortfolioInstruments();
      final transactions = await SupabaseService.getTransactions();
      setState(() {
        _instruments = instruments;
        _transactions = transactions;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading data: $e')),
        );
      }
    }
  }

  Future<void> _saveTransaction() async {
    if (_selectedInstrumentId == null ||
        _quantityController.text.isEmpty ||
        _priceController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please fill all fields')),
      );
      return;
    }

    try {
      await SupabaseService.saveTransaction(
        instrumentId: int.parse(_selectedInstrumentId!),
        transactionType: _transactionType,
        quantity: double.parse(_quantityController.text),
        price: double.parse(_priceController.text),
        transactionDate: _dateController.text,
      );

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('✅ Transaction saved successfully!'),
            backgroundColor: Colors.green,
          ),
        );
        _quantityController.clear();
        _priceController.clear();
        setState(() => _selectedInstrumentId = null);
        _loadData(); // Reload to show new transaction
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error saving transaction: $e')),
        );
      }
    }
  }

  Future<void> _selectDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: DateTime.now(),
      firstDate: DateTime(2020),
      lastDate: DateTime.now(),
    );
    if (picked != null) {
      setState(() {
        _dateController.text = DateFormat('yyyy-MM-dd').format(picked);
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    return SingleChildScrollView(
      child: Column(
        children: [
          // Transaction Form
          Card(
            margin: const EdgeInsets.all(16),
            elevation: 4,
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Text(
                    'Record Transaction',
                    style: Theme.of(context).textTheme.headlineSmall,
                  ),
                  const SizedBox(height: 16),

                  // Transaction Type
                  Row(
                    children: [
                      Expanded(
                        child: RadioListTile<String>(
                          title: const Text('Buy'),
                          value: 'buy',
                          groupValue: _transactionType,
                          onChanged: (value) {
                            setState(() => _transactionType = value!);
                          },
                        ),
                      ),
                      Expanded(
                        child: RadioListTile<String>(
                          title: const Text('Sell'),
                          value: 'sell',
                          groupValue: _transactionType,
                          onChanged: (value) {
                            setState(() => _transactionType = value!);
                          },
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),

                  // Instrument
                  DropdownButtonFormField<String>(
                    value: _selectedInstrumentId,
                    decoration: const InputDecoration(
                      labelText: 'Instrument',
                      border: OutlineInputBorder(),
                    ),
                    items: _instruments.map((instrument) {
                      return DropdownMenuItem(
                        value: instrument['id'].toString(),
                        child: Text(instrument['name']),
                      );
                    }).toList(),
                    onChanged: (value) {
                      setState(() => _selectedInstrumentId = value);
                    },
                  ),
                  const SizedBox(height: 16),

                  // Quantity
                  TextFormField(
                    controller: _quantityController,
                    decoration: const InputDecoration(
                      labelText: 'Quantity',
                      border: OutlineInputBorder(),
                    ),
                    keyboardType:
                        const TextInputType.numberWithOptions(decimal: true),
                  ),
                  const SizedBox(height: 16),

                  // Price
                  TextFormField(
                    controller: _priceController,
                    decoration: const InputDecoration(
                      labelText: 'Price per Unit',
                      border: OutlineInputBorder(),
                    ),
                    keyboardType:
                        const TextInputType.numberWithOptions(decimal: true),
                  ),
                  const SizedBox(height: 16),

                  // Date
                  TextFormField(
                    controller: _dateController,
                    decoration: const InputDecoration(
                      labelText: 'Transaction Date',
                      border: OutlineInputBorder(),
                    ),
                    readOnly: true,
                    onTap: _selectDate,
                  ),
                  const SizedBox(height: 24),

                  // Save Button
                  ElevatedButton.icon(
                    onPressed: _saveTransaction,
                    icon: const Icon(Icons.save),
                    label: const Text('Save Transaction'),
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      backgroundColor: Colors.blue,
                      foregroundColor: Colors.white,
                    ),
                  ),
                ],
              ),
            ),
          ),

          // Recent Transactions List
          if (_transactions.isNotEmpty)
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Recent Transactions',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  const SizedBox(height: 8),
                  ListView.builder(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    itemCount:
                        _transactions.length > 10 ? 10 : _transactions.length,
                    itemBuilder: (context, index) {
                      final transaction = _transactions[index];
                      return Card(
                        child: ListTile(
                          leading: Icon(
                            transaction['transaction_type'] == 'buy'
                                ? Icons.add_circle
                                : Icons.remove_circle,
                            color: transaction['transaction_type'] == 'buy'
                                ? Colors.green
                                : Colors.red,
                          ),
                          title:
                              Text(transaction['instrument_name'] ?? 'Unknown'),
                          subtitle: Text(
                            '${transaction['quantity']} @ ${currencyFormatter.format(transaction['price'])}\n'
                            '${transaction['transaction_date']}',
                          ),
                          isThreeLine: true,
                        ),
                      );
                    },
                  ),
                ],
              ),
            ),
        ],
      ),
    );
  }
}

// Tab 3: Instruments
class InstrumentsTab extends StatefulWidget {
  const InstrumentsTab({super.key});

  @override
  State<InstrumentsTab> createState() => _InstrumentsTabState();
}

class _InstrumentsTabState extends State<InstrumentsTab> {
  List<Map<String, dynamic>> _instruments = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadInstruments();
  }

  Future<void> _loadInstruments() async {
    try {
      final data = await SupabaseService.getPortfolioInstruments();
      setState(() {
        _instruments = data;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading instruments: $e')),
        );
      }
    }
  }

  void _showAddInstrumentDialog() {
    final nameController = TextEditingController();
    final isinController = TextEditingController();
    final tickerController = TextEditingController();
    String? selectedType = 'stock';
    String? selectedCurrency = 'HUF';

    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setState) => AlertDialog(
          title: const Text('Add Instrument'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: nameController,
                  decoration: const InputDecoration(labelText: 'Name'),
                ),
                TextField(
                  controller: isinController,
                  decoration:
                      const InputDecoration(labelText: 'ISIN (optional)'),
                ),
                TextField(
                  controller: tickerController,
                  decoration:
                      const InputDecoration(labelText: 'Ticker (optional)'),
                ),
                const SizedBox(height: 16),
                DropdownButtonFormField<String>(
                  value: selectedType,
                  decoration: const InputDecoration(labelText: 'Type'),
                  items: ['stock', 'bond', 'fund', 'etf', 'crypto', 'other']
                      .map((type) => DropdownMenuItem(
                          value: type, child: Text(type.toUpperCase())))
                      .toList(),
                  onChanged: (value) {
                    setState(() => selectedType = value);
                  },
                ),
                const SizedBox(height: 16),
                DropdownButtonFormField<String>(
                  value: selectedCurrency,
                  decoration: const InputDecoration(labelText: 'Currency'),
                  items: ['HUF', 'USD', 'EUR']
                      .map((currency) => DropdownMenuItem(
                          value: currency, child: Text(currency)))
                      .toList(),
                  onChanged: (value) {
                    setState(() => selectedCurrency = value);
                  },
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () async {
                if (nameController.text.isEmpty) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Name is required')),
                  );
                  return;
                }

                try {
                  await SupabaseService.addInstrument(
                    name: nameController.text,
                    isin: isinController.text.isEmpty
                        ? null
                        : isinController.text,
                    ticker: tickerController.text.isEmpty
                        ? null
                        : tickerController.text,
                    instrumentType: selectedType!,
                    currency: selectedCurrency!,
                  );

                  if (mounted) {
                    Navigator.pop(context);
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text('✅ Instrument added successfully!'),
                        backgroundColor: Colors.green,
                      ),
                    );
                    _loadInstruments();
                  }
                } catch (e) {
                  if (mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text('Error: $e')),
                    );
                  }
                }
              },
              child: const Text('Add'),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.all(16),
          child: ElevatedButton.icon(
            onPressed: _showAddInstrumentDialog,
            icon: const Icon(Icons.add),
            label: const Text('Add New Instrument'),
            style: ElevatedButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: 16),
              backgroundColor: Colors.green,
              foregroundColor: Colors.white,
            ),
          ),
        ),
        Expanded(
          child: _isLoading
              ? const Center(child: CircularProgressIndicator())
              : ListView.builder(
                  itemCount: _instruments.length,
                  itemBuilder: (context, index) {
                    final instrument = _instruments[index];
                    return Card(
                      margin: const EdgeInsets.symmetric(
                          horizontal: 16, vertical: 4),
                      child: ListTile(
                        leading: CircleAvatar(
                          child: Text(
                            instrument['instrument_type'][0].toUpperCase(),
                          ),
                        ),
                        title: Text(instrument['name']),
                        subtitle: Text(
                          '${instrument['instrument_type']} • ${instrument['currency']}'
                          '${instrument['isin'] != null ? '\nISIN: ${instrument['isin']}' : ''}',
                        ),
                        trailing: IconButton(
                          icon: const Icon(Icons.edit),
                          onPressed: () {
                            // TODO: Implement edit functionality
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(
                                  content: Text('Edit feature coming soon')),
                            );
                          },
                        ),
                      ),
                    );
                  },
                ),
        ),
      ],
    );
  }
}
