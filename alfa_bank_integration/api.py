import requests
from config import API_BASE_URL, CERT_PATH, KEY_PATH
from auth import get_access_token

def fetch_bank_transactions():
    token = get_access_token()
    url = f"{API_BASE_URL}/transactions"  # заменить на конкретный путь из API

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers, cert=(CERT_PATH, KEY_PATH))
    response.raise_for_status()
    return response.json()