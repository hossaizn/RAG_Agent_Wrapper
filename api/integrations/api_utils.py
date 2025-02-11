import requests
import wikipediaapi

# OpenFDA API (Healthcare)
def get_drug_info(drug_name):
    """Fetches drug details from OpenFDA API."""
    url = f"https://api.fda.gov/drug/label.json?search=openfda.brand_name:{drug_name}&limit=1"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()

        if "results" in data and len(data["results"]) > 0:
            drug_data = data["results"][0]

            # Extract meaningful details
            summary = {
                "Brand Name": drug_data.get("openfda", {}).get("brand_name", ["Unknown"])[0],
                "Generic Name": drug_data.get("openfda", {}).get("generic_name", ["Unknown"])[0],
                "Purpose": drug_data.get("purpose", ["Not available"])[0],
                "Active Ingredient": drug_data.get("active_ingredient", ["Not available"])[0],
                "Usage": drug_data.get("indications_and_usage", ["Not available"])[0],
                "Warnings": drug_data.get("warnings", ["No warnings available"])[0],
                "Dosage": drug_data.get("dosage_and_administration", ["Not available"])[0],
                "Manufacturer": drug_data.get("openfda", {}).get("manufacturer_name", ["Unknown"])[0]
            }
            return summary  

    return {"error": "Drug information not found."}


# Alpha Vantage API (Finance)
# Predefined mapping for company names to their stock symbols
STOCK_SYMBOLS = {
    "Tesla": "TSLA",
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Google": "GOOGL",
    "Amazon": "AMZN",
    "Nvidia": "NVDA",
    "Meta": "META",
    "Netflix": "NFLX"
}

def extract_stock_symbol(user_input):
    """Extracts stock symbol from user input based on predefined mappings."""
    for company, symbol in STOCK_SYMBOLS.items():
        if company.lower() in user_input.lower():
            return symbol
    return None  

def get_stock_price(user_input, api_key="9BJWJA0Z4DPNVAO6"):
    """Fetches stock market data and extracts key stock details."""
    
    # Extract stock symbol from user input
    symbol = extract_stock_symbol(user_input)
    
    # If no valid stock symbol found, return an error message
    if not symbol:
        return {"error": "Could not identify stock symbol. Please specify a valid company name."}
    
    # Fetch stock data using the correct symbol
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json().get("Global Quote", {})
        if data:
            return {
                "Symbol": data.get("01. symbol", "N/A"),
                "Open Price": data.get("02. open", "N/A"),
                "High Price": data.get("03. high", "N/A"),
                "Low Price": data.get("04. low", "N/A"),
                "Current Price": data.get("05. price", "N/A"),
                "Previous Close": data.get("08. previous close", "N/A"),
                "Change": data.get("09. change", "N/A"),
                "Change %": data.get("10. change percent", "N/A")
            }
    
    return {"error": f"Stock data not available for {symbol}."}

# Open Library API (Education)
def get_book_info(book_title):
    """Fetches book details from Open Library API."""
    url = f"https://openlibrary.org/search.json?title={book_title}&limit=1"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if "docs" in data and len(data["docs"]) > 0:
            book = data["docs"][0]
            return {
                "Title": book.get("title", "Unknown"),
                "Author": book.get("author_name", ["Unknown"])[0],
                "First Published": book.get("first_publish_year", "Unknown"),
                "Edition Count": book.get("edition_count", "N/A"),
                "OpenLibrary ID": book.get("key", "N/A")
            }
    return {"error": "Book not found."}


# Wikipedia API (General Knowledge)
def get_wikipedia_summary(topic):
    """Fetches a Wikipedia summary for a given topic with a user-agent."""
    wiki_wiki = wikipediaapi.Wikipedia(user_agent="YourAppName/1.0 (your@email.com)", language="en")
    page = wiki_wiki.page(topic)

    if page.exists():
        return {
            "Title": page.title,
            "Summary": page.summary[:500]  # Limit response to 500 characters
        }
    
    return {"error": f"No Wikipedia page found for '{topic}'. Try a more specific term."}
