"""
Bugster API service for CLI.
"""

import aiohttp
import logging
from typing import Dict, Optional
from bugster.utils.user_config import get_api_key

# Set up logging
logger = logging.getLogger(__name__)

API_BASE_URL = "https://api.bugster.app/v1"


async def get_user_info() -> Optional[Dict]:
    """Get user information from Bugster API."""
    api_key = get_api_key()
    if not api_key:
        logger.error("No API key found")
        return None

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    url = f"{API_BASE_URL}/me"
    logger.info(f"Fetching user info from {url}")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Successfully got user info: {data}")
                    return {
                        "org_id": data.get("org_id"),
                        "user_id": data.get("user_id")
                    }
                logger.error(f"Failed to get user info. Status: {response.status}")
                return None
        except Exception as e:
            logger.error(f"Error getting user info: {str(e)}")
            return None 