from .text_utils import preprocess_text
from .song_loader import load_songs
from .song_ranker import rank_songs

def find_best_song(query: str):
    keywords, _ = preprocess_text(query)
    songs = load_songs()
    ranked = rank_songs(songs, keywords)

    if not ranked:
        return None

    best = ranked[0]
    song = best["song"]

    return {
        "title": song["title"],
        "audio_path": song["audio_path"],
        "tags": song["tags"],
        "artist": song.get("artist", "Unknown"),
        "emotion": song.get("emotion", "neutral"),
        "confidence": min(best["score"] / 10, 1.0)
    }
