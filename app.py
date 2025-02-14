import openai
import requests

# Mock config
OPENAI_KEY = "sk-xxx"
KIWI_ENDPOINT = "https://api.tequila.kiwi.com/v2/search"

def parse_query(text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "system",
            "content": "Extract ONLY as JSON: {departure_date: 'YYYY-MM-DD', origin: 'CITY', destination: 'CITY'}"
        },{
            "role": "user", 
            "content": text
        }]
    )
    return eval(response.choices[0].message.content)

def get_flights(params):
    return requests.get(KIWI_ENDPOINT, params=params).json()

def main():
    user_input = input("Flight request: ")
    params = parse_query(user_input)
    
    print(f"\nSearching {params['origin']}->{params['destination']}...")
    flights = get_flights({
        "fly_from": params["origin"],
        "fly_to": params["destination"],
        "date_from": params["departure_date"],
        "limit": 3
    })
    
    print("\nTop options:")
    for i,f in enumerate(flights["data"][:3]):
        print(f"{i+1}. {f['airlines'][0]} ${f['price']}")
    
    if input("\nBook #1? (y/n): ") == "y":
        print("✅ Mock booking complete!")

if __name__ == "__main__":
    main() 