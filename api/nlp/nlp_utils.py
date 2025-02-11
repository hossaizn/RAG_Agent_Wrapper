import spacy

# Load pre-trained spaCy model
nlp = spacy.load("en_core_web_sm")

# Defining intent classification keywords
INTENT_KEYWORDS = {
    "greeting": ["hello", "hi", "hey"],
    "goodbye": ["bye", "goodbye", "see you"],
    "booking": ["book", "schedule", "reserve"],
    "information": ["tell me about", "give me info", "what is"],
    "question": ["who", "what", "where", "when", "why", "how"]
}

def detect_intent(user_input):
    """Detects intent based on keywords."""
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(word in user_input.lower() for word in keywords):
            return intent
    return "unknown"

def extract_entities(user_input):
    """Extracts named entities from user input."""
    doc = nlp(user_input)
    entities = {ent.label_: ent.text for ent in doc.ents}
    return entities
