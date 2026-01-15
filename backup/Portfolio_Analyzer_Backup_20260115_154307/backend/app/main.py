from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from typing import List, Optional
from pydantic import BaseModel
from . import crud, models, wealth_crud
from .db import get_db, engine

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Portfolio Analyzer API")

@app.get("/")
def root():
    return {"message": "Portfolio Analyzer API", "version": "1.0"}

@app.get("/portfolio/{portfolio_id}/snapshot")
def get_snapshot(
    portfolio_id: int,
    snapshot_date: date = None,
    db: Session = Depends(get_db)
):
    """Get portfolio snapshot for a specific date"""
    if snapshot_date is None:
        snapshot_date = date.today()
    
    snapshot = crud.get_portfolio_snapshot(db, portfolio_id, snapshot_date)
    
    if not snapshot:
        raise HTTPException(status_code=404, detail="No data for this date")
    
    result = []
    for item in snapshot:
        instrument = db.query(models.Instrument).get(item.instrument_id)
        
        # Check if price came from manual override first (highest priority)
        manual_price = db.query(models.ManualPrice).filter(
            models.ManualPrice.instrument_id == item.instrument_id,
            models.ManualPrice.override_date <= snapshot_date,
            models.ManualPrice.price == item.price
        ).order_by(models.ManualPrice.override_date.desc()).first()
        
        if manual_price:
            price_source = f"manual ({manual_price.created_by or 'user'})"
        else:
            # Get the price source from regular prices table
            price_record = db.query(models.Price).filter(
                models.Price.instrument_id == item.instrument_id,
                models.Price.price_date <= snapshot_date,
                models.Price.price == item.price
            ).order_by(models.Price.price_date.desc()).first()
            price_source = price_record.source if price_record else "unknown"
        
        result.append({
            "isin": instrument.isin,
            "name": instrument.name,
            "instrument_type": instrument.instrument_type,
            "quantity": float(item.quantity),
            "price": float(item.price),
            "currency": item.instrument_currency,
            "fx_rate": float(item.fx_rate),
            "value_huf": float(item.value_huf),
            "price_source": price_source
        })
    
    return result

@app.get("/portfolio/{portfolio_id}/summary")
def get_summary(
    portfolio_id: int,
    snapshot_date: date = None,
    db: Session = Depends(get_db)
):
    """Get portfolio summary"""
    if snapshot_date is None:
        snapshot_date = date.today()
    
    summary = crud.get_portfolio_summary(db, portfolio_id, snapshot_date)
    
    return {
        "portfolio_id": portfolio_id,
        "snapshot_date": snapshot_date.isoformat(),
        "total_value_huf": float(summary.total_value_huf) if summary.total_value_huf else 0,
        "instrument_count": summary.instrument_count
    }

@app.get("/portfolio/{portfolio_id}/history")
def get_portfolio_history(
    portfolio_id: int,
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db)
):
    """Get portfolio value history for a date range"""
    
    # Get all portfolio values in date range
    portfolio_values = db.query(models.PortfolioValueDaily).filter(
        models.PortfolioValueDaily.portfolio_id == portfolio_id,
        models.PortfolioValueDaily.snapshot_date >= start_date,
        models.PortfolioValueDaily.snapshot_date <= end_date
    ).order_by(models.PortfolioValueDaily.snapshot_date).all()
    
    if not portfolio_values:
        return []
    
    # Join with instruments to get names
    results = []
    for pv in portfolio_values:
        instrument = db.query(models.Instrument).filter(
            models.Instrument.id == pv.instrument_id
        ).first()
        
        results.append({
            "date": pv.snapshot_date.isoformat(),
            "instrument_id": pv.instrument_id,
            "name": instrument.name if instrument else "Unknown",
            "isin": instrument.isin if instrument else None,
            "instrument_type": instrument.instrument_type if instrument else None,
            "quantity": float(pv.quantity),
            "price": float(pv.price),
            "currency": pv.instrument_currency,
            "fx_rate": float(pv.fx_rate),
            "value_huf": float(pv.value_huf)
        })
    
    return results

# ===== PYDANTIC SCHEMAS =====

class TransactionCreate(BaseModel):
    portfolio_id: int
    instrument_id: int
    transaction_date: date
    transaction_type: str  # BUY, SELL, ADJUST
    quantity: float
    price: Optional[float] = None
    notes: Optional[str] = None
    created_by: Optional[str] = None

class ManualPriceCreate(BaseModel):
    instrument_id: int
    override_date: date
    price: float
    currency: str
    reason: Optional[str] = None
    created_by: Optional[str] = None

class InstrumentCreate(BaseModel):
    isin: str
    name: str
    currency: str
    instrument_type: Optional[str] = None
    ticker: Optional[str] = None
    source: Optional[str] = None

# ===== TRANSACTION ENDPOINTS =====

@app.post("/transactions")
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    """Add a new transaction (BUY, SELL, ADJUST)"""
    try:
        new_transaction = crud.add_transaction(
            db=db,
            portfolio_id=transaction.portfolio_id,
            instrument_id=transaction.instrument_id,
            transaction_date=transaction.transaction_date,
            transaction_type=transaction.transaction_type,
            quantity=transaction.quantity,
            price=transaction.price,
            notes=transaction.notes,
            created_by=transaction.created_by
        )
        return {
            "id": new_transaction.id,
            "portfolio_id": new_transaction.portfolio_id,
            "instrument_id": new_transaction.instrument_id,
            "transaction_date": new_transaction.transaction_date.isoformat(),
            "transaction_type": new_transaction.transaction_type,
            "quantity": float(new_transaction.quantity),
            "price": float(new_transaction.price) if new_transaction.price else None,
            "notes": new_transaction.notes,
            "created_by": new_transaction.created_by,
            "created_at": new_transaction.created_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/transactions/{portfolio_id}")
def get_transaction_history(
    portfolio_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    instrument_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get transaction history for a portfolio"""
    transactions = crud.get_transactions(
        db=db,
        portfolio_id=portfolio_id,
        start_date=start_date,
        end_date=end_date,
        instrument_id=instrument_id
    )
    
    results = []
    for tx in transactions:
        instrument = db.query(models.Instrument).get(tx.instrument_id)
        results.append({
            "id": tx.id,
            "transaction_date": tx.transaction_date.isoformat(),
            "transaction_type": tx.transaction_type,
            "instrument_name": instrument.name if instrument else "Unknown",
            "isin": instrument.isin if instrument else None,
            "quantity": float(tx.quantity),
            "price": float(tx.price) if tx.price else None,
            "notes": tx.notes,
            "created_by": tx.created_by,
            "created_at": tx.created_at.isoformat()
        })
    
    return results

# ===== MANUAL PRICE ENDPOINTS =====

@app.post("/prices/manual")
def create_manual_price(manual_price: ManualPriceCreate, db: Session = Depends(get_db)):
    """Add or update a manual price override"""
    try:
        new_manual_price = crud.add_manual_price(
            db=db,
            instrument_id=manual_price.instrument_id,
            override_date=manual_price.override_date,
            price=manual_price.price,
            currency=manual_price.currency,
            reason=manual_price.reason,
            created_by=manual_price.created_by
        )
        return {
            "id": new_manual_price.id,
            "instrument_id": new_manual_price.instrument_id,
            "override_date": new_manual_price.override_date.isoformat(),
            "price": float(new_manual_price.price),
            "currency": new_manual_price.currency,
            "reason": new_manual_price.reason,
            "created_by": new_manual_price.created_by,
            "created_at": new_manual_price.created_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/prices/manual")
def get_manual_price_overrides(
    instrument_id: Optional[int] = None,
    override_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Get manual price overrides"""
    manual_prices = crud.get_manual_prices(
        db=db,
        instrument_id=instrument_id,
        override_date=override_date
    )
    
    results = []
    for mp in manual_prices:
        instrument = db.query(models.Instrument).get(mp.instrument_id)
        results.append({
            "id": mp.id,
            "instrument_name": instrument.name if instrument else "Unknown",
            "isin": instrument.isin if instrument else None,
            "override_date": mp.override_date.isoformat(),
            "price": float(mp.price),
            "currency": mp.currency,
            "reason": mp.reason,
            "created_by": mp.created_by,
            "created_at": mp.created_at.isoformat()
        })
    
    return results

# ===== INSTRUMENT ENDPOINTS =====

@app.post("/instruments")
def create_instrument(instrument: InstrumentCreate, db: Session = Depends(get_db)):
    """Add a new instrument"""
    try:
        new_instrument = crud.add_new_instrument(
            db=db,
            isin=instrument.isin,
            name=instrument.name,
            currency=instrument.currency,
            instrument_type=instrument.instrument_type,
            ticker=instrument.ticker,
            source=instrument.source
        )
        return {
            "id": new_instrument.id,
            "isin": new_instrument.isin,
            "name": new_instrument.name,
            "currency": new_instrument.currency,
            "instrument_type": new_instrument.instrument_type,
            "ticker": new_instrument.ticker,
            "source": new_instrument.source,
            "created_at": new_instrument.created_at.isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/instruments")
def get_all_instruments_api(db: Session = Depends(get_db)):
    """Get all instruments"""
    instruments = crud.get_all_instruments(db)
    
    results = []
    for inst in instruments:
        results.append({
            "id": inst.id,
            "isin": inst.isin,
            "name": inst.name,
            "currency": inst.currency,
            "instrument_type": inst.instrument_type,
            "ticker": inst.ticker,
            "source": inst.source
        })
    
    return results

@app.get("/instruments/{isin}")
def get_instrument_by_isin_api(isin: str, db: Session = Depends(get_db)):
    """Get instrument by ISIN"""
    instrument = crud.get_instrument_by_isin(db, isin)
    
    if not instrument:
        raise HTTPException(status_code=404, detail=f"Instrument with ISIN {isin} not found")
    
    return {
        "id": instrument.id,
        "isin": instrument.isin,
        "name": instrument.name,
        "currency": instrument.currency,
        "instrument_type": instrument.instrument_type,
        "ticker": instrument.ticker,
        "source": instrument.source
    }

# ===== WEALTH MANAGEMENT SCHEMAS =====

class WealthCategoryCreate(BaseModel):
    category_type: str
    name: str
    currency: str
    is_liability: bool = False

class WealthCategoryUpdate(BaseModel):
    category_type: Optional[str] = None
    name: Optional[str] = None
    currency: Optional[str] = None
    is_liability: Optional[bool] = None

class WealthValueCreate(BaseModel):
    wealth_category_id: int
    value_date: str  # YYYY-MM-DD
    present_value: float
    note: Optional[str] = None

# ===== WEALTH CATEGORY ENDPOINTS =====

@app.get("/wealth/categories")
def get_wealth_categories_api(
    category_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all wealth categories"""
    categories = wealth_crud.get_wealth_categories(db, category_type)
    return [
        {
            "id": c.id,
            "category_type": c.category_type,
            "name": c.name,
            "currency": c.currency,
            "is_liability": c.is_liability,
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "updated_at": c.updated_at.isoformat() if c.updated_at else None
        }
        for c in categories
    ]

@app.post("/wealth/categories")
def create_wealth_category_api(
    category: WealthCategoryCreate,
    db: Session = Depends(get_db)
):
    """Add a new wealth category"""
    try:
        result = wealth_crud.add_wealth_category(
            db=db,
            category_type=category.category_type,
            name=category.name,
            currency=category.currency,
            is_liability=category.is_liability
        )
        return {
            "id": result.id,
            "category_type": result.category_type,
            "name": result.name,
            "currency": result.currency,
            "is_liability": result.is_liability,
            "message": f"Wealth category '{category.name}' added successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/wealth/categories/{category_id}")
def update_wealth_category_api(
    category_id: int,
    category: WealthCategoryUpdate,
    db: Session = Depends(get_db)
):
    """Update a wealth category"""
    try:
        # Filter out None values
        update_data = {k: v for k, v in category.dict().items() if v is not None}
        
        result = wealth_crud.update_wealth_category(db, category_id, **update_data)
        
        return {
            "id": result.id,
            "category_type": result.category_type,
            "name": result.name,
            "currency": result.currency,
            "is_liability": result.is_liability,
            "message": "Category updated successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/wealth/categories/{category_id}")
def delete_wealth_category_api(category_id: int, db: Session = Depends(get_db)):
    """Delete a wealth category and all its values"""
    success = wealth_crud.delete_wealth_category(db, category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted successfully"}

# ===== WEALTH VALUE ENDPOINTS =====

@app.post("/wealth/values")
def create_wealth_value_api(value: WealthValueCreate, db: Session = Depends(get_db)):
    """Add or update wealth value for a specific date"""
    try:
        from datetime import datetime
        value_date = datetime.strptime(value.value_date, "%Y-%m-%d").date()
        
        result = wealth_crud.add_or_update_wealth_value(
            db=db,
            wealth_category_id=value.wealth_category_id,
            value_date=value_date,
            present_value=value.present_value,
            note=value.note
        )
        
        return {
            "id": result.id,
            "wealth_category_id": result.wealth_category_id,
            "value_date": result.value_date.isoformat(),
            "present_value": float(result.present_value),
            "note": result.note,
            "message": "Wealth value saved successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/wealth/values/{value_date}")
def get_wealth_values_api(
    value_date: str,
    category_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all wealth values for a specific date"""
    try:
        from datetime import datetime
        date_obj = datetime.strptime(value_date, "%Y-%m-%d").date()
        return wealth_crud.get_wealth_values(db, date_obj, category_type)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/wealth/history/{category_id}")
def get_wealth_history_api(
    category_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get historical values for a wealth category"""
    try:
        from datetime import datetime
        
        start = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
        end = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None
        
        values = wealth_crud.get_wealth_value_history(db, category_id, start, end)
        
        return [
            {
                "id": v.id,
                "date": v.value_date.isoformat(),
                "value": float(v.present_value),
                "note": v.note,
                "created_at": v.created_at.isoformat() if v.created_at else None,
                "updated_at": v.updated_at.isoformat() if v.updated_at else None
            }
            for v in values
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/wealth/values/{value_id}")
def delete_wealth_value_api(value_id: int, db: Session = Depends(get_db)):
    """Delete a wealth value"""
    success = wealth_crud.delete_wealth_value(db, value_id)
    if not success:
        raise HTTPException(status_code=404, detail="Value not found")
    return {"message": "Value deleted successfully"}

# ===== TOTAL WEALTH ENDPOINTS =====

@app.get("/wealth/total/{snapshot_date}")
def get_total_wealth_api(
    snapshot_date: str,
    portfolio_id: int = 1,
    db: Session = Depends(get_db)
):
    """Get total wealth (portfolio + other assets - liabilities)"""
    try:
        from datetime import datetime
        date_obj = datetime.strptime(snapshot_date, "%Y-%m-%d").date()
        
        return wealth_crud.calculate_total_wealth(db, date_obj, portfolio_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/wealth/snapshot/{snapshot_date}")
def save_wealth_snapshot_api(
    snapshot_date: str,
    portfolio_id: int = 1,
    db: Session = Depends(get_db)
):
    """Calculate and save total wealth snapshot"""
    try:
        from datetime import datetime
        date_obj = datetime.strptime(snapshot_date, "%Y-%m-%d").date()
        
        # Calculate total wealth
        wealth_data = wealth_crud.calculate_total_wealth(db, date_obj, portfolio_id)
        
        # Save snapshot
        snapshot = wealth_crud.save_total_wealth_snapshot(
            db=db,
            snapshot_date=date_obj,
            portfolio_value_huf=wealth_data['portfolio_value_huf'],
            other_assets_huf=wealth_data['other_assets_huf'],
            total_liabilities_huf=wealth_data['total_liabilities_huf'],
            cash_huf=wealth_data['breakdown'].get('cash', 0.0),
            property_huf=wealth_data['breakdown'].get('property', 0.0),
            pension_huf=wealth_data['breakdown'].get('pension', 0.0),
            other_huf=wealth_data['breakdown'].get('other', 0.0)
        )
        
        return {
            "snapshot_date": snapshot.snapshot_date.isoformat(),
            "portfolio_value_huf": float(snapshot.portfolio_value_huf),
            "other_assets_huf": float(snapshot.other_assets_huf),
            "total_liabilities_huf": float(snapshot.total_liabilities_huf),
            "net_wealth_huf": float(snapshot.net_wealth_huf),
            "message": "Snapshot saved successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/wealth/snapshots")
def get_wealth_snapshots_api(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get historical wealth snapshots"""
    try:
        from datetime import datetime
        
        start = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
        end = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None
        
        snapshots = wealth_crud.get_wealth_snapshots(db, start, end)
        
        return [
            {
                "snapshot_date": s.snapshot_date.isoformat(),
                "portfolio_value_huf": float(s.portfolio_value_huf),
                "other_assets_huf": float(s.other_assets_huf),
                "total_liabilities_huf": float(s.total_liabilities_huf),
                "net_wealth_huf": float(s.net_wealth_huf),
                "cash_huf": float(s.cash_huf),
                "property_huf": float(s.property_huf),
                "pension_huf": float(s.pension_huf),
                "other_huf": float(s.other_huf)
            }
            for s in snapshots
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/wealth/yoy/{snapshot_date}")
def get_yoy_change_api(snapshot_date: str, db: Session = Depends(get_db)):
    """Get Year-over-Year wealth change"""
    try:
        from datetime import datetime
        date_obj = datetime.strptime(snapshot_date, "%Y-%m-%d").date()
        
        result = wealth_crud.calculate_yoy_change(db, date_obj)
        
        if not result:
            raise HTTPException(status_code=404, detail="No snapshot found for this date")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/etl/run-daily-update")
def run_daily_update():
    """
    Trigger the daily ETL pipeline:
    1. Fetch FX rates
    2. Fetch instrument prices
    3. Calculate portfolio values
    
    This endpoint runs the complete ETL and can be called from the UI.
    Safe to run multiple times per day - idempotent operation.
    """
    try:
        from .etl.run_daily_etl import run_daily_etl
        import io
        import sys
        
        # Capture output
        output_buffer = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = output_buffer
        
        try:
            run_daily_etl()
            output = output_buffer.getvalue()
        finally:
            sys.stdout = old_stdout
        
        return {
            "status": "success",
            "message": "Daily update completed successfully",
            "output": output,
            "timestamp": date.today().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"ETL failed: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    from .config import settings
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)
