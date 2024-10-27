import ollama
import yfinance as yf
from faiss import symbol
from haversine import haversine
import requests
import json

client = ollama.Client()
model = "llama3.2"
mylat = 47.60621
mylon = -122.33207

def get_distance(latitude, longitude):
        distance_in_miles = haversine((mylat, mylon), latitude, longitude, unit='mi')
        return distance_in_miles

def get_stock_price(symbol):
    try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="1d", interval="1m")
            latest = hist.iloc[-1]
            return {
                "timestamp": str(latest.name),
                "open": latest["Open"],
                "high": latest["High"],
                "low": latest["Low"],
                "close": latest["Close"],
                "volume": latest["Volume"]
            }
    except:
            print(f"Could not find relevant STOCK PRICE FOR {symbol}")

def get_stock_symbol(stock_name):
        schema = {
                "stock": "string",
                "symbol": "string"
        }

        payload = {
                "model": model,
                "messages": [
                        {"role": "system",
                         "content": f"You are a helpful assistant who is going to be an expert in Finance. Get the Stock Code of {stock_name}. Output in JSON using the schema defined here: {schema}."},
                        {"role": "user", "content": stock_name}
                ],
                "options": {
                        "temperature": 0.0
                },
                "format": "json",
                "stream": False
        }

        response = requests.post("http://localhost:11434/api/chat", json=payload)
        output_info = json.loads(response.json()["message"]["content"])

        return output_info["symbol"]

available_functions = {"get_stock_price": get_stock_price}

def converse_with_function_calling(messages):
        response = ollama.chat(
            model=model,
            messages=messages,
            tools=[{
              'type': 'function',
              'function': {
                'name': 'get_stock_price',
                'description': 'Get the stock price of a stock symbol',
                'parameters': {
                  'type': 'object',
                  'properties': {
                    'city': {
                      'type': 'string',
                      'description': 'The stock symbol for which to retrieve data.',
                    },
                  },
                  'required': ['symbol'],
                },
              },
            },
          ],
        )

        messages.append(response["message"])

        if not response["message"].get("tool_calls"):
                print("The model didn't use the function. Its response was:")
                print(response["message"]["content"])

        if response["message"].get("tool_calls"):
                for tool in response["message"]["tool_calls"]:
                        function_to_call = available_functions[tool["function"]["name"]]
                        # print(function_to_call(get_stock_symbol(stock_name=company)))
                        function_response = function_to_call(get_stock_symbol(stock_name=company))
                        messages.append(
                                {
                                        "role": "tool",
                                        "content": json.dumps(function_response),
                                }
                        )
                final_response = client.chat(model=model, messages=messages)
                print(final_response["message"]["content"])

company = "microsoft"
messages = [{"role": "user", "content": f"what is the stock price of {company} today"}]
converse_with_function_calling(messages=messages)