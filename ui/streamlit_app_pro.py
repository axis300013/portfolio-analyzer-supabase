"""
Enhanced Portfolio Analyzer UI with Historical Trends
"""
import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta, date

st.set_page_config(
    page_title="Portfolio Analyzer Pro",
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
</style>
""", unsafe_allow_html=True)

# Header
st.title("📊 Portfolio Analyzer Pro")
st.markdown("Real-time portfolio tracking with historical trends")

# Sidebar
st.sidebar.header("⚙️ Configuration")
portfolio_id = st.sidebar.number_input("Portfolio ID", value=1, min_value=1)

# Main tabs
tab1, tab2, tab3 = st.tabs(["📸 Current Snapshot", "📈 Historical Trends", "📊 Analytics"])

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
                    max_value = daily_totals['value_huf'].max()
                    min_value = daily_totals['value_huf'].min()
                    
                    # Display metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
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
                    
                    with col3:
                        st.metric(
                            "Peak Value",
                            f"{max_value:,.0f} HUF"
                        )
                    
                    with col4:
                        st.metric(
                            "Lowest Value",
                            f"{min_value:,.0f} HUF"
                        )
                    
                    st.markdown("---")
                    
                    # Line chart - Total Portfolio Value
                    st.subheader("Total Portfolio Value Over Time")
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=daily_totals['date'],
                        y=daily_totals['value_huf'],
                        mode='lines+markers',
                        name='Portfolio Value',
                        line=dict(color='#1f77b4', width=3),
                        marker=dict(size=8),
                        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Value: %{y:,.0f} HUF<extra></extra>'
                    ))
                    
                    fig.update_layout(
                        xaxis_title="Date",
                        yaxis_title="Value (HUF)",
                        hovermode='x unified',
                        height=500,
                        showlegend=True
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Individual instruments
                    st.markdown("---")
                    st.subheader("Performance by Instrument")
                    
                    instruments = sorted(df['name'].unique())
                    selected_instruments = st.multiselect(
                        "Select instruments to compare:",
                        instruments,
                        default=instruments[:min(3, len(instruments))],
                        key="instruments_select"
                    )
                    
                    if selected_instruments:
                        fig2 = go.Figure()
                        
                        for instrument in selected_instruments:
                            inst_data = df[df['name'] == instrument].sort_values('date')
                            fig2.add_trace(go.Scatter(
                                x=inst_data['date'],
                                y=inst_data['value_huf'],
                                mode='lines+markers',
                                name=instrument,
                                hovertemplate=f'<b>{instrument}</b><br>' +
                                             'Date: %{x|%Y-%m-%d}<br>' +
                                             'Value: %{y:,.0f} HUF<extra></extra>'
                            ))
                        
                        fig2.update_layout(
                            xaxis_title="Date",
                            yaxis_title="Value (HUF)",
                            hovermode='x unified',
                            height=500,
                            showlegend=True
                        )
                        
                        st.plotly_chart(fig2, use_container_width=True)
                    
                    # Data table
                    st.markdown("---")
                    st.subheader("Raw Data")
                    
                    with st.expander("📋 View/Download Data"):
                        # Format data for display
                        df_display = df.copy()
                        df_display['date'] = df_display['date'].dt.strftime('%Y-%m-%d')
                        df_display['quantity'] = df_display['quantity'].apply(lambda x: f"{x:,.2f}")
                        df_display['price'] = df_display['price'].apply(lambda x: f"{x:,.4f}")
                        df_display['value_huf'] = df_display['value_huf'].apply(lambda x: f"{x:,.2f}")
                        
                        st.dataframe(df_display, use_container_width=True, hide_index=True)
                        
                        # Download button
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download CSV",
                            data=csv,
                            file_name=f"portfolio_history_{start_date}_{end_date}.csv",
                            mime="text/csv"
                        )
                else:
                    st.warning("No historical data found for selected date range")
            else:
                st.error(f"API Error: {response.status_code} - {response.text}")
        
        except Exception as e:
            st.error(f"Error loading history: {str(e)}")

# ==================== TAB 3: Analytics ====================
with tab3:
    st.subheader("📊 Portfolio Analytics")
    st.info("Advanced analytics coming soon!")
    
    st.markdown("""
    **Planned Features:**
    - Asset allocation trends
    - Risk metrics
    - Performance attribution
    - Correlation analysis
    - Sector exposure
    """)

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### 📋 Data Sources")
st.sidebar.markdown("- **Equities**: Yahoo Finance")
st.sidebar.markdown("- **Funds**: Erste Market")
st.sidebar.markdown("- **FX Rates**: ExchangeRate-API")
st.sidebar.markdown("- **Last Updated**: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
