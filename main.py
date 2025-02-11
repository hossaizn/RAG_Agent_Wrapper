from fastapi import FastAPI, HTTPException, Query
import cohere
from config import COHERE_API_KEY
from api.nlp.nlp_utils import detect_intent, extract_entities
from api.integrations.api_utils import get_drug_info, get_stock_price, get_book_info, get_wikipedia_summary

# Initialize FastAPI
app = FastAPI()

# Initialize Cohere Client
client = cohere.Client(COHERE_API_KEY)

# Store chat history
conversation_history = []

@app.get("/")
def home():
    """Health check endpoint."""
    return {"message": "Chatbot Wrapper using Cohere API is Running!"}

@app.post("/chat")
def chat(user_input: str = Query(..., min_length=1, description="User input cannot be empty.")):
    """Handles chatbot queries with memory for multi-turn conversations."""
    try:
        # Ensure input is not empty
        if not user_input.strip():
            raise HTTPException(status_code=400, detail="Input cannot be empty.")

        # Intent & Extract Entities
        intent = detect_intent(user_input)
        entities = extract_entities(user_input)  # Extracts named entities

        # Handle API Calls
        api_response = None
        api_source = None  # Track API

        # Handle Drug Queries (OpenFDA API)
        if intent == "drug" or any(word in user_input.lower() for word in ["medicine", "pill", "aspirin"]):
            drug_name = next(iter(entities.values()), "aspirin")  # Default to "aspirin" if no entity found
            api_response = get_drug_info(drug_name)
            api_source = "OpenFDA API" if api_response and "error" not in api_response else None

        # Handle Stock Queries (Alpha Vantage API)
        elif intent == "finance" or "stock" in user_input.lower():
            stock_symbol = next(iter(entities.values()), "AAPL")  # Default to Apple stock if no entity found
            api_response = get_stock_price(stock_symbol, "9BJWJA0Z4DPNVAO6")
            api_source = "Alpha Vantage API" if api_response and "error" not in api_response else None

        # Handle Book Queries (Google Books API)
        elif intent == "book" or "book" in user_input.lower():
            book_title = next(iter(entities.values()), "Python")  # Default to "Python" book if no entity found
            api_response = get_book_info(book_title)
            api_source = "Google Books API" if api_response and "error" not in api_response else None

        # Handle Wikipedia Queries
        elif intent == "information":
            topic = next(iter(entities.values()), None)  # Extract topic dynamically
            if topic:
                api_response = get_wikipedia_summary(topic)
                api_source = "Wikipedia API" if api_response and "error" not in api_response else None

        # If an API response exists, return immediately
        if api_response and api_source:
            return {
                "status": "success",
                "user_input": user_input,
                "ai_response": "This information was retrieved from an external API.",
                "api_response": api_response,  
                "api_source": api_source, 
                "intent": intent,
                "entities": entities
            }

        # If No API Response, Proceed with AI-Based Response
        # Append user input to conversation history
        conversation_history.append({"role": "user", "content": user_input})

        # Combine conversation history into a formatted context string
        conversation_context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history])

        # Send formatted history to Cohere API
        response = client.chat(
            message=conversation_context,
            model="command-r"
        )

        # Ensure response is valid
        if not response or not response.text:
            raise HTTPException(status_code=500, detail="AI response is empty.")

        # Append AI response to history
        conversation_history.append({"role": "assistant", "content": response.text})

        return {
            "status": "success",
            "user_input": user_input,
            "ai_response": response.text,  
            "intent": intent,
            "entities": entities,
            "api_response": None,  # No API data used
            "conversation_history": conversation_history[-5:]  # Show last 5 messages
        }

    except HTTPException as http_err:
        return {"status": "error", "message": http_err.detail}

    except Exception as e:
        return {"status": "error", "message": f"An unexpected error occurred: {str(e)}"}

@app.get("/chat/history")
def get_history():
    """Returns chat history."""
    if not conversation_history:
        return {"status": "error", "message": "No conversation history found."}
    return {"status": "success", "conversation_history": conversation_history}

@app.delete("/chat/reset")
def reset_history():
    """Resets chat history."""
    conversation_history.clear()
    return {"status": "success", "message": "Chat history cleared!"}

@app.post("/nlp/intent")
def get_intent(user_input: str = Query(..., min_length=1, description="User input cannot be empty.")):
    """Detects user intent based on input."""
    try:
        intent = detect_intent(user_input)
        return {"status": "success", "intent": intent}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/nlp/entities")
def get_entities(user_input: str = Query(..., min_length=1, description="User input cannot be empty.")):
    """Extracts entities from user input."""
    try:
        entities = extract_entities(user_input)
        return {"status": "success", "entities": entities}
    except Exception as e:
        return {"status": "error", "message": str(e)}

