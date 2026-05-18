from datetime import datetime
from typing import List
import os
from app.db.mongodb import songs_collection


def insert_song(song_data: dict):
    song_data["created_at"] = datetime.utcnow()
    return songs_collection.insert_one(song_data)


def get_all_songs() -> List[dict]:
    return list(songs_collection.find({}, {"_id": 0}))


def find_songs_by_tags(tags: list) -> List[dict]:
    return list(
        songs_collection.find(
            {"tags": {"$in": tags}},
            {"_id": 0}
        )
    )


def find_songs_by_emotion(emotion: str) -> List[dict]:
    return list(
        songs_collection.find(
            {"emotion": emotion},
            {"_id": 0}
        )
    )


def initialize_sample_songs():
    """Call this ONCE at startup"""
    print("DEBUG: Initializing sample songs...")
    print(f"DEBUG: Current song count: {songs_collection.count_documents({})}")
    
    # Only add sample songs if database is completely empty
    if songs_collection.count_documents({}) == 0:
        print("DEBUG: Database is empty, adding sample songs...")

    sample_songs = [
       
        

         {
            "title": "First Last SCHOOL",
            "audio_path": "/audio/0/First-Last.mp3",
            "tags": ["First-Last", "custom_0"],
            "language": "English",
            "artist": "Aswinth",
            "emotion": "custom_0",
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
    print(" Sample TuneFlex songs inserted")
    
    # Always scan audio directory for new files
    audio_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/audio"))
    scan_and_load_audio_files(audio_dir)
    print(f"DEBUG: Final song count: {songs_collection.count_documents({})}")


def scan_and_load_audio_files(audio_dir: str):
    """Scan audio directory and upload to Cloudinary, then load into database"""
    print(f"DEBUG: Scanning audio directory for Cloudinary upload: {audio_dir}")
    
    if not os.path.exists(audio_dir):
        print(f"DEBUG: Audio directory does not exist: {audio_dir}")
        return
    
    # Import Cloudinary function
    try:
        from app.cloudinary_config import upload_audio_to_cloudinary
        print("DEBUG: Cloudinary upload function available")
    except ImportError as e:
        print(f"DEBUG: Cloudinary not available: {e}")
        print("DEBUG: Will only create local entries without Cloudinary URLs")
        upload_audio_to_cloudinary = None
    
    audio_files = []
    for root, dirs, files in os.walk(audio_dir):
        for file in files:
            if file.lower().endswith(('.mp3', '.wav', '.m4a', '.flac', '.aac')):
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, audio_dir)
                audio_files.append((relative_path, full_path))
    
    print(f"DEBUG: Found {len(audio_files)} audio files")
    
    for relative_path, full_path in audio_files:
        # Check if song already exists in database
        existing_song = songs_collection.find_one({"title": os.path.splitext(os.path.basename(relative_path))[0]})
        if existing_song:
            print(f"DEBUG: Song already exists in DB: {relative_path}")
            continue
        
        # Create song record
        file_name = os.path.splitext(os.path.basename(relative_path))[0]
        
        # Extract playlist from path (e.g., playlist/nature_mix/song.mp3 -> nature_mix)
        path_parts = relative_path.replace('\\', '/').split('/')
        playlist = None
        if len(path_parts) >= 2 and path_parts[0] == 'playlist':
            folder_name = path_parts[1].replace('_', ' ').lower()
            playlist = folder_name
        
        song_data = {
            "title": file_name.replace('-', ' ').replace('_', ' ').title(),
            "tags": [file_name.lower(), "scanned"],
            "language": "English",
            "artist": "Unknown Artist",
            "emotion": "neutral",
            "duration": 200,  # Default duration
        }
        
        if playlist:
            song_data["playlist"] = playlist
            song_data["tags"].append(playlist.lower())
        
        # Upload to Cloudinary if available
        if upload_audio_to_cloudinary:
            try:
                cloudinary_url = upload_audio_to_cloudinary(full_path)
                song_data["audio_path"] = cloudinary_url
                normalized_path = relative_path.replace('\\', '/')
                song_data["audio_url"] = f"https://variedly-unspirited-archie.ngrok-free.dev/audio/{normalized_path}"
                print(f"DEBUG: Uploaded to Cloudinary: {file_name} -> {cloudinary_url}")
            except Exception as e:
                print(f"DEBUG: Cloudinary upload failed for {file_name}: {e}")
                # Fallback to local path
                normalized_path = relative_path.replace('\\', '/')
                song_data["audio_path"] = f"/audio/{normalized_path}"
                song_data["audio_url"] = f"https://variedly-unspirited-archie.ngrok-free.dev/audio/{normalized_path}"
        else:
            # No Cloudinary - use local path with ngrok URL
            normalized_path = relative_path.replace('\\', '/')
            song_data["audio_path"] = f"/audio/{normalized_path}"
            song_data["audio_url"] = f"https://variedly-unspirited-archie.ngrok-free.dev/audio/{normalized_path}"
            print(f"DEBUG: Using local path for {file_name}")
        
        try:
            insert_song(song_data)
            print(f"DEBUG: Added song to DB: {file_name}")
        except Exception as e:
            print(f"DEBUG: Error adding song {file_name} to DB: {e}")
