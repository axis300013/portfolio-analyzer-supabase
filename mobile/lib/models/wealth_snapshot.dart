class WealthSnapshot {
  final int id;
  final int itemId;
  final DateTime snapshotDate;
  final double valueInOriginalCurrency;
  final double fxRate;
  final double valueHuf;
  final String? itemName;
  final String? category;
  final String? currency;

  WealthSnapshot({
    required this.id,
    required this.itemId,
    required this.snapshotDate,
    required this.valueInOriginalCurrency,
    required this.fxRate,
    required this.valueHuf,
    this.itemName,
    this.category,
    this.currency,
  });

  factory WealthSnapshot.fromJson(Map<String, dynamic> json) {
    final wealthCategory = json['wealth_categories'];
    final presentValue = ((json['present_value'] ?? 0) as num).toDouble();
    final categoryType = (wealthCategory?['category_type'] as String? ?? 'other').toUpperCase();
    final isLiability = wealthCategory?['is_liability'] == true;
    
    // Map database category_type to UI categories
    String uiCategory;
    if (isLiability || categoryType == 'LOAN') {
      uiCategory = 'LIABILITIES';
    } else {
      uiCategory = categoryType; // 'CASH', 'PROPERTY', 'PENSION', 'OTHER'
    }
    
    return WealthSnapshot(
      id: json['id'] as int,
      itemId: json['wealth_category_id'] as int,
      snapshotDate: DateTime.parse(json['value_date'] as String),
      valueInOriginalCurrency: presentValue,
      fxRate: 1.0, // Always HUF, no FX conversion needed
      valueHuf: presentValue,
      itemName: wealthCategory?['name'] as String?,
      category: uiCategory,
      currency: wealthCategory?['currency'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'item_id': itemId,
      'snapshot_date': snapshotDate.toIso8601String(),
      'value_in_original_currency': valueInOriginalCurrency,
      'fx_rate': fxRate,
      'value_huf': valueHuf,
    };
  }
}
