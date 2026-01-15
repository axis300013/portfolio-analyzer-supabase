"""Check today's wealth and portfolio data"""
from backend.app.database import get_db
from backend.app import models
from datetime import date

def check_todays_data():
    db = next(get_db())
    today = date.today()
    
    print(f"\n=== Data for {today} ===\n")
    
    # Check wealth_values
    wealth_values = db.query(models.WealthValue).filter(
        models.WealthValue.date == today
    ).all()
    
    print(f"Wealth Values: {len(wealth_values)} records")
    print("\nBy Category:")
    categories = {}
    for wv in wealth_values:
        cat = f"{wv.category.category_type} - {wv.category.name}"
        is_liability = wv.category.is_liability
        if cat not in categories:
            categories[cat] = {'total': 0, 'is_liability': is_liability, 'items': []}
        categories[cat]['total'] += float(wv.present_value)
        categories[cat]['items'].append({
            'subcategory': wv.subcategory,
            'value': float(wv.present_value),
            'currency': wv.currency
        })
    
    for cat, data in sorted(categories.items()):
        liability_marker = " (LIABILITY)" if data['is_liability'] else ""
        print(f"\n  {cat}{liability_marker}: {data['total']:,.2f}")
        for item in data['items']:
            print(f"    - {item['subcategory']}: {item['value']:,.2f} {item['currency']}")
    
    # Check portfolio values
    portfolio_values = db.query(models.PortfolioValueDaily).filter(
        models.PortfolioValueDaily.snapshot_date == today
    ).all()
    
    print(f"\n\nPortfolio Values: {len(portfolio_values)} records")
    total_portfolio = sum(float(pv.value_huf) for pv in portfolio_values)
    print(f"Total Portfolio Value: {total_portfolio:,.2f} HUF")
    
    # Calculate totals
    print("\n\n=== SUMMARY ===")
    assets = sum(data['total'] for cat, data in categories.items() if not data['is_liability'])
    liabilities = sum(data['total'] for cat, data in categories.items() if data['is_liability'])
    
    print(f"Portfolio Value: {total_portfolio:,.2f} HUF")
    print(f"Other Assets: {assets:,.2f} HUF")
    print(f"Liabilities: {liabilities:,.2f} HUF")
    print(f"Net Wealth: {total_portfolio + assets - liabilities:,.2f} HUF")

if __name__ == "__main__":
    check_todays_data()
