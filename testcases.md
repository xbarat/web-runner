# Test Cases

Okay, let's chase the problem of bridging LLMs with APIs for reliable multi-agent web automation, using the "hello-world" prototype approach. Here are 5 different use cases, focusing on making them work simply, not perfectly:

**1. Simple Data Retrieval and Display:**

* **Scenario:** User asks, "What's the current price of Bitcoin?"
* **RAG Component:** LLM retrieves relevant info about Bitcoin (current price API, maybe a short description) from a pre-defined knowledge base or a simple web search.
* **API Orchestration:** LLM constructs an API call to a price tracking service (e.g., CoinGecko, CoinMarketCap) using a pre-defined API spec.
* **Output:** LLM formats the retrieved price and displays it to the user.
* **"Hello World" Focus:**  Make sure the LLM can correctly construct *one* API call and display the result.

**2. Basic Task Automation (Single Action):**

* **Scenario:** User says, "Add 'Buy groceries' to my Todoist list."
* **RAG Component:** LLM understands the intent ("add to Todoist") and extracts the task ("Buy groceries").
* **API Orchestration:** LLM constructs an API call to Todoist's API (using a pre-defined API spec) to add the task.
* **Output:** Confirmation message: "Added 'Buy groceries' to your Todoist list."
* **"Hello World" Focus:**  Get the LLM to trigger *one* specific action in Todoist (or a similar service) based on natural language input.

**3.  Conditional Logic Based on API Results:**

* **Scenario:** User says, "If the weather in London is above 20 degrees Celsius, send me a reminder to pack sunscreen."
* **RAG Component:** LLM retrieves weather information from a weather API (e.g., OpenWeatherMap).
* **API Orchestration:** LLM uses conditional logic:
    * If temperature > 20°C, construct and execute an API call to a notification service (e.g., email, SMS) to send the reminder.
    * If temperature <= 20°C, display a message: "The weather is currently below 20 degrees, no need for sunscreen (yet)."
* **"Hello World" Focus:** Implement *one* simple conditional check based on the API response and trigger the appropriate action.

**4. Chained API Calls (Simple Workflow):**

* **Scenario:** User says, "Find a recipe for pasta, then add the ingredients to my shopping list."
* **RAG Component:** LLM retrieves pasta recipes from a recipe API (e.g., Spoonacular). User selects one.  LLM extracts the ingredients.
* **API Orchestration:**
    1. LLM calls the recipe API to get the recipe.
    2. LLM calls the shopping list API (e.g., a simple custom API or integration with a shopping list app) to add the ingredients.
* **Output:** Confirmation: "Ingredients added to your shopping list."
* **"Hello World" Focus:** Chain *two* API calls together in a defined sequence.

**5.  Agent Identification and Basic Authorization:**

* **Scenario:** User (pre-identified with an ID or token) says, "Create a new invoice for company X for $100."
* **RAG Component:** LLM understands the request and extracts the relevant information.
* **API Orchestration:** LLM constructs an API call to an invoicing service.  Crucially, this call includes the user's ID/token for authentication.  The invoicing service validates the token before creating the invoice.
* **Output:** Confirmation: "Invoice created."
* **"Hello World" Focus:** Implement a *very basic* form of authentication for a *single* user.

**Key Considerations for all "Hello World" Prototypes:**

* **Pre-defined API Specs:**  Start with well-defined API specifications (e.g., OpenAPI/Swagger) for the services you're using.
* **Simplified Authentication:**  For initial tests, use simple API keys or tokens.  Don't overcomplicate authentication at this stage.
* **Limited Scope:** Focus on making *one thing* work end-to-end.
* **Modular Design:**  Design the components (LLM interaction, API call construction, API response handling) in a modular way so they can be easily extended later.

By focusing on these "hello world" prototypes, we can incrementally build towards more complex and reliable multi-agent web automation. Each step validates a specific part of the overall architecture and helps us learn how to best bridge the gap between LLMs and APIs.
