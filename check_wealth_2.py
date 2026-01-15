#!/usr/bin/env python
"""Check wealth values for category_id=2"""
import os
os.environ['RAILWAY_ENVIRONMENT'] = 'production'

from backend.app.db import SessionLocal
from backend.app.models import WealthValue

db = SessionLocal()
values = db.query(WealthValue).filter(
    WealthValue.wealth_category_id == 2
).order_by(WealthValue.value_date.desc()).limit(5).all()

print(f"Found {len(values)} records for category_id=2:\n")
for v in values:
    print(f"  ID {v.id}: value={v.present_value}, date={v.value_date}")
