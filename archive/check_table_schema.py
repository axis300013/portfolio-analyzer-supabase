from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv
import os

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
inspector = inspect(engine)
cols = inspector.get_columns('total_wealth_snapshots')
print('Columns in total_wealth_snapshots:')
for col in cols:
    print(f'  - {col["name"]} ({col["type"]})')
