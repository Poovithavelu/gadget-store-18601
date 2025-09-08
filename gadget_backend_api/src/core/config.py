from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Note: Do not store secrets in code. Provide them via environment variables.
    """

    # FastAPI/general
    ENV: str = Field(default="development", description="Environment name")
    DEBUG: bool = Field(default=True, description="Enable debug mode")
    CORS_ALLOW_ORIGINS: str = Field(default="*", description="Comma separated list of allowed origins")

    # Security / JWT
    JWT_SECRET_KEY: str = Field(default="CHANGE_ME_SECRET", description="JWT secret key (set in .env)")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60 * 24, description="Access token expiry in minutes")

    # Database (MySQL)
    # Use environment variables provided by the database container
    MYSQL_URL: Optional[str] = Field(default=None, description="Full SQLAlchemy MySQL URL. If not set, will be constructed.")
    MYSQL_HOST: str = Field(default="localhost", description="MySQL host")
    MYSQL_PORT: int = Field(default=3306, description="MySQL port")
    MYSQL_USER: str = Field(default="root", description="MySQL user")
    MYSQL_PASSWORD: str = Field(default="password", description="MySQL password")
    MYSQL_DB: str = Field(default="gadget_store", description="MySQL database name")

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    # PUBLIC_INTERFACE
    def sqlalchemy_database_uri(self) -> str:
        """Build the SQLAlchemy connection URI for MySQL if MYSQL_URL is not provided."""
        if self.MYSQL_URL:
            return self.MYSQL_URL
        return f"mysql+aiomysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}?charset=utf8mb4"


@lru_cache
def get_settings() -> Settings:
    """Load and cache settings."""
    return Settings()


settings = get_settings()

# OpenAPI tag metadata
openapi_tags = [
    {"name": "System", "description": "System operations like health check."},
    {"name": "Auth", "description": "User authentication operations."},
    {"name": "Users", "description": "User management operations."},
    {"name": "Products", "description": "Product catalog operations."},
    {"name": "Orders", "description": "Order management operations."},
]
