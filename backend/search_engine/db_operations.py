from typing import List, Optional
from datetime import datetime
from app.db.mongodb import songs_collection


def get_all_songs() -> List[dict]:
    return list(songs_collection.find({}, {"_id": 0}))


def find_songs_by_tags(tags: List[str]) -> List[dict]:
    return list(
        songs_collection.find({"tags": {"$in": tags}}, {"_id": 0})
    )


def find_songs_by_emotion(emotion: str) -> List[dict]:
    return list(
        songs_collection.find({"emotion": emotion}, {"_id": 0})
    )
