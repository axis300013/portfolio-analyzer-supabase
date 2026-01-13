"""
Copy Static Wealth Values from Previous Day
This ensures that wealth items that don't change automatically (properties, loans, etc.)
are copied forward to today's date.
"""
from datetime import date, timedelta
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

load_dotenv()

# Initialize database connection
database_url = os.getenv('DATABASE_URL')
engine = create_engine(database_url)
SessionLocal = sessionmaker(bind=engine)


def copy_static_wealth_values(target_date: date = None):
    """
    Copy static wealth values from the most recent previous day to target_date.
    
    Static values are those that don't change automatically (properties, cash, loans).
    Automated values (like pension balances) are fetched separately and should not be copied.
    
    Args:
        target_date: Date to copy values to (defaults to today)
    """
    if target_date is None:
        target_date = date.today()
    
    db = SessionLocal()
    try:
        # Categories that should be copied (not automated)
        # Self Fund and Voluntary Fund are automated, so exclude them
        AUTOMATED_CATEGORIES = ['Self Fund', 'Voluntary Fund']
        
        # Find the most recent date with wealth values before target_date
        result = db.execute(
            text("""
                SELECT DISTINCT value_date 
                FROM wealth_values 
                WHERE value_date < :target_date
                ORDER BY value_date DESC 
                LIMIT 1
            """),
            {"target_date": target_date}
        )
        
        previous_date_row = result.fetchone()
        
        if not previous_date_row:
            print("  ⚠ No previous wealth values found to copy")
            return 0
        
        previous_date = previous_date_row[0]
        print(f"  Copying static wealth values from {previous_date} to {target_date}")
        
        # Get all wealth values from previous date (excluding automated ones)
        result = db.execute(
            text("""
                SELECT wv.wealth_category_id, wv.present_value, wv.note, wc.name
                FROM wealth_values wv
                JOIN wealth_categories wc ON wv.wealth_category_id = wc.id
                WHERE wv.value_date = :previous_date
                AND wc.name NOT IN :automated_categories
            """),
            {
                "previous_date": previous_date,
                "automated_categories": tuple(AUTOMATED_CATEGORIES)
            }
        )
        
        values_to_copy = result.fetchall()
        
        if not values_to_copy:
            print("  ⚠ No static wealth values found to copy")
            return 0
        
        copied_count = 0
        updated_count = 0
        skipped_count = 0
        
        for category_id, present_value, note, category_name in values_to_copy:
            # Check if value already exists for target_date
            existing = db.execute(
                text("""
                    SELECT id FROM wealth_values 
                    WHERE wealth_category_id = :category_id 
                    AND value_date = :target_date
                """),
                {"category_id": category_id, "target_date": target_date}
            ).fetchone()
            
            if existing:
                # Don't overwrite existing values (might be manually updated)
                skipped_count += 1
                continue
            else:
                # Insert new value
                db.execute(
                    text("""
                        INSERT INTO wealth_values 
                        (wealth_category_id, value_date, present_value, note)
                        VALUES (:category_id, :value_date, :value, :note)
                    """),
                    {
                        "category_id": category_id,
                        "value_date": target_date,
                        "value": float(present_value),
                        "note": f"Copied from {previous_date}" + (f" - {note}" if note else "")
                    }
                )
                copied_count += 1
        
        db.commit()
        
        print(f"  ✓ Copied {copied_count} static wealth values")
        if skipped_count > 0:
            print(f"  ℹ Skipped {skipped_count} values (already exist for {target_date})")
        
        return copied_count
        
    except Exception as e:
        db.rollback()
        print(f"  ✗ Error copying wealth values: {e}")
        raise e
    finally:
        db.close()


def run_copy_wealth():
    """Main entry point for copying wealth values"""
    print("\n" + "="*50)
    print("Copying Static Wealth Values")
    print("="*50)
    
    try:
        copied = copy_static_wealth_values()
        print("="*50)
        return copied
    except Exception as e:
        print(f"Failed to copy wealth values: {e}")
        print("="*50)
        return 0


if __name__ == "__main__":
    run_copy_wealth()
