import requests
from .config import settings

def get_access_token():
    data = {
        "grant_type": "client_credentials",
        "client_id": settings.CLIENT_ID,
        "client_secret": settings.CLIENT_SECRET,
        "scope": settings.SCOPE
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    response = requests.post(
        settings.TOKEN_URL,
        data=data,
        headers=headers,
        cert=(settings.CERT_PATH, settings.KEY_PATH)
    )
    response.raise_for_status()
    return response.json()["access_token"]