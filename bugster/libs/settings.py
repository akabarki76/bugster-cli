from enum import Enum

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    LOCAL = "localhost"
    DEVELOPMENT = "development"
    PRODUCTION = "production"


class LibsSettings(BaseSettings):
    """Pydantic settings for the `libs` module."""

    environment: Environment = Field(default=Environment.PRODUCTION)

    # API Configuration
    bugster_api_url: str = Field(default="api_url_placeholder")
    websocket_url: str = Field(default="websocket_url_placeholder")

    # PostHog Analytics Configuration
    posthog_api_key: str = Field(default="phc_api_key_placeholder")
    posthog_host: str = Field(default="https://us.i.posthog.com")
    posthog_enabled: bool = Field(default=True)



    # Configuraciones específicas por ambiente
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")

    def __init__(self, **kwargs):
        """Initialize settings."""
        super().__init__(**kwargs)
        # Auto-configurar según el ambiente
        if self.environment == Environment.LOCAL:
            self.debug = True
            self.log_level = "DEBUG"
        elif self.environment == Environment.DEVELOPMENT:
            self.debug = True
            self.log_level = "INFO"
        else:  # PRODUCTION
            self.debug = False
            self.log_level = "WARNING"

    def _get_api_url(self) -> str:
        """Return the API URL based on the environment."""
        return self._api_urls[self.environment]
    
    @property
    def websocket_url(self) -> str:
        """Return the WebSocket URL based on the environment."""
        return self._ws_urls[self.environment]

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore", 
        env_prefix="BUGSTER_"
    )


libs_settings = LibsSettings()
