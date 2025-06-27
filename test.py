import requests
from dotenv import load_dotenv
import os

load_dotenv()

url = (
    "https://fwubmi.openai.azure.com/openai/deployments/fwuBMI_gpt-4.1/chat/completions"
)
params = {"api-version": "2025-01-01-preview"}

headers = {"Content-Type": "application/json", "api-key": os.getenv("OPENAI_API_KEY")}

data = {
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me a joke about computers."},
    ]
}

response = requests.post(url, params=params, headers=headers, json=data)
print(response.json())
