from enum import Enum


class Environment(str, Enum):
    """Environment enum for the application."""
    LOCAL = "local"
    DEVELOPMENT = "development"
    PRODUCTION = "production" 