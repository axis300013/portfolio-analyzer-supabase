"""
Supabase REST diagnostic: latest wealth rows per category (post-2026-01-01)
Prints distribution by category_type (with is_liability override) and lists CASH items.
"""

import os
import sys
from datetime import date
from pathlib import Path

# Ensure project root on sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
  sys.path.insert(0, str(ROOT))

# Load .env manually to avoid shell quoting issues
env_path = ROOT / ".env"
if env_path.exists():
  for line in env_path.read_text().splitlines():
    if "=" in line and not line.strip().startswith("#"):
      key, val = line.split("=", 1)
      os.environ.setdefault(key.strip(), val.strip())

from backend.app.supabase_client import SupabaseRESTClient

client = SupabaseRESTClient()

# Fetch wealth values ordered by category then newest first
result = (
  client.client.table("wealth_values")
  .select("*, wealth_categories(name, category_type, is_liability)")
  .order("wealth_category_id")
  .order("value_date", desc=True)
  .execute()
)
rows = result.data or []
print(f"Fetched rows: {len(rows)}")

# Keep latest per category
latest = {}
for item in rows:
  cid = item.get("wealth_category_id")
  if cid not in latest:
    latest[cid] = item

print(f"Unique categories: {len(latest)}")

cutoff = date(2026, 1, 1)
filtered = []
for item in latest.values():
  value_date = item.get("value_date")
  if value_date is None:
    continue
  if value_date < cutoff.isoformat():
    continue
  filtered.append(item)

# Distribution
type_counts = {}
for item in filtered:
  cat = item.get("wealth_categories") or {}
  is_liability = cat.get("is_liability") is True
  raw_type = (cat.get("category_type") or "").upper().strip()
  normalized = "LIABILITIES" if is_liability else (raw_type or "UNKNOWN")
  type_counts[normalized] = type_counts.get(normalized, 0) + 1

print("Post-cutoff type distribution:", type_counts)

# List CASH items
print("CASH items (normalized):")
for item in filtered:
  cat = item.get("wealth_categories") or {}
  raw_type = (cat.get("category_type") or "").upper().strip()
  is_liability = cat.get("is_liability") is True
  normalized = "LIABILITIES" if is_liability else (raw_type or "UNKNOWN")
  if normalized == "CASH":
    name = cat.get("name")
    value = item.get("present_value")
    vdate = item.get("value_date")
    print(f"- {name} | {value} | {vdate} | raw_type={raw_type}")
