"""
Audio file serving for local audio files
This allows playback of local audio files without Cloudinary
"""

import os
import shutil
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

def setup_audio_serving(app: FastAPI):
    """
    Setup audio file serving for local files
    """
    
    # Create audio directory if it doesn't exist
    audio_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/audio"))
    os.makedirs(audio_dir, exist_ok=True)
    
    # Mount static files for audio
    app.mount("/audio", StaticFiles(directory=audio_dir), name="audio")
    
    # Create sample audio files if they don't exist
    create_sample_audio_files(audio_dir)
    
    print(f"Audio files served from: {audio_dir}")
    print(f"Access audio at: http://localhost:8080/audio/filename.mp3")

def create_sample_audio_files(audio_dir: str):
    """
    Create sample audio files for testing
    """
    
    # List of sample files that should exist
    sample_files = [
        'classroom_smiles.mp3',
        'silent_tears.mp3',
        'gym_power.mp3', 
        'athikaalai.mp3',
        'First-Last.mp3'
    ]
    
    # Create a simple audio file (you should replace with actual audio files)
    for filename in sample_files:
        file_path = os.path.join(audio_dir, filename)
        
        if not os.path.exists(file_path):
            # Create a placeholder file (replace with actual audio)
            try:
                # You can download sample audio files or use your own
                # For now, create a dummy file
                with open(file_path, 'wb') as f:
                    f.write(b'placeholder_audio_data')
                print(f"Created placeholder: {filename}")
            except Exception as e:
                print(f"Error creating {filename}: {e}")
        else:
            print(f"File exists: {filename}")

def get_audio_url(audio_path: str) -> str:
    """
    Convert local audio path to proper URL
    """
    
    if audio_path.startswith('/audio/'):
        # Already in correct format
        return f"http://localhost:8080{audio_path}"
    elif audio_path.startswith('./'):
        # Convert ./audio/file.mp3 to /audio/file.mp3
        return audio_path.replace('./', '/').replace('http://localhost:8080', '')
    elif 'cloudinary' in audio_path or 'firebase' in audio_path:
        # Already a remote URL
        return audio_path
    else:
        # Assume it's a local path that needs conversion
        if audio_path.endswith(('.mp3', '.wav', '.m4a', '.ogg')):
            filename = os.path.basename(audio_path)
            return f"http://localhost:8080/audio/{filename}"
        else:
            return audio_path

def update_songs_with_working_urls():
    """
    Update songs in database with working audio URLs
    """
    from app.db.mongodb import songs_collection
    
    print("Updating songs with working audio URLs...")
    
    songs = list(songs_collection.find({}))
    updated_count = 0
    
    for song in songs:
        old_path = song.get('audio_path', '')
        title = song.get('title', 'Unknown')
        
        # Convert to working URL
        new_url = get_audio_url(old_path)
        
        if old_path != new_url:
            songs_collection.update_one(
                {'_id': song['_id']},
                {'$set': {'audio_path': new_url}}
            )
            updated_count += 1
            print(f"Updated {title}: {old_path} -> {new_url}")
    
    print(f"Updated {updated_count} songs with working URLs")
