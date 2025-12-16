/// Helper functions for YoY analytics calculations
/// Ported from Python analytics_helpers.py
library;

class AnalyticsHelpers {
  /// Calculate rolling 12-month (Dec-to-Dec) YoY % change
  ///
  /// For each date, finds the prior year's December value and calculates
  /// percentage change: ((current - prior) / abs(prior)) * 100
  ///
  /// Returns: Map with YoY% columns added to each row
  static List<Map<String, dynamic>> calculateRollingYoY({
    required List<Map<String, dynamic>> data,
    required String dateCol,
    required List<String> valueCols,
  }) {
    if (data.isEmpty) return [];

    List<Map<String, dynamic>> result = [];

    for (var row in data) {
      Map<String, dynamic> newRow = Map.from(row);
      DateTime currentDate = DateTime.parse(row[dateCol]);

      for (var col in valueCols) {
        dynamic currentValue = row[col];
        if (currentValue == null || currentValue == 0) {
          newRow['${col}_YoY%'] = null;
          continue;
        }

        // Find December of prior year
        int priorDecYear = currentDate.year - 1;
        DateTime priorDec = DateTime(priorDecYear, 12, 31);

        // Find closest date to prior December (last available month if Dec doesn't exist)
        Map<String, dynamic>? priorYearRow;
        for (var r in data) {
          DateTime rowDate = DateTime.parse(r[dateCol]);
          if (rowDate.year == priorDecYear && rowDate.isBefore(priorDec) ||
              rowDate.isAtSameMomentAs(priorDec)) {
            if (priorYearRow == null ||
                DateTime.parse(r[dateCol])
                    .isAfter(DateTime.parse(priorYearRow[dateCol]))) {
              priorYearRow = r;
            }
          }
        }

        if (priorYearRow != null && priorYearRow[col] != null) {
          double priorValue = (priorYearRow[col] as num).toDouble();
          double currentVal = (currentValue as num).toDouble();

          if (priorValue != 0) {
            double yoyPct =
                ((currentVal - priorValue) / priorValue.abs()) * 100;
            newRow['${col}_YoY%'] = yoyPct;
          } else {
            newRow['${col}_YoY%'] = null;
          }
        } else {
          newRow['${col}_YoY%'] = null;
        }
      }

      result.add(newRow);
    }

    return result;
  }

  /// Calculate YoY % change where each year is compared to prior year's December
  ///
  /// Returns: List of maps with Year and YoY% columns
  static List<Map<String, dynamic>> calculateYoYBaseline({
    required List<Map<String, dynamic>> data,
    required String dateCol,
    required List<String> valueCols,
  }) {
    if (data.isEmpty) return [];

    // Group data by year and get December baseline (or last month)
    Map<int, Map<String, dynamic>> baselines = {};

    for (var row in data) {
      DateTime rowDate = DateTime.parse(row[dateCol]);
      int year = rowDate.year;

      if (!baselines.containsKey(year)) {
        baselines[year] = row;
      } else {
        DateTime currentBaseline = DateTime.parse(baselines[year]![dateCol]);

        // Prefer December, otherwise take the latest month
        if (rowDate.month == 12) {
          if (currentBaseline.month != 12 || rowDate.isAfter(currentBaseline)) {
            baselines[year] = row;
          }
        } else if (currentBaseline.month != 12 &&
            rowDate.isAfter(currentBaseline)) {
          baselines[year] = row;
        }
      }
    }

    // Calculate YoY for each year (including years without prior year data)
    List<Map<String, dynamic>> yoyRecords = [];
    List<int> sortedYears = baselines.keys.toList()..sort();

    for (int year in sortedYears) {
      Map<String, dynamic> record = {'Year': year};

      if (baselines.containsKey(year - 1)) {
        Map<String, dynamic> priorBaseline = baselines[year - 1]!;
        Map<String, dynamic> currentBaseline = baselines[year]!;

        for (var col in valueCols) {
          var priorVal = priorBaseline[col];
          var currentVal = currentBaseline[col];

          if (priorVal != null &&
              currentVal != null &&
              (priorVal as num) != 0) {
            double priorValue = (priorVal as num).toDouble();
            double currentValue = (currentVal as num).toDouble();
            double yoyPct =
                ((currentValue - priorValue) / priorValue.abs()) * 100;
            record['${col}_YoY%'] = yoyPct;
          } else {
            record['${col}_YoY%'] = null;
          }
        }
      } else {
        // No prior year data - set YoY% to null but still include the record
        for (var col in valueCols) {
          record['${col}_YoY%'] = null;
        }
      }

      yoyRecords.add(record);
    }

    return yoyRecords;
  }

  /// Format a number as percentage with 1 decimal place
  static String formatPercent(dynamic value) {
    if (value == null) return 'N/A';
    if (value is num) {
      return '${value.toStringAsFixed(1)}%';
    }
    return 'N/A';
  }

  /// Format a number with thousands separator
  static String formatNumber(dynamic value) {
    if (value == null || value == 0) return '-';
    if (value is num) {
      return value.toInt().toString().replaceAllMapped(
            RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))'),
            (Match m) => '${m[1]},',
          );
    }
    return '-';
  }

  /// Pivot data: transform rows to columns
  /// Used for creating transposed tables (dates as columns, metrics as rows)
  static Map<String, Map<String, dynamic>> pivotData({
    required List<Map<String, dynamic>> data,
    required String indexCol,
    required String columnsCol,
    required String valuesCol,
  }) {
    Map<String, Map<String, dynamic>> pivoted = {};

    for (var row in data) {
      String indexValue = row[indexCol]?.toString() ?? '';
      String columnValue = row[columnsCol]?.toString() ?? '';
      dynamic value = row[valuesCol];

      if (!pivoted.containsKey(indexValue)) {
        pivoted[indexValue] = {};
      }
      pivoted[indexValue]![columnValue] = value;
    }

    return pivoted;
  }

  /// Apply granularity filter to time series data
  static List<Map<String, dynamic>> applyGranularity({
    required List<Map<String, dynamic>> data,
    required String dateCol,
    required String granularity,
  }) {
    if (data.isEmpty) return [];
    if (granularity == 'Daily') return data;

    if (granularity == 'Monthly') {
      // Get last value of each month
      Map<String, Map<String, dynamic>> monthlyData = {};

      for (var row in data) {
        DateTime date = DateTime.parse(row[dateCol]);
        String monthKey =
            '${date.year}-${date.month.toString().padLeft(2, '0')}';

        if (!monthlyData.containsKey(monthKey)) {
          monthlyData[monthKey] = row;
        } else {
          DateTime existingDate =
              DateTime.parse(monthlyData[monthKey]![dateCol]);
          if (date.isAfter(existingDate)) {
            monthlyData[monthKey] = row;
          }
        }
      }

      List<Map<String, dynamic>> result = monthlyData.values.toList();
      result.sort((a, b) =>
          DateTime.parse(a[dateCol]).compareTo(DateTime.parse(b[dateCol])));
      return result;
    }

    if (granularity == 'Yearly') {
      // Get last month of each year (prefer December)
      Map<int, Map<String, dynamic>> yearlyData = {};

      for (var row in data) {
        DateTime date = DateTime.parse(row[dateCol]);
        int year = date.year;

        if (!yearlyData.containsKey(year)) {
          yearlyData[year] = row;
        } else {
          DateTime existingDate = DateTime.parse(yearlyData[year]![dateCol]);

          // Prefer December, otherwise take the latest month
          if (date.month == 12) {
            if (existingDate.month != 12 || date.isAfter(existingDate)) {
              yearlyData[year] = row;
            }
          } else if (existingDate.month != 12 && date.isAfter(existingDate)) {
            yearlyData[year] = row;
          }
        }
      }

      List<Map<String, dynamic>> result = yearlyData.values.toList();
      result.sort((a, b) =>
          DateTime.parse(a[dateCol]).compareTo(DateTime.parse(b[dateCol])));
      return result;
    }

    return data;
  }
}
