from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    GL_API_TOKEN: str
    PROFILE_ID: Optional[str] = None
    INSTA_USERNAME: str
    INSTA_PASSWORD: str
    INSTA_SECRET_CODE: str
    BRIGHTDATA_USER_NAME: str
    BRIGHTDATA_PASSWORD: str
    BRIGHTDATA_ZONE: str
    PROXY_COUNTRY: str
    PROXY_IP: Optional[str] = None

    model_config = SettingsConfigDict(
        # env_file="../.env",
        # extra="forbid"
    )

Config = Settings()
