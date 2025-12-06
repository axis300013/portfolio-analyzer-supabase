from datetime import date, datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_
from ..db import SessionLocal
from ..models import Portfolio, Holding, Instrument, Price, FxRate, PortfolioValueDaily, ManualPrice

def get_latest_price(instrument_id: int, price_date: date, db: Session) -> Decimal:
    """Get latest price for instrument on or before date
    
    Priority order:
    1. Manual price overrides (highest priority)
    2. Non-test prices (real data from APIs)
    3. Test data (fallback)
    """
    # First priority: Check for manual price override
    manual_price = db.query(ManualPrice).filter(
        and_(
            ManualPrice.instrument_id == instrument_id,
            ManualPrice.override_date <= price_date
        )
    ).order_by(ManualPrice.override_date.desc()).first()
    
    if manual_price:
        return manual_price.price
    
    # Second priority: Try to get non-test prices (API data)
    price = db.query(Price).filter(
        and_(
            Price.instrument_id == instrument_id,
            Price.price_date <= price_date,
            Price.source != 'test'
        )
    ).order_by(Price.price_date.desc()).first()
    
    if price:
        return price.price
    
    # Third priority: Fall back to test data
    price = db.query(Price).filter(
        and_(
            Price.instrument_id == instrument_id,
            Price.price_date <= price_date
        )
    ).order_by(Price.price_date.desc()).first()
    
    return price.price if price else None

def get_fx_rate(currency: str, target_currency: str, rate_date: date, db: Session) -> Decimal:
    """Get FX rate for date"""
    if currency == target_currency:
        return Decimal('1.0')
    
    fx = db.query(FxRate).filter(
        and_(
            FxRate.base_currency == currency,
            FxRate.target_currency == target_currency,
            FxRate.rate_date <= rate_date
        )
    ).order_by(FxRate.rate_date.desc()).first()
    
    return fx.rate if fx else None

def calculate_portfolio_values(portfolio_id: int, snapshot_date: date, db: Session):
    """Calculate and store portfolio values for a date"""
    holdings = db.query(Holding).filter(
        Holding.portfolio_id == portfolio_id
    ).all()
    
    calculated = 0
    for holding in holdings:
        instrument = holding.instrument
        
        # Get price
        price = get_latest_price(instrument.id, snapshot_date, db)
        if not price:
            print(f"⚠ No price for {instrument.name}")
            continue
        
        # Get FX rate
        fx_rate = get_fx_rate(instrument.currency, 'HUF', snapshot_date, db)
        if not fx_rate:
            print(f"⚠ No FX rate for {instrument.currency}")
            continue
        
        # Calculate value
        value_huf = Decimal(holding.quantity) * price * fx_rate
        
        # Check if record already exists
        existing = db.query(PortfolioValueDaily).filter(
            PortfolioValueDaily.portfolio_id == portfolio_id,
            PortfolioValueDaily.snapshot_date == snapshot_date,
            PortfolioValueDaily.instrument_id == instrument.id
        ).first()
        
        if existing:
            # Update existing record
            existing.quantity = holding.quantity
            existing.price = price
            existing.fx_rate = fx_rate
            existing.value_huf = value_huf
            existing.calculated_at = datetime.now()
        else:
            # Create new record
            value_record = PortfolioValueDaily(
                portfolio_id=portfolio_id,
                snapshot_date=snapshot_date,
                instrument_id=instrument.id,
                quantity=holding.quantity,
                price=price,
                instrument_currency=instrument.currency,
                fx_rate=fx_rate,
                value_huf=value_huf
            )
            db.add(value_record)
        
        calculated += 1
    
    db.commit()
    print(f"✓ Calculated values for {calculated} holdings")

def run_calculate_values():
    """Calculate values for all portfolios"""
    db = SessionLocal()
    try:
        today = date.today()
        portfolios = db.query(Portfolio).all()
        
        for portfolio in portfolios:
            print(f"\nCalculating values for '{portfolio.name}'...")
            calculate_portfolio_values(portfolio.id, today, db)
            
    finally:
        db.close()

if __name__ == "__main__":
    run_calculate_values()
