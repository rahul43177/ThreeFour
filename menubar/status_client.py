import requests

API_URL = "http://127.0.0.1:8787/api/status"


def get_status() -> dict | None:
    """Fetch current status from ThreeFour API. Returns None on any error."""
    try:
        response = requests.get(API_URL, timeout=2)
        response.raise_for_status()
        return response.json()
    except Exception:
        return None
