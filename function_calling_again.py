import requests
import json
import sys
from haversine import haversine

stock_name = "Apple"
schema = {
                "stock": "string",
                "symbol": "string"
        }

payload = {
  "model": "llama3.2",
  "messages": [
    # {"role": "system", "content": f"You are a helpful assistant who is going to be an expert in Finance. Get the Stock Code of {stock_name}. Output in JSON using the schema defined here: {schema}."},
    {"role": "user", "content": f"You are a helpful assistant who is going to be an expert in Finance. Get the Stock Code of {stock_name}. Output in JSON using the schema defined here: {schema}."}
  ],
  "options": {
    "temperature": 0.0
  },
  "format": "json",
  "stream": False
}

response = requests.post("http://localhost:11434/api/chat", json=payload)

cityinfo = json.loads(response.json()["message"]["content"])

print(cityinfo['symbol'])

