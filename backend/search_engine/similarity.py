WEIGHTS = {
    "sad": 3,
    "romantic": 3,
    "happy": 2,
    "love": 2,
    "heartbreak": 3,
    "dance": 1,
    "classroom": 2,
    "children": 2,
    "fun": 2,
    "bright": 1,
    "gym": 3,
    "motivated": 2,
    "strong": 2,
    "energy": 2,
    "celebrate": 2,
    "party": 2,
    "joy": 2,
    "fight": 2,
    "angry": 2,
    "calm": 1,
    "peace": 1,
    "relax": 1,
    "study": 1,
    "work": 1,
    "custom_0": 5,
    "athikaalai": 5,
}

def calculate_score(query_words, song_tags):
    """
    Calculate similarity score between query words and song tags
    """
    score = 0
    for word in query_words:
        if word in song_tags:
            score += WEIGHTS.get(word, 1)
    return score
