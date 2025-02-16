# Issues

## Need for Adaptable Automation

Here are some potential solutions that relate to our discussion of RPA enhancements:

- **More Flexible Selectors**: Instead of relying on very specific selectors that are easily broken, the system could use more general or robust selectors that are less likely to be affected by minor website changes.  Perhaps using relative selectors or searching for patterns instead of exact element matches.

- **Visual Recognition**: More advanced RPA tools, or integrations with AI/ML, could use visual recognition to identify airline names based on their visual appearance, even if the underlying HTML structure changes.  This is a move towards more intelligent automation, which is where LLMs and AI tie in.

- **API Integration (Ideal)**: If Google Flights offered an official API for accessing flight data, the flight booking system could use the API instead of web scraping.  This would be the most robust solution, as APIs are generally more stable and less prone to breaking due to website changes.  This relates to our discussions of API orchestration and the benefits of using APIs over scraping when possible.

- **LLM-assisted Scraping**:  LLMs could be used to make the scraping process more adaptive.  An LLM could analyze the HTML of the Google Flights page and dynamically generate the correct selectors, even if the page structure has changed.  This would be a more advanced approach, but it could significantly improve the reliability of the web scraping.  This goes back to the idea of LLMs as the "brains" of the operation, with tools like Zapier (or a web scraping library) as the "hands."  The LLM could even be trained to recognize the "Unknown Airline" output as an error condition and trigger a process to update the selectors.

- **API Integration (Ideal)**: If Google Flights offered an official API for accessing flight data, the flight booking system could use the API instead of web scraping.  This would be the most robust solution, as APIs are generally more stable and less prone to breaking due to website changes.  This relates to our discussions of API orchestration and the benefits of using APIs over scraping when possible.

