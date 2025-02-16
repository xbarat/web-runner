# *CASE 1: Book a flight*
Book a flight from New York to Miami on March 15, 2025
challenge - API is hard to get, headless browser using playwright is the best option

try these APIs:
- Skyscanner API: https://rapidapi.com/skyscanner/api/skyscanner-flight-search
- Amadeus API: https://developers.amadeus.com/
- Kiwi API: https://tequila.kiwi.com/


## Finding the API key is a pain

```python
url = "https://partners.api.skyscanner.net/apiservices/browseroutes/v1.0/US/USD/en-US/NYC/LAX/2024-03-20"
headers = {"apikey": "YOUR_API_KEY"}

response = requests.get(url, headers=headers)
print(response.json())  # Structured flight data
```


