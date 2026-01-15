"""
CRUD operations for wealth management
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import date, datetime
from typing import List, Optional
from decimal import Decimal
from . import models

# ==================== WEALTH CATEGORY OPERATIONS ====================

def get_wealth_categories(db: Session, category_type: Optional[str] = None) -> List[models.WealthCategory]:
    """Get all wealth categories, optionally filtered by type"""
    query = db.query(models.WealthCategory)
    if category_type:
        query = query.filter(models.WealthCategory.category_type == category_type)
    return query.order_by(models.WealthCategory.category_type, models.WealthCategory.name).all()


def add_wealth_category(
    db: Session,
    category_type: str,
    name: str,
    currency: str,
    is_liability: bool = False
) -> models.WealthCategory:
    """Add a new wealth category"""
    category = models.WealthCategory(
        category_type=category_type,
        name=name,
        currency=currency,
        is_liability=is_liability
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def update_wealth_category(
    db: Session,
    category_id: int,
    **kwargs
) -> models.WealthCategory:
    """Update a wealth category"""
    category = db.query(models.WealthCategory).filter(
        models.WealthCategory.id == category_id
    ).first()
    
    if not category:
        raise ValueError(f"Wealth category {category_id} not found")
    
    for key, value in kwargs.items():
        if hasattr(category, key) and key not in ['id', 'created_at']:
            setattr(category, key, value)
    
    category.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(category)
    return category


def delete_wealth_category(db: Session, category_id: int) -> bool:
    """Delete a wealth category and all its values"""
    category = db.query(models.WealthCategory).filter(
        models.WealthCategory.id == category_id
    ).first()
    
    if not category:
        return False
    
    db.delete(category)
    db.commit()
    return True


# ==================== WEALTH VALUE OPERATIONS ====================

def add_or_update_wealth_value(
    db: Session,
    wealth_category_id: int,
    value_date: date,
    present_value: float,
    note: Optional[str] = None
) -> models.WealthValue:
    """Add or update wealth value for a specific date"""
    
    # Check if value already exists
    wealth_value = db.query(models.WealthValue).filter(
        models.WealthValue.wealth_category_id == wealth_category_id,
        models.WealthValue.value_date == value_date
    ).first()
    
    if wealth_value:
        # Update existing
        wealth_value.present_value = Decimal(str(present_value))
        wealth_value.note = note
        wealth_value.updated_at = datetime.utcnow()
    else:
        # Create new
        wealth_value = models.WealthValue(
            wealth_category_id=wealth_category_id,
            value_date=value_date,
            present_value=Decimal(str(present_value)),
            note=note
        )
        db.add(wealth_value)
    
    db.commit()
    db.refresh(wealth_value)
    return wealth_value


def get_wealth_values(
    db: Session,
    value_date: date,
    category_type: Optional[str] = None
) -> List[dict]:
    """Get all wealth values for a specific date"""
    query = db.query(models.WealthValue, models.WealthCategory).join(
        models.WealthCategory
    ).filter(
        models.WealthValue.value_date == value_date
    )
    
    if category_type:
        query = query.filter(models.WealthCategory.category_type == category_type)
    
    results = []
    for value, category in query.all():
        results.append({
            "id": value.id,
            "category_id": category.id,
            "category_type": category.category_type,
            "name": category.name,
            "currency": category.currency,
            "is_liability": category.is_liability,
            "present_value": float(value.present_value),
            "note": value.note,
            "value_date": value.value_date.isoformat()
        })
    
    return results


def get_wealth_value_history(
    db: Session,
    wealth_category_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> List[models.WealthValue]:
    """Get historical values for a wealth category"""
    query = db.query(models.WealthValue).filter(
        models.WealthValue.wealth_category_id == wealth_category_id
    )
    
    if start_date:
        query = query.filter(models.WealthValue.value_date >= start_date)
    if end_date:
        query = query.filter(models.WealthValue.value_date <= end_date)
    
    return query.order_by(models.WealthValue.value_date.desc()).all()


def delete_wealth_value(db: Session, value_id: int) -> bool:
    """Delete a wealth value"""
    value = db.query(models.WealthValue).filter(
        models.WealthValue.id == value_id
    ).first()
    
    if not value:
        return False
    
    db.delete(value)
    db.commit()
    return True


# ==================== TOTAL WEALTH CALCULATIONS ====================

def get_latest_fx_rates(db: Session, target_date: date) -> dict:
    """Get latest FX rates for a given date"""
    fx_rates = {'HUF': 1.0}
    
    for currency in ['USD', 'EUR', 'GBP', 'CHF']:
        fx_record = db.query(models.FxRate).filter(
            models.FxRate.target_currency == currency,
            models.FxRate.rate_date <= target_date
        ).order_by(models.FxRate.rate_date.desc()).first()
        
        if fx_record:
            fx_rates[currency] = float(fx_record.rate)
        else:
            # Fallback rates
            fallback_rates = {'USD': 327.87, 'EUR': 380.23, 'GBP': 450.0, 'CHF': 400.0}
            fx_rates[currency] = fallback_rates[currency]
    
    return fx_rates


def calculate_total_wealth(
    db: Session,
    snapshot_date: date,
    portfolio_id: int = 1
) -> dict:
    """Calculate total wealth combining portfolio and other assets"""
    
    # Get portfolio value
    portfolio_values = db.query(models.PortfolioValueDaily).filter(
        models.PortfolioValueDaily.portfolio_id == portfolio_id,
        models.PortfolioValueDaily.snapshot_date == snapshot_date
    ).all()
    
    portfolio_value_huf = sum(float(pv.value_huf) for pv in portfolio_values) if portfolio_values else 0.0
    
    # Get all wealth values for this date
    wealth_values = get_wealth_values(db, snapshot_date)
    
    # Get latest FX rates
    fx_rates = get_latest_fx_rates(db, snapshot_date)
    
    # Calculate assets and liabilities in HUF
    total_assets_huf = 0.0
    total_liabilities_huf = 0.0
    
    breakdown = {
        'cash': 0.0,
        'property': 0.0,
        'pension': 0.0,
        'loans': 0.0,
        'other': 0.0
    }
    
    for wv in wealth_values:
        value_huf = wv['present_value'] * fx_rates.get(wv['currency'], 1.0)
        
        if wv['is_liability']:
            # Loans are stored as positive values but represent liabilities
            total_liabilities_huf += abs(value_huf)
            breakdown['loans'] += abs(value_huf)
        else:
            total_assets_huf += value_huf
            cat_type = wv['category_type']
            breakdown[cat_type] = breakdown.get(cat_type, 0.0) + value_huf
    
    other_assets_huf = total_assets_huf
    net_wealth_huf = portfolio_value_huf + total_assets_huf - total_liabilities_huf
    
    return {
        'snapshot_date': snapshot_date.isoformat(),
        'portfolio_value_huf': portfolio_value_huf,
        'other_assets_huf': other_assets_huf,
        'total_assets_huf': portfolio_value_huf + total_assets_huf,
        'total_liabilities_huf': total_liabilities_huf,
        'net_wealth_huf': net_wealth_huf,
        'breakdown': breakdown,
        'wealth_details': wealth_values,
        'fx_rates': fx_rates
    }


def save_total_wealth_snapshot(
    db: Session,
    snapshot_date: date,
    portfolio_value_huf: float,
    other_assets_huf: float,
    total_liabilities_huf: float,
    cash_huf: float = 0.0,
    property_huf: float = 0.0,
    pension_huf: float = 0.0,
    other_huf: float = 0.0
) -> models.TotalWealthSnapshot:
    """Save a total wealth snapshot"""
    
    net_wealth_huf = portfolio_value_huf + other_assets_huf - total_liabilities_huf
    
    # Check if snapshot exists
    snapshot = db.query(models.TotalWealthSnapshot).filter(
        models.TotalWealthSnapshot.snapshot_date == snapshot_date
    ).first()
    
    if snapshot:
        # Update existing
        snapshot.portfolio_value_huf = Decimal(str(portfolio_value_huf))
        snapshot.other_assets_huf = Decimal(str(other_assets_huf))
        snapshot.total_liabilities_huf = Decimal(str(total_liabilities_huf))
        snapshot.net_wealth_huf = Decimal(str(net_wealth_huf))
        snapshot.cash_huf = Decimal(str(cash_huf))
        snapshot.property_huf = Decimal(str(property_huf))
        snapshot.pension_huf = Decimal(str(pension_huf))
        snapshot.other_huf = Decimal(str(other_huf))
    else:
        # Create new
        snapshot = models.TotalWealthSnapshot(
            snapshot_date=snapshot_date,
            portfolio_value_huf=Decimal(str(portfolio_value_huf)),
            other_assets_huf=Decimal(str(other_assets_huf)),
            total_liabilities_huf=Decimal(str(total_liabilities_huf)),
            net_wealth_huf=Decimal(str(net_wealth_huf)),
            cash_huf=Decimal(str(cash_huf)),
            property_huf=Decimal(str(property_huf)),
            pension_huf=Decimal(str(pension_huf)),
            other_huf=Decimal(str(other_huf))
        )
        db.add(snapshot)
    
    db.commit()
    db.refresh(snapshot)
    return snapshot


def get_wealth_snapshots(
    db: Session,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> List[models.TotalWealthSnapshot]:
    """Get historical wealth snapshots"""
    query = db.query(models.TotalWealthSnapshot)
    
    if start_date:
        query = query.filter(models.TotalWealthSnapshot.snapshot_date >= start_date)
    if end_date:
        query = query.filter(models.TotalWealthSnapshot.snapshot_date <= end_date)
    
    return query.order_by(models.TotalWealthSnapshot.snapshot_date.desc()).all()


def calculate_yoy_change(
    db: Session,
    current_date: date
) -> dict:
    """Calculate Year-over-Year change in wealth"""
    from dateutil.relativedelta import relativedelta
    
    # Get current snapshot
    current = db.query(models.TotalWealthSnapshot).filter(
        models.TotalWealthSnapshot.snapshot_date == current_date
    ).first()
    
    if not current:
        return None
    
    # Get snapshot from 1 year ago
    one_year_ago = current_date - relativedelta(years=1)
    previous = db.query(models.TotalWealthSnapshot).filter(
        models.TotalWealthSnapshot.snapshot_date <= one_year_ago
    ).order_by(models.TotalWealthSnapshot.snapshot_date.desc()).first()
    
    if not previous:
        return {
            'current_date': current_date.isoformat(),
            'current_wealth': float(current.net_wealth_huf),
            'yoy_change': None,
            'yoy_percentage': None
        }
    
    change = float(current.net_wealth_huf) - float(previous.net_wealth_huf)
    percentage = (change / float(previous.net_wealth_huf)) * 100 if previous.net_wealth_huf != 0 else 0
    
    return {
        'current_date': current_date.isoformat(),
        'previous_date': previous.snapshot_date.isoformat(),
        'current_wealth': float(current.net_wealth_huf),
        'previous_wealth': float(previous.net_wealth_huf),
        'yoy_change': change,
        'yoy_percentage': percentage
    }
