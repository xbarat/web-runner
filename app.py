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
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "user", 
                "content": text
            }],
            functions=[{
                "name": "extract_flight_details",
                "description": "Extract flight search parameters from natural language query",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "departure_date": {
                            "type": "string",
                            "description": "Flight departure date in YYYY-MM-DD format"
                        },
                        "origin": {
                            "type": "string",
                            "description": "City of departure (no airport codes)"
                        },
                        "destination": {
                            "type": "string",
                            "description": "City of arrival (no airport codes)"
                        }
                    },
                    "required": ["departure_date", "origin", "destination"]
                }
            }],
            function_call={"name": "extract_flight_details"}
        )
        
        # Extract the function call arguments
        function_args = json.loads(response.choices[0].message.function_call.arguments)
        
        # Validate date format
        try:
            datetime.strptime(function_args['departure_date'], '%Y-%m-%d')
        except ValueError:
            raise ValueError("Invalid date format. Expected YYYY-MM-DD")
        
        return function_args
            
    except Exception as e:
        raise ValueError(f"Error extracting flight details: {str(e)}")

def search_flights(page, params):
    """Search flights using Playwright to scrape Google Flights"""
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
                # Store the element for booking later
                flight_card = elem
                
                # Get airline information with improved selectors
                airline = None
                airline_text = "Unknown Airline"
                airline_selectors = [
                    '[class*="J1Dfkc"]',          # Common airline name class
                    '[class*="airline-name"]',     # Direct airline name
                    'img[alt*="Airlines"]',        # Airline logo alt text
                    '[class*="carrier-text"]',     # Carrier text
                    '[class*="h3z9Fd"]',          # Another common airline class
                    '.JMc5Xc'                     # Backup selector
                ]
                
                for selector in airline_selectors:
                    airline = elem.query_selector(selector)
                    if airline:
                        if 'img' in selector:
                            # For images, get the alt text
                            alt_text = airline.get_attribute('alt')
                            if alt_text:
                                airline_text = alt_text.replace(' Airlines', '').replace(' Logo', '')
                        else:
                            # For text elements, get the inner text
                            text = airline.inner_text().strip()
                            if text:
                                airline_text = text
                        if airline_text != "Unknown Airline":
                            break
                
                # Get price with improved selectors and cleaning
                price = None
                price_text = "Price not available"
                price_selectors = [
                    '[aria-label*="$"]',                    # Price in aria-label
                    '[class*="YMlIz"] span:last-child',     # Price amount
                    '[class*="BVAVmf"]',                    # Another price class
                    '[class*="price"]:not([class*="round-trip"])', # Price excluding round trip text
                    'span:has-text("$")'                    # Any span with dollar sign
                ]
                
                for selector in price_selectors:
                    price = elem.query_selector(selector)
                    if price:
                        raw_price = price.inner_text().strip()
                        # Clean up price text
                        if '$' in raw_price:
                            # Extract just the price amount
                            import re
                            price_match = re.search(r'\$[\d,]+', raw_price)
                            if price_match:
                                price_text = price_match.group(0)
                                break
                
                # Get departure and arrival times with improved format
                times = elem.query_selector_all('[class*="zxVSec"]')
                departure_time = "Time not available"
                if times:
                    time_text = times[0].inner_text().strip()
                    # Clean up time format
                    time_parts = time_text.split('–')
                    if len(time_parts) >= 1:
                        departure_time = time_parts[0].strip()
                
                # Get duration with improved selectors
                duration = None
                duration_text = "Duration not available"
                duration_selectors = [
                    '[class*="vmXl8d"]',          # Duration class
                    '[class*="duration"]',         # Generic duration
                    '[class*="flight-time"]'       # Flight time
                ]
                
                for selector in duration_selectors:
                    duration = elem.query_selector(selector)
                    if duration:
                        duration_text = duration.inner_text().strip()
                        # Clean up duration text if needed
                        if duration_text and 'hr' in duration_text.lower():
                            break
                
                flight_info = {
                    "airline": airline_text,
                    "price": price_text,
                    "departure_time": departure_time,
                    "duration": duration_text,
                    "element": flight_card  # Store the element for booking
                }
                print(f"Extracted flight info: {flight_info}")
                flights.append(flight_info)
                
            except Exception as e:
                print(f"Error extracting flight details: {str(e)}")
                continue
        
        return flights
        
    except Exception as e:
        print(f"Error during flight search: {str(e)}")
        return []

def book_flight(page, flight):
    """Actually book the selected flight"""
    try:
        # Click the flight card to start booking
        flight['element'].click()
        print("\nStarting booking process...")
        
        # Wait for the booking details to load
        page.wait_for_selector('[class*="booking-details"]', timeout=5000)
        
        # Look for "Select" or "Book" buttons
        selectors = [
            'button:has-text("Select")',
            'button:has-text("Book")',
            '[role="button"]:has-text("Select")',
            '[role="button"]:has-text("Book")'
        ]
        
        select_button = None
        for selector in selectors:
            select_button = page.query_selector(selector)
            if select_button:
                print(f"Found booking button with selector: {selector}")
                break
        
        if not select_button:
            print("Could not find booking button")
            return False
            
        # Click the select/book button
        select_button.click()
        print("Clicked booking button")
        
        # Wait for booking options to appear
        page.wait_for_timeout(2000)
        
        # Look for booking provider links
        booking_links = page.query_selector_all('a[href*="booking"], a[href*="expedia"], a[href*="airline"]')
        
        if booking_links:
            # Get the first booking link
            booking_url = booking_links[0].get_attribute('href')
            print(f"\nRedirecting to booking provider: {booking_url}")
            
            # Open booking URL in the same page
            page.goto(booking_url)
            return True
        else:
            print("No booking providers found")
            return False
            
    except Exception as e:
        print(f"Error during booking: {str(e)}")
        return False

def main():
    try:
        # Get user input
        user_input = input("Flight request: ")
        
        # Parse the query
        print("\nParsing your request...")
        params = parse_query(user_input)
        
        # Initialize browser and search flights
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
            )
            page = context.new_page()
            
            try:
                # Search flights
                flights = search_flights(page, params)
                
                if not flights:
                    print("\n❌ No flights found. Please try different dates or cities.")
                    return
                    
                # Display options
                print("\nAvailable flights:")
                for i, flight in enumerate(flights, 1):
                    print(f"{i}. {flight['airline']}")
                    print(f"   Departure: {flight['departure_time']}")
                    print(f"   Duration: {flight['duration']}")
                    print(f"   Price: {flight['price']}")
                    print()
                
                # Get booking confirmation
                choice = input("\nEnter flight number to book (1-3) or 'q' to quit: ")
                if choice.lower() == 'q':
                    print("Booking cancelled. Goodbye!")
                    return
                    
                choice = int(choice)
                if 1 <= choice <= len(flights):
                    selected = flights[choice-1]
                    confirm = input(f"\nConfirm booking {selected['airline']} for {selected['price']}? (y/n): ")
                    
                    if confirm.lower() == 'y':
                        print("\nInitiating booking process...")
                        if book_flight(page, selected):
                            print("\n✅ Successfully initiated booking process!")
                            print("Please complete your booking in the opened browser window.")
                            input("Press Enter when you're done to close the browser...")
                        else:
                            print("\n❌ Could not complete booking process automatically.")
                            print("Please visit https://www.google.com/travel/flights to book manually.")
                    else:
                        print("\nBooking cancelled. Goodbye!")
                else:
                    print("\nInvalid selection. Booking cancelled.")
                    
            finally:
                browser.close()
                
    except Exception as e:
        print(f"\n❌ Sorry, an error occurred: {str(e)}")
        print("Please try again.")

if __name__ == "__main__":
    main() 