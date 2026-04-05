import requests
import config  # usamos tus credenciales desde config.py

def obtener_token():
    url = "https://api.siigo.com/auth"
    payload = {
        "username": config.SIIGO_USERNAME,
        "access_key": config.SIIGO_ACCESS_KEY
    }
    headers = {
        "Content-Type": "application/json",
        "Partner-Id": "Lubrisol"
    }

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    if "access_token" in data:
        return f"Bearer {data['access_token']}"
    else:
        print("⚠️ Error al generar token:", data)
        return None

def consultar_cliente(identificacion, token):
    url = f"https://api.siigo.com/v1/customers?identification={identificacion}"
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "Partner-Id": "Lubrisol"
    }

    response = requests.get(url, headers=headers)
    print("Status:", response.status_code)
    print("JSON completo:")
    print(response.json())

if __name__ == "__main__":
    token = obtener_token()
    if token:
        consultar_cliente("901286434", token)  # Cliente de prueba