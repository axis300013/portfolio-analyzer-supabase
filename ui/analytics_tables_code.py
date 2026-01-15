"""
This file contains the code snippets to add 6 YoY analytics tables to the Streamlit app.
Insert these after each main table section.
"""

# ============================================================================
# ANALYTICS TABLES 1 & 2: After "Portfolio Summary Over Time" download button
# Insert after line: key="download_summary"
# ============================================================================

ANALYTICS_AFTER_PORTFOLIO_SUMMARY = """
                # Analytics Table 1: Summary Analytics (Rolling 12M YoY%)
                st.markdown("#### 📈 Summary Analytics - Rolling 12-Month % Change")
                st.caption("Year-over-Year percentage change (Dec-to-Dec comparison)")
                
                # Calculate rolling YoY
                value_cols_summary = ['Portfolio Total (HUF)', 'cash_huf', 'property_huf', 'pension_huf', 'loans_huf', 'net_wealth_huf']
                df_yoy_rolling = calculate_rolling_yoy_analytics(
                    df_combined_analytics.copy(),
                    'Date',
                    value_cols_summary
                )
                
                # Create display dataframe with only YoY columns
                yoy_cols = [col for col in df_yoy_rolling.columns if 'YoY%' in col]
                df_yoy_display = df_yoy_rolling[['Date'] + yoy_cols].copy()
                
                # Rename columns for display
                df_yoy_display.columns = df_yoy_display.columns.str.replace('_YoY%', '')
                df_yoy_display.columns = df_yoy_display.columns.str.replace('_huf', '')
                df_yoy_display.columns = df_yoy_display.columns.str.replace(' (HUF)', '')
                
                # Transpose and format
                df_yoy_display['Date'] = pd.to_datetime(df_yoy_display['Date']).dt.strftime('%Y-%m-%d')
                df_yoy_display = df_yoy_display.set_index('Date').T.reset_index()
                df_yoy_display.rename(columns={'index': 'Metric'}, inplace=True)
                
                # Format as percentages
                for col in df_yoy_display.columns:
                    if col != 'Metric':
                        df_yoy_display[col] = df_yoy_display[col].apply(
                            lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A"
                        )
                
                st.dataframe(df_yoy_display, use_container_width=True, hide_index=True)
                
                # Analytics Table 2: Summary Analytics YoY (vs Prior Year December)
                st.markdown("#### 📊 Summary Analytics YoY - Year-over-Year vs Prior December")
                st.caption("Each year compared to prior year's December baseline")
                
                df_yoy_baseline = calculate_yoy_vs_baseline(
                    df_combined_analytics.copy(),
                    'Date',
                    value_cols_summary
                )
                
                if not df_yoy_baseline.empty:
                    df_yoy_baseline_display = df_yoy_baseline.copy()
                    
                    # Rename columns for display
                    df_yoy_baseline_display.columns = df_yoy_baseline_display.columns.str.replace('_YoY%', '')
                    df_yoy_baseline_display.columns = df_yoy_baseline_display.columns.str.replace('_huf', '')
                    df_yoy_baseline_display.columns = df_yoy_baseline_display.columns.str.replace(' (HUF)', '')
                    
                    # Transpose: years in columns
                    df_yoy_baseline_display = df_yoy_baseline_display.set_index('Year').T.reset_index()
                    df_yoy_baseline_display.rename(columns={'index': 'Metric'}, inplace=True)
                    
                    # Format as percentages
                    for col in df_yoy_baseline_display.columns:
                        if col != 'Metric':
                            df_yoy_baseline_display[col] = df_yoy_baseline_display[col].apply(
                                lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A"
                            )
                    
                    st.dataframe(df_yoy_baseline_display, use_container_width=True, hide_index=True)
                else:
                    st.info("Insufficient data for year-over-year comparison")
"""

# ============================================================================
# ANALYTICS TABLES 3 & 4: After "Portfolio Detail by Instrument" download button  
# Insert after line: key="download_detail"
# ============================================================================

ANALYTICS_AFTER_PORTFOLIO_DETAIL = """
                # Analytics Table 3: Summary Analytics for Portfolio (by Instrument)
                st.markdown("#### 📈 Summary Analytics for Portfolio - Rolling 12-Month % Change")
                st.caption("Year-over-Year percentage change by instrument (Dec-to-Dec)")
                
                # Calculate YoY for each instrument
                df_instruments_yoy = pd.DataFrame()
                for instrument in df_daily['instrument_name'].unique():
                    inst_data = df_daily[df_daily['instrument_name'] == instrument].copy()
                    inst_data = inst_data.sort_values('Date')
                    
                    # Calculate YoY for this instrument
                    inst_yoy = calculate_rolling_yoy_analytics(
                        inst_data[['Date', 'value_huf']].copy(),
                        'Date',
                        ['value_huf']
                    )
                    
                    inst_yoy['instrument_name'] = instrument
                    df_instruments_yoy = pd.concat([df_instruments_yoy, inst_yoy])
                
                # Pivot: instruments in rows, dates in columns, show YoY%
                if not df_instruments_yoy.empty and 'value_huf_YoY%' in df_instruments_yoy.columns:
                    df_inst_yoy_pivot = df_instruments_yoy.pivot_table(
                        index='instrument_name',
                        columns='Date',
                        values='value_huf_YoY%'
                    ).reset_index()
                    
                    df_inst_yoy_display = df_inst_yoy_pivot.copy()
                    df_inst_yoy_display.rename(columns={'instrument_name': 'Instrument'}, inplace=True)
                    
                    # Format date columns
                    df_inst_yoy_display.columns = [
                        col.strftime('%Y-%m-%d') if isinstance(col, pd.Timestamp) else col 
                        for col in df_inst_yoy_display.columns
                    ]
                    
                    # Format as percentages
                    for col in df_inst_yoy_display.columns:
                        if col != 'Instrument':
                            df_inst_yoy_display[col] = df_inst_yoy_display[col].apply(
                                lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A"
                            )
                    
                    st.dataframe(df_inst_yoy_display, use_container_width=True, hide_index=True)
                else:
                    st.info("Insufficient data for portfolio YoY analysis")
                
                # Analytics Table 4: Summary Analytics YoY Portfolio
                st.markdown("#### 📊 Summary Analytics YoY Portfolio - Year-over-Year by Instrument")
                st.caption("Each year compared to prior year's December baseline by instrument")
                
                df_inst_yoy_baseline_all = pd.DataFrame()
                for instrument in df_daily['instrument_name'].unique():
                    inst_data = df_daily[df_daily['instrument_name'] == instrument].copy()
                    inst_data = inst_data.sort_values('Date')
                    
                    inst_yoy_baseline = calculate_yoy_vs_baseline(
                        inst_data[['Date', 'value_huf']].copy(),
                        'Date',
                        ['value_huf']
                    )
                    
                    if not inst_yoy_baseline.empty:
                        inst_yoy_baseline['Instrument'] = instrument
                        df_inst_yoy_baseline_all = pd.concat([df_inst_yoy_baseline_all, inst_yoy_baseline])
                
                if not df_inst_yoy_baseline_all.empty:
                    # Pivot: instruments in rows, years in columns
                    df_inst_baseline_pivot = df_inst_yoy_baseline_all.pivot_table(
                        index='Instrument',
                        columns='Year',
                        values='value_huf_YoY%'
                    ).reset_index()
                    
                    # Format as percentages
                    for col in df_inst_baseline_pivot.columns:
                        if col != 'Instrument':
                            df_inst_baseline_pivot[col] = df_inst_baseline_pivot[col].apply(
                                lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A"
                            )
                    
                    st.dataframe(df_inst_baseline_pivot, use_container_width=True, hide_index=True)
                else:
                    st.info("Insufficient data for portfolio YoY baseline analysis")
"""

# ============================================================================
# ANALYTICS TABLES 5 & 6: After "Wealth Detail by Category" dataframe
# Insert after the wealth pivot dataframe display
# ============================================================================

ANALYTICS_AFTER_WEALTH_DETAIL = """
                        # Analytics Table 5: Summary Analytics for Wealth (by Category)
                        st.markdown("#### 📈 Summary Analytics for Wealth - Rolling 12-Month % Change")
                        st.caption("Year-over-Year percentage change by wealth category (Dec-to-Dec)")
                        
                        # Calculate YoY for each category
                        df_wealth_yoy = pd.DataFrame()
                        for category in df_wealth_detail['category_name'].unique():
                            cat_data = df_wealth_detail[df_wealth_detail['category_name'] == category].copy()
                            cat_data = cat_data.sort_values('value_date')
                            
                            # Calculate YoY for this category
                            cat_yoy = calculate_rolling_yoy_analytics(
                                cat_data[['value_date', 'present_value']].copy(),
                                'value_date',
                                ['present_value']
                            )
                            
                            cat_yoy['category_name'] = category
                            df_wealth_yoy = pd.concat([df_wealth_yoy, cat_yoy])
                        
                        # Pivot: categories in rows, dates in columns, show YoY%
                        if not df_wealth_yoy.empty and 'present_value_YoY%' in df_wealth_yoy.columns:
                            df_wealth_yoy_pivot = df_wealth_yoy.pivot_table(
                                index='category_name',
                                columns='value_date',
                                values='present_value_YoY%'
                            ).reset_index()
                            
                            df_wealth_yoy_display = df_wealth_yoy_pivot.copy()
                            df_wealth_yoy_display.rename(columns={'category_name': 'Category'}, inplace=True)
                            
                            # Format date columns
                            df_wealth_yoy_display.columns = [
                                col.strftime('%Y-%m-%d') if isinstance(col, pd.Timestamp) else col 
                                for col in df_wealth_yoy_display.columns
                            ]
                            
                            # Format as percentages
                            for col in df_wealth_yoy_display.columns:
                                if col != 'Category':
                                    df_wealth_yoy_display[col] = df_wealth_yoy_display[col].apply(
                                        lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A"
                                    )
                            
                            st.dataframe(df_wealth_yoy_display, use_container_width=True, hide_index=True)
                        else:
                            st.info("Insufficient data for wealth YoY analysis")
                        
                        # Analytics Table 6: Summary Analytics YoY Wealth
                        st.markdown("#### 📊 Summary Analytics YoY Wealth - Year-over-Year by Category")
                        st.caption("Each year compared to prior year's December baseline by category")
                        
                        df_wealth_yoy_baseline_all = pd.DataFrame()
                        for category in df_wealth_detail['category_name'].unique():
                            cat_data = df_wealth_detail[df_wealth_detail['category_name'] == category].copy()
                            cat_data = cat_data.sort_values('value_date')
                            
                            cat_yoy_baseline = calculate_yoy_vs_baseline(
                                cat_data[['value_date', 'present_value']].copy(),
                                'value_date',
                                ['present_value']
                            )
                            
                            if not cat_yoy_baseline.empty:
                                cat_yoy_baseline['Category'] = category
                                df_wealth_yoy_baseline_all = pd.concat([df_wealth_yoy_baseline_all, cat_yoy_baseline])
                        
                        if not df_wealth_yoy_baseline_all.empty:
                            # Pivot: categories in rows, years in columns
                            df_wealth_baseline_pivot = df_wealth_yoy_baseline_all.pivot_table(
                                index='Category',
                                columns='Year',
                                values='present_value_YoY%'
                            ).reset_index()
                            
                            # Format as percentages
                            for col in df_wealth_baseline_pivot.columns:
                                if col != 'Category':
                                    df_wealth_baseline_pivot[col] = df_wealth_baseline_pivot[col].apply(
                                        lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A"
                                    )
                            
                            st.dataframe(df_wealth_baseline_pivot, use_container_width=True, hide_index=True)
                        else:
                            st.info("Insufficient data for wealth YoY baseline analysis")
"""

if __name__ == "__main__":
    print("=" * 80)
    print("ANALYTICS TABLES INSERTION GUIDE")
    print("=" * 80)
    print("\n1. Insert ANALYTICS_AFTER_PORTFOLIO_SUMMARY after the download_summary button")
    print("2. Insert ANALYTICS_AFTER_PORTFOLIO_DETAIL after the download_detail button")
    print("3. Insert ANALYTICS_AFTER_WEALTH_DETAIL after the wealth pivot dataframe display")
    print("\nEach section adds 2 analytics tables with YoY% calculations.")
    print("=" * 80)
