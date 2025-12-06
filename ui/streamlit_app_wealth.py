"""
Portfolio Analyzer UI with Wealth Management
Complete system for portfolio + total wealth tracking
"""
import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

st.set_page_config(
    page_title="Portfolio & Wealth Analyzer",
    page_icon="💰",
    layout="wide"
)

API_URL = "http://localhost:8000"

# Custom CSS - Dark Theme
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #000000;
    }
    
    /* Main content area */
    .main {
        background-color: #000000;
    }
    
    /* Text colors */
    .stApp, .stMarkdown, p, span, div, label {
        color: #b0b0b0 !important;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #d0d0d0 !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1a1a1a;
    }
    
    [data-testid="stSidebar"] * {
        color: #b0b0b0 !important;
    }
    
    /* Metric boxes */
    [data-testid="stMetric"] {
        background-color: #1a1a1a;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #333333;
    }
    
    [data-testid="stMetricLabel"] {
        color: #909090 !important;
    }
    
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
    }
    
    /* Input fields */
    .stTextInput input, .stNumberInput input, .stDateInput input, 
    .stSelectbox select, .stTextArea textarea {
        background-color: #1a1a1a !important;
        color: #b0b0b0 !important;
        border: 1px solid #333333 !important;
    }
    
    /* Buttons */
    .stButton button {
        background-color: #2a2a2a !important;
        color: #b0b0b0 !important;
        border: 1px solid #404040 !important;
    }
    
    .stButton button:hover {
        background-color: #3a3a3a !important;
        border: 1px solid #505050 !important;
    }
    
    /* Download buttons */
    .stDownloadButton button {
        background-color: #2a2a2a !important;
        color: #b0b0b0 !important;
        border: 1px solid #404040 !important;
    }
    
    /* Dataframes */
    [data-testid="stDataFrame"] {
        background-color: #1a1a1a !important;
    }
    
    /* Info boxes */
    .stAlert, [data-baseweb="notification"] {
        background-color: #1a1a1a !important;
        border: 1px solid #333333 !important;
        color: #b0b0b0 !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #000000;
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #1a1a1a;
        color: #808080 !important;
        border: 1px solid #333333;
        border-radius: 4px 4px 0 0;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #2a2a2a;
        color: #ffffff !important;
        border-bottom: 2px solid #4a4a4a;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #1a1a1a !important;
        color: #b0b0b0 !important;
        border: 1px solid #333333 !important;
    }
    
    /* Code blocks */
    .stCodeBlock, code {
        background-color: #1a1a1a !important;
        color: #b0b0b0 !important;
        border: 1px solid #333333 !important;
    }
    
    /* Horizontal rule */
    hr {
        border-color: #333333 !important;
    }
    
    /* Radio buttons */
    .stRadio label {
        color: #b0b0b0 !important;
    }
    
    /* Checkbox */
    .stCheckbox label {
        color: #b0b0b0 !important;
    }
    
    /* Slider */
    .stSlider label {
        color: #b0b0b0 !important;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("💰 Portfolio & Wealth Analyzer")
st.markdown("Complete wealth tracking: Securities Portfolio + Cash + Property + Pensions - Loans")

# Sidebar
st.sidebar.header("⚙️ Configuration")
portfolio_id = st.sidebar.number_input("Portfolio ID", value=1, min_value=1)

# Add Data Update section to sidebar
st.sidebar.markdown("---")
st.sidebar.header("🔄 Data Update")
st.sidebar.markdown("""
**Update portfolio data with latest prices and FX rates**

This fetches:
- Latest FX rates (USD, EUR, GBP, CHF)
- Latest instrument prices
- Recalculates portfolio values

Safe to run anytime - takes 2-3 minutes.
""")

if st.sidebar.button("🔄 Run Daily Update", type="primary", use_container_width=True):
    with st.sidebar:
        with st.spinner("Running daily update..."):
            try:
                update_response = requests.post(f"{API_URL}/etl/run-daily-update", timeout=180)
                
                if update_response.status_code == 200:
                    result = update_response.json()
                    st.success("✅ Daily update completed!")
                    
                    with st.expander("📋 View Update Log"):
                        st.code(result.get('output', 'No output'), language='text')
                    
                    st.info(f"🕐 Last updated: {result.get('timestamp')}")
                    
                    # Auto-refresh the page
                    st.rerun()
                else:
                    st.error(f"❌ Update failed: {update_response.text}")
            except requests.Timeout:
                st.error("⏱️ Update timed out. It may still be running. Check back in a minute.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

st.sidebar.markdown("---")
st.sidebar.markdown("""
**💡 Tip**: You can run updates monthly or as needed. 
The system carries forward prices for missing days.
""")

# Main tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Total Wealth Dashboard",
    "💼 Wealth Management", 
    "📈 Wealth Trends",
    "📸 Portfolio Snapshot",
    "🔧 Portfolio Management",
    "📋 Analytical Data"
])

# ==================== TAB 1: Total Wealth Dashboard ====================
with tab1:
    st.subheader("💰 Total Wealth Overview")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        snapshot_date_wealth = st.date_input(
            "Snapshot Date",
            value=date.today(),
            key="wealth_snapshot_date"
        )
    
    with col2:
        st.write("")
        st.write("")
        if st.button("🔄 Refresh", key="refresh_wealth"):
            st.rerun()
    
    try:
        # Get total wealth
        response = requests.get(f"{API_URL}/wealth/total/{snapshot_date_wealth.isoformat()}")
        
        if response.status_code == 200:
            wealth_data = response.json()
            
            # Display key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "📊 Portfolio Value",
                    f"{wealth_data['portfolio_value_huf']:,.0f} HUF",
                    help="Value of securities portfolio"
                )
            
            with col2:
                st.metric(
                    "💵 Other Assets",
                    f"{wealth_data['other_assets_huf']:,.0f} HUF",
                    help="Cash + Property + Pensions"
                )
            
            with col3:
                st.metric(
                    "💳 Liabilities",
                    f"{wealth_data['total_liabilities_huf']:,.0f} HUF",
                    delta=f"-{wealth_data['total_liabilities_huf']:,.0f}",
                    delta_color="inverse",
                    help="Total loans and debts"
                )
            
            with col4:
                net_wealth = wealth_data['net_wealth_huf']
                st.metric(
                    "💎 Net Wealth",
                    f"{net_wealth:,.0f} HUF",
                    help="Portfolio + Assets - Liabilities"
                )
            
            # USD equivalent
            usd_equivalent = net_wealth / wealth_data['fx_rates'].get('USD', 327.87)
            st.info(f"💵 **Net Wealth in USD**: ${usd_equivalent:,.2f}")
            
            st.markdown("---")
            
            # Breakdown
            st.subheader("Asset Breakdown")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Asset breakdown
                breakdown = wealth_data['breakdown']
                
                breakdown_df = pd.DataFrame([
                    {"Category": "Portfolio", "Value": wealth_data['portfolio_value_huf']},
                    {"Category": "Cash", "Value": breakdown.get('cash', 0)},
                    {"Category": "Property", "Value": breakdown.get('property', 0)},
                    {"Category": "Pension", "Value": breakdown.get('pension', 0)},
                    {"Category": "Other", "Value": breakdown.get('other', 0)}
                ])
                
                fig_assets = px.pie(
                    breakdown_df,
                    values='Value',
                    names='Category',
                    title='Asset Allocation',
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig_assets.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_assets, use_container_width=True)
            
            with col2:
                # Summary table
                st.markdown("#### Summary")
                
                summary_data = [
                    {"Item": "Securities Portfolio", "Value HUF": f"{wealth_data['portfolio_value_huf']:,.0f}"},
                    {"Item": "Cash Accounts", "Value HUF": f"{breakdown.get('cash', 0):,.0f}"},
                    {"Item": "Properties", "Value HUF": f"{breakdown.get('property', 0):,.0f}"},
                    {"Item": "Pensions", "Value HUF": f"{breakdown.get('pension', 0):,.0f}"},
                    {"Item": "Other Assets", "Value HUF": f"{breakdown.get('other', 0):,.0f}"},
                    {"Item": "**Total Assets**", "Value HUF": f"**{wealth_data['total_assets_huf']:,.0f}**"},
                    {"Item": "Loans & Liabilities", "Value HUF": f"-{breakdown.get('loans', 0):,.0f}"},
                    {"Item": "**NET WEALTH**", "Value HUF": f"**{net_wealth:,.0f}**"}
                ]
                
                st.dataframe(pd.DataFrame(summary_data), hide_index=True, use_container_width=True)
            
            # Detailed wealth items
            st.markdown("---")
            st.subheader("Detailed Wealth Items")
            
            if wealth_data.get('wealth_details'):
                df_details = pd.DataFrame(wealth_data['wealth_details'])
                
                # Format display
                df_display = df_details.copy()
                df_display['present_value'] = df_display['present_value'].apply(lambda x: f"{x:,.2f}")
                df_display['type'] = df_display['is_liability'].apply(lambda x: "Liability" if x else "Asset")
                
                df_display = df_display[[
                    'category_type', 'name', 'present_value', 'currency', 'type', 'note'
                ]]
                df_display.columns = ['Type', 'Name', 'Value', 'Currency', 'Asset/Liability', 'Note']
                
                st.dataframe(df_display, hide_index=True, use_container_width=True)
            else:
                st.info("No wealth values recorded for this date. Go to 'Wealth Management' tab to add values.")
            
            # Portfolio details breakdown
            st.markdown("---")
            st.subheader("Securities Portfolio Details")
            
            try:
                portfolio_response = requests.get(
                    f"{API_URL}/portfolio/{portfolio_id}/snapshot",
                    params={"snapshot_date": snapshot_date_wealth}
                )
                
                if portfolio_response.status_code == 200:
                    portfolio_items = portfolio_response.json()
                    
                    if portfolio_items:
                        df_portfolio = pd.DataFrame(portfolio_items)
                        
                        # Format display
                        df_port_display = df_portfolio.copy()
                        df_port_display['quantity'] = df_port_display['quantity'].apply(lambda x: f"{x:,.2f}")
                        df_port_display['price'] = df_port_display['price'].apply(lambda x: f"{x:,.4f}")
                        df_port_display['value_huf'] = df_port_display['value_huf'].apply(lambda x: f"{x:,.2f}")
                        
                        df_port_display = df_port_display[[
                            'name', 'instrument_type', 'quantity', 'price', 
                            'currency', 'value_huf', 'price_source'
                        ]]
                        df_port_display.columns = [
                            'Instrument', 'Type', 'Quantity', 'Price', 
                            'Currency', 'Value (HUF)', 'Price Source'
                        ]
                        
                        st.dataframe(df_port_display, use_container_width=True, hide_index=True)
                    else:
                        st.info("No portfolio holdings for this date.")
                else:
                    st.warning(f"Could not load portfolio details: {portfolio_response.status_code}")
            except Exception as e:
                st.warning(f"Error loading portfolio details: {str(e)}")
            
            # Save snapshot button
            st.markdown("---")
            if st.button("💾 Save This Snapshot", key="save_snapshot"):
                save_response = requests.post(f"{API_URL}/wealth/snapshot/{snapshot_date_wealth.isoformat()}")
                if save_response.status_code == 200:
                    st.success("✅ Snapshot saved successfully!")
                else:
                    st.error(f"❌ Error saving snapshot: {save_response.text}")
        
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
    
    except Exception as e:
        st.error(f"Error loading wealth data: {str(e)}")

# ==================== TAB 2: Wealth Management ====================
with tab2:
    st.subheader("💼 Wealth Management")
    
    st.info("💡 **Tip**: Use 'Copy from Previous Day' to quickly populate today's values, then adjust as needed.")
    
    # Get all categories
    try:
        cat_response = requests.get(f"{API_URL}/wealth/categories")
        
        if cat_response.status_code == 200:
            categories = cat_response.json()
            
            # Group by type
            cash_items = [c for c in categories if c['category_type'] == 'cash']
            property_items = [c for c in categories if c['category_type'] == 'property']
            pension_items = [c for c in categories if c['category_type'] == 'pension']
            loan_items = [c for c in categories if c['category_type'] == 'loan']
            other_items = [c for c in categories if c['category_type'] == 'other']
            
            # Auto-copy feature at the top
            st.markdown("### 📋 Quick Actions")
            col_copy1, col_copy2, col_copy3 = st.columns([2, 2, 1])
            
            with col_copy1:
                copy_from_date = st.date_input(
                    "Copy from date",
                    value=date.today() - timedelta(days=1),
                    key="copy_from_date"
                )
            
            with col_copy2:
                copy_to_date = st.date_input(
                    "Copy to date",
                    value=date.today(),
                    key="copy_to_date"
                )
            
            with col_copy3:
                st.write("")
                st.write("")
                if st.button("📥 Copy Values", key="copy_previous_day", use_container_width=True):
                    # Get values from source date
                    copy_response = requests.get(f"{API_URL}/wealth/values/{copy_from_date.isoformat()}")
                    
                    if copy_response.status_code == 200:
                        source_values = copy_response.json()
                        
                        if source_values:
                            success_count = 0
                            error_count = 0
                            
                            with st.spinner(f"Copying {len(source_values)} values..."):
                                for val in source_values:
                                    payload = {
                                        "wealth_category_id": val['category_id'],  # Fixed: use 'category_id' not 'wealth_category_id'
                                        "value_date": copy_to_date.isoformat(),
                                        "present_value": val['present_value'],
                                        "note": f"Copied from {copy_from_date.isoformat()}"
                                    }
                                    
                                    save_response = requests.post(f"{API_URL}/wealth/values", json=payload)
                                    
                                    if save_response.status_code == 200:
                                        success_count += 1
                                    else:
                                        error_count += 1
                            
                            if error_count == 0:
                                st.success(f"✅ Successfully copied {success_count} values from {copy_from_date} to {copy_to_date}")
                            else:
                                st.warning(f"⚠️ Copied {success_count} values, {error_count} failed")
                            
                            st.rerun()
                        else:
                            st.warning(f"No values found for {copy_from_date}")
                    else:
                        st.error(f"Could not load values from {copy_from_date}")
            
            st.markdown("---")
            
            # Display by category
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 💵 Add/Update Values")
                
                value_date = st.date_input(
                    "Date",
                    value=date.today(),
                    key="value_date_input"
                )
                
                # Select category type
                cat_type = st.selectbox(
                    "Category Type",
                    ["cash", "property", "pension", "loan", "other"],
                    key="cat_type_select"
                )
                
                # Filter categories by type
                filtered_cats = [c for c in categories if c['category_type'] == cat_type]
                
                if filtered_cats:
                    cat_options = {f"{c['name']} ({c['currency']})": c for c in filtered_cats}
                    
                    selected_cat_name = st.selectbox(
                        "Select Item",
                        options=list(cat_options.keys()),
                        key="cat_select"
                    )
                    
                    selected_cat = cat_options[selected_cat_name]
                    
                    col_val, col_note = st.columns([1, 2])
                    
                    with col_val:
                        value = st.number_input(
                            f"Value ({selected_cat['currency']})",
                            min_value=0.0,
                            value=0.0,
                            step=1000.0,
                            format="%.2f",
                            key="value_input"
                        )
                    
                    with col_note:
                        note = st.text_area(
                            "Note (optional)",
                            key="note_input",
                            height=100
                        )
                    
                    if st.button("💾 Save Value", key="save_value", use_container_width=True):
                        payload = {
                            "wealth_category_id": selected_cat['id'],
                            "value_date": value_date.isoformat(),
                            "present_value": float(value),
                            "note": note if note else None
                        }
                        
                        save_response = requests.post(f"{API_URL}/wealth/values", json=payload)
                        
                        if save_response.status_code == 200:
                            st.success(f"✅ Value saved for {selected_cat['name']}")
                            st.rerun()
                        else:
                            st.error(f"❌ Error: {save_response.text}")
                else:
                    st.info(f"No items in category '{cat_type}'")
            
            with col2:
                st.markdown("### 📋 Current Values")
                
                check_date = st.date_input(
                    "View values for date",
                    value=date.today(),
                    key="check_date"
                )
                
                if st.button("🔍 Load Values", key="load_values"):
                    values_response = requests.get(f"{API_URL}/wealth/values/{check_date.isoformat()}")
                    
                    if values_response.status_code == 200:
                        values = values_response.json()
                        
                        if values:
                            df_values = pd.DataFrame(values)
                            
                            # Group by type
                            for cat_type in ['cash', 'property', 'pension', 'loan', 'other']:
                                type_values = [v for v in values if v['category_type'] == cat_type]
                                
                                if type_values:
                                    st.markdown(f"#### {cat_type.title()}")
                                    
                                    type_df = pd.DataFrame(type_values)
                                    type_display = type_df[['name', 'present_value', 'currency', 'note']].copy()
                                    type_display.columns = ['Name', 'Value', 'Currency', 'Note']
                                    
                                    st.dataframe(type_display, hide_index=True, use_container_width=True)
                            
                            st.success(f"✅ Loaded {len(values)} values for {check_date}")
                        else:
                            st.info(f"No values found for {check_date}")
                    else:
                        st.error(f"Error: {values_response.text}")
            
            # Category summary
            st.markdown("---")
            st.markdown("### 📊 Wealth Categories Summary")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("💵 Cash Accounts", len(cash_items))
            with col2:
                st.metric("🏠 Properties", len(property_items))
            with col3:
                st.metric("💼 Pensions", len(pension_items))
            with col4:
                st.metric("💳 Loans", len(loan_items))
            
            # Add new category
            with st.expander("➕ Add New Wealth Category"):
                with st.form("add_category_form"):
                    new_cat_name = st.text_input("Name")
                    new_cat_type = st.selectbox("Type", ["cash", "property", "pension", "loan", "other"])
                    new_cat_currency = st.selectbox("Currency", ["HUF", "EUR", "USD", "GBP", "CHF"])
                    new_cat_liability = st.checkbox("Is this a liability (loan)?")
                    
                    if st.form_submit_button("Add Category"):
                        if new_cat_name:
                            payload = {
                                "category_type": new_cat_type,
                                "name": new_cat_name,
                                "currency": new_cat_currency,
                                "is_liability": new_cat_liability
                            }
                            
                            add_response = requests.post(f"{API_URL}/wealth/categories", json=payload)
                            
                            if add_response.status_code == 200:
                                st.success(f"✅ Category '{new_cat_name}' added!")
                                st.rerun()
                            else:
                                st.error(f"❌ Error: {add_response.text}")
                        else:
                            st.error("Name is required")
        
        else:
            st.error(f"Failed to load categories: {cat_response.text}")
    
    except Exception as e:
        st.error(f"Error: {str(e)}")

# ==================== TAB 3: Wealth Trends ====================
with tab3:
    st.subheader("📈 Wealth Trends & Analysis")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        trend_start = st.date_input(
            "Start Date",
            value=date.today() - timedelta(days=180),
            key="trend_start"
        )
    
    with col2:
        trend_end = st.date_input(
            "End Date",
            value=date.today(),
            key="trend_end"
        )
    
    with col3:
        st.write("")
        st.write("")
        if st.button("🔄 Refresh", key="refresh_trends"):
            st.rerun()
    
    # Auto-load trends on page load
    try:
        # Get daily portfolio values for the date range
        portfolio_history_response = requests.get(
            f"{API_URL}/portfolio/{portfolio_id}/history",
            params={
                "start_date": trend_start.isoformat(),
                "end_date": trend_end.isoformat()
            }
        )
        
        if portfolio_history_response.status_code == 200:
            portfolio_data = portfolio_history_response.json()
            
            if portfolio_data:
                # Group by date and sum values
                df_portfolio = pd.DataFrame(portfolio_data)
                df_portfolio['date'] = pd.to_datetime(df_portfolio['date'])
                
                daily_portfolio = df_portfolio.groupby('date').agg({
                    'value_huf': 'sum'
                }).reset_index()
                daily_portfolio.columns = ['snapshot_date', 'portfolio_value_huf']
                
                # Get wealth snapshots for the same period
                snapshots_response = requests.get(
                    f"{API_URL}/wealth/snapshots",
                    params={
                        "start_date": trend_start.isoformat(),
                        "end_date": trend_end.isoformat()
                    }
                )
                
                # Merge portfolio values with wealth snapshots
                if snapshots_response.status_code == 200:
                    snapshots = snapshots_response.json()
                    
                    if snapshots:
                        df_snapshots = pd.DataFrame(snapshots)
                        df_snapshots['snapshot_date'] = pd.to_datetime(df_snapshots['snapshot_date'])
                        
                        # Select only columns that exist in snapshots
                        available_cols = ['snapshot_date', 'net_wealth_huf']
                        for col in ['cash_huf', 'property_huf', 'pension_huf', 'other_huf', 'loans_huf', 'portfolio_value_huf']:
                            if col in df_snapshots.columns:
                                available_cols.append(col)
                        
                        df_snapshots_filtered = df_snapshots[available_cols]
                        
                        # Merge with daily portfolio values
                        df_combined = pd.merge(
                            daily_portfolio,
                            df_snapshots_filtered,
                            on='snapshot_date',
                            how='left',
                            suffixes=('', '_snapshot')
                        )
                        
                        # Use portfolio value from daily data, supplement with snapshot wealth data
                        if 'portfolio_value_huf_snapshot' in df_combined.columns:
                            df_combined['portfolio_value_huf'] = df_combined['portfolio_value_huf'].fillna(df_combined['portfolio_value_huf_snapshot'])
                    else:
                        # No wealth snapshots, use portfolio only
                        df_combined = daily_portfolio
                        df_combined['net_wealth_huf'] = df_combined['portfolio_value_huf']
                else:
                    # No wealth snapshots, use portfolio only
                    df_combined = daily_portfolio
                    df_combined['net_wealth_huf'] = df_combined['portfolio_value_huf']
                
                df_combined = df_combined.sort_values('snapshot_date')
                
                # Calculate net wealth for all days (portfolio + latest other wealth values)
                # Get latest wealth values to use for all days without snapshots
                latest_wealth_response = requests.get(f"{API_URL}/wealth/values/{trend_end.isoformat()}")
                latest_other_assets = 0
                
                if latest_wealth_response.status_code == 200:
                    latest_values = latest_wealth_response.json()
                    if latest_values:
                        for val in latest_values:
                            if not val['is_liability']:
                                latest_other_assets += val['present_value']
                
                # If no net_wealth_huf column, calculate it for all rows
                if 'net_wealth_huf' not in df_combined.columns or df_combined['net_wealth_huf'].isna().all():
                    df_combined['net_wealth_huf'] = df_combined['portfolio_value_huf'] + latest_other_assets
                else:
                    # Fill missing net_wealth with portfolio + latest other assets
                    df_combined['net_wealth_huf'] = df_combined['net_wealth_huf'].fillna(
                        df_combined['portfolio_value_huf'] + latest_other_assets
                    )
                
                # Key metrics
                latest = df_combined.iloc[-1]
                first = df_combined.iloc[0]
                
                portfolio_change = latest['portfolio_value_huf'] - first['portfolio_value_huf']
                portfolio_change_pct = (portfolio_change / first['portfolio_value_huf']) * 100 if first['portfolio_value_huf'] != 0 else 0
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Current Portfolio Value",
                        f"{latest['portfolio_value_huf']:,.0f} HUF"
                    )
                
                with col2:
                    st.metric(
                        "Period Change",
                        f"{portfolio_change:+,.0f} HUF",
                        f"{portfolio_change_pct:+.2f}%"
                    )
                
                with col3:
                    st.metric(
                        "Data Points",
                        len(df_combined)
                    )
                
                st.markdown("---")
                
                # Portfolio value trend (primary chart)
                st.markdown("#### Portfolio Value Trend (Daily)")
                
                fig_portfolio = go.Figure()
                
                fig_portfolio.add_trace(go.Scatter(
                    x=df_combined['snapshot_date'],
                    y=df_combined['portfolio_value_huf'],
                    mode='lines+markers',
                    name='Portfolio Value',
                    line=dict(color='#1976D2', width=3),
                    marker=dict(size=6),
                    fill='tozeroy',
                    fillcolor='rgba(25, 118, 210, 0.1)',
                    hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Portfolio: %{y:,.0f} HUF<extra></extra>'
                ))
                
                fig_portfolio.update_layout(
                    xaxis_title="Date",
                    yaxis_title="Portfolio Value (HUF)",
                    hovermode='x unified',
                    height=400
                )
                
                st.plotly_chart(fig_portfolio, use_container_width=True)
                
                # Net wealth trend (always show)
                st.markdown("#### Net Wealth Over Time (Daily)")
                
                fig_net = go.Figure()
                
                fig_net.add_trace(go.Scatter(
                    x=df_combined['snapshot_date'],
                    y=df_combined['net_wealth_huf'],
                    mode='lines+markers',
                    name='Net Wealth',
                    line=dict(color='#2E7D32', width=3),
                    marker=dict(size=6),
                    fill='tozeroy',
                    fillcolor='rgba(46, 125, 50, 0.1)',
                    hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Net Wealth: %{y:,.0f} HUF<extra></extra>'
                ))
                
                fig_net.update_layout(
                    xaxis_title="Date",
                    yaxis_title="Net Wealth (HUF)",
                    hovermode='x unified',
                    height=400
                )
                
                st.plotly_chart(fig_net, use_container_width=True)
                
                # Component breakdown - show portfolio vs other wealth
                st.markdown("#### All Wealth Components Over Time")
                
                # Calculate other assets for all days (using latest values)
                if latest_other_assets > 0:
                    df_combined['other_assets_huf'] = latest_other_assets
                else:
                    df_combined['other_assets_huf'] = df_combined['net_wealth_huf'] - df_combined['portfolio_value_huf']
                
                fig2 = go.Figure()
                
                # Portfolio (bottom layer)
                fig2.add_trace(go.Scatter(
                    x=df_combined['snapshot_date'],
                    y=df_combined['portfolio_value_huf'],
                    name='Portfolio',
                    mode='lines',
                    line=dict(width=0.5, color='#1976D2'),
                    stackgroup='one',
                    fillcolor='rgba(25, 118, 210, 0.7)',
                    hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Portfolio: %{y:,.0f} HUF<extra></extra>'
                ))
                
                # Other Assets (top layer)
                fig2.add_trace(go.Scatter(
                    x=df_combined['snapshot_date'],
                    y=df_combined['other_assets_huf'],
                    name='Other Assets (Cash, Property, Pensions)',
                    mode='lines',
                    line=dict(width=0.5, color='#388E3C'),
                    stackgroup='one',
                    fillcolor='rgba(56, 142, 60, 0.7)',
                    hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Other Assets: %{y:,.0f} HUF<extra></extra>'
                ))
                
                fig2.update_layout(
                    xaxis_title="Date",
                    yaxis_title="Value (HUF)",
                    hovermode='x unified',
                    height=400,
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                st.plotly_chart(fig2, use_container_width=True)
                
                # If we have detailed wealth snapshots, show detailed breakdown too
                if 'cash_huf' in df_combined.columns and df_combined['cash_huf'].notna().any():
                    st.markdown("#### Detailed Wealth Breakdown (Snapshot Days Only)")
                    st.info("💡 This chart shows detailed breakdown of Cash, Property, and Pensions on days when you save wealth snapshots.")
                    
                    df_wealth = df_combined[df_combined['cash_huf'].notna()]
                    
                    if not df_wealth.empty:
                        fig3 = go.Figure()
                        
                        fig3.add_trace(go.Scatter(
                            x=df_wealth['snapshot_date'],
                            y=df_wealth['portfolio_value_huf'],
                            name='Portfolio',
                            stackgroup='one',
                            fillcolor='#1976D2'
                        ))
                        
                        fig3.add_trace(go.Scatter(
                            x=df_wealth['snapshot_date'],
                            y=df_wealth['cash_huf'],
                            name='Cash',
                            stackgroup='one',
                            fillcolor='#388E3C'
                        ))
                        
                        if 'property_huf' in df_wealth.columns:
                            fig3.add_trace(go.Scatter(
                                x=df_wealth['snapshot_date'],
                                y=df_wealth['property_huf'],
                                name='Property',
                                stackgroup='one',
                                fillcolor='#F57C00'
                            ))
                        
                        if 'pension_huf' in df_wealth.columns:
                            fig3.add_trace(go.Scatter(
                                x=df_wealth['snapshot_date'],
                                y=df_wealth['pension_huf'],
                                name='Pension',
                                stackgroup='one',
                                fillcolor='#7B1FA2'
                            ))
                        
                        fig3.update_layout(
                            xaxis_title="Date",
                            yaxis_title="Value (HUF)",
                            hovermode='x unified',
                            height=400
                        )
                        
                        st.plotly_chart(fig3, use_container_width=True)
            else:
                st.info("No portfolio data found for selected period. Try running 'Daily Update' or check your date range.")
        else:
            st.error(f"API Error: {portfolio_history_response.status_code}")
    
    except Exception as e:
        st.error(f"Error loading trends: {str(e)}")

# ==================== TAB 4: Portfolio Snapshot ====================
with tab4:
    st.subheader("📸 Securities Portfolio Snapshot")
    
    snapshot_date = st.date_input(
        "Snapshot Date",
        value=date.today(),
        key="portfolio_snapshot_date"
    )
    
    try:
        response = requests.get(
            f"{API_URL}/portfolio/{portfolio_id}/snapshot",
            params={"snapshot_date": snapshot_date}
        )
        
        if response.status_code == 200:
            snapshot = response.json()
            
            if snapshot:
                total_value = sum(item["value_huf"] for item in snapshot)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Portfolio Value", f"{total_value:,.0f} HUF")
                
                with col2:
                    st.metric("Instruments", len(snapshot))
                
                df = pd.DataFrame(snapshot)
                
                df_display = df.copy()
                df_display['quantity'] = df_display['quantity'].apply(lambda x: f"{x:,.2f}")
                df_display['price'] = df_display['price'].apply(lambda x: f"{x:,.4f}")
                df_display['value_huf'] = df_display['value_huf'].apply(lambda x: f"{x:,.2f}")
                
                df_display = df_display[[
                    'name', 'instrument_type', 'quantity', 'price', 
                    'currency', 'value_huf', 'price_source'
                ]]
                df_display.columns = [
                    'Instrument', 'Type', 'Quantity', 'Price', 
                    'Currency', 'Value (HUF)', 'Source'
                ]
                
                st.dataframe(df_display, use_container_width=True, hide_index=True)
            else:
                st.warning("No portfolio data for selected date")
        else:
            st.error(f"API Error: {response.status_code}")
    
    except Exception as e:
        st.error(f"Error: {str(e)}")

# ==================== TAB 5: Portfolio Management ====================
with tab5:
    st.subheader("🔧 Portfolio Management")
    
    # Sub-tabs for different management functions
    mgmt_tab1, mgmt_tab2, mgmt_tab3 = st.tabs([
        "💼 Transactions",
        "💲 Price Overrides",
        "➕ Add Instrument"
    ])
    
    # ============ TRANSACTIONS SUB-TAB ============
    with mgmt_tab1:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### ➕ Add New Transaction")
            
            with st.form("transaction_form"):
                # Get instruments for dropdown
                try:
                    instruments_response = requests.get(f"{API_URL}/instruments")
                    if instruments_response.status_code == 200:
                        instruments = instruments_response.json()
                        instrument_options = {f"{inst['name']} ({inst['isin']})": inst['id'] 
                                             for inst in instruments}
                        
                        selected_instrument = st.selectbox(
                            "Instrument",
                            options=list(instrument_options.keys()),
                            key="tx_instrument"
                        )
                        
                        transaction_type = st.selectbox(
                            "Transaction Type",
                            options=["BUY", "SELL", "ADJUST"],
                            key="tx_type",
                            help="BUY: Add to position, SELL: Reduce position, ADJUST: Set exact quantity"
                        )
                        
                        transaction_date = st.date_input(
                            "Transaction Date",
                            value=date.today(),
                            key="tx_date"
                        )
                        
                        col_qty, col_price = st.columns(2)
                        
                        with col_qty:
                            quantity = st.number_input(
                                "Quantity",
                                min_value=0.01,
                                value=1.0,
                                step=0.01,
                                key="tx_quantity"
                            )
                        
                        with col_price:
                            price = st.number_input(
                                "Price (optional)",
                                min_value=0.0,
                                value=0.0,
                                step=0.01,
                                key="tx_price",
                                help="Leave at 0 to use market price"
                            )
                        
                        notes = st.text_area(
                            "Notes (optional)",
                            key="tx_notes"
                        )
                        
                        created_by = st.text_input(
                            "Created By",
                            value="admin",
                            key="tx_created_by"
                        )
                        
                        submitted = st.form_submit_button("💾 Submit Transaction", use_container_width=True)
                        
                        if submitted:
                            try:
                                instrument_id = instrument_options[selected_instrument]
                                
                                payload = {
                                    "portfolio_id": portfolio_id,
                                    "instrument_id": instrument_id,
                                    "transaction_date": transaction_date.isoformat(),
                                    "transaction_type": transaction_type,
                                    "quantity": float(quantity),
                                    "price": float(price) if price > 0 else None,
                                    "notes": notes if notes else None,
                                    "created_by": created_by
                                }
                                
                                response = requests.post(f"{API_URL}/transactions", json=payload)
                                
                                if response.status_code == 200:
                                    st.success("✅ Transaction added successfully!")
                                    st.json(response.json())
                                else:
                                    st.error(f"❌ Error: {response.text}")
                            
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
                    
                    else:
                        st.error("Failed to load instruments")
                
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        with col2:
            st.markdown("#### 📋 Transaction History")
            
            col_date1, col_date2 = st.columns(2)
            
            with col_date1:
                tx_start_date = st.date_input(
                    "From",
                    value=date.today() - timedelta(days=30),
                    key="tx_start"
                )
            
            with col_date2:
                tx_end_date = st.date_input(
                    "To",
                    value=date.today(),
                    key="tx_end"
                )
            
            if st.button("🔍 Load Transactions", key="load_transactions"):
                try:
                    response = requests.get(
                        f"{API_URL}/transactions/{portfolio_id}",
                        params={
                            "start_date": tx_start_date.isoformat(),
                            "end_date": tx_end_date.isoformat()
                        }
                    )
                    
                    if response.status_code == 200:
                        transactions = response.json()
                        
                        if transactions:
                            df_tx = pd.DataFrame(transactions)
                            
                            # Format for display
                            df_tx_display = df_tx[[
                                'transaction_date', 'transaction_type', 'instrument_name',
                                'quantity', 'price', 'notes', 'created_by'
                            ]].copy()
                            
                            df_tx_display.columns = [
                                'Date', 'Type', 'Instrument', 'Quantity', 'Price', 'Notes', 'By'
                            ]
                            
                            st.dataframe(df_tx_display, use_container_width=True, hide_index=True)
                            st.info(f"📊 Total transactions: {len(transactions)}")
                        else:
                            st.info("No transactions found for selected period")
                    else:
                        st.error(f"API Error: {response.status_code}")
                
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    # ============ PRICE OVERRIDES SUB-TAB ============
    with mgmt_tab2:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### ➕ Add Price Override")
            
            with st.form("price_override_form"):
                try:
                    instruments_response = requests.get(f"{API_URL}/instruments")
                    if instruments_response.status_code == 200:
                        instruments = instruments_response.json()
                        instrument_options = {f"{inst['name']} ({inst['isin']})": inst['id'] 
                                             for inst in instruments}
                        
                        selected_instrument_price = st.selectbox(
                            "Instrument",
                            options=list(instrument_options.keys()),
                            key="price_instrument"
                        )
                        
                        override_date = st.date_input(
                            "Override Date",
                            value=date.today(),
                            key="price_date"
                        )
                        
                        col_price, col_currency = st.columns(2)
                        
                        with col_price:
                            override_price = st.number_input(
                                "Price",
                                min_value=0.01,
                                value=100.0,
                                step=0.01,
                                key="override_price"
                            )
                        
                        with col_currency:
                            currency = st.selectbox(
                                "Currency",
                                options=["HUF", "USD", "EUR", "GBP", "CHF"],
                                key="price_currency"
                            )
                        
                        reason = st.text_area(
                            "Reason",
                            placeholder="Why is this override needed?",
                            key="price_reason"
                        )
                        
                        created_by_price = st.text_input(
                            "Created By",
                            value="admin",
                            key="price_created_by"
                        )
                        
                        submitted_price = st.form_submit_button("💾 Set Price Override", use_container_width=True)
                        
                        if submitted_price:
                            try:
                                instrument_id = instrument_options[selected_instrument_price]
                                
                                payload = {
                                    "instrument_id": instrument_id,
                                    "override_date": override_date.isoformat(),
                                    "price": float(override_price),
                                    "currency": currency,
                                    "reason": reason if reason else None,
                                    "created_by": created_by_price
                                }
                                
                                response = requests.post(f"{API_URL}/prices/manual", json=payload)
                                
                                if response.status_code == 200:
                                    st.success("✅ Price override added successfully!")
                                    st.json(response.json())
                                else:
                                    st.error(f"❌ Error: {response.text}")
                            
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
                    
                    else:
                        st.error("Failed to load instruments")
                
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        with col2:
            st.markdown("#### 📋 Active Price Overrides")
            
            if st.button("🔄 Load Overrides", key="load_overrides"):
                try:
                    response = requests.get(f"{API_URL}/prices/manual")
                    
                    if response.status_code == 200:
                        overrides = response.json()
                        
                        if overrides:
                            df_overrides = pd.DataFrame(overrides)
                            
                            df_overrides_display = df_overrides[[
                                'override_date', 'instrument_name', 'price', 
                                'currency', 'reason', 'created_by'
                            ]].copy()
                            
                            df_overrides_display.columns = [
                                'Date', 'Instrument', 'Price', 'Currency', 'Reason', 'By'
                            ]
                            
                            st.dataframe(df_overrides_display, use_container_width=True, hide_index=True)
                            st.info(f"📊 Total overrides: {len(overrides)}")
                        else:
                            st.info("No price overrides found")
                    else:
                        st.error(f"API Error: {response.status_code}")
                
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    # ============ ADD INSTRUMENT SUB-TAB ============
    with mgmt_tab3:
        st.markdown("#### ➕ Add New Instrument")
        
        with st.form("add_instrument_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                inst_name = st.text_input("Instrument Name", key="inst_name")
                inst_type = st.selectbox(
                    "Type",
                    options=["EQUITY", "FUND", "BOND", "CASH", "OTHER"],
                    key="inst_type"
                )
                inst_isin = st.text_input("ISIN", key="inst_isin")
            
            with col2:
                inst_currency = st.selectbox(
                    "Currency",
                    options=["HUF", "USD", "EUR", "GBP", "CHF"],
                    key="inst_currency"
                )
                inst_ticker = st.text_input("Ticker Symbol (optional)", key="inst_ticker")
                inst_exchange = st.text_input("Exchange (optional)", key="inst_exchange")
            
            inst_notes = st.text_area("Notes (optional)", key="inst_notes")
            
            submitted_inst = st.form_submit_button("💾 Add Instrument", use_container_width=True)
            
            if submitted_inst:
                if inst_name and inst_isin:
                    try:
                        payload = {
                            "name": inst_name,
                            "instrument_type": inst_type,
                            "isin": inst_isin,
                            "ticker": inst_ticker if inst_ticker else None,
                            "currency": inst_currency,
                            "exchange": inst_exchange if inst_exchange else None,
                            "notes": inst_notes if inst_notes else None
                        }
                        
                        response = requests.post(f"{API_URL}/instruments", json=payload)
                        
                        if response.status_code == 200:
                            st.success("✅ Instrument added successfully!")
                            st.json(response.json())
                        else:
                            st.error(f"❌ Error: {response.text}")
                    
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                else:
                    st.error("Name and ISIN are required")
        
        # List existing instruments
        st.markdown("---")
        st.markdown("#### 📋 Existing Instruments")
        
        if st.button("🔄 Load Instruments", key="load_instruments_list"):
            try:
                response = requests.get(f"{API_URL}/instruments")
                
                if response.status_code == 200:
                    instruments = response.json()
                    
                    if instruments:
                        df_inst = pd.DataFrame(instruments)
                        
                        df_inst_display = df_inst[[
                            'name', 'instrument_type', 'isin', 'ticker', 
                            'currency', 'exchange'
                        ]].copy()
                        
                        df_inst_display.columns = [
                            'Name', 'Type', 'ISIN', 'Ticker', 'Currency', 'Exchange'
                        ]
                        
                        st.dataframe(df_inst_display, use_container_width=True, hide_index=True)
                        st.info(f"📊 Total instruments: {len(instruments)}")
                    else:
                        st.info("No instruments found")
                else:
                    st.error(f"API Error: {response.status_code}")
            
            except Exception as e:
                st.error(f"Error: {str(e)}")

# ==================== TAB 6: Analytical Data ====================
with tab6:
    st.subheader("📋 Analytical Data - Detailed Time Series")
    
    st.info("📊 **View portfolio and wealth data with daily granularity** - Download for Excel analysis")
    
    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
    
    with col1:
        analytics_start = st.date_input(
            "Start Date",
            value=date.today() - timedelta(days=90),
            key="analytics_start"
        )
    
    with col2:
        analytics_end = st.date_input(
            "End Date",
            value=date.today(),
            key="analytics_end"
        )
    
    with col3:
        granularity = st.selectbox(
            "Granularity",
            options=["Daily", "Monthly"],
            key="granularity"
        )
    
    with col4:
        st.write("")
        st.write("")
        if st.button("📊 Load Data", key="load_analytics", use_container_width=True):
            st.rerun()
    
    try:
        # Get daily portfolio values
        portfolio_response = requests.get(
            f"{API_URL}/portfolio/{portfolio_id}/history",
            params={
                "start_date": analytics_start.isoformat(),
                "end_date": analytics_end.isoformat()
            }
        )
        
        if portfolio_response.status_code == 200:
            portfolio_data = portfolio_response.json()
            
            if portfolio_data:
                # Create detailed dataframe
                df_portfolio_detail = pd.DataFrame(portfolio_data)
                df_portfolio_detail['date'] = pd.to_datetime(df_portfolio_detail['date'])
                
                # Rename 'name' to 'instrument_name' for consistency
                if 'name' in df_portfolio_detail.columns:
                    df_portfolio_detail.rename(columns={'name': 'instrument_name'}, inplace=True)
                
                # Aggregate by date and instrument
                df_daily = df_portfolio_detail.groupby(['date', 'instrument_name', 'instrument_type']).agg({
                    'quantity': 'sum',
                    'price': 'mean',
                    'value_huf': 'sum'
                }).reset_index()
                
                # Total portfolio by date
                df_portfolio_total = df_portfolio_detail.groupby('date').agg({
                    'value_huf': 'sum'
                }).reset_index()
                df_portfolio_total.columns = ['Date', 'Portfolio Total (HUF)']
                
                # Get wealth snapshots
                wealth_response = requests.get(
                    f"{API_URL}/wealth/snapshots",
                    params={
                        "start_date": analytics_start.isoformat(),
                        "end_date": analytics_end.isoformat()
                    }
                )
                
                wealth_df = None
                if wealth_response.status_code == 200:
                    wealth_snapshots = wealth_response.json()
                    if wealth_snapshots:
                        wealth_df = pd.DataFrame(wealth_snapshots)
                        wealth_df['snapshot_date'] = pd.to_datetime(wealth_df['snapshot_date'])
                        wealth_df = wealth_df.rename(columns={'snapshot_date': 'Date'})
                
                # Merge portfolio and wealth
                if wealth_df is not None:
                    df_combined_analytics = pd.merge(
                        df_portfolio_total,
                        wealth_df[[col for col in ['Date', 'cash_huf', 'property_huf', 'pension_huf', 'other_huf', 'loans_huf', 'net_wealth_huf'] if col in wealth_df.columns]],
                        on='Date',
                        how='outer'
                    )
                else:
                    df_combined_analytics = df_portfolio_total.copy()
                
                df_combined_analytics = df_combined_analytics.sort_values('Date')
                
                # If monthly granularity, resample
                if granularity == "Monthly":
                    df_combined_analytics.set_index('Date', inplace=True)
                    df_combined_analytics = df_combined_analytics.resample('ME').last()
                    df_combined_analytics.reset_index(inplace=True)
                    
                    # Also aggregate daily detail to monthly
                    df_daily['date'] = pd.to_datetime(df_daily['date'])
                    df_daily.set_index('date', inplace=True)
                    df_daily_monthly = df_daily.groupby([pd.Grouper(freq='ME'), 'instrument_name', 'instrument_type']).agg({
                        'quantity': 'last',
                        'price': 'last',
                        'value_huf': 'last'
                    }).reset_index()
                    df_daily = df_daily_monthly
                    df_daily.rename(columns={'date': 'Date'}, inplace=True)
                else:
                    df_daily.rename(columns={'date': 'Date'}, inplace=True)
                
                # Display summary metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Date Range",
                        f"{len(df_combined_analytics)} points"
                    )
                
                with col2:
                    st.metric(
                        "Instruments Tracked",
                        df_daily['instrument_name'].nunique()
                    )
                
                with col3:
                    st.metric(
                        "Granularity",
                        granularity
                    )
                
                st.markdown("---")
                
                # Section 1: Portfolio Summary Over Time
                st.markdown("### 📊 Portfolio Summary Over Time")
                
                # Transpose: dates in columns, elements in rows
                df_combined_display = df_combined_analytics.copy()
                df_combined_display['Date'] = df_combined_display['Date'].dt.strftime('%Y-%m-%d')
                
                # Set Date as index and transpose
                df_combined_display = df_combined_display.set_index('Date').T
                
                # Reset index to make element names a column
                df_combined_display = df_combined_display.reset_index()
                df_combined_display.columns.name = None
                df_combined_display.rename(columns={'index': 'Metric'}, inplace=True)
                
                # Format metric names for better readability
                metric_names = {
                    'Portfolio Total (HUF)': 'Portfolio Total',
                    'cash_huf': 'Cash',
                    'property_huf': 'Property',
                    'pension_huf': 'Pension',
                    'other_huf': 'Other Assets',
                    'loans_huf': 'Loans',
                    'net_wealth_huf': 'Net Wealth'
                }
                df_combined_display['Metric'] = df_combined_display['Metric'].map(lambda x: metric_names.get(x, x))
                
                # Format numbers in all date columns
                for col in df_combined_display.columns:
                    if col != 'Metric':
                        df_combined_display[col] = df_combined_display[col].apply(lambda x: f"{x:,.0f}" if pd.notna(x) and str(x).replace('.','').replace('-','').isdigit() else x)
                
                st.dataframe(df_combined_display, use_container_width=True, hide_index=True)
                
                # Download button for summary
                csv_summary = df_combined_analytics.to_csv(index=False)
                st.download_button(
                    label="📥 Download Summary CSV",
                    data=csv_summary,
                    file_name=f"wealth_summary_{analytics_start}_{analytics_end}_{granularity.lower()}.csv",
                    mime="text/csv",
                    key="download_summary"
                )
                
                st.markdown("---")
                
                # Section 2: Portfolio Detail (by Instrument)
                st.markdown("### 🔍 Portfolio Detail by Instrument")
                
                # Pivot table: dates in columns, instruments in rows
                df_pivot = df_daily.pivot_table(
                    index='instrument_name',
                    columns='Date',
                    values='value_huf',
                    aggfunc='sum'
                ).reset_index()
                
                df_pivot_display = df_pivot.copy()
                
                # Rename first column
                df_pivot_display.rename(columns={'instrument_name': 'Instrument'}, inplace=True)
                
                # Format date columns
                df_pivot_display.columns = [
                    col.strftime('%Y-%m-%d') if isinstance(col, pd.Timestamp) else col 
                    for col in df_pivot_display.columns
                ]
                
                # Format numbers in all date columns
                for col in df_pivot_display.columns:
                    if col != 'Instrument':
                        df_pivot_display[col] = df_pivot_display[col].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "")
                
                st.dataframe(df_pivot_display, use_container_width=True, hide_index=True)
                
                # Download button for detail
                csv_detail = df_daily.to_csv(index=False)
                st.download_button(
                    label="📥 Download Detail CSV",
                    data=csv_detail,
                    file_name=f"portfolio_detail_{analytics_start}_{analytics_end}_{granularity.lower()}.csv",
                    mime="text/csv",
                    key="download_detail"
                )
                
                st.markdown("---")
                
                # Section 3: Instrument Breakdown Table
                st.markdown("### 📈 Instrument Breakdown (Latest)")
                
                latest_date = df_daily['Date'].max()
                df_latest = df_daily[df_daily['Date'] == latest_date].copy()
                df_latest = df_latest.sort_values('value_huf', ascending=False)
                
                df_latest_display = df_latest[['instrument_name', 'instrument_type', 'quantity', 'price', 'value_huf']].copy()
                df_latest_display['quantity'] = df_latest_display['quantity'].apply(lambda x: f"{x:,.2f}")
                df_latest_display['price'] = df_latest_display['price'].apply(lambda x: f"{x:,.4f}")
                df_latest_display['value_huf'] = df_latest_display['value_huf'].apply(lambda x: f"{x:,.0f}")
                df_latest_display.columns = ['Instrument', 'Type', 'Quantity', 'Price', 'Value (HUF)']
                
                st.dataframe(df_latest_display, use_container_width=True, hide_index=True)
                
            else:
                st.warning("No portfolio data found for selected period")
        else:
            st.error(f"API Error: {portfolio_response.status_code}")
    
    except Exception as e:
        st.error(f"Error loading analytical data: {str(e)}")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### 💰 Wealth Tracking")
st.sidebar.markdown("- ✅ Total wealth calculation")
st.sidebar.markdown("- ✅ Monthly value tracking")
st.sidebar.markdown("- ✅ Multi-currency support")
st.sidebar.markdown("- ✅ YoY analysis")
st.sidebar.markdown("---")
st.sidebar.markdown("**Last Updated**: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
