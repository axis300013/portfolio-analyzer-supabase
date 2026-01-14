import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cursor = conn.cursor()
cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'portfolio_values_daily' ORDER BY ordinal_position")
print("portfolio_values_daily columns:", [row[0] for row in cursor.fetchall()])
conn.close()
