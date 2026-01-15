"""
Portfolio Analyzer UI with Portfolio Management Features
"""
import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta, date

st.set_page_config(
    page_title="Portfolio Analyzer - Management",
    page_icon="📊",
    layout="wide"
)

API_URL = "http://localhost:8000"

# Custom CSS
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    .success-box {
        padding: 10px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        color: #155724;
    }
    .error-box {
        padding: 10px;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("📊 Portfolio Analyzer - Management Console")
st.markdown("Real-time portfolio tracking, transactions, and price management")

# Sidebar
st.sidebar.header("⚙️ Configuration")
portfolio_id = st.sidebar.number_input("Portfolio ID", value=1, min_value=1)

# Main tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📸 Current Snapshot", 
    "📈 Historical Trends", 
    "💼 Transactions",
    "💲 Price Overrides",
    "➕ Add Instrument",
    "📊 Analytics"
])

# ==================== TAB 1: Current Snapshot ====================
with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        snapshot_date = st.date_input(
            "Snapshot Date",
            value=date.today(),
            key="snapshot_date"
        )
    
    with col2:
        st.write("")
        st.write("")
        if st.button("🔄 Refresh Data", key="refresh_snapshot"):
            st.rerun()
    
    try:
        # Get snapshot
        response = requests.get(
            f"{API_URL}/portfolio/{portfolio_id}/snapshot",
            params={"snapshot_date": snapshot_date}
        )
        
        if response.status_code == 200:
            snapshot = response.json()
            
            if snapshot:
                # Calculate total
                total_value = sum(item["value_huf"] for item in snapshot)
                
                # Display metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Total Portfolio Value",
                        f"{total_value:,.0f} HUF",
                        delta=None
                    )
                
                with col2:
                    usd_value = total_value / 327.87  # Approximate USD rate
                    st.metric(
                        "USD Equivalent",
                        f"${usd_value:,.2f}"
                    )
                
                with col3:
                    st.metric(
                        "Instruments",
                        len(snapshot)
                    )
                
                st.markdown("---")
                
                # Holdings table
                st.subheader("Holdings Breakdown")
                
                df = pd.DataFrame(snapshot)
                
                # Format for display
                df_display = df.copy()
                df_display['quantity'] = df_display['quantity'].apply(lambda x: f"{x:,.2f}")
                df_display['price'] = df_display['price'].apply(lambda x: f"{x:,.4f}")
                df_display['value_huf'] = df_display['value_huf'].apply(lambda x: f"{x:,.2f}")
                df_display['fx_rate'] = df_display['fx_rate'].apply(lambda x: f"{x:,.4f}" if x != 1 else "-")
                
                # Reorder and rename columns
                df_display = df_display[[
                    'name', 'instrument_type', 'quantity', 'price', 
                    'currency', 'fx_rate', 'value_huf', 'price_source'
                ]]
                df_display.columns = [
                    'Instrument', 'Type', 'Quantity', 'Price', 
                    'Currency', 'FX Rate', 'Value (HUF)', 'Source'
                ]
                
                st.dataframe(df_display, use_container_width=True, hide_index=True)
                
                # Asset allocation pie chart
                st.subheader("Asset Allocation")
                
                fig_pie = px.pie(
                    df,
                    values='value_huf',
                    names='name',
                    title='Portfolio Composition by Value'
                )
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                
                st.plotly_chart(fig_pie, use_container_width=True)
                
            else:
                st.warning("No data available for selected date")
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
    
    except Exception as e:
        st.error(f"Error loading snapshot: {str(e)}")

# ==================== TAB 2: Historical Trends ====================
with tab2:
    st.subheader("📈 Historical Portfolio Performance")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=date.today() - timedelta(days=30),
            key="hist_start"
        )
    
    with col2:
        end_date = st.date_input(
            "End Date",
            value=date.today(),
            key="hist_end"
        )
    
    with col3:
        st.write("")
        st.write("")
        load_history = st.button("📊 Load Data", key="load_history")
    
    if load_history:
        try:
            response = requests.get(
                f"{API_URL}/portfolio/{portfolio_id}/history",
                params={
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data:
                    df = pd.DataFrame(data)
                    df['date'] = pd.to_datetime(df['date'])
                    
                    # Aggregate by date for total portfolio value
                    daily_totals = df.groupby('date').agg({
                        'value_huf': 'sum'
                    }).reset_index()
                    
                    # Calculate statistics
                    first_value = daily_totals['value_huf'].iloc[0]
                    last_value = daily_totals['value_huf'].iloc[-1]
                    change = last_value - first_value
                    change_pct = (change / first_value) * 100 if first_value != 0 else 0
                    
                    # Display metrics
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric(
                            "Current Value",
                            f"{last_value:,.0f} HUF"
                        )
                    
                    with col2:
                        st.metric(
                            "Period Change",
                            f"{change:+,.0f} HUF",
                            f"{change_pct:+.2f}%"
                        )
                    
                    st.markdown("---")
                    
                    # Line chart
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=daily_totals['date'],
                        y=daily_totals['value_huf'],
                        mode='lines+markers',
                        name='Portfolio Value',
                        line=dict(color='#1f77b4', width=3),
                        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Value: %{y:,.0f} HUF<extra></extra>'
                    ))
                    
                    fig.update_layout(
                        xaxis_title="Date",
                        yaxis_title="Value (HUF)",
                        hovermode='x unified',
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No historical data found")
            else:
                st.error(f"API Error: {response.status_code}")
        
        except Exception as e:
            st.error(f"Error loading history: {str(e)}")

# ==================== TAB 3: Transactions ====================
with tab3:
    st.subheader("💼 Transaction Management")
    
    # Two columns: Add transaction form and history
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
                        key="tx_type"
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
                            key="tx_price"
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
                            
                            response = requests.post(
                                f"{API_URL}/transactions",
                                json=payload
                            )
                            
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
                st.error(f"Error loading instruments: {str(e)}")
    
    with col2:
        st.markdown("#### 📋 Transaction History")
        
        # Filter options
        with st.expander("🔍 Filter Options"):
            col_start, col_end = st.columns(2)
            
            with col_start:
                filter_start = st.date_input(
                    "Start Date",
                    value=date.today() - timedelta(days=30),
                    key="tx_filter_start"
                )
            
            with col_end:
                filter_end = st.date_input(
                    "End Date",
                    value=date.today(),
                    key="tx_filter_end"
                )
        
        if st.button("🔄 Load Transactions", key="load_transactions"):
            try:
                params = {
                    "start_date": filter_start.isoformat(),
                    "end_date": filter_end.isoformat()
                }
                
                response = requests.get(
                    f"{API_URL}/transactions/{portfolio_id}",
                    params=params
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

# ==================== TAB 4: Price Overrides ====================
with tab4:
    st.subheader("💲 Manual Price Override Management")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### ➕ Add Price Override")
        
        with st.form("price_override_form"):
            # Get instruments
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
                            
                            response = requests.post(
                                f"{API_URL}/prices/manual",
                                json=payload
                            )
                            
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

# ==================== TAB 5: Add Instrument ====================
with tab5:
    st.subheader("➕ Add New Instrument")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.form("add_instrument_form"):
            st.markdown("#### New Instrument Details")
            
            isin = st.text_input(
                "ISIN *",
                placeholder="e.g., US0378331005",
                key="inst_isin"
            )
            
            name = st.text_input(
                "Name *",
                placeholder="e.g., Apple Inc.",
                key="inst_name"
            )
            
            col_curr, col_type = st.columns(2)
            
            with col_curr:
                inst_currency = st.selectbox(
                    "Currency *",
                    options=["HUF", "USD", "EUR", "GBP", "CHF"],
                    key="inst_currency"
                )
            
            with col_type:
                inst_type = st.selectbox(
                    "Type",
                    options=["", "EQUITY", "BOND", "FUND", "ETF", "OTHER"],
                    key="inst_type"
                )
            
            ticker = st.text_input(
                "Ticker (optional)",
                placeholder="e.g., AAPL",
                key="inst_ticker"
            )
            
            source = st.text_input(
                "Data Source (optional)",
                placeholder="e.g., Yahoo Finance",
                key="inst_source"
            )
            
            st.markdown("*Required fields")
            
            submitted_inst = st.form_submit_button("💾 Add Instrument", use_container_width=True)
            
            if submitted_inst:
                if not isin or not name:
                    st.error("❌ ISIN and Name are required!")
                else:
                    try:
                        payload = {
                            "isin": isin.upper(),
                            "name": name,
                            "currency": inst_currency,
                            "instrument_type": inst_type if inst_type else None,
                            "ticker": ticker if ticker else None,
                            "source": source if source else None
                        }
                        
                        response = requests.post(
                            f"{API_URL}/instruments",
                            json=payload
                        )
                        
                        if response.status_code == 200:
                            st.success("✅ Instrument added successfully!")
                            result = response.json()
                            st.json(result)
                            
                            st.info(f"Instrument ID: {result['id']}")
                        else:
                            st.error(f"❌ Error: {response.text}")
                    
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
    
    with col2:
        st.markdown("#### 📋 Current Instruments")
        
        if st.button("🔄 Load Instruments", key="load_all_instruments"):
            try:
                response = requests.get(f"{API_URL}/instruments")
                
                if response.status_code == 200:
                    instruments = response.json()
                    
                    st.metric("Total Instruments", len(instruments))
                    
                    with st.expander("View All Instruments"):
                        df_inst = pd.DataFrame(instruments)
                        df_inst_display = df_inst[['name', 'isin', 'instrument_type', 'currency']].copy()
                        df_inst_display.columns = ['Name', 'ISIN', 'Type', 'Currency']
                        
                        st.dataframe(df_inst_display, use_container_width=True, hide_index=True)
                else:
                    st.error(f"API Error: {response.status_code}")
            
            except Exception as e:
                st.error(f"Error: {str(e)}")

# ==================== TAB 6: Analytics ====================
with tab6:
    st.subheader("📊 Portfolio Analytics")
    st.info("Advanced analytics coming soon!")
    
    st.markdown("""
    **Planned Features:**
    - Transaction impact analysis
    - Price override effectiveness
    - Asset allocation trends
    - Performance attribution
    """)

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### 🛠️ Management Tools")
st.sidebar.markdown("- ✅ Transaction tracking")
st.sidebar.markdown("- ✅ Manual price overrides")
st.sidebar.markdown("- ✅ Instrument management")
st.sidebar.markdown("---")
st.sidebar.markdown("### 📋 Data Sources")
st.sidebar.markdown("- **Equities**: Yahoo Finance")
st.sidebar.markdown("- **Funds**: Erste Market")
st.sidebar.markdown("- **FX Rates**: ExchangeRate-API")
st.sidebar.markdown("---")
st.sidebar.markdown("**Last Updated**: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
