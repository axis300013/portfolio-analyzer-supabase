import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../services/supabase_service.dart';

class WealthManagementScreen extends StatefulWidget {
  const WealthManagementScreen({super.key});

  @override
  State<WealthManagementScreen> createState() => _WealthManagementScreenState();
}

class _WealthManagementScreenState extends State<WealthManagementScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Wealth Management'),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'Categories', icon: Icon(Icons.category)),
            Tab(text: 'Update Values', icon: Icon(Icons.attach_money)),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: const [
          WealthCategoriesTab(),
          WealthValuesTab(),
        ],
      ),
    );
  }
}

// ============================================================================
// TAB 1: Wealth Categories (CRUD)
// ============================================================================

class WealthCategoriesTab extends StatefulWidget {
  const WealthCategoriesTab({super.key});

  @override
  State<WealthCategoriesTab> createState() => _WealthCategoriesTabState();
}

class _WealthCategoriesTabState extends State<WealthCategoriesTab> {
  List<Map<String, dynamic>> _categories = [];
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _loadCategories();
  }

  Future<void> _loadCategories() async {
    setState(() => _isLoading = true);
    try {
      final categories = await SupabaseService.getWealthItems();
      setState(() {
        _categories = categories;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading categories: $e')),
        );
      }
    }
  }

  Future<void> _showAddCategoryDialog() async {
    final nameController = TextEditingController();
    final descriptionController = TextEditingController();
    String categoryType = 'Asset';
    bool isLiability = false;

    await showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          title: const Text('Add Wealth Category'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: nameController,
                  decoration: const InputDecoration(
                    labelText: 'Category Name *',
                    hintText: 'e.g., Real Estate, Stocks',
                  ),
                ),
                const SizedBox(height: 16),
                DropdownButtonFormField<String>(
                  value: categoryType,
                  decoration: const InputDecoration(labelText: 'Type *'),
                  items: [
                    'Asset',
                    'Liability',
                    'Investment',
                    'Cash',
                    'Property',
                    'Other'
                  ]
                      .map((type) =>
                          DropdownMenuItem(value: type, child: Text(type)))
                      .toList(),
                  onChanged: (value) {
                    setDialogState(() => categoryType = value!);
                  },
                ),
                const SizedBox(height: 16),
                Row(
                  children: [
                    Checkbox(
                      value: isLiability,
                      onChanged: (value) {
                        setDialogState(() => isLiability = value!);
                      },
                    ),
                    const Text('Is Liability'),
                  ],
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: descriptionController,
                  decoration: const InputDecoration(
                    labelText: 'Description (optional)',
                    hintText: 'Brief description',
                  ),
                  maxLines: 2,
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
                    const SnackBar(content: Text('Category name is required')),
                  );
                  return;
                }

                try {
                  await SupabaseService.addWealthCategory(
                    name: nameController.text.trim(),
                    categoryType: categoryType,
                    isLiability: isLiability,
                    description: descriptionController.text.trim().isEmpty
                        ? null
                        : descriptionController.text.trim(),
                  );

                  if (context.mounted) {
                    Navigator.pop(context);
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                          content: Text('Category added successfully!')),
                    );
                    _loadCategories();
                  }
                } catch (e) {
                  if (context.mounted) {
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

  Future<void> _showEditCategoryDialog(Map<String, dynamic> category) async {
    final nameController = TextEditingController(text: category['name']);
    final descriptionController =
        TextEditingController(text: category['description'] ?? '');
    String categoryType = category['category_type'] ?? 'Asset';
    bool isLiability = category['is_liability'] ?? false;

    await showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          title: const Text('Edit Category'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: nameController,
                  decoration:
                      const InputDecoration(labelText: 'Category Name *'),
                ),
                const SizedBox(height: 16),
                DropdownButtonFormField<String>(
                  value: categoryType.toLowerCase(),
                  decoration: const InputDecoration(labelText: 'Type *'),
                  items: [
                    'asset',
                    'liability',
                    'investment',
                    'cash',
                    'property',
                    'other'
                  ]
                      .map((type) => DropdownMenuItem(
                          value: type,
                          child:
                              Text(type[0].toUpperCase() + type.substring(1))))
                      .toList(),
                  onChanged: (value) {
                    setDialogState(() => categoryType = value!);
                  },
                ),
                const SizedBox(height: 16),
                Row(
                  children: [
                    Checkbox(
                      value: isLiability,
                      onChanged: (value) {
                        setDialogState(() => isLiability = value!);
                      },
                    ),
                    const Text('Is Liability'),
                  ],
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: descriptionController,
                  decoration: const InputDecoration(labelText: 'Description'),
                  maxLines: 2,
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
                try {
                  await SupabaseService.updateWealthCategory(
                    id: category['id'] as int,
                    name: nameController.text.trim(),
                    categoryType: categoryType,
                    isLiability: isLiability,
                    description: descriptionController.text.trim().isEmpty
                        ? null
                        : descriptionController.text.trim(),
                  );

                  if (context.mounted) {
                    Navigator.pop(context);
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Category updated!')),
                    );
                    _loadCategories();
                  }
                } catch (e) {
                  if (context.mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text('Error: $e')),
                    );
                  }
                }
              },
              child: const Text('Update'),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _deleteCategory(int id, String name) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Category'),
        content: Text('Are you sure you want to delete "$name"?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('Delete'),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      try {
        await SupabaseService.deleteWealthCategory(id);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Category deleted')),
          );
          _loadCategories();
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Error: $e')),
          );
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.all(16.0),
          child: Row(
            children: [
              Expanded(
                child: Text(
                  '${_categories.length} Categories',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
              ),
              ElevatedButton.icon(
                onPressed: _showAddCategoryDialog,
                icon: const Icon(Icons.add),
                label: const Text('Add Category'),
              ),
            ],
          ),
        ),
        Expanded(
          child: _isLoading
              ? const Center(child: CircularProgressIndicator())
              : _categories.isEmpty
                  ? const Center(
                      child:
                          Text('No categories found.\nAdd one to get started!'),
                    )
                  : ListView.builder(
                      itemCount: _categories.length,
                      itemBuilder: (context, index) {
                        final category = _categories[index];
                        final isLiability = category['is_liability'] ?? false;

                        return Card(
                          margin: const EdgeInsets.symmetric(
                              horizontal: 16, vertical: 8),
                          child: ListTile(
                            leading: CircleAvatar(
                              backgroundColor: isLiability
                                  ? Colors.red.shade100
                                  : Colors.green.shade100,
                              child: Icon(
                                isLiability
                                    ? Icons.remove_circle
                                    : Icons.add_circle,
                                color: isLiability ? Colors.red : Colors.green,
                              ),
                            ),
                            title: Text(
                              category['name'] ?? 'Unnamed',
                              style:
                                  const TextStyle(fontWeight: FontWeight.bold),
                            ),
                            subtitle: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                    'Type: ${category['category_type'] ?? 'N/A'}'),
                                if (category['description'] != null)
                                  Text(
                                    category['description'],
                                    style: TextStyle(
                                      fontSize: 12,
                                      color: Colors.grey.shade600,
                                    ),
                                  ),
                              ],
                            ),
                            trailing: PopupMenuButton(
                              itemBuilder: (context) => [
                                const PopupMenuItem(
                                  value: 'edit',
                                  child: Row(
                                    children: [
                                      Icon(Icons.edit, size: 20),
                                      SizedBox(width: 8),
                                      Text('Edit'),
                                    ],
                                  ),
                                ),
                                const PopupMenuItem(
                                  value: 'delete',
                                  child: Row(
                                    children: [
                                      Icon(Icons.delete,
                                          size: 20, color: Colors.red),
                                      SizedBox(width: 8),
                                      Text('Delete',
                                          style: TextStyle(color: Colors.red)),
                                    ],
                                  ),
                                ),
                              ],
                              onSelected: (value) {
                                if (value == 'edit') {
                                  _showEditCategoryDialog(category);
                                } else if (value == 'delete') {
                                  _deleteCategory(
                                      category['id'], category['name']);
                                }
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

// ============================================================================
// TAB 2: Update Wealth Values
// ============================================================================

class WealthValuesTab extends StatefulWidget {
  const WealthValuesTab({super.key});

  @override
  State<WealthValuesTab> createState() => _WealthValuesTabState();
}

class _WealthValuesTabState extends State<WealthValuesTab> {
  List<Map<String, dynamic>> _categories = [];
  int? _selectedCategoryId;
  Map<String, dynamic>? _selectedCategory;
  final _valueController = TextEditingController();
  final _notesController = TextEditingController();
  DateTime _selectedDate = DateTime.now();
  bool _isLoading = false;
  List<Map<String, dynamic>> _recentValues = [];

  final currencyFormatter = NumberFormat.currency(
    locale: 'hu_HU',
    symbol: 'Ft',
    decimalDigits: 0,
  );

  @override
  void initState() {
    super.initState();
    _loadCategories();
    _loadRecentValues();
  }

  @override
  void dispose() {
    _valueController.dispose();
    _notesController.dispose();
    super.dispose();
  }

  Future<void> _loadCategories() async {
    try {
      final categories = await SupabaseService.getWealthItems();
      setState(() => _categories = categories);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading categories: $e')),
        );
      }
    }
  }

  Future<void> _loadRecentValues() async {
    setState(() => _isLoading = true);
    try {
      final values = await SupabaseService.getLatestWealthValues();
      setState(() {
        _recentValues = values;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error loading values: $e')),
        );
      }
    }
  }

  Future<void> _selectDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _selectedDate,
      firstDate: DateTime(2020),
      lastDate: DateTime.now(),
    );
    if (picked != null) {
      setState(() => _selectedDate = picked);
    }
  }

  Future<void> _saveWealthValue() async {
    if (_selectedCategoryId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select a category')),
      );
      return;
    }

    if (_valueController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter a value')),
      );
      return;
    }

    final value = double.tryParse(_valueController.text);
    if (value == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Invalid value format')),
      );
      return;
    }

    try {
      await SupabaseService.saveWealthValue(
        categoryId: _selectedCategoryId!,
        presentValue: value,
        valueDate: DateFormat('yyyy-MM-dd').format(_selectedDate),
        note: _notesController.text.trim().isEmpty
            ? null
            : _notesController.text.trim(),
      );

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Wealth value saved successfully!')),
        );

        // Clear form
        setState(() {
          _valueController.clear();
          _notesController.clear();
          _selectedCategoryId = null;
          _selectedDate = DateTime.now();
        });

        _loadRecentValues();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Form Card
            Card(
              elevation: 4,
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Text(
                      'Update Wealth Value',
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                    const SizedBox(height: 16),

                    // Category Dropdown
                    DropdownButtonFormField<int>(
                      value: _selectedCategoryId,
                      decoration: const InputDecoration(
                        labelText: 'Wealth Category *',
                        border: OutlineInputBorder(),
                      ),
                      items: _categories.map((cat) {
                        final isLiability = cat['is_liability'] ?? false;
                        return DropdownMenuItem<int>(
                          value: cat['id'] as int,
                          child: Row(
                            children: [
                              Icon(
                                isLiability
                                    ? Icons.remove_circle
                                    : Icons.add_circle,
                                size: 16,
                                color: isLiability ? Colors.red : Colors.green,
                              ),
                              const SizedBox(width: 8),
                              Text(cat['name'] ?? 'Unnamed'),
                            ],
                          ),
                        );
                      }).toList(),
                      onChanged: (value) {
                        setState(() {
                          _selectedCategoryId = value;
                          _selectedCategory = _categories.firstWhere(
                            (cat) => cat['id'] == value,
                            orElse: () => {},
                          );
                        });
                      },
                    ),
                    const SizedBox(height: 16),

                    // Value Input
                    TextField(
                      controller: _valueController,
                      decoration: InputDecoration(
                        labelText: _selectedCategory != null
                            ? 'Current Value (${_selectedCategory!['currency'] ?? 'HUF'}) *'
                            : 'Current Value *',
                        hintText: _selectedCategory != null
                            ? 'Enter amount in ${_selectedCategory!['currency'] ?? 'HUF'}'
                            : 'Select a category first',
                        border: const OutlineInputBorder(),
                      ),
                      keyboardType:
                          const TextInputType.numberWithOptions(decimal: true),
                    ),
                    const SizedBox(height: 16),

                    // Date Picker
                    InkWell(
                      onTap: _selectDate,
                      child: InputDecorator(
                        decoration: const InputDecoration(
                          labelText: 'Value Date',
                          border: OutlineInputBorder(),
                          suffixIcon: Icon(Icons.calendar_today),
                        ),
                        child: Text(
                          DateFormat('yyyy-MM-dd').format(_selectedDate),
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),

                    // Notes Input
                    TextField(
                      controller: _notesController,
                      decoration: const InputDecoration(
                        labelText: 'Notes (optional)',
                        hintText: 'Additional information',
                        border: OutlineInputBorder(),
                      ),
                      maxLines: 2,
                    ),
                    const SizedBox(height: 24),

                    // Save Button
                    ElevatedButton.icon(
                      onPressed: _saveWealthValue,
                      icon: const Icon(Icons.save),
                      label: const Text('Save Wealth Value'),
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.all(16),
                      ),
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 24),

            // Recent Values Section
            Text(
              'Current Wealth Values',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 8),

            _isLoading
                ? const Center(
                    child: Padding(
                      padding: EdgeInsets.all(32.0),
                      child: CircularProgressIndicator(),
                    ),
                  )
                : _recentValues.isEmpty
                    ? const Card(
                        child: Padding(
                          padding: EdgeInsets.all(32.0),
                          child: Center(
                            child: Text('No wealth values recorded yet'),
                          ),
                        ),
                      )
                    : ListView.builder(
                        shrinkWrap: true,
                        physics: const NeverScrollableScrollPhysics(),
                        itemCount: _recentValues.length,
                        itemBuilder: (context, index) {
                          final value = _recentValues[index];
                          final isLiability = value['is_liability'] ?? false;
                          final amount = value['present_value'] ?? 0.0;

                          return Card(
                            margin: const EdgeInsets.only(bottom: 8),
                            child: ListTile(
                              leading: CircleAvatar(
                                backgroundColor: isLiability
                                    ? Colors.red.shade100
                                    : Colors.green.shade100,
                                child: Icon(
                                  isLiability
                                      ? Icons.trending_down
                                      : Icons.trending_up,
                                  color:
                                      isLiability ? Colors.red : Colors.green,
                                ),
                              ),
                              title: Text(
                                value['category_name'] ?? 'Unknown',
                                style: const TextStyle(
                                    fontWeight: FontWeight.bold),
                              ),
                              subtitle: Text(
                                'Type: ${value['category_type'] ?? 'N/A'}',
                              ),
                              trailing: Column(
                                mainAxisAlignment: MainAxisAlignment.center,
                                crossAxisAlignment: CrossAxisAlignment.end,
                                children: [
                                  Text(
                                    currencyFormatter.format(amount),
                                    style: TextStyle(
                                      fontWeight: FontWeight.bold,
                                      fontSize: 16,
                                      color: isLiability
                                          ? Colors.red
                                          : Colors.green,
                                    ),
                                  ),
                                  if (value['value_date'] != null)
                                    Text(
                                      value['value_date']
                                          .toString()
                                          .substring(0, 10),
                                      style: TextStyle(
                                        fontSize: 12,
                                        color: Colors.grey.shade600,
                                      ),
                                    ),
                                ],
                              ),
                            ),
                          );
                        },
                      ),
          ],
        ),
      ),
    );
  }
}
