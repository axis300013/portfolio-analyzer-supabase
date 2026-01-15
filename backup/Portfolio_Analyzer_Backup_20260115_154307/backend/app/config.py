from pydantic_settings import BaseSettings
import os
from pathlib import Path

class Settings(BaseSettings):
    # Database Configuration (supports both local and Supabase)
    database_url: str
    
    # MNB API for exchange rates
    mnb_api_url: str = "https://api.mnb.hu/FeedService"
    
    # API Server Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # UI Configuration
    ui_port: int = 8501
    
    # Optional: Database connection pool settings for Supabase
    database_pool_size: int = 5
    database_max_overflow: int = 10
    
    class Config:
        # Look for .env in the project root (parent of backend/)
        env_file = str(Path(__file__).parent.parent.parent / ".env")
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields in .env (like SUPABASE_ANON_KEY for mobile app)

settings = Settings()

# Validate connection string
if not settings.database_url:
    raise ValueError(
        "DATABASE_URL not found in environment variables. "
        "Please create a .env file with your Supabase connection string. "
        "See .env.example for template."
    )

