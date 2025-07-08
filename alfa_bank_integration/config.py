import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("ALFA_CLIENT_ID")
CLIENT_SECRET = os.getenv("ALFA_CLIENT_SECRET")
CERT_PATH = os.getenv("ALFA_CERT_PATH", "certs/Company.cer")
KEY_PATH = os.getenv("ALFA_KEY_PATH", "certs/Company.key")
TOKEN_URL = os.getenv("ALFA_TOKEN_URL", "https://baas.alfabank.ru/oidc/token")
API_BASE_URL = os.getenv("ALFA_API_BASE_URL", "https://baas.alfabank.ru/api")
SCOPE = os.getenv("ALFA_SCOPE", "")