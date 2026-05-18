"""
Script to update movie and throwback songs in MongoDB with correct audio file paths
Run this ONCE to fix the database entries
"""

from app.db.mongodb import songs_collection
from datetime import datetime

MOVIE_SONGS_UPDATE = {
    "Aasa Pulla": {
        "title": "Aasa Pulla",
        "audio_path": "/audio/movies/Aasa_Pulla.mp3",
        "audio_url": "https://variedly-unspirited-archie.ngrok-free.dev/audio/movies/Aasa%20Pulla.mp3",
        "tags": ["Aasa Pulla", "movies"],
        "artist": "Anirudh Ravichander",
        "emotion": "movies",
        "language": "Tamil"
    },
    "Friendship": {
        "title": "Friendship",
        "audio_path": "/audio/movies/Friendship.mp3",
        "audio_url": "https://variedly-unspirited-archie.ngrok-free.dev/audio/movies/Friendship.mp3",
        "tags": ["Friendship", "movies"],
        "artist": "Anirudh Ravichander",
        "emotion": "movies",
        "language": "Tamil"
    },
    "Nalla Nanban": {
        "title": "Nalla Nanban",
        "audio_path": "/audio/movies/Nalla_Nanban.mp3",
        "audio_url": "https://variedly-unspirited-archie.ngrok-free.dev/audio/movies/Nalla%20Nanban.mp3",
        "tags": ["Nalla Nanban", "movies"],
        "artist": "Anirudh Ravichander",
        "emotion": "movies",
        "language": "Tamil"
    },
    "ThaniOruvan": {
        "title": "Thani Oruvan",
        "audio_path": "/audio/movies/ThaniOruvan.mp3",
        "audio_url": "https://variedly-unspirited-archie.ngrok-free.dev/audio/movies/ThaniOruvan.mp3",
        "tags": ["Thani Oruvan", "movies"],
        "artist": "Anirudh Ravichander",
        "emotion": "movies",
        "language": "Tamil"
    }
}

THROWBACK_SONGS_UPDATE = {
    "April": {
        "title": "April",
        "audio_path": "/audio/Throwback/April.mp3",
        "audio_url": "https://variedly-unspirited-archie.ngrok-free.dev/audio/Throwback/April.mp3",
        "tags": ["April", "Throwback"],
        "artist": "Anirudh Ravichander",
        "emotion": "Throwback",
        "language": "Tamil"
    },
    "Sha La La": {
        "title": "Sha La La",
        "audio_path": "/audio/Throwback/Sha_La_La.mp3",
        "audio_url": "https://variedly-unspirited-archie.ngrok-free.dev/audio/Throwback/Sha%20La%20La.mp3",
        "tags": ["Sha La La", "Throwback"],
        "artist": "Anirudh Ravichander",
        "emotion": "Throwback",
        "language": "Tamil"
    },
    "Vennilavae": {
        "title": "Vennilavae",
        "audio_path": "/audio/Throwback/Vennilavae.mp3",
        "audio_url": "https://variedly-unspirited-archie.ngrok-free.dev/audio/Throwback/Vennilavae.mp3",
        "tags": ["Vennilavae", "Throwback"],
        "artist": "Anirudh Ravichander",
        "emotion": "Throwback",
        "language": "Tamil"
    }
}

def update_movie_songs():
    """Update or insert movie songs in database"""
    print("Updating Movie songs...")
    
    for key, song_data in MOVIE_SONGS_UPDATE.items():
        result = songs_collection.update_one(
            {"title": song_data["title"]},
            {"$set": {
                **song_data,
                "updated_at": datetime.utcnow()
            }},
            upsert=True  # Insert if doesn't exist
        )
        
        if result.matched_count > 0:
            print(f"  ✓ Updated: {song_data['title']}")
        else:
            print(f"  ✓ Inserted: {song_data['title']}")

def update_throwback_songs():
    """Update or insert throwback songs in database"""
    print("Updating Throwback songs...")
    
    for key, song_data in THROWBACK_SONGS_UPDATE.items():
        result = songs_collection.update_one(
            {"title": song_data["title"]},
            {"$set": {
                **song_data,
                "updated_at": datetime.utcnow()
            }},
            upsert=True  # Insert if doesn't exist
        )
        
        if result.matched_count > 0:
            print(f"  ✓ Updated: {song_data['title']}")
        else:
            print(f"  ✓ Inserted: {song_data['title']}")

def verify_updates():
    """Verify the updates were successful"""
    print("\nVerifying updates...")
    
    all_titles = list(MOVIE_SONGS_UPDATE.keys()) + list(THROWBACK_SONGS_UPDATE.keys())
    for title_key in all_titles:
        # Find by actual title name
        if title_key in MOVIE_SONGS_UPDATE:
            title = MOVIE_SONGS_UPDATE[title_key]["title"]
        else:
            title = THROWBACK_SONGS_UPDATE[title_key]["title"]
            
        song = songs_collection.find_one({"title": title})
        if song:
            print(f"  ✓ {title}: {song.get('audio_url', 'NO URL')}")
        else:
            print(f"  ✗ {title}: NOT FOUND in database")

if __name__ == "__main__":
    print("=" * 60)
    print("TuneFlex Database Update Script")
    print("=" * 60)
    
    try:
        update_movie_songs()
        update_throwback_songs()
        verify_updates()
        
        print("\n" + "=" * 60)
        print("✓ Database update complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        raise
