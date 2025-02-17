import requests
import openai
from datetime import datetime
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def parse_query(text: str) -> dict:
    """Use LLM to extract cryptocurrency and currency from natural language query"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": f"Extract cryptocurrency and currency from: {text}"
            }],
            functions=[{
                "name": "get_crypto_price",
                "description": "Get current cryptocurrency price",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "cryptocurrency": {
                            "type": "string",
                            "enum": ["bitcoin", "ethereum", "solana"],
                            "description": "Cryptocurrency to get price for"
                        },
                        "currency": {
                            "type": "string",
                            "enum": ["usd", "eur", "gbp"],
                            "description": "Fiat currency for price display"
                        }
                    },
                    "required": ["cryptocurrency", "currency"]
                }
            }],
            function_call={"name": "get_crypto_price"}
        )
        
        args = json.loads(response.choices[0].message.function_call.arguments)
        return args
        
    except Exception as e:
        raise ValueError(f"LLM parsing error: {str(e)}")

def get_crypto_price(crypto: str, currency: str) -> dict:
    """Retrieve cryptocurrency price using CoinGecko API"""
    try:
        response = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={
                "ids": crypto,
                "vs_currencies": currency,
                "include_last_updated_at": "true"
            }
        )
        response.raise_for_status()
        data = response.json()
        
        return {
            "price": data[crypto][currency],
            "last_updated": datetime.fromtimestamp(data[crypto]["last_updated_at"]),
            "currency": currency.upper(),
            "crypto": crypto.capitalize()
        }
            
    except requests.exceptions.RequestException as e:
        return {"error": f"API Error: {str(e)}"}
    except KeyError as e:
        return {"error": f"Data parsing error: {str(e)}"}

def handle_query(query: str) -> str:
    """RAG-based query handler with API orchestration"""
    try:
        # LLM-based parsing
        params = parse_query(query)
        
        # API call orchestration
        price_data = get_crypto_price(
            params['cryptocurrency'],
            params['currency']
        )
        
        # Format response
        if "error" in price_data:
            return f"❌ Error: {price_data['error']}"
            
        return (
            f"💰 {price_data['crypto']} Price\n"
            f"-----------------------\n"
            f"Price: {price_data['currency']} {price_data['price']:,.2f}\n"
            f"Last Updated: {price_data['last_updated'].strftime('%Y-%m-%d %H:%M:%S UTC')}"
        )
        
    except Exception as e:
        return f"❌ System error: {str(e)}"

def main():
    print("Bitcoin Price Checker")
    print("---------------------")
    print("Type 'exit' to quit\n")
    
    while True:
        user_input = input("Your question: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            break
            
        response = handle_query(user_input)
        print("\n" + response + "\n")

if __name__ == "__main__":
    main() 