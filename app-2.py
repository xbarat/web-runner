import requests
from datetime import datetime

def get_bitcoin_price():
    """Retrieve current Bitcoin price using CoinGecko API"""
    try:
        response = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={
                "ids": "bitcoin",
                "vs_currencies": "usd",
                "include_last_updated_at": "true"
            }
        )
        response.raise_for_status()
        data = response.json()
        
        if "last_updated_at" not in data["bitcoin"]:
            return {"error": "API response missing timestamp data"}
            
        return {
            "price": data["bitcoin"]["usd"],
            "last_updated": datetime.fromtimestamp(data["bitcoin"]["last_updated_at"]),
            "currency": "USD"
        }
            
    except requests.exceptions.RequestException as e:
        return {"error": f"API Error: {str(e)}"}
    except (KeyError, TypeError) as e:
        return {"error": f"Data parsing error: {str(e)}"}
    except ValueError as e:
        return {"error": f"Invalid timestamp format: {str(e)}"}

def format_response(price_data):
    """Format the price data for user display"""
    if "error" in price_data:
        return f"❌ Error: {price_data['error']}"
        
    return (
        f"₿ Bitcoin Price Update\n"
        f"-----------------------\n"
        f"Price: ${price_data['price']:,.2f}\n"
        f"Last Updated: {price_data['last_updated'].strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
        f"Currency: {price_data['currency']}"
    )

def handle_query(query):
    """Simple RAG-style query handler"""
    if not any(keyword in query.lower() for keyword in ["bitcoin", "btc", "price"]):
        return "I specialize in Bitcoin price information. Ask me about BTC's current value."
    
    price_data = get_bitcoin_price()
    return format_response(price_data)

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