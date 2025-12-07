"""
Display detailed portfolio breakdown with all real prices
"""
from backend.app.db import SessionLocal
from backend.app.models import Price, Holding, FxRate
from datetime import date

db = SessionLocal()

holdings = db.query(Holding).filter(Holding.portfolio_id == 1).all()

print('\n' + '='*90)
print('  PORTFOLIO HOLDINGS SUMMARY - 2025-12-02 (ALL REAL PRICES)  '.center(90))
print('='*90 + '\n')

total_huf = 0

for h in holdings:
    price = db.query(Price).filter(
        Price.instrument_id == h.instrument_id,
        Price.price_date == date(2025, 12, 2),
        Price.source != 'test'
    ).order_by(Price.retrieved_at.desc()).first()
    
    if price:
        value_local = float(price.price) * float(h.quantity)
        fx = 1.0
        
        if price.currency != 'HUF':
            fx_rate = db.query(FxRate).filter(
                FxRate.base_currency == price.currency,
                FxRate.target_currency == 'HUF',
                FxRate.rate_date == date(2025, 12, 2)
            ).first()
            if fx_rate:
                fx = float(fx_rate.rate)
        
        value_huf = value_local * fx
        total_huf += value_huf
        
        print(f'{h.instrument.name[:50]:50} | {h.instrument.instrument_type.upper():6}')
        print(f'  ISIN: {h.instrument.isin:12} | Quantity: {h.quantity:>15,.0f}')
        print(f'  Price: {price.price:>12,.6f} {price.currency:3} | Source: {price.source}')
        if price.currency != 'HUF':
            print(f'  FX Rate: {fx:>10,.4f} {price.currency}/HUF')
        print(f'  Value: {value_huf:>18,.2f} HUF')
        print()

print('='*90)
print(f'{'TOTAL PORTFOLIO VALUE:':50} {total_huf:>18,.2f} HUF')
print(f'{'':50} ~${total_huf/327.87:>17,.2f} USD')
print('='*90 + '\n')

db.close()
