"""
Test data persistence and historical data availability
"""
from backend.app.db import SessionLocal
from backend.app.models import PortfolioValueDaily, Price, FxRate
from datetime import date

db = SessionLocal()

print('\n' + '='*80)
print('  DATA PERSISTENCE CHECK'.center(80))
print('='*80 + '\n')

# Count records
pv_count = db.query(PortfolioValueDaily).count()
price_count = db.query(Price).count()
fx_count = db.query(FxRate).count()

print(f'Portfolio Values: {pv_count} records')
print(f'Prices: {price_count} records')
print(f'FX Rates: {fx_count} records')

print('\n' + '-'*80)
print('SAMPLE HISTORICAL DATA')
print('-'*80 + '\n')

# Get latest portfolio value
latest_pv = db.query(PortfolioValueDaily).order_by(
    PortfolioValueDaily.snapshot_date.desc()
).first()

if latest_pv:
    print(f'Latest portfolio value: {latest_pv.snapshot_date} = {latest_pv.value_huf:,.2f} HUF')

# Get dates with data
dates = db.query(PortfolioValueDaily.snapshot_date).distinct().order_by(
    PortfolioValueDaily.snapshot_date.desc()
).limit(10).all()

print(f'\nDates with portfolio data:')
for d in dates:
    count = db.query(PortfolioValueDaily).filter(
        PortfolioValueDaily.snapshot_date == d[0]
    ).count()
    total = db.query(PortfolioValueDaily.value_huf).filter(
        PortfolioValueDaily.snapshot_date == d[0]
    ).all()
    total_value = sum(float(v[0]) for v in total)
    print(f'  {d[0]}: {count} instruments = {total_value:,.2f} HUF')

# Check price history
print('\n' + '-'*80)
print('PRICE HISTORY SAMPLE (Latest 5 records)')
print('-'*80 + '\n')

prices = db.query(Price).join(Price.instrument).order_by(
    Price.price_date.desc(), 
    Price.retrieved_at.desc()
).limit(5).all()

for p in prices:
    print(f'{p.price_date} | {p.instrument.name[:40]:40} | {p.price:>12.4f} {p.currency} ({p.source})')

print('\n' + '='*80 + '\n')

db.close()
