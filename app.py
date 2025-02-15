import openai
from playwright.sync_api import sync_playwright
import json
from datetime import datetime, timedelta
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def parse_query(text):
    """Use OpenAI to extract flight search parameters from natural language"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "system",
            "content": "Extract flight details as JSON with format: {departure_date: 'YYYY-MM-DD', origin: 'CITY', destination: 'CITY'}"
        },{
            "role": "user", 
            "content": text
        }]
    )
    return json.loads(response.choices[0].message.content)

def search_flights(params):
    """Search flights using Playwright to scrape Google Flights"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Set to False to see the browser
        page = browser.new_page()
        
        # Format the Google Flights URL
        url = (f"https://www.google.com/travel/flights?q=Flights%20to%20"
               f"{params['destination']}%20from%20{params['origin']}%20on%20"
               f"{params['departure_date']}")
        
        print("\nSearching flights...")
        page.goto(url)
        
        # Wait for results to load
        page.wait_for_selector('div[role="list"]', timeout=10000)
        time.sleep(2)  # Additional wait for dynamic content
        
        # Extract flight information
        flights = []
        flight_elements = page.query_selector_all('div[role="listitem"]')[:3]  # Get first 3 flights
        
        for elem in flight_elements:
            try:
                # Extract details (adjust selectors based on current Google Flights structure)
                airline = elem.query_selector('div[class*="airline"]')
                price = elem.query_selector('div[class*="price"]')
                time_elements = elem.query_selector_all('div[class*="time"]')
                
                if airline and price and time_elements:
                    flights.append({
                        "airline": airline.inner_text(),
                        "price": price.inner_text().replace('$', '').strip(),
                        "departure_time": time_elements[0].inner_text() if time_elements else "N/A",
                        "duration": time_elements[1].inner_text() if len(time_elements) > 1 else "N/A"
                    })
            except Exception as e:
                continue
        
        browser.close()
        return flights

def main():
    try:
        # Get user input
        user_input = input("Flight request: ")
        
        # Parse the query
        print("\nParsing your request...")
        params = parse_query(user_input)
        
        # Search flights
        flights = search_flights(params)
        
        if not flights:
            print("\n❌ No flights found. Please try different dates or cities.")
            return
            
        # Display options
        print("\nAvailable flights:")
        for i, flight in enumerate(flights, 1):
            print(f"{i}. {flight['airline']}")
            print(f"   Departure: {flight['departure_time']}")
            print(f"   Duration: {flight['duration']}")
            print(f"   Price: ${flight['price']}")
            print()
        
        # Get booking confirmation
        choice = input("\nEnter flight number to book (1-3) or 'q' to quit: ")
        if choice.lower() == 'q':
            print("Booking cancelled. Goodbye!")
            return
            
        choice = int(choice)
        if 1 <= choice <= len(flights):
            selected = flights[choice-1]
            confirm = input(f"\nConfirm booking {selected['airline']} for ${selected['price']}? (y/n): ")
            
            if confirm.lower() == 'y':
                booking_ref = f"BOOK{hash(str(selected))%1000:03d}"
                print(f"\n✅ Flight found! Due to scraping limitations, please complete booking at:")
                print(f"https://www.google.com/travel/flights")
                print(f"\nFlight details:")
                print(f"Airline: {selected['airline']}")
                print(f"Price: ${selected['price']}")
                print(f"Reference: {booking_ref}")
            else:
                print("\nBooking cancelled. Goodbye!")
        else:
            print("\nInvalid selection. Booking cancelled.")
            
    except Exception as e:
        print(f"\n❌ Sorry, an error occurred: {str(e)}")
        print("Please try again.")

if __name__ == "__main__":
    main() 