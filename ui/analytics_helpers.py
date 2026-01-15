"""
Helper functions for YoY analytics calculations
Used by both desktop and mobile apps
"""
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple

def calculate_rolling_yoy_analytics(df: pd.DataFrame, date_col: str, value_cols: List[str]) -> pd.DataFrame:
    """
    Calculate rolling 12-month (Dec-to-Dec) YoY % change
    
    Args:
        df: DataFrame with time series data
        date_col: Name of the date column
        value_cols: List of column names to calculate YoY for
    
    Returns:
        DataFrame with YoY% columns added
    """
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.sort_values(date_col)
    
    result_df = df.copy()
    
    for col in value_cols:
        yoy_col_name = f"{col}_YoY%"
        result_df[yoy_col_name] = None
        
        for idx in result_df.index:
            current_date = result_df.loc[idx, date_col]
            current_value = result_df.loc[idx, col]
            
            # Find December of prior year
            prior_dec_year = current_date.year - 1
            prior_dec = pd.Timestamp(year=prior_dec_year, month=12, day=31)
            
            # Find closest date to prior December (last available month if Dec doesn't exist)
            prior_year_data = result_df[
                (result_df[date_col].dt.year == prior_dec_year) &
                (result_df[date_col] <= prior_dec)
            ]
            
            if not prior_year_data.empty:
                prior_value = prior_year_data.iloc[-1][col]  # Last record of that year
                
                if pd.notna(current_value) and pd.notna(prior_value) and prior_value != 0:
                    yoy_pct = ((current_value - prior_value) / abs(prior_value)) * 100
                    result_df.loc[idx, yoy_col_name] = yoy_pct
    
    return result_df


def calculate_yoy_vs_baseline(df: pd.DataFrame, date_col: str, value_cols: List[str]) -> pd.DataFrame:
    """
    Calculate YoY % change where each year is compared to prior year's December
    
    Args:
        df: DataFrame with time series data
        date_col: Name of the date column
        value_cols: List of column names to calculate YoY for
    
    Returns:
        DataFrame pivoted by years with YoY% values
    """
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df['Year'] = df[date_col].dt.year
    
    # Get December baseline for each year (or last available month)
    baselines = {}
    for year in df['Year'].unique():
        year_data = df[df['Year'] == year]
        if not year_data.empty:
            # Try to get December, otherwise get last month
            dec_data = year_data[year_data[date_col].dt.month == 12]
            if not dec_data.empty:
                baselines[year] = dec_data.iloc[-1]
            else:
                baselines[year] = year_data.iloc[-1]
    
    # Calculate YoY for each year (include ALL years, even if no prior year exists)
    yoy_records = []
    for year in sorted(baselines.keys()):
        record = {'Year': year}
        
        if year - 1 in baselines:
            prior_baseline = baselines[year - 1]
            current_baseline = baselines[year]
            
            for col in value_cols:
                prior_val = prior_baseline[col]
                current_val = current_baseline[col]
                
                if pd.notna(prior_val) and pd.notna(current_val) and prior_val != 0:
                    yoy_pct = ((current_val - prior_val) / abs(prior_val)) * 100
                    record[f"{col}_YoY%"] = yoy_pct
                else:
                    record[f"{col}_YoY%"] = None
        else:
            # No prior year data - set YoY% to None but still include the record
            for col in value_cols:
                record[f"{col}_YoY%"] = None
        
        yoy_records.append(record)
    
    return pd.DataFrame(yoy_records)


def apply_granularity(df: pd.DataFrame, date_col: str, granularity: str, value_cols: List[str]) -> pd.DataFrame:
    """
    Apply granularity filter to time series data
    
    Args:
        df: DataFrame with time series data
        date_col: Name of the date column
        granularity: "Daily", "Monthly", or "Yearly"
        value_cols: Columns to aggregate (take last value)
    
    Returns:
        DataFrame with applied granularity
    """
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    
    if granularity == "Daily":
        return df
    
    elif granularity == "Monthly":
        df.set_index(date_col, inplace=True)
        agg_dict = {col: 'last' for col in value_cols}
        df = df.groupby(pd.Grouper(freq='ME')).agg(agg_dict).reset_index()
        return df
    
    elif granularity == "Yearly":
        df['Year'] = df[date_col].dt.year
        # For each year, get the last available month (preferably December)
        yearly_data = []
        for year in df['Year'].unique():
            year_data = df[df['Year'] == year]
            # Try December first
            dec_data = year_data[year_data[date_col].dt.month == 12]
            if not dec_data.empty:
                yearly_data.append(dec_data.iloc[-1])
            else:
                # Use last available month of that year
                yearly_data.append(year_data.iloc[-1])
        
        result_df = pd.DataFrame(yearly_data)
        result_df = result_df.drop('Year', axis=1, errors='ignore')
        return result_df
    
    return df


def format_analytics_table(df: pd.DataFrame, transpose: bool = True, 
                           negative_rows: List[str] = None) -> pd.DataFrame:
    """
    Format analytics table for display
    
    Args:
        df: DataFrame to format
        transpose: If True, dates become columns
        negative_rows: List of row names that should display as negative
    
    Returns:
        Formatted DataFrame ready for display
    """
    df_display = df.copy()
    
    if transpose and 'Date' in df_display.columns:
        df_display['Date'] = pd.to_datetime(df_display['Date']).dt.strftime('%Y-%m-%d')
        df_display = df_display.set_index('Date').T.reset_index()
        df_display.columns.name = None
        df_display.rename(columns={'index': 'Metric'}, inplace=True)
    
    # Format numbers
    for col in df_display.columns:
        if col not in ['Metric', 'Instrument', 'Category', 'Year']:
            for idx in df_display.index:
                val = df_display.loc[idx, col]
                
                # Check if this is a percentage column
                if pd.notna(val):
                    # Handle YoY% columns
                    if 'Metric' in df_display.columns and 'YoY%' in str(df_display.loc[idx, 'Metric']):
                        df_display.loc[idx, col] = f"{float(val):.1f}%"
                    # Handle negative rows (liabilities)
                    elif negative_rows and 'Metric' in df_display.columns:
                        if df_display.loc[idx, 'Metric'] in negative_rows:
                            if str(val).replace('.','').replace('-','').isdigit():
                                df_display.loc[idx, col] = f"-{abs(float(val)):,.0f}"
                    # Regular numbers
                    elif str(val).replace('.','').replace('-','').isdigit():
                        df_display.loc[idx, col] = f"{float(val):,.0f}"
    
    return df_display
