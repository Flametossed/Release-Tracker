from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # IGDB/Twitch credentials
    igdb_client_id: str
    igdb_client_secret: str
    
    # Database
    mongo_url: str = "mongodb://localhost:27017/gametracker"
    
    # Application settings
    app_name: str = "Game Release Tracker API"
    debug: bool = False
    
    # Cache settings
    cache_ttl: int = 3600  # 1 hour
    
    # Rate limiting
    requests_per_second: float = 3.5  # Slightly under IGDB's 4/sec limit
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()