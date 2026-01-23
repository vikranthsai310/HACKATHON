"""
Configuration settings for HRM Decision System
"""

import os
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True
    
    # LLM Configuration
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-flash"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 2048
    
    # HRM Configuration
    HRM_MODEL_PATH: Optional[str] = None
    HRM_USE_SIMULATION: bool = True
    HRM_DEVICE: str = "cpu"
    
    # Action Executor Configuration
    EXECUTOR_DRY_RUN: bool = True
    EXECUTOR_TIMEOUT: int = 30
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "standard"
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    CORS_ALLOW_CREDENTIALS: bool = True
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings
