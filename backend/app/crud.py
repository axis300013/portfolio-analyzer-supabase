from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func
from datetime import date, datetime
from . import models
from typing import List, Optional

def get_portfolio_snapshot(db: Session, portfolio_id: int, snapshot_date: date):
    """Get portfolio snapshot for a date"""
    return db.query(models.PortfolioValueDaily).filter(
        and_(
            models.PortfolioValueDaily.portfolio_id == portfolio_id,
            models.PortfolioValueDaily.snapshot_date == snapshot_date
        )
    ).all()

def get_portfolio_summary(db: Session, portfolio_id: int, snapshot_date: date):
    """Get aggregated portfolio summary"""
    
    result = db.query(
        func.sum(models.PortfolioValueDaily.value_huf).label('total_value_huf'),
        func.count(models.PortfolioValueDaily.id).label('instrument_count')
    ).filter(
        and_(
            models.PortfolioValueDaily.portfolio_id == portfolio_id,
            models.PortfolioValueDaily.snapshot_date == snapshot_date
        )
    ).first()
    
    return result

# ===== PORTFOLIO MANAGEMENT FUNCTIONS =====

def add_transaction(
    db: Session, 
    portfolio_id: int, 
    instrument_id: int, 
    transaction_date: date,
    transaction_type: str,
    quantity: float,
    price: Optional[float] = None,
    notes: Optional[str] = None,
    created_by: Optional[str] = None
) -> models.Transaction:
    """Add a new transaction (BUY, SELL, ADJUST)"""
    transaction = models.Transaction(
        portfolio_id=portfolio_id,
        instrument_id=instrument_id,
        transaction_date=transaction_date,
        transaction_type=transaction_type.upper(),
        quantity=quantity,
        price=price,
        notes=notes,
        created_by=created_by
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction

def get_transactions(
    db: Session, 
    portfolio_id: int, 
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    instrument_id: Optional[int] = None
) -> List[models.Transaction]:
    """Get transaction history with optional filters"""
    query = db.query(models.Transaction).filter(
        models.Transaction.portfolio_id == portfolio_id
    )
    
    if start_date:
        query = query.filter(models.Transaction.transaction_date >= start_date)
    if end_date:
        query = query.filter(models.Transaction.transaction_date <= end_date)
    if instrument_id:
        query = query.filter(models.Transaction.instrument_id == instrument_id)
    
    return query.order_by(desc(models.Transaction.transaction_date)).all()

def add_manual_price(
    db: Session,
    instrument_id: int,
    override_date: date,
    price: float,
    currency: str,
    reason: Optional[str] = None,
    created_by: Optional[str] = None
) -> models.ManualPrice:
    """Add or update manual price override"""
    # Check if override already exists
    existing = db.query(models.ManualPrice).filter(
        and_(
            models.ManualPrice.instrument_id == instrument_id,
            models.ManualPrice.override_date == override_date
        )
    ).first()
    
    if existing:
        existing.price = price
        existing.currency = currency
        existing.reason = reason
        existing.created_by = created_by
        existing.created_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return existing
    else:
        manual_price = models.ManualPrice(
            instrument_id=instrument_id,
            override_date=override_date,
            price=price,
            currency=currency,
            reason=reason,
            created_by=created_by
        )
        db.add(manual_price)
        db.commit()
        db.refresh(manual_price)
        return manual_price

def get_manual_prices(
    db: Session,
    instrument_id: Optional[int] = None,
    override_date: Optional[date] = None
) -> List[models.ManualPrice]:
    """Get manual price overrides"""
    query = db.query(models.ManualPrice)
    
    if instrument_id:
        query = query.filter(models.ManualPrice.instrument_id == instrument_id)
    if override_date:
        query = query.filter(models.ManualPrice.override_date == override_date)
    
    return query.order_by(desc(models.ManualPrice.override_date)).all()

def add_new_instrument(
    db: Session,
    isin: str,
    name: str,
    currency: str,
    instrument_type: Optional[str] = None,
    ticker: Optional[str] = None,
    source: Optional[str] = None
) -> models.Instrument:
    """Add a new instrument to the database"""
    # Check if instrument already exists
    existing = db.query(models.Instrument).filter(
        models.Instrument.isin == isin
    ).first()
    
    if existing:
        raise ValueError(f"Instrument with ISIN {isin} already exists")
    
    instrument = models.Instrument(
        isin=isin,
        name=name,
        currency=currency,
        instrument_type=instrument_type,
        ticker=ticker,
        source=source
    )
    db.add(instrument)
    db.commit()
    db.refresh(instrument)
    return instrument

def get_all_instruments(db: Session) -> List[models.Instrument]:
    """Get all instruments"""
    return db.query(models.Instrument).order_by(models.Instrument.name).all()

def get_instrument_by_isin(db: Session, isin: str) -> Optional[models.Instrument]:
    """Get instrument by ISIN"""
    return db.query(models.Instrument).filter(
        models.Instrument.isin == isin
    ).first()
