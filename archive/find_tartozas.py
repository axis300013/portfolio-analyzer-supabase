import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cursor = conn.cursor()
cursor.execute("SELECT id, name FROM wealth_categories WHERE name LIKE '%Tartoz%' OR name LIKE '%fel%'")
print("Tartozás categories:", [row for row in cursor.fetchall()])
cursor.execute("SELECT id, name FROM wealth_categories WHERE is_liability = true")
print("\nAll liability categories:")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]}")
conn.close()
