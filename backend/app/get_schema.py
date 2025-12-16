"""Get wealth_values schema"""
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv
import os

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
inspector = inspect(engine)
cols = inspector.get_columns('wealth_values')

print("wealth_values columns:")
for c in cols:
    print(f"  {c['name']}: {c['type']}")
