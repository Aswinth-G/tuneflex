from pymongo import MongoClient
from datetime import datetime

client = MongoClient("mongodb://localhost:27017")
db = client["tuneflex"]

songs_collection = db["songs"]
users_collection = db["users"]


def initialize_sample_songs():
    if songs_collection.count_documents({}) > 0:
        return

    sample_songs = [
        {
            "title": "Classroom Smiles",
            "audio_path": "/audio/classroom_smiles.mp3",
            "tags": ["happy", "children", "fun", "bright"],
            "language": "English",
            "artist": "TuneFlex",
            "emotion": "happy",
            "created_at": datetime.utcnow()
        },
        {
            "title": "Silent Tears",
            "audio_path": "/audio/silent_tears.mp3",
            "tags": ["sad", "heartbreak"],
            "language": "English",
            "artist": "TuneFlex",
            "emotion": "sad",
            "created_at": datetime.utcnow()
        },
        {
            "title": "Gym Power",
            "audio_path": "/audio/gym_power.mp3",
            "tags": ["gym", "motivated", "energy"],
            "language": "English",
            "artist": "TuneFlex",
            "emotion": "motivated",
            "created_at": datetime.utcnow()
        },
          {
            "title": "athikaalai",
            "audio_path": "/audio/athikaalai/PuthithanaAthikaalayoRingtonebyTeddy1.mp3",
            "tags": ["PuthithanaAthikaalayoRingtonebyTeddy1", "athikaalai"],
            "language": "English",
            "artist": "Aswinth",
            "emotion": "athikaalai",
            "created_at": datetime.utcnow()
        }
    ]

    songs_collection.insert_many(sample_songs)

