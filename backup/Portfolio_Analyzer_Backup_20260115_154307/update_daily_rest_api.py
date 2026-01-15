"""
Daily ETL using Supabase REST API (HTTPS)
This bypasses PostgreSQL port 5432 blocks
"""
import os
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

# Load environment
load_dotenv()
# Don't set RAILWAY_ENVIRONMENT here - let it come from actual environment
# This allows Selenium fetchers to run on Desktop but skip on Railway

# Import existing ETL modules (these still rely on the DB engine)
from backend.app.etl.fetch_fx_mnb import run_fx_fetch
from backend.app.etl.fetch_prices import run_price_fetch
from backend.app.etl.calculate_values import run_calculate_values
from backend.app.etl.copy_wealth_values import run_copy_wealth
from backend.app.etl.fetch_wealth_automated import run_wealth_fetch
from backend.app.supabase_client import get_supabase_client


def create_total_wealth_snapshot_rest(snapshot_date):
    """Calculate and store total wealth snapshot using Supabase REST."""
    client = get_supabase_client()

    # Portfolio value
    portfolio_rows = client.get_portfolio_values_by_date(snapshot_date.isoformat()) or []
    portfolio_value_huf = sum(float(r.get("value_huf", 0)) for r in portfolio_rows)

    # Wealth values for the date
    wealth_values = client.get_wealth_values_by_date(snapshot_date.isoformat()) or []

    # FX cache
    fx_cache = {"HUF": 1.0}

    def fx_rate_for(currency: str):
        if currency in fx_cache:
            return fx_cache[currency]
        rec = client.get_fx_rate_on_or_before(currency, "HUF", snapshot_date.isoformat())
        rate = float(rec["rate"]) if rec else 1.0
        fx_cache[currency] = rate
        return rate

    total_assets_huf = 0.0
    total_liabilities_huf = 0.0
    breakdown = {"cash": 0.0, "property": 0.0, "pension": 0.0, "loans": 0.0, "other": 0.0}

    for wv in wealth_values:
        currency = wv.get("wealth_categories", {}).get("currency") or "HUF"
        is_liability = wv.get("wealth_categories", {}).get("is_liability") or False
        cat_type = wv.get("wealth_categories", {}).get("category_type") or "other"
        value_huf = float(wv.get("present_value", 0)) * fx_rate_for(currency)

        if is_liability:
            total_liabilities_huf += abs(value_huf)
            breakdown["loans"] += abs(value_huf)
        else:
            total_assets_huf += value_huf
            breakdown[cat_type] = breakdown.get(cat_type, 0.0) + value_huf

    other_assets_huf = total_assets_huf
    net_wealth_huf = portfolio_value_huf + total_assets_huf - total_liabilities_huf

    client.insert_wealth_snapshot(
        {
            "snapshot_date": snapshot_date.isoformat(),
            "portfolio_value_huf": portfolio_value_huf,
            "other_assets_huf": other_assets_huf,
            "total_liabilities_huf": total_liabilities_huf,
            "net_wealth_huf": net_wealth_huf,
            "cash_huf": breakdown.get("cash", 0.0),
            "property_huf": breakdown.get("property", 0.0),
            "pension_huf": breakdown.get("pension", 0.0),
            "other_huf": breakdown.get("other", 0.0),
        }
    )

    print(
        f"[ETL] Snapshot saved: {snapshot_date} - Net Wealth: {net_wealth_huf:,.0f} HUF"
    )


def run_daily_etl_via_rest_api():
    """Run daily ETL using the same steps as run_daily_etl, with a Supabase HTTPS client initialized."""

    print("🚀 Starting Daily ETL via Supabase REST API (HTTPS)")
    print("=" * 60)

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY/ANON_KEY must be set in .env")

    # Establish HTTPS client (REST) — keeps us off port 5432 for auxiliary calls
    create_client(url, key)

    print(f"Running Daily ETL - {datetime.now().date()}")
    print("Step 1: Fetching FX rates from MNB...")
    run_fx_fetch()

    print("\nStep 2: Fetching instrument prices...")
    run_price_fetch()

    print("\nStep 3: Calculating portfolio values...")
    run_calculate_values()

    print("\nStep 4: Copying static wealth values from previous day...")
    run_copy_wealth()

    print("\nStep 5: Fetching automated wealth values...")
    run_wealth_fetch()

    print("\nStep 6: Creating total wealth snapshot...")
    try:
        today = datetime.now().date()
        create_total_wealth_snapshot_rest(today)
    except Exception as e:
        print(f"[ETL] Error creating snapshot: {e}")

    print("\n" + "=" * 50)
    print("ETL Complete!")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    run_daily_etl_via_rest_api()
