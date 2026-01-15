import streamlit as st
import requests
import pandas as pd
from datetime import date, datetime, timedelta

st.set_page_config(page_title="Portfolio Analyzer", layout="wide")

# Configuration
API_URL = "http://localhost:8000"

st.title("📊 Portfolio Analyzer")

# Add refresh info at the top
st.info("🔄 Click 'Load Portfolio' to fetch the latest data with real-time prices")

# Sidebar
st.sidebar.header("Settings")
portfolio_id = st.sidebar.number_input("Portfolio ID", value=1, min_value=1)
snapshot_date = st.sidebar.date_input("Snapshot Date", value=date.today())

# Main content
col1, col2 = st.columns(2)

with col1:
    if st.button("🔄 Load Portfolio", type="primary"):
        try:
            # Get snapshot with cache-busting timestamp
            response = requests.get(
                f"{API_URL}/portfolio/{portfolio_id}/snapshot",
                params={"snapshot_date": snapshot_date.isoformat()},
                headers={"Cache-Control": "no-cache"}
            )
            response.raise_for_status()
            
            data = response.json()
            
            if data:
                df = pd.DataFrame(data)
                
                # Calculate total before formatting
                total = df['value_huf'].sum()
                
                # Show last update time
                st.success(f"✓ Loaded {len(df)} holdings at {datetime.now().strftime('%H:%M:%S')}")
                
                # Format numbers for display
                df['quantity'] = df['quantity'].apply(lambda x: f"{x:,.2f}")
                df['price'] = df['price'].apply(lambda x: f"{x:,.2f}")
                df['fx_rate'] = df['fx_rate'].apply(lambda x: f"{x:,.4f}")
                df['value_huf'] = df['value_huf'].apply(lambda x: f"{x:,.2f}")
                
                st.dataframe(df, use_container_width=True)
                
                # Display total
                st.metric("Total Portfolio Value", f"{total:,.2f} HUF")
                
            else:
                st.warning("No data available for this date")
                
        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to API: {e}")
        except Exception as e:
            st.error(f"Error: {e}")

with col2:
    if st.button("📈 Get Summary"):
        try:
            response = requests.get(
                f"{API_URL}/portfolio/{portfolio_id}/summary",
                params={"snapshot_date": snapshot_date.isoformat()}
            )
            response.raise_for_status()
            summary = response.json()
            
            st.metric("Total Value", f"{summary['total_value_huf']:,.2f} HUF")
            st.metric("Number of Instruments", summary['instrument_count'])
            
        except Exception as e:
            st.error(f"Error: {e}")

# Footer
st.sidebar.markdown("---")
st.sidebar.info("💡 Tip: Run ETL jobs to update prices and FX rates")
