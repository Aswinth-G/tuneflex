from .similarity import calculate_score

def rank_songs(songs, keywords):
    ranked = []

    for song in songs:
        score = calculate_score(keywords, song.get("tags", []))
        if score > 0:
            ranked.append({"song": song, "score": score})

    ranked.sort(key=lambda x: x["score"], reverse=True)
    return ranked
