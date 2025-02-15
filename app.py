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
        browser = p.chromium.launch(headless=False)  # Set to False to help with bot detection
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        )
        page = context.new_page()
        
        # Format the Google Flights URL
        url = (f"https://www.google.com/travel/flights?q=Flights%20to%20"
               f"{params['destination']}%20from%20{params['origin']}%20on%20"
               f"{params['departure_date']}")
        
        print("\nSearching flights...")
        try:
            # Navigate to the page
            page.goto(url)
            
            # Wait for any of these selectors that might indicate results have loaded
            selectors = [
                '[role="main"] [role="list"]',
                '[role="main"] [role="article"]',
                'div[class*="gws-flights-results__"]',
                'div[class*="gws-flights__"]'
            ]
            
            # Try each selector with longer timeout
            selector_found = False
            for selector in selectors:
                try:
                    print(f"Trying selector: {selector}")
                    page.wait_for_selector(selector, timeout=8000)
                    print(f"Found results with selector: {selector}")
                    selector_found = True
                    break
                except Exception as e:
                    print(f"Selector {selector} not found: {str(e)}")
                    continue
            
            if not selector_found:
                print("No selectors matched. Trying alternative approach...")
            
            # Additional wait for dynamic content
            page.wait_for_timeout(5000)
            
            # Try multiple selectors for flight cards
            flight_elements = []
            card_selectors = [
                'div[role="listitem"]',
                '[role="main"] li',
                'div[class*="gws-flights-results__result-item"]',
                'div[class*="gws-flights__"]'
            ]
            
            for selector in card_selectors:
                print(f"Trying to find flight cards with selector: {selector}")
                flight_elements = page.query_selector_all(selector)
                if flight_elements:
                    print(f"Found {len(flight_elements)} flight elements with selector: {selector}")
                    break
            
            flights = []
            for elem in flight_elements[:3]:  # Get first 3 flights
                try:
                    # Take a screenshot of the element for debugging
                    elem.screenshot(path=f"flight_card_{len(flights)}.png")
                    
                    # Try multiple selectors for each piece of information
                    airline = None
                    airline_selectors = [
                        '[class*="airline"]', 
                        '[class*="carrier"]',
                        'img[alt*="airline"]',
                        '[class*="operator"]'
                    ]
                    for airline_selector in airline_selectors:
                        airline = elem.query_selector(airline_selector)
                        if airline:
                            print(f"Found airline with selector: {airline_selector}")
                            break
                    
                    price = None
                    price_selectors = [
                        '[class*="price"]',
                        '[class*="amount"]',
                        'span[class*="gws-flights-results__price"]',
                        'div[class*="gws-flights-results__price"]'
                    ]
                    for price_selector in price_selectors:
                        price = elem.query_selector(price_selector)
                        if price:
                            print(f"Found price with selector: {price_selector}")
                            break
                    
                    time_elements = []
                    time_selectors = [
                        '[class*="time"]',
                        '[class*="duration"]',
                        '[class*="gws-flights-results__times"]',
                        '[class*="gws-flights-results__duration"]'
                    ]
                    for time_selector in time_selectors:
                        time_elements = elem.query_selector_all(time_selector)
                        if time_elements:
                            print(f"Found time elements with selector: {time_selector}")
                            break
                    
                    # Get the raw HTML for debugging
                    html_content = elem.inner_html()
                    print(f"\nFlight card HTML:\n{html_content[:200]}...")  # Print first 200 chars
                    
                    if airline or price:  # At least one piece of information found
                        flight_info = {
                            "airline": airline.inner_text() if airline else "Unknown Airline",
                            "price": price.inner_text().replace('$', '').strip() if price else "Price not available",
                            "departure_time": time_elements[0].inner_text() if time_elements else "Time not available",
                            "duration": time_elements[1].inner_text() if len(time_elements) > 1 else "Duration not available"
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
            # Take a final screenshot before closing
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