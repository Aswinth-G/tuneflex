import os
import sys
from pymongo import MongoClient
from datetime import datetime

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "tuneflex"

DETECTION_FOLDER_SONGS = [
    # From data/audio/movies/
    {
        "_id": "movie_thani_oruvan",
        "title": "Thani Oruvan",
        "artist": "Anirudh Ravichander",
        "album": "Thani Oruvan",
        "duration": 250,
        "emotion": "romantic",
        "keywords": ["thani", "oruvan", "romantic", "love"],
        "language": "Tamil",
        "audio_path": "movies/ThaniOruvan.mp3",
        "priority": 1
    },
    {
        "_id": "movie_aasa_pulla",
        "title": "Aasa Pulla",
        "artist": "Anirudh Ravichander",
        "album": "Aasa Pulla",
        "duration": 180,
        "emotion": "energetic",
        "keywords": ["aasa", "pulla", "energetic", "friendship"],
        "language": "Tamil",
        "audio_path": "movies/Aasa Pulla.mp3",
        "priority": 1
    },
    {
        "_id": "movie_friendship",
        "title": "Friendship",
        "artist": "Anirudh Ravichander",
        "album": "Friendship",
        "duration": 200,
        "emotion": "happy",
        "keywords": ["friendship", "happy", "fun", "emotional"],
        "language": "Tamil",
        "audio_path": "movies/Friendship.mp3",
        "priority": 1
    },
    {
        "_id": "movie_nalla_nanban",
        "title": "Nalla Nanban",
        "artist": "Anirudh Ravichander",
        "album": "Nalla Nanban",
        "duration": 220,
        "emotion": "happy",
        "keywords": ["nanban", "friendship", "happy", "fun"],
        "language": "Tamil",
        "audio_path": "movies/Nalla Nanban.mp3",
        "priority": 1
    },
    
    # From data/audio/Throwback/
    {
        "_id": "throwback_april",
        "title": "April",
        "artist": "Anirudh Ravichander",
        "album": "Throwback Songs",
        "duration": 180,
        "emotion": "happy",
        "keywords": ["april", "happy", "spring"],
        "language": "Tamil",
        "audio_path": "Throwback/April.mp3",
        "priority": 1
    },
    {
        "_id": "throwback_sha_la_la",
        "title": "Sha La La",
        "artist": "Anirudh Ravichander",
        "album": "Throwback Songs",
        "duration": 200,
        "emotion": "happy",
        "keywords": ["sha", "la", "happy", "dance"],
        "language": "Tamil",
        "audio_path": "Throwback/Sha La La.mp3",
        "priority": 1
    },
    {
        "_id": "throwback_vennilavae",
        "title": "Vennilavae",
        "artist": "Anirudh Ravichander",
        "album": "Throwback Songs",
        "duration": 210,
        "emotion": "romantic",
        "keywords": ["vennilavae", "romantic", "love", "tamil"],
        "language": "Tamil",
        "audio_path": "Throwback/Vennilavae.mp3",
        "priority": 1
    },
    
    # From data/audio/athikaalai/
    {
        "_id": "athikaalai_ringtone",
        "title": "Puthithana Athikaalayo Ringtone",
        "artist": "Teddy",
        "album": "Athikaalai Songs",
        "duration": 60,
        "emotion": "athikaalai",
        "keywords": ["athikaalai", "ringtone", "teddy"],
        "language": "Tamil",
        "audio_path": "athikaalai/PuthithanaAthikaalayoRingtonebyTeddy1189287257.mp3",
        "priority": 1
    },
    
    # From data/audio/hiphop/
    {
        "_id": "hiphop_dhom",
        "title": "Dhom",
        "artist": "Anirudh Ravichander",
        "album": "Hiphop Songs",
        "duration": 240,
        "emotion": "hiphop",
        "keywords": ["dhom", "hiphop", "tamil", "rap"],
        "language": "Tamil",
        "audio_path": "hiphop/dhom.mp3",
        "priority": 1
    },
    {
        "_id": "hiphop_hi",
        "title": "Hi",
        "artist": "Anirudh Ravichander",
        "album": "Hiphop Songs",
        "duration": 200,
        "emotion": "hiphop",
        "keywords": ["hi", "hiphop", "greeting"],
        "language": "Tamil",
        "audio_path": "hiphop/hi.mp3",
        "priority": 1
    },
    {
        "_id": "hiphop_oxygen",
        "title": "Oxygen",
        "artist": "Anirudh Ravichander",
        "album": "Hiphop Songs",
        "duration": 220,
        "emotion": "hiphop",
        "keywords": ["oxygen", "hiphop", "energy"],
        "language": "Tamil",
        "audio_path": "hiphop/Oxygen.mp3",
        "priority": 1
    },
    {
        "_id": "hiphop_poraada",
        "title": "Poraada",
        "artist": "Anirudh Ravichander",
        "album": "Hiphop Songs",
        "duration": 210,
        "emotion": "hiphop",
        "keywords": ["poraada", "hiphop", "tamil", "beat"],
        "language": "Tamil",
        "audio_path": "hiphop/Poraada.mp3",
        "priority": 1
    },
    {
        "_id": "hiphop_vilambara",
        "title": "Vilambara",
        "artist": "Anirudh Ravichander",
        "album": "Hiphop Songs",
        "duration": 230,
        "emotion": "hiphop",
        "keywords": ["vilambara", "hiphop", "tamil", "rap"],
        "language": "Tamil",
        "audio_path": "hiphop/Vilambara.mp3",
        "priority": 1
    },
    
    # From data/audio/neeum_naanum/
    {
        "_id": "neeum_naanum",
        "title": "Neeyum Naanum Anbe",
        "artist": "Mass Tamilan",
        "album": "Neeum Naanum",
        "duration": 240,
        "emotion": "love",
        "keywords": ["neeum", "naanum", "love", "together"],
        "language": "Tamil",
        "audio_path": "neeum_naanum/Neeyum-Naanum-Anbe-MassTamilan.com.mp3",
        "priority": 1
    },
    
    # From data/audio/0/
    {
        "_id": "first_last_edhirthu",
        "title": "Edhirthu Nil",
        "artist": "Unknown",
        "album": "Class 0 Songs",
        "duration": 200,
        "emotion": "custom_0",
        "keywords": ["edhirthu", "nil", "class0"],
        "language": "Tamil",
        "audio_path": "0/Edhirthu-Nil.mp3",
        "priority": 1
    },
    {
        "_id": "first_last_jada",
        "title": "Jada Jaada Jaada",
        "artist": "Unknown",
        "album": "Class 0 Songs",
        "duration": 180,
        "emotion": "custom_0",
        "keywords": ["jada", "jaada", "class0"],
        "language": "Tamil",
        "audio_path": "0/Jada-Jada-Jaada.mp3",
        "priority": 1
    },
    {
        "_id": "first_last_unmaiorunaal",
        "title": "Unmaiorunaal Vellum",
        "artist": "Unknown",
        "album": "Class 0 Songs",
        "duration": 200,
        "emotion": "custom_0",
        "keywords": ["unmaiorunaal", "vellum", "class0"],
        "language": "Tamil",
        "audio_path": "0/Unmaiorunaal-Vellum.mp3",
        "priority": 1
    }
]

def add_all_detection_songs():
    """Add all songs from detection folders to database"""
    print("Adding All Detection Folder Songs to Database")
    print("=" * 60)
    
    try:
        # Connect to MongoDB
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        songs_collection = db.songs
        
        added_count = 0
        updated_count = 0
        
        for song_data in DETECTION_FOLDER_SONGS:
            # Check if song already exists
            existing_song = songs_collection.find_one({"_id": song_data["_id"]})
            
            if existing_song:
                print(f"Song '{song_data['title']}' already exists. Updating...")
                
                # Update existing song
                update_data = {
                    "$set": {
                        "keywords": song_data["keywords"],
                        "audio_url": f"https://variedly-unspirited-archie.ngrok-free.dev/audio/{song_data['audio_path']}",
                        "priority": 1,
                        "updated_at": datetime.now().isoformat()
                    }
                }
                
                result = songs_collection.update_one(
                    {"_id": song_data["_id"]},
                    update_data
                )
                
                if result.modified_count:
                    updated_count += 1
                    print(f"Updated '{song_data['title']}' with priority=1")
                else:
                    print(f"Failed to update '{song_data['title']}'")
                    
            else:
                # Add new song
                new_song = {
                    "_id": song_data["_id"],
                    "title": song_data["title"],
                    "artist": song_data["artist"],
                    "album": song_data["album"],
                    "duration": song_data["duration"],
                    "emotion": song_data["emotion"],
                    "keywords": song_data["keywords"],
                    "language": song_data["language"],
                    "audio_path": song_data["audio_path"],
                    "audio_url": f"https://variedly-unspirited-archie.ngrok-free.dev/audio/{song_data['audio_path']}",
                    "priority": 1,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
                
                result = songs_collection.insert_one(new_song)
                if result.inserted_id:
                    added_count += 1
                    print(f"Added '{song_data['title']}' to database")
                else:
                    print(f"Failed to add '{song_data['title']}'")
        
        print(f"\nSummary:")
        print(f"   Added: {added_count} new songs")
        print(f"   Updated: {updated_count} existing songs")
        print(f"   Total processed: {len(DETECTION_FOLDER_SONGS)} songs")
        
        # Verify songs were added
        print(f"\nVerifying songs were added:")
        verification_songs = list(songs_collection.find({"priority": 1}))
        print(f"Found {len(verification_songs)} user songs (priority=1):")
        
        for song in verification_songs:
            title = song.get("title", "Unknown")
            audio_path = song.get("audio_path", "No path")
            print(f"   - {title}")
            print(f"     Path: {audio_path}")
        
        client.close()
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("TuneFlex - Add All Detection Folder Songs")
    print("=" * 60)
    
    print("Songs to Add:")
    print("- Thani Oruvan (movies/ThaniOruvan.mp3)")
    print("- Aasa Pulla (movies/Aasa Pulla.mp3)")
    print("- Friendship (movies/Friendship.mp3)")
    print("- Nalla Nanban (movies/Nalla Nanban.mp3)")
    print("- April (Throwback/April.mp3)")
    print("- Sha La La (Throwback/Sha La La.mp3)")
    print("- Vennilavae (Throwback/Vennilavae.mp3)")
    print("- Puthithana Athikaalayo Ringtone (athikaalai/PuthithanaAthikaalayoRingtonebyTeddy1189287257.mp3)")
    print("- Dhom (hiphop/dhom.mp3)")
    print("- Hi (hiphop/hi.mp3)")
    print("- Oxygen (hiphop/Oxygen.mp3)")
    print("- Poraada (hiphop/Poraada.mp3)")
    print("- Vilambara (hiphop/Vilambara.mp3)")
    print("- Neeyum Naanum Anbe (neeum_naanum/Neeyum-Naanum-Anbe-MassTamilan.com.mp3)")
    print("- Edhirthu Nil (0/Edhirthu-Nil.mp3)")
    print("- Jada Jaada Jaada (0/Jada-Jada-Jaada.mp3)")
    print("- Unmaiorunaal Vellum (0/Unmaiorunaal-Vellum.mp3)")
    
    print(f"\nAdding {len(DETECTION_FOLDER_SONGS)} songs from detection folders...")
    add_all_detection_songs()
