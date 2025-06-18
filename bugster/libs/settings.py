# bugster/libs/settings.py
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from bugster.libs.enums import Environment


class LibsSettings(BaseModel):
    """Pydantic settings for the `libs` module."""
    
    # HARDCODED FOR TESTING
    environment: Environment = Environment.LOCAL
    
    # URLs por ambiente
    _api_urls: dict = {
        Environment.LOCAL: "http://localhost:8000",
        Environment.DEVELOPMENT: "https://dev.bugster.api",
        Environment.PRODUCTION: "https://api.bugster.app"
    }
    
    # WebSocket URLs por ambiente
    _ws_urls: dict = {
        Environment.LOCAL: "ws://localhost:8765",
        Environment.DEVELOPMENT: "wss://websocket.bugster.app/prod/",
        Environment.PRODUCTION: "wss://websocket.bugster.app/prod/"
    }

    # Configuraciones específicas por ambiente
    debug: bool = False
    log_level: str = "INFO"
    bugster_api_url: str = ""
    
    def __init__(self, **kwargs):
        """Initialize settings."""
        super().__init__(**kwargs)
        self.environment = kwargs.get("environment", Environment.LOCAL)
        self.bugster_api_url = self._get_api_url()
        
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
        extra="ignore",
        env_prefix="BUGSTER_"
    )


libs_settings = LibsSettings()