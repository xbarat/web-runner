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
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        )
        page = context.new_page()
        
        url = (f"https://www.google.com/travel/flights?q=Flights%20to%20"
               f"{params['destination']}%20from%20{params['origin']}%20on%20"
               f"{params['departure_date']}")
        
        print("\nSearching flights...")
        try:
            page.goto(url)
            
            # Wait for the main content to load
            print("Waiting for main content...")
            page.wait_for_selector('[role="main"]', timeout=10000)
            
            # Additional wait for dynamic content
            page.wait_for_timeout(5000)
            
            # Find flight cards
            print("Looking for flight cards...")
            flight_elements = page.query_selector_all('[role="main"] li')
            
            if not flight_elements:
                print("No flight elements found")
                return []
                
            print(f"Found {len(flight_elements)} potential flight elements")
            
            flights = []
            for elem in flight_elements[:3]:  # Get first 3 flights
                try:
                    # Get the raw HTML for debugging
                    html_content = elem.inner_html()
                    print(f"\nProcessing flight card:\n{html_content[:200]}...")
                    
                    # Updated selectors based on the actual HTML structure
                    airline = None
                    airline_selectors = [
                        'img[alt*="logo"]',  # Airline logos often have "logo" in alt text
                        '.JMc5Xc',           # Class seen in the HTML
                        '[class*="operator"]',
                        '[class*="airline"]'
                    ]
                    for airline_selector in airline_selectors:
                        airline = elem.query_selector(airline_selector)
                        if airline:
                            print(f"Found airline with selector: {airline_selector}")
                            # If it's an image, try to get the alt text
                            if 'img' in airline_selector:
                                airline_text = airline.get_attribute('alt')
                            else:
                                airline_text = airline.inner_text()
                            if airline_text:
                                break
                    
                    # Try to find price
                    price = None
                    price_selectors = [
                        '[class*="YMlIz"]',    # Common price class
                        '[class*="gQ6yfe"]',   # Class from the HTML
                        'span:has-text("$")',  # Any span containing a dollar sign
                        '[class*="price"]'
                    ]
                    for price_selector in price_selectors:
                        price = elem.query_selector(price_selector)
                        if price:
                            print(f"Found price with selector: {price_selector}")
                            break
                    
                    # Try to find time information
                    time_info = None
                    time_selectors = [
                        '.zxVSec',           # Time class
                        '.vmXl8d',           # Duration class
                        '[class*="time"]',
                        '[class*="duration"]'
                    ]
                    for time_selector in time_selectors:
                        time_info = elem.query_selector(time_selector)
                        if time_info:
                            print(f"Found time info with selector: {time_selector}")
                            break
                    
                    # If we found any information, add it to flights
                    if airline_text or price:
                        flight_info = {
                            "airline": airline_text if airline_text else "Unknown Airline",
                            "price": price.inner_text().strip() if price else "Price not available",
                            "departure_time": time_info.inner_text() if time_info else "Time not available",
                            "duration": "Duration not available"  # We'll add duration in a future update
                        }
                        print(f"Extracted flight info: {flight_info}")
                        flights.append(flight_info)
                except Exception as e:
                    print(f"Error extracting flight details: {str(e)}")
                    continue
            
            if flights:
                print(f"\nSuccessfully found {len(flights)} flights")
                return flights
            else:
                print("\nNo flights could be extracted from the page")
                return []
            
        except Exception as e:
            print(f"Error during flight search: {str(e)}")
            return []
        
        finally:
            try:
                page.screenshot(path="final_page.png")
            except:
                pass
            browser.close()

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