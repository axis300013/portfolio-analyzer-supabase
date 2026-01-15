import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT COUNT(*) as total, MIN(value_date) as min_date, MAX(value_date) as max_date 
        FROM wealth_values 
        WHERE note LIKE '%history.csv%'
    """)).fetchone()
    
    print(f"Historical wealth records imported: {result[0]}")
    print(f"Date range: {result[1]} to {result[2]}")
    
    # Check categories
    result = conn.execute(text("""
        SELECT category_type, COUNT(*) as count
        FROM wealth_categories wc
        JOIN wealth_values wv ON wc.id = wv.wealth_category_id
        WHERE wv.note LIKE '%history.csv%'
        GROUP BY category_type
        ORDER BY category_type
    """)).fetchall()
    
    print("\nBy category:")
    for row in result:
        print(f"  {row[0]}: {row[1]} records")
