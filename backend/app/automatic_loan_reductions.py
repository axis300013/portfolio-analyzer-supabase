"""
Automatic Monthly Loan Reductions
Reduces specific loan/liability amounts on the 1st of each month
"""
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import text
import os

# Monthly reduction amounts (negative because they reduce the loan)
MONTHLY_REDUCTIONS = {
    "Hitel állomány CIB, Peterdy": Decimal("236667"),
    "Kawasaki kötelezettség": Decimal("40000"),
    "Cabrio kötelezettség": Decimal("118958"),
    "Tartozás felém": Decimal("40000")
}

# File to track last reduction date
LAST_REDUCTION_FILE = "data/last_loan_reduction.txt"


def get_last_reduction_date():
    """Get the date of the last loan reduction"""
    try:
        if os.path.exists(LAST_REDUCTION_FILE):
            with open(LAST_REDUCTION_FILE, 'r') as f:
                date_str = f.read().strip()
                return datetime.strptime(date_str, "%Y-%m-%d").date()
    except Exception as e:
        print(f"Error reading last reduction date: {e}")
    return None


def save_last_reduction_date(reduction_date: date):
    """Save the date of the last loan reduction"""
    try:
        os.makedirs(os.path.dirname(LAST_REDUCTION_FILE), exist_ok=True)
        with open(LAST_REDUCTION_FILE, 'w') as f:
            f.write(reduction_date.strftime("%Y-%m-%d"))
    except Exception as e:
        print(f"Error saving last reduction date: {e}")


def should_run_reduction(today: date) -> bool:
    """
    Check if we should run loan reduction:
    - It's a new month since last reduction
    - Or never run before
    """
    last_reduction = get_last_reduction_date()
    
    if last_reduction is None:
        # Never run before
        return True
    
    # Check if we're in a new month
    if today.year > last_reduction.year or today.month > last_reduction.month:
        return True
    
    return False


def apply_loan_reductions(db: Session, reduction_date: date = None) -> dict:
    """
    Apply monthly loan reductions
    
    Args:
        db: Database session
        reduction_date: Date to apply reductions (defaults to today)
    
    Returns:
        dict with results
    """
    if reduction_date is None:
        reduction_date = date.today()
    
    results = {
        "date": reduction_date.isoformat(),
        "reductions_applied": [],
        "errors": []
    }
    
    try:
        # Get all wealth categories
        categories_query = text("""
            SELECT id, name, currency 
            FROM wealth_categories 
            WHERE is_liability = true
        """)
        categories = db.execute(categories_query).fetchall()
        category_map = {cat.name: (cat.id, cat.currency) for cat in categories}
        
        for category_name, reduction_amount in MONTHLY_REDUCTIONS.items():
            try:
                if category_name not in category_map:
                    results["errors"].append(f"Category '{category_name}' not found")
                    continue
                
                category_id, currency = category_map[category_name]
                
                # Get current value
                current_query = text("""
                    SELECT present_value 
                    FROM wealth_values 
                    WHERE wealth_category_id = :category_id 
                    ORDER BY value_date DESC 
                    LIMIT 1
                """)
                current = db.execute(current_query, {"category_id": category_id}).fetchone()
                
                if not current:
                    results["errors"].append(f"No current value for '{category_name}'")
                    continue
                
                current_value = Decimal(str(current.present_value))
                new_value = current_value - reduction_amount
                
                # Ensure loan doesn't go below zero
                if new_value < 0:
                    new_value = Decimal("0")
                
                # Check if value already exists for this date
                existing_query = text("""
                    SELECT id FROM wealth_values 
                    WHERE wealth_category_id = :category_id 
                    AND value_date = :value_date
                """)
                existing = db.execute(existing_query, {
                    "category_id": category_id,
                    "value_date": reduction_date
                }).fetchone()
                
                if existing:
                    # Update existing
                    update_query = text("""
                        UPDATE wealth_values 
                        SET present_value = :new_value,
                            note = :note,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = :id
                    """)
                    db.execute(update_query, {
                        "id": existing.id,
                        "new_value": float(new_value),
                        "note": f"Automatic monthly reduction: -{reduction_amount:,.0f} {currency}"
                    })
                else:
                    # Insert new
                    insert_query = text("""
                        INSERT INTO wealth_values 
                        (wealth_category_id, value_date, present_value, note)
                        VALUES (:category_id, :value_date, :new_value, :note)
                    """)
                    db.execute(insert_query, {
                        "category_id": category_id,
                        "value_date": reduction_date,
                        "new_value": float(new_value),
                        "note": f"Automatic monthly reduction: -{reduction_amount:,.0f} {currency}"
                    })
                
                db.commit()
                
                results["reductions_applied"].append({
                    "category": category_name,
                    "previous_value": float(current_value),
                    "reduction": float(reduction_amount),
                    "new_value": float(new_value),
                    "currency": currency
                })
                
            except Exception as e:
                results["errors"].append(f"Error processing '{category_name}': {str(e)}")
                db.rollback()
        
        # Save last reduction date
        save_last_reduction_date(reduction_date)
        
    except Exception as e:
        results["errors"].append(f"General error: {str(e)}")
        db.rollback()
    
    return results


def check_and_run_automatic_reductions(db: Session) -> dict:
    """
    Check if reductions should run and execute if needed
    Called on app startup
    """
    today = date.today()
    
    if not should_run_reduction(today):
        return {
            "status": "skipped",
            "message": "Loan reductions already applied this month",
            "last_reduction": get_last_reduction_date().isoformat() if get_last_reduction_date() else None
        }
    
    print("Running automatic monthly loan reductions...")
    results = apply_loan_reductions(db, today)
    
    if results["reductions_applied"]:
        print(f"✓ Applied {len(results['reductions_applied'])} loan reductions")
        for r in results["reductions_applied"]:
            print(f"  - {r['category']}: {r['previous_value']:,.0f} → {r['new_value']:,.0f} {r['currency']}")
    
    if results["errors"]:
        print(f"⚠ Errors: {len(results['errors'])}")
        for e in results["errors"]:
            print(f"  - {e}")
    
    return {
        "status": "completed",
        "results": results
    }


if __name__ == "__main__":
    # Test script
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from dotenv import load_dotenv
    
    load_dotenv()
    
    database_url = os.getenv('DATABASE_URL')
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(bind=engine)
    
    db = SessionLocal()
    try:
        result = check_and_run_automatic_reductions(db)
        print("\nResult:", result)
    finally:
        db.close()
