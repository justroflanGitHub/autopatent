import requests
import json
import os
import uuid
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

CLIENT_ID = os.getenv('GIGACHAT_CLIENT_ID')
CLIENT_SECRET = os.getenv('GIGACHAT_CLIENT_SECRET')

def get_access_token():
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': str(uuid.uuid4())
    }
    data = {
        'scope': 'GIGACHAT_API_PERS',
        'grant_type': 'client_credentials'
    }
    auth = (CLIENT_ID, CLIENT_SECRET)
    response = requests.post(url, headers=headers, data=data, auth=auth, verify=False)
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        raise Exception(f"Ошибка получения токена: {response.status_code} - {response.text}")

def chat_with_gigachat(message):
    access_token = get_access_token()
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    data = {
        "model": "GigaChat",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": message
            }
        ],
        "temperature": 0.7,
        "max_tokens": 1000
    }
    response = requests.post(url, headers=headers, json=data, verify=False)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Ошибка запроса: {response.status_code} - {response.text}")

if __name__ == "__main__":
    try:
        message = "Привет, Gigachat! Расскажи о себе в двух предложениях."
        response = chat_with_gigachat(message)
        print("Ответ от Gigachat:")
        print(json.dumps(response, indent=4, ensure_ascii=False))
    except Exception as e:
        print(f"Ошибка: {e}")
