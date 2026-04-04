import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # App General info
    PROJECT_NAME: str = "Portfolio & AI Agent Backend"
    API_V1_STR: str = "/api/v1"
    
    # Auth
    JWT_SECRET: str = os.getenv("JWT_SECRET", "secret")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # 24 hours
    
    # Databases
    ATLAS_URL: str = os.getenv("atlas_URL")
    DB_NAME: str = os.getenv("atlas_DB_NAME", "portfolio_data")
    
    # Cloudinary
    CLOUDINARY_CLOUD_NAME: str = os.getenv("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY: str = os.getenv("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET: str = os.getenv("CLOUDINARY_API_SECRET")

settings = Settings()
