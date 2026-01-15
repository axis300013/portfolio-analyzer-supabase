class PortfolioSnapshot {
  final int id;
  final int instrumentId;
  final DateTime snapshotDate;
  final double quantity;
  final double priceInOriginalCurrency;
  final double valueInOriginalCurrency;
  final double fxRate;
  final double valueHuf;
  final String? instrumentName;
  final String? instrumentType;
  final String? currency;

  PortfolioSnapshot({
    required this.id,
    required this.instrumentId,
    required this.snapshotDate,
    required this.quantity,
    required this.priceInOriginalCurrency,
    required this.valueInOriginalCurrency,
    required this.fxRate,
    required this.valueHuf,
    this.instrumentName,
    this.instrumentType,
    this.currency,
  });

  factory PortfolioSnapshot.fromJson(Map<String, dynamic> json) {
    final price = ((json['price'] ?? 0) as num).toDouble();
    final quantity = ((json['quantity'] ?? 0) as num).toDouble();
    final fxRate = ((json['fx_rate'] ?? 1) as num).toDouble();
    
    return PortfolioSnapshot(
      id: json['id'] as int,
      instrumentId: json['instrument_id'] as int,
      snapshotDate: DateTime.parse(json['snapshot_date'] as String),
      quantity: quantity,
      priceInOriginalCurrency: price,
      valueInOriginalCurrency: price * quantity,
      fxRate: fxRate,
      valueHuf: ((json['value_huf'] ?? 0) as num).toDouble(),
      instrumentName: json['instruments']?['name'] as String?,
      instrumentType: json['instruments']?['instrument_type'] as String?,
      currency: json['instruments']?['currency'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'instrument_id': instrumentId,
      'snapshot_date': snapshotDate.toIso8601String(),
      'quantity': quantity,
      'price_in_original_currency': priceInOriginalCurrency,
      'value_in_original_currency': valueInOriginalCurrency,
      'fx_rate': fxRate,
      'value_huf': valueHuf,
    };
  }
}
