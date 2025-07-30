import requests
from .config import settings
from .auth import get_access_token

def fetch_bank_transactions():
    token = get_access_token()
    url = f"{settings.API_BASE_URL}/transactions"  # используем settings.API_BASE_URL

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers, cert=(settings.CERT_PATH, settings.KEY_PATH))  # используем settings
    response.raise_for_status()
    return response.json()