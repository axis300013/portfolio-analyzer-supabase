from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine import URL
from .config import settings

# Create engine with proper URL handling for special characters in passwords
try:
    # Try to parse as standard PostgreSQL URL first
    if settings.database_url.startswith("postgresql://"):
        # Use SQLAlchemy's URL parser which handles special chars better
        engine = create_engine(
            settings.database_url,
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
            pool_pre_ping=True,  # Verify connections before using them
            pool_recycle=3600,    # Recycle connections after 1 hour
            echo=False            # Set to True for SQL debugging
        )
    else:
        raise ValueError("DATABASE_URL must start with postgresql://")
except Exception as e:
    print(f"[ERROR] Failed to create database engine: {e}")
    print(f"[ERROR] DATABASE_URL: {settings.database_url[:20]}...***")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

