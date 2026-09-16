import spacy
from spacy.pipeline import EntityRuler

# Load your fine-tuned Transformer pipeline
nlp = spacy.load("./models/output_trf/model-last") 

# Add EntityRuler component BEFORE the statistical NER
ruler = nlp.add_pipe("entity_ruler", before="ner")

# Define deterministic Regex patterns
patterns = [
    # Email pattern
    {"label": "EMAIL", "pattern": [{"TEXT": {"REGEX": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"}}]},
    # Phone number patterns (handles international and common delimiters)
    {"label": "PHONE", "pattern": [{"TEXT": {"REGEX": r"^\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{3,4}[-.\s]?\d{4}$"}}]},
    # LinkedIn / Portfolio links
    {"label": "LINK", "pattern": [{"TEXT": {"REGEX": r"^https?://(www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+/?$"}}]}
]

ruler.add_patterns(patterns)