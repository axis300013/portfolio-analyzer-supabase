"""
Copy Static Wealth Values from Previous Day
This ensures that wealth items that don't change automatically (properties, loans, etc.)
are copied forward to today's date.
"""
from datetime import date
from ..supabase_client import get_supabase_client


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
    
    client = get_supabase_client()

    # Categories that should be copied (not automated)
    automated_categories = {'Self Fund', 'Voluntary Fund'}

    # Find most recent date with wealth values before target_date
    prev_rows = (
        client.client.table("wealth_values")
        .select("value_date")
        .lt("value_date", target_date.isoformat())
        .order("value_date", desc=True)
        .limit(1)
        .execute()
    ).data

    if not prev_rows:
        print("  ⚠ No previous wealth values found to copy")
        return 0

    previous_date = prev_rows[0]["value_date"]
    print(f"  Copying static wealth values from {previous_date} to {target_date}")

    # Get all wealth values from previous date (joined with categories)
    prev_values = (
        client.client.table("wealth_values")
        .select("wealth_category_id, present_value, note, wealth_categories(name)")
        .eq("value_date", previous_date)
        .execute()
    ).data

    # Filter out automated categories
    values_to_copy = [
        v for v in prev_values if v.get("wealth_categories", {}).get("name") not in automated_categories
    ]

    if not values_to_copy:
        print("  ⚠ No static wealth values found to copy")
        return 0

    copied_count = 0
    skipped_count = 0

    for value in values_to_copy:
        category_id = value["wealth_category_id"]

        # Check if value already exists for target_date
        existing = (
            client.client.table("wealth_values")
            .select("id")
            .eq("wealth_category_id", category_id)
            .eq("value_date", target_date.isoformat())
            .limit(1)
            .execute()
        ).data

        if existing:
            skipped_count += 1
            continue

        note = value.get("note") or ""
        composed_note = f"Copied from {previous_date}" + (f" - {note}" if note else "")

        client.insert_wealth_value(
            {
                "wealth_category_id": category_id,
                "value_date": target_date.isoformat(),
                "present_value": float(value["present_value"]),
                "note": composed_note,
            }
        )
        copied_count += 1

    print(f"  ✓ Copied {copied_count} static wealth values")
    if skipped_count > 0:
        print(f"  ℹ Skipped {skipped_count} values (already exist for {target_date})")

    return copied_count


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
