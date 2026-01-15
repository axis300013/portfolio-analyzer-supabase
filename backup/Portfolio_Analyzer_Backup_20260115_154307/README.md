# Portfolio Analyzer

A comprehensive portfolio management system for tracking investments, fetching market data, and analyzing portfolio performance.

## Features

- **Multi-currency support**: Track instruments in USD, EUR, HUF
- **Automatic FX rates**: Fetch daily exchange rates from MNB (Magyar Nemzeti Bank)
- **Price tracking**: Template for fetching instrument prices from various sources
- **Portfolio valuation**: Calculate daily portfolio values in HUF
- **REST API**: FastAPI-based backend with interactive documentation
- **Web UI**: Streamlit dashboard for portfolio visualization
- **ETL pipeline**: Automated data fetching and calculation

## Project Structure

```
Portfolio Analyzer/
├── backend/
│   └── app/
│       ├── etl/                    # ETL scripts
│       │   ├── fetch_fx_mnb.py    # MNB FX rate fetcher
│       │   ├── fetch_prices.py    # Price fetcher (template)
│       │   ├── calculate_values.py # Portfolio calculator
│       │   └── run_daily_etl.py   # ETL orchestrator
│       ├── config.py               # Configuration
│       ├── db.py                   # Database connection
│       ├── models.py               # SQLAlchemy models
│       ├── crud.py                 # CRUD operations
│       ├── main.py                 # FastAPI application
│       └── import_initial_data.py  # Data import script
├── data/
│   └── initial_holdings.csv        # Portfolio holdings
├── sql/
│   └── create_tables.sql          # Database schema
├── ui/
│   └── streamlit_app.py           # Streamlit UI
├── .env                           # Environment variables
├── docker-compose.yml             # PostgreSQL container
├── requirements.txt               # Python dependencies
└── run_etl.bat                    # ETL scheduler script
```

## Quick Start

### Prerequisites

- Python 3.10+
- Docker Desktop (for PostgreSQL)
- Git (optional)

### Installation

1. **Clone or download the project**

2. **Create virtual environment**
   ```powershell
   python -m venv venv
   venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Start PostgreSQL**
   ```powershell
   docker-compose up -d
   ```

5. **Create database schema**
   ```powershell
   # Wait 15 seconds for PostgreSQL to start
   timeout /t 15
   Get-Content sql\create_tables.sql | docker exec -i portfolio_db psql -U portfolio_user -d portfolio_db
   ```

6. **Import initial data**
   ```powershell
   python -m backend.app.import_initial_data
   ```

7. **Run ETL to populate data**
   ```powershell
   python -m backend.app.etl.run_daily_etl
   ```

8. **Start API server** (Terminal 1)
   ```powershell
   python -m backend.app.main
   ```

9. **Start UI** (Terminal 2 - new terminal)
   ```powershell
   cd "c:\Users\SzalmaNB1\Downloads\cabeceo\visual studio\Portfolio Analyzer"
   venv\Scripts\Activate.ps1
   streamlit run ui\streamlit_app.py
   ```

10. **Access the application**
    - API Documentation: http://localhost:8000/docs
    - Streamlit UI: http://localhost:8501

## Usage

### API Endpoints

- `GET /` - API information
- `GET /portfolio/{portfolio_id}/snapshot?snapshot_date=YYYY-MM-DD` - Get portfolio holdings
- `GET /portfolio/{portfolio_id}/summary?snapshot_date=YYYY-MM-DD` - Get portfolio summary

### Web UI

1. Open http://localhost:8501
2. Select Portfolio ID (default: 1)
3. Choose snapshot date
4. Click "🔄 Load Portfolio" to view holdings
5. Click "📈 Get Summary" for portfolio metrics

### Running ETL

**Manual run:**
```powershell
python -m backend.app.etl.run_daily_etl
```

**Scheduled run (Windows):**
- Double-click `run_etl.bat`
- Or set up Windows Task Scheduler to run daily

## Database Schema

### Tables

- **instruments** - Financial instruments (stocks, bonds, funds)
- **portfolios** - User portfolios
- **holdings** - Portfolio positions
- **prices** - Historical prices
- **fx_rates** - Exchange rates
- **portfolio_values_daily** - Daily portfolio valuations
- **data_sources** - Data source tracking
- **fetch_logs** - ETL execution logs

## Configuration

Edit `.env` file:

```env
DATABASE_URL=postgresql://portfolio_user:portfolio_pass@localhost:5432/portfolio_db
MNB_API_URL=https://www.mnb.hu/arfolyamok.asmx
API_HOST=0.0.0.0
API_PORT=8000
```

## Initial Holdings

Your portfolio includes 9 instruments:

1. Erste Bond Dollar Corporate USD R01 VTA (bond, USD)
2. ERSTE ESG STOCK COST AVERAGING EUR ALAPOK ALAPJA (fund, EUR)
3. MAGYAR TELEKOM (equity, HUF)
4. MOL (equity, HUF)
5. OTP (equity, HUF)
6. 2028/O BÓNUSZ MAGYAR ÁLLAMPAPÍR (bond, HUF)
7. MBH AMBÍCIÓ ABSZOLÚT HOZAMÚ SZÁRMAZTATOTT ALAP (fund, HUF)
8. MBH INGATLANPIACI ABSZOLÚT HOZAMÚ SZÁRMAZTATOTT ALAP (fund, HUF)
9. MBH USA RÉSZVÉNY ALAP HUF SOROZAT (fund, HUF)

## Technology Stack

- **Backend**: FastAPI, SQLAlchemy, Pydantic
- **Database**: PostgreSQL 16 (Docker)
- **UI**: Streamlit
- **Data Processing**: Pandas
- **HTTP Client**: Requests
- **Container**: Docker Compose

## Development

### Running Tests

```powershell
# Test database connection
python -c "from backend.app.db import engine; print('✓ Database connected!' if engine.connect() else '✗ Failed')"

# Test ETL
python -m backend.app.etl.run_daily_etl

# Test API
curl http://localhost:8000/
```

### Adding New Instruments

1. Add rows to `data/initial_holdings.csv`
2. Run: `python -m backend.app.import_initial_data`

### Implementing Price Fetchers

Edit `backend/app/etl/fetch_prices.py` to add real price sources:

- Budapest Stock Exchange API
- Fund issuer websites
- Bond pricing services

## Troubleshooting

### Docker not running
```powershell
# Check Docker
docker ps

# Start container
docker-compose up -d
```

### Port already in use
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process
taskkill /PID <PID> /F
```

### No data in UI
```powershell
# Run ETL to populate data
python -m backend.app.etl.run_daily_etl
```

### Module import errors
```powershell
# Reinstall dependencies
pip install -r requirements.txt
```

## Next Steps

1. **Implement price fetchers** - Add real APIs for BSE, funds, bonds
2. **Add authentication** - Secure API with JWT tokens
3. **Enhanced UI** - Add charts, historical analysis
4. **Automated tests** - Unit and integration tests
5. **Cloud deployment** - Deploy to Azure/AWS
6. **Monitoring** - Add logging and alerts

## License

Private project for personal portfolio management.

## Contact

For questions or issues, contact the development team.

---

**Created**: December 2, 2025  
**Version**: 1.0  
**Status**: MVP Complete ✓
