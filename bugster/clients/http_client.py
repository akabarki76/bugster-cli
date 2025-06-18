import requests
from typing import Any, Dict, Optional

from bugster.libs.settings import libs_settings

class BugsterHTTPError(Exception):
    """Bugster HTTP error."""
    pass

class HTTPClient:
    def __init__(self, base_url: str, timeout: int = 60):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
        url = f"{self.base_url}{endpoint}"
        response = self.session.get(url, params=params, timeout=self.timeout, **kwargs)
        response.raise_for_status()
        return response.json() if response.content else None

    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None, json: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
        url = f"{self.base_url}{endpoint}"
        response = self.session.post(url, data=data, json=json, timeout=self.timeout, **kwargs)
        response.raise_for_status()
        return response.json() if response.content else None

    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None, json: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
        url = f"{self.base_url}{endpoint}"
        response = self.session.put(url, data=data, json=json, timeout=self.timeout, **kwargs)
        response.raise_for_status()
        return response.json() if response.content else None

    def delete(self, endpoint: str, **kwargs) -> Any:
        url = f"{self.base_url}{endpoint}"
        response = self.session.delete(url, timeout=self.timeout, **kwargs)
        response.raise_for_status()
        return response.json() if response.content else None

    def set_auth_header(self, token: str, auth_type: str = "Bearer"):
        self.session.headers.update({"Authorization": f"{auth_type} {token}"})

    def set_headers(self, headers: Dict[str, str]):
        self.session.headers.update(headers)

    def remove_header(self, header_name: str):
        self.session.headers.pop(header_name, None)

    def close(self):
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

class BugsterHTTPClient(HTTPClient):
    def __init__(self):
        super().__init__(base_url=libs_settings.bugster_api_url)
