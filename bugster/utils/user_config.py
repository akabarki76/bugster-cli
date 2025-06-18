"""
User configuration utilities for Bugster CLI.
"""

import os
import json
from pathlib import Path
from typing import Optional

CONFIG_FILE = Path.home() / ".bugsterrc"
ENV_API_KEY = "BUGSTER_CLI_API_KEY"


def get_user_config_file() -> Path:
    """Get the path to the config file."""
    return Path(CONFIG_FILE)


def load_user_config() -> dict:
    """Load configuration from file."""
    config_file = get_user_config_file()
    if not config_file.exists():
        return {}

    try:
        with open(config_file) as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}


def save_user_config(config: dict) -> None:
    """Save configuration to file."""
    config_file = get_user_config_file()

    # Create parent directories if they don't exist
    config_file.parent.mkdir(parents=True, exist_ok=True)

    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)


def get_api_key() -> Optional[str]:
    """Get API key from environment or config file."""
    # First check environment variable
    api_key = os.getenv(ENV_API_KEY)
    if api_key:
        return api_key

    # Then check config file
    config = load_user_config()
    return config.get("apiKey")


def save_api_key(api_key: str) -> None:
    """Save API key to config file."""
    config = load_user_config()
    config["apiKey"] = api_key
    save_user_config(config)


def get_org_id() -> Optional[str]:
    """Get organization ID from config file."""
    config = load_user_config()
    return config.get("orgId")


def save_org_id(org_id: str) -> None:
    """Save organization ID to config file."""
    config = load_user_config()
    config["orgId"] = org_id
    save_user_config(config)


def get_user_id() -> Optional[str]:
    """Get user ID from config file."""
    config = load_user_config()
    return config.get("userId")


def save_user_id(user_id: str) -> None:
    """Save user ID to config file."""
    config = load_user_config()
    config["userId"] = user_id
    save_user_config(config)
