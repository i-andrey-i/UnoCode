import requests
from config import CLIENT_ID, CLIENT_SECRET, CERT_PATH, KEY_PATH, TOKEN_URL, SCOPE

def get_access_token():
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": SCOPE
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    response = requests.post(
        TOKEN_URL,
        data=data,
        headers=headers,
        cert=(CERT_PATH, KEY_PATH)
    )
    response.raise_for_status()
    return response.json()["access_token"]