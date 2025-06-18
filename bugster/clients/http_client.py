from typing import Any, Dict, Optional

import requests
from loguru import logger

from bugster.libs.settings import libs_settings


class BugsterHTTPError(Exception):
    """Bugster HTTP error."""

    def __init__(self, message: str):
        """Initialize the Bugster HTTP error."""
        super().__init__(message)


class HTTPClient:
    """HTTP client for making API requests."""

    def __init__(self, base_url: str, timeout: int = 60):
        """Initialize the HTTP client."""
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()

    def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> requests.Response:
        """Make a PUT request."""
        return self._make_request("PUT", endpoint, data=data, json=json, **kwargs)

    def get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs
    ) -> requests.Response:
        """Make a GET request."""
        return self._make_request("GET", endpoint, params=params, **kwargs)

    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> requests.Response:
        """Make a POST request."""
        return self._make_request("POST", endpoint, data=data, json=json, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        """Make a DELETE request."""
        return self._make_request("DELETE", endpoint, **kwargs)

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[dict]:
        """Make an HTTP request and handle common errors."""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(method, url, **kwargs)
            
            # If it's a 404 from the issues endpoint, don't log it as an error
            if response.status_code == 404 and "/issues" in endpoint:
                return None
                
            if not response.ok:
                logger.error(f"HTTP error for {method} {url}: {response.status_code} {response.reason} - {response.text}")
                response.raise_for_status()
            
            return response.json() if response.content else None
            
        except requests.exceptions.RequestException as e:
            if isinstance(e, requests.exceptions.HTTPError) and e.response.status_code == 404 and "/issues" in endpoint:
                return None
            logger.error(f"Request failed: {str(e)}")
            raise

    def set_auth_header(self, token: str, auth_type: str = "Bearer"):
        """Set authentication header for all requests."""
        self.session.headers.update({"Authorization": f"{auth_type} {token}"})

    def set_headers(self, headers: Dict[str, str]):
        """Set custom headers for all requests."""
        self.session.headers.update(headers)

    def remove_header(self, header_name: str):
        """Remove a header from all requests."""
        self.session.headers.pop(header_name, None)

    def close(self):
        """Close the session."""
        self.session.close()

    def __enter__(self):
        """Enter the context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager."""
        self.close()


class BugsterHTTPClient(HTTPClient):
    """HTTP client for the Bugster API."""

    def __init__(self):
        """Initialize the HTTP client."""
        super().__init__(base_url=libs_settings.bugster_api_url)
