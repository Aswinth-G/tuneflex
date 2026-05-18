from pydantic import BaseModel
from typing import List

class SongSchema(BaseModel):
    title: str
    tags: List[str]
    language: str
    artist: str
    emotion: str
    audio_path: str
