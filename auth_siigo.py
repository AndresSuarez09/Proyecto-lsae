# auth_siigo.py

import requests
import config

def obtener_token_siigo():
    print("🔐 Generando token JWT desde Siigo...")

    url = "https://api.siigo.com/auth"
    headers = {
        "Content-Type": "application/json",
        "Partner-Id": "Lubrisol"  # Lubrisol de Colombia LTDA
    }

    body = {
        "username": config.SIIGO_USERNAME,
        "access_key": config.SIIGO_ACCESS_KEY
    }

    response = requests.post(url, headers=headers, json=body)
    response.raise_for_status()

    data = response.json()
    token = data.get("access_token")

    if not token or not token.startswith("eyJ"):
        raise ValueError("❌ Token inválido recibido desde Siigo.")

    return f"Bearer {token}"
