import requests
import json
from django.conf import settings


class OdooAPIClient:
    def __init__(self, session_id=None):
        """
        Initializes the API client with a base URL and optional session ID.
        """
        self.base_url = settings.ODOO_BASE_URL
        self.session_id = session_id

    def _get_headers(self):
        """
        Returns the required headers for API requests.
        """
        headers = {
            "Content-Type": "application/json",
        }
        if self.session_id:
            headers["Cookie"] = f"session_id={self.session_id}"
        return headers

    def send_request(self, endpoint, method="POST", data=None):
        """
        Sends an HTTP request to the specified endpoint with the given method and data.
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()

        try:
            response = requests.request(method, url, headers=headers, json=data)
            response.raise_for_status()  # Raise HTTP errors (4xx, 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Request Failed: {e}")
            # return {"error": str(e)}
            return False




