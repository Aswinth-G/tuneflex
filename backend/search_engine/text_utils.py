import re

STOP_WORDS = {
    "song", "music", "play", "listen",
    "a", "the", "is", "and", "or", "but",
    "in", "on", "at", "to", "for"
}

def preprocess_text(text: str):
    text = text.lower()
    text = re.sub(r"[^a-z\s]", "", text)
    words = text.split()
    filtered_words = [w for w in words if w not in STOP_WORDS]
    return filtered_words, text
