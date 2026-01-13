import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM wealth_values WHERE value_date = '2026-01-01'")
jan1 = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM wealth_values WHERE value_date = '2026-01-02'")
jan2 = cursor.fetchone()[0]

print(f"Jan 1, 2026 wealth values: {jan1}")
print(f"Jan 2, 2026 wealth values: {jan2}")

if jan1 == jan2:
    print(f"\n✅ All {jan1} values successfully copied!")
else:
    print(f"\n⚠️ Mismatch: {jan1 - jan2} values still missing")

conn.close()
