import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # App General info
    PROJECT_NAME: str = "Portfolio & AI Agent Backend"
    API_V1_STR: str = "/api/v1"
    
    # Auth
    JWT_SECRET: str = "secret"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # 24 hours
    
    # Databases
    ATLAS_URL: Optional[str] = None
    atlas_URL: Optional[str] = None  
    DB_NAME: str = "portfolio_data"
    atlas_DB_NAME: Optional[str] = None 
    
    # Cloudinary (Optional)
    CLOUDINARY_CLOUD_NAME: Optional[str] = None
    CLOUDINARY_API_KEY: Optional[str] = None
    CLOUDINARY_API_SECRET: Optional[str] = None
    CLOUDINARY_URL: Optional[str] = None 

    # Load from .env in project root
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def get_atlas_url(self) -> str:
        # Prioritize lowercase or uppercase from env
        return self.atlas_URL or self.ATLAS_URL or os.getenv("atlas_URL") or "mongodb://localhost:27017"

    @property
    def get_db_name(self) -> str:
        return self.atlas_DB_NAME or self.DB_NAME or os.getenv("atlas_DB_NAME") or "portfolio_data"

    @property
    def is_cloudinary_configured(self) -> bool:
        # We are good if we have individual keys OR the combined URL
        return (self.CLOUDINARY_CLOUD_NAME and self.CLOUDINARY_API_KEY) or self.CLOUDINARY_URL

settings = Settings()
