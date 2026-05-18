from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, validator
from typing import Optional
from urllib.parse import quote
import asyncio
import bcrypt
import jwt
import os
import uuid
import shutil
import tempfile
import signal
import threading
import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# REQUIRED IMPORTS (core functionality)
from app.db.mongodb import users_collection, songs_collection
from app.db.song_repository import get_all_songs
from app.db.mongodb import initialize_sample_songs
from app.db.song_repository import find_songs_by_emotion, insert_song

# OPTIONAL IMPORTS (features that can fail independently)
try:
    from app.yolo.detector import run_yolo_classification
    print("YOLO detection service loaded successfully")
except ImportError as e:
    print(f"YOLO import failed: {e}")
    run_yolo_classification = None

try:
    from search_engine.search import find_best_song
    print("Search service loaded successfully")
except ImportError as e:
    print(f"Search import failed: {e}")
    find_best_song = None

try:
    from search_engine.emotion_mapper import map_keywords_to_emotions, map_class_to_emotion
    print("Emotion mapping service loaded successfully")
except ImportError as e:
    print(f"Emotion mapping import failed: {e}")
    map_keywords_to_emotions = None
    map_class_to_emotion = None

try:
    from app.cloudinary_config import upload_audio_to_cloudinary
    print("Cloudinary service loaded successfully")
except ImportError as e:
    print(f"Cloudinary import failed: {e}")
    upload_audio_to_cloudinary = None

# IMPORT TEXT TO SING - FROM SAME app DIRECTORY
from app.text_to_sing import TextToSing

tts_engine = None

def _generate_song_blocking(lyrics: str, singer: str, mode: str) -> dict:
    """Blocking helper to instantiate TextToSing and generate a song."""
    tts = TextToSing()
    return tts.generate_song(lyrics, singer, mode)

app = FastAPI(title="TuneFlex API")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    """Format validation errors for frontend display"""
    errors = {}
    for error in exc.errors():
        field = error['loc'][-1] if error['loc'] else 'general'
        message = error['msg']
        if field == 'email' and 'valid email address' in message.lower():
            message = 'Email must be a valid format like user@gmail.com'
        errors[field] = message
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Validation failed",
            "errors": errors,
            "type": "validation_error"
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Format HTTP exceptions for frontend display"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "type": "http_error"
        }
    )

@app.on_event("startup")
def startup_event():
    try:
        initialize_sample_songs()
        print("Sample songs initialized")
        
        # Create audio directory for local files
        audio_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/audio"))
        os.makedirs(audio_dir, exist_ok=True)
        print(f"Audio directory ready: {audio_dir}")
        
    except Exception as e:
        print("Song initialization error:", e)

audio_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/audio"))
app.mount("/audio", StaticFiles(directory=audio_dir), name="audio")

executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="tts_worker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    allow_credentials=True
)

SECRET_KEY = "tuneflex-secret"

def validate_password(password: str) -> tuple[bool, str]:
    """
    Validate password strength.
    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character (!@#$%^&*)"
    return True, "Password is valid"

def validate_email(email: str) -> tuple[bool, str]:
    """Validate email format"""
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.fullmatch(email_regex, email):
        return False, "Email must be a valid format like user@gmail.com"
    return True, "Email is valid"

def validate_username(username: str) -> tuple[bool, str]:
    """
    Validate username.
    Requirements:
    - 3-20 characters
    - Only letters, numbers, and underscores
    """
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    if len(username) > 20:
        return False, "Username must be at most 20 characters"
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    return True, "Username is valid"

class LoginRequest(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    password: str

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

class SearchRequest(BaseModel):
    query: str

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

@app.post("/auth/register")
def register(data: RegisterRequest):
    """
    Register a new user with validation
    """
    # Manual validation with detailed error collection
    errors = {}
    
    # Validate username
    if not data.username or not data.username.strip():
        errors["username"] = "Username cannot be empty"
    else:
        is_valid, message = validate_username(data.username)
        if not is_valid:
            errors["username"] = message
    
    # Validate email
    if not data.email or not data.email.strip():
        errors["email"] = "Email cannot be empty"
    else:
        is_valid, message = validate_email(data.email)
        if not is_valid:
            errors["email"] = message
    
    # Validate password
    if not data.password or not data.password.strip():
        errors["password"] = "Password cannot be empty"
    else:
        is_valid, message = validate_password(data.password)
        if not is_valid:
            errors["password"] = message
    
    # If there are validation errors, return them
    if errors:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "message": "Validation failed",
                "errors": errors,
                "type": "validation_error"
            }
        )
    
    if users_collection is None:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": "Database connection not available",
                "type": "http_error"
            }
        )
    
    # Check if email already exists (case-insensitive)
    existing_email = users_collection.find_one({"email": data.email.lower()})
    if existing_email:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "message": "Email already registered",
                "type": "http_error"
            }
        )
    
    # Check if username already exists (case-insensitive)
    existing_username = users_collection.find_one({"username": {"$regex": f"^{re.escape(data.username)}$", "$options": "i"}})
    if existing_username:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "message": "Username already taken",
                "type": "http_error"
            }
        )
    
    try:
        users_collection.insert_one({
            "username": data.username,
            "email": data.email.lower(),
            "password": hash_password(data.password),
            "created_at": datetime.utcnow()
        })
        
        return {
            "success": True,
            "message": "Registered successfully",
            "username": data.username,
            "email": data.email
        }
    except Exception as e:
        print(f"Registration error: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": "Registration failed. Please try again.",
                "type": "http_error"
            }
        )

@app.post("/auth/login")
def login(data: LoginRequest):
    if users_collection is None:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": "Database connection not available",
                "type": "http_error"
            }
        )
        
    user = None   

    if data.email:
        user = users_collection.find_one({"email": data.email.lower()})
    elif data.username:
        user = users_collection.find_one({"username": {"$regex": f"^{re.escape(data.username)}$", "$options": "i"}})

    if not user:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "success": False,
                "message": "User not found",
                "type": "http_error"
            }
        )
    
    if not verify_password(data.password, user["password"]):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "success": False,
                "message": "Invalid credentials",
                "type": "http_error"
            }
        )

    token = jwt.encode({"email": str(user["email"])}, SECRET_KEY, algorithm="HS256")

    return {
        "success": True,
        "message": "Login successful",
        "token": token,
        "username": user.get("username", "")
    }

@app.post("/search-song")
def search_song(data: SearchRequest):
    """Search for best matching song"""
    print(f"DEBUG: Searching for best song: {data.query}")
    
    if find_best_song is None:
        print("DEBUG: Search service unavailable")
        return {"songs": []}
        
    try:
        result = find_best_song(data.query)
        print(f"DEBUG: find_best_song returned: {result}")
        
        if not result:
            print("DEBUG: No result found")
            return {"songs": []}
        
        # Ensure all required fields are present for Android SongResponse model
        audio_path = result.get("audio_path", "")
        audio_url = result.get("audio_url", "")
        
        # Set audio_url if not present
        if not audio_url:
            audio_url = build_audio_url(audio_path)
        
        # Complete song response with all required fields
        complete_result = {
            "_id": result.get("_id", f"search_{data.query}_{hash(str(result)) % 10000}"),
            "title": result.get("title", "Unknown"),
            "artist": result.get("artist", "Unknown Artist"),
            "album": result.get("album", None),
            "duration": result.get("duration", 200),
            "audio_path": audio_path,
            "audio_url": audio_url,
            "emotion": result.get("emotion", "neutral"),
            "tags": result.get("tags", []),
            "language": result.get("language", "English"),
            "created_at": result.get("created_at", "2024-01-01T00:00:00Z"),
            "updated_at": result.get("updated_at", "2024-01-01T00:00:00Z")
        }
        
        print(f"DEBUG: Returning complete song: {complete_result.get('title', 'Unknown')}")
        print(f"DEBUG: Audio URL: {complete_result['audio_url']}")
        return {"songs": [complete_result]}
        
    except Exception as e:
        print(f"DEBUG: Search error: {e}")
        return {"songs": []}

@app.post("/search-songs-by-tag")
def search_songs_by_tag(data: SearchRequest):
    """Search songs by tag/genre/keyword"""
    print(f"DEBUG: Searching songs by tag: {data.query}")
    try:
        all_songs = get_all_songs()
        print(f"DEBUG: Total songs in database: {len(all_songs)}")
        
        # Search in title, artist, tags, and emotion
        matching_songs = []
        search_query = data.query.lower().strip()
        
        for song in all_songs:
            # Check if search query matches any field
            title_match = search_query in song.get("title", "").lower()
            artist_match = search_query in song.get("artist", "").lower()
            emotion_match = search_query in song.get("emotion", "").lower()
            
            # Check tags
            tags_match = False
            tags = song.get("tags", [])
            if isinstance(tags, list):
                tags_match = any(search_query in str(tag).lower() for tag in tags)
            
            # Check language
            language_match = search_query in song.get("language", "").lower()
            
            if title_match or artist_match or emotion_match or tags_match or language_match:
                # Ensure all required fields are present for Android SongResponse model
                audio_path = song.get("audio_path", "")
                audio_url = song.get("audio_url", "")
                
                # Set audio_url if not present
                if not audio_url:
                    audio_url = build_audio_url(audio_path)
                
                # Complete song response with all required fields
                complete_song = {
                    "_id": song.get("_id", str(song.get("title", "unknown"))),
                    "title": song.get("title", "Unknown"),
                    "artist": song.get("artist", "Unknown Artist"),
                    "album": song.get("album", None),
                    "duration": song.get("duration", 200),
                    "audio_path": audio_path,
                    "audio_url": audio_url,
                    "emotion": song.get("emotion", "neutral"),
                    "tags": song.get("tags", []),
                    "language": song.get("language", "English"),
                    "created_at": song.get("created_at", "2024-01-01T00:00:00Z"),
                    "updated_at": song.get("updated_at", "2024-01-01T00:00:00Z")
                }
                
                matching_songs.append(complete_song)
        
        print(f"DEBUG: Found {len(matching_songs)} matching songs")
        return {"songs": matching_songs}
        
    except Exception as e:
        print(f"Error searching songs by tag: {e}")
        return {"songs": []}


def build_audio_url(audio_path: str, request: Optional[Request] = None) -> str:
    if not audio_path:
        return ""
    if audio_path.startswith("http"):
        return audio_path
    if audio_path.startswith("/"):
        encoded_path = quote(audio_path, safe="/")
        if request is not None:
            base_url = str(request.base_url).rstrip("/")
            return f"{base_url}{encoded_path}"
        return f"https://variedly-unspirited-archie.ngrok-free.dev{encoded_path}"
    return audio_path

@app.get("/songs/artist/{artist_name}")
def get_artist_songs(artist_name: str, request: Request):
    """Get songs for a specific artist."""
    try:
        all_songs = get_all_songs()
        artist_query = artist_name.lower().strip()
        print(f"DEBUG: /songs/artist/{artist_name} called")

        artist_songs = []
        for song in all_songs:
            artist = str(song.get("artist", ""))
            title = str(song.get("title", ""))
            tags = song.get("tags", [])
            if isinstance(tags, str):
                tags = [tag.strip() for tag in tags.split(",")]

            if artist_query in artist.lower() or artist_query in title.lower() or any(artist_query in str(tag).lower() for tag in tags):
                audio_path = song.get("audio_path", "")
                audio_url = song.get("audio_url", "")
                if not audio_url:
                    audio_url = build_audio_url(audio_path, request)

                song_data = {
                    "_id": str(song.get("_id", song.get("title", ""))),
                    "title": song.get("title", ""),
                    "artist": artist,
                    "album": song.get("album", ""),
                    "duration": song.get("duration", 200),
                    "audio_path": audio_path,
                    "audio_url": audio_url,
                    "emotion": song.get("emotion", ""),
                    "tags": tags,
                    "language": song.get("language", ""),
                    "created_at": song.get("created_at", ""),
                    "updated_at": song.get("updated_at", "")
                }
                artist_songs.append(song_data)

        print(f"DEBUG: Found {len(artist_songs)} songs for artist '{artist_name}'")
        return {"songs": artist_songs}
    except Exception as e:
        print(f"Error getting artist songs: {e}")
        return {"songs": []}


@app.get("/songs")
def get_songs(request: Request):
    try:
        songs = get_all_songs()
        base_url = str(request.base_url).rstrip("/")

        for song in songs:
            audio_path = song.get("audio_path", "")
            song["audio_url"] = build_audio_url(audio_path, request)

        return {"songs": songs}
    except Exception as e:
        print(f"Error getting songs: {e}")
        return {"songs": []}

@app.get("/songs/hiphop")
def get_hiphop_songs(request: Request):
    """Get all hiphop songs - simple GET endpoint"""
    print("DEBUG: /songs/hiphop endpoint called")
    try:
        all_songs = get_all_songs()
        print(f"DEBUG: Total songs in database: {len(all_songs)}")
        
        # Use ngrok URL for audio
        ngrok_url = "https://variedly-unspirited-archie.ngrok-free.dev"
        print(f"DEBUG: Using ngrok URL: {ngrok_url}")
        
        # Filter only hiphop songs
        hiphop_songs = []
        for song in all_songs:
            # Check if hiphop in tags or artist
            tags = song.get("tags", [])
            if isinstance(tags, str):
                tags = [tag.strip() for tag in tags.split(",")]
            
            artist_match = "hiphop" in song.get("artist", "").lower()
            title_match = "hiphop" in song.get("title", "").lower()
            tag_match = any("hiphop" in tag.lower() for tag in tags)
            
            print(f"DEBUG: Song - Artist: {song.get('artist', '')}, Title: {song.get('title', '')}, Tags: {tags}")
            print(f"DEBUG: Matches - Artist: {artist_match}, Title: {title_match}, Tag: {tag_match}")
            
            if artist_match or title_match or tag_match:
                # Create song with proper format for Android
                song_data = {
                    "_id": str(song.get("_id", "")),
                    "title": song.get("title", ""),
                    "artist": song.get("artist", ""),
                    "album": song.get("album", "Hiphop Collection"),
                    "audio_path": song.get("audio_path", ""),
                    "audio_url": f"{ngrok_url}{song.get('audio_path', '')}",
                    "emotion": song.get("emotion", "energetic"),
                    "tags": tags,
                    "language": song.get("language", "Tamil"),
                    "duration": song.get("duration", 200),
                    "created_at": song.get("created_at", ""),
                    "updated_at": song.get("updated_at", "")
                }
                hiphop_songs.append(song_data)
                print(f"DEBUG: Added hiphop song: {song_data['title']} -> {song_data['audio_url']}")
        
        print(f"DEBUG: Found {len(hiphop_songs)} hiphop songs")
        print(f"DEBUG: Returning songs: {[s['title'] for s in hiphop_songs]}")
        return {"songs": hiphop_songs}
    except Exception as e:
        print(f"DEBUG: Error getting hiphop songs: {e}")
        return {"songs": []}

@app.post("/upload-song")
async def upload_song(
    file: UploadFile = File(...),
    title: str = Form(...),
    artist: str = Form(...),
    emotion: str = Form(...),
    tags: str = Form(...), # Comma-separated tags
    language: str = Form("English")
):
    """
    Upload a song file to Cloudinary and save metadata to MongoDB
    """
    if upload_audio_to_cloudinary is None:
        raise HTTPException(status_code=503, detail="Cloudinary upload service not available")
        
    try:
        # Validate file type
        if not file.filename.endswith(('.mp3', '.wav', '.m4a', '.ogg')):
            raise HTTPException(status_code=400, detail="Invalid file type. Only audio files allowed.")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_path = tmp_file.name
        
        try:
            # Upload to Cloudinary
            cloudinary_url = upload_audio_to_cloudinary(tmp_path)
            
            # Parse tags
            tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
            
            # Save to MongoDB
            song_data = {
                "title": title,
                "artist": artist,
                "audio_path": cloudinary_url,  # Store Cloudinary URL instead of local path
                "emotion": emotion,
                "tags": tag_list,
                "language": language,
                "created_at": datetime.utcnow()
            }
            
            insert_song(song_data)
            
            return {
                "message": "Song uploaded successfully",
                "title": title,
                "cloudinary_url": cloudinary_url,
                "tags": tag_list
            }
            
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/detect")
async def detect_image(file: UploadFile = File(...)):
    print(f"DEBUG: Detect endpoint called with file: {file.filename}, content_type: {file.content_type}")
    print(f"DEBUG: File object details: {file}")
    print(f"DEBUG: File size: {file.size if hasattr(file, 'size') else 'Unknown'}")
    
    if run_yolo_classification is None:
        print("DEBUG: YOLO service not available")
        raise HTTPException(status_code=503, detail="YOLO detection service not available")
        
    try:
        # Validate file
        if not file.filename:
            print("DEBUG: No filename provided")
            raise HTTPException(status_code=400, detail="No file provided")
            
        print(f"DEBUG: Processing file: {file.filename}")
        
        # Get file extension safely
        if "." in file.filename:
            extension = file.filename.split(".")[-1].lower()
        else:
            extension = "jpg"  
            
        print(f"DEBUG: File extension: {extension}")
            
        # Validate image extension
        allowed_extensions = ["jpg", "jpeg", "png", "bmp", "tiff"]
        if extension not in allowed_extensions:
            print(f"DEBUG: Invalid extension: {extension}")
            raise HTTPException(status_code=400, detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}")
        
        filename = f"{uuid.uuid4()}.{extension}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        print(f"DEBUG: Saving to: {file_path}")

        # Save file with proper seeking
        if hasattr(file, 'seek'):
            file.file.seek(0)  # Reset file pointer to beginning
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Verify file was saved and has content
        if not os.path.exists(file_path):
            print("DEBUG: File was not saved")
            raise HTTPException(status_code=500, detail="Failed to save uploaded file")
            
        file_size = os.path.getsize(file_path)
        print(f"DEBUG: File saved, size: {file_size} bytes")
        
        if file_size == 0:
            print("DEBUG: File is empty")
            raise HTTPException(status_code=500, detail="Uploaded file is empty")

        print("DEBUG: Running YOLO detection...")
        detections = run_yolo_classification(file_path)
        print(f"DEBUG: YOLO returned: {detections}")
        
        # Clean up file
        if os.path.exists(file_path):
            os.remove(file_path)
            print("DEBUG: File cleaned up")

        if not detections:
            print("DEBUG: No detections found")
            return {"message": "No classification detected"}

  
        class_id = detections[0]["class_id"]
        class_name = detections[0]["class_name"]
        print(f"DEBUG: Best detection - class_id: {class_id}, class_name: {class_name}")
        
        # Map class ID → emotion
        if map_class_to_emotion is None:
            print("DEBUG: Emotion mapping not available")
            raise HTTPException(status_code=503, detail="Emotion mapping service not available")
            
        emotion = map_class_to_emotion(class_id)
        print(f"DEBUG: Mapped to emotion: {emotion}")
        
       
        songs = find_songs_by_emotion(emotion)
        print(f"DEBUG: Found {len(songs)} songs for emotion {emotion}")
        
        if not songs:
            print(f"DEBUG: No songs found for emotion {emotion}, checking all songs...")
            
            all_songs = get_all_songs()
            songs = [s for s in all_songs if s.get("class_id") == class_id]
            print(f"DEBUG: Found {len(songs)} songs by class_id {class_id}")
        
        if not songs:
            return {
                "filename": filename,
                "classifications": detections,
                "class_id": class_id,
                "class_name": class_name,
                "object": class_name,
                "emotion": emotion,
                "song": f"No song available for {emotion}",
                "audio_path": None,
                "audio_url": None
            }

       
        if class_id == 0:
            print(f"DEBUG: Class 0 detected - returning mood selection options")
            
            
            mood_songs = {
                "happy": {
                    "primary": {
                        "_id": "mood_happy_1",
                        "title": "First-Last",
                        "artist": "TuneFlex Collection",
                        "album": "Class 0 Collection",
                        "duration": 240,
                        "audio_path": "/audio/0/First-Last.mp3",
                        "audio_url": f"https://variedly-unspirited-archie.ngrok-free.dev/audio/0/First-Last.mp3",
                        "emotion": "happy",
                        "tags": ["happy", "first_last"],
                        "language": "Tamil",
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_at": "2024-01-01T00:00:00Z"
                    },
                    "secondary": {
                        "_id": "mood_happy_2",
                        "title": "Jada-Jada-Jaada",
                        "artist": "TuneFlex Collection",
                        "album": "Class 0 Collection",
                        "duration": 210,
                        "audio_path": "/audio/0/Jada-Jada-Jaada.mp3",
                        "audio_url": f"https://variedly-unspirited-archie.ngrok-free.dev/audio/0/Jada-Jada-Jaada.mp3",
                        "emotion": "happy",
                        "tags": ["happy", "motivation", "jada_jada"],
                        "language": "Tamil",
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_at": "2024-01-01T00:00:00Z"
                    }
                },
                "sad": {
                    "primary": {
                        "_id": "mood_sad_1",
                        "title": "Unmaiorunaal-Vellum",
                        "artist": "TuneFlex Collection",
                        "album": "Class 0 Collection",
                        "duration": 195,
                        "audio_path": "/audio/0/Unmaiorunaal-Vellum.mp3",
                        "audio_url": f"https://variedly-unspirited-archie.ngrok-free.dev/audio/0/Unmaiorunaal-Vellum.mp3",
                        "emotion": "sad",
                        "tags": ["sad", "unmaiorunaal"],
                        "language": "Tamil",
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_at": "2024-01-01T00:00:00Z"
                    }
                },
                "positive_vibe": {
                    "primary": {
                        "_id": "mood_positive_1",
                        "title": "Edhirthu-Nil",
                        "artist": "TuneFlex Collection",
                        "album": "Class 0 Collection",
                        "duration": 240,
                        "audio_path": "/audio/0/Edhirthu-Nil.mp3",
                        "audio_url": f"https://variedly-unspirited-archie.ngrok-free.dev/audio/0/Edhirthu-Nil.mp3",
                        "emotion": "positive_vibe",
                        "tags": ["positive_vibe", "edhirthu_nil"],
                        "language": "Tamil",
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_at": "2024-01-01T00:00:00Z"
                    }
                }
            }
            
            print(f"DEBUG: Available moods: {list(mood_songs.keys())}")
            
            return {
                "filename": filename,
                "classifications": detections,
                "class_id": class_id,
                "class_name": class_name,
                "object": class_name,
                "emotion": "custom_0",
                "song": "Select your mood",  
                "audio_path": None,
                "audio_url": None,
                "mood_selection": True,  
                "available_moods": list(mood_songs.keys()),
                "mood_songs": mood_songs,  
                "songs": []   }

        # Take first song for other classes
        selected_song = songs[0]
        print(f"DEBUG: Selected song: {selected_song['title']}")
        
        # Get proper audio URL
        audio_url = selected_song.get("audio_url", "")
        if not audio_url or "localhost" in audio_url:
            # Build URL from audio_path if needed
            audio_path = selected_song.get("audio_path", "")
            if audio_path:
                audio_url = build_audio_url(audio_path)
        
        print(f"DEBUG: Selected song URL: {audio_url}")

        return {
            "filename": filename,
            "classifications": detections,
            "class_id": class_id,
            "class_name": class_name,
            "object": class_name,
            "emotion": emotion,
            "song": selected_song["title"],
            "audio_path": selected_song["audio_path"],
            "audio_url": audio_url,
            "songs": [selected_song]  # Single song for other classes
        }
    
    except HTTPException as e:
        print(f"DEBUG: HTTPException occurred: status_code={e.status_code}, detail={e.detail}")
        raise
    except Exception as e:
        print(f"DEBUG: Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        # Clean up file on error
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        return {"message": f"Detection failed: {str(e)}"}

@app.post("/text-to-sing")
async def text_to_sing_endpoint(
    text: str = Form(...),
    emotion: Optional[str] = Form(None),
    voice_style: Optional[str] = Form(None),
    mode: Optional[str] = Form("pop")
):
    print(f"DEBUG: Received text={text}, emotion={emotion}, voice_style={voice_style}, mode={mode}")
    
    try:
        print("DEBUG: Using TTS engine (worker thread instantiation)...")
        
        # Map emotion to singer
        singer_mapping = {
            "happy": "female", 
            "sad": "male",
            "angry": "robot",
            "neutral": "female",
            "excited": "female"
        }
        singer = singer_mapping.get(voice_style, "female")
        print(f"DEBUG: Mapped singer={singer}")
        
        # Map emotion to mode
        mode_mapping = {
            "happy": "pop",
            "sad": "calm", 
            "angry": "hiphop",
            "neutral": "melody",
            "excited": "pop"
        }
        mode = mode_mapping.get(emotion, "pop")
        print(f"DEBUG: Mapped mode={mode}")
        
        # Run the blocking audio generation in a thread to avoid blocking the event loop
        try:
            estimated_timeout = max(45.0, len(text) * 1.5 + 15.0)
            print(f"DEBUG: using dynamic timeout {estimated_timeout:.1f}s for text length {len(text)}")
            result = await asyncio.wait_for(
                asyncio.to_thread(
                    _generate_song_blocking,
                    text,  # generate_song's first param is lyrics 
                    singer,
                    mode
                ),
                timeout=estimated_timeout
            )
            print("DEBUG: Audio generation completed:", result)
        except asyncio.TimeoutError:
            print("DEBUG: Audio generation timed out")
            return {"success": False, "message": "Audio generation timed out"}
        except Exception as e:
            print("DEBUG: Audio generation exception:", str(e))
            import traceback
            traceback.print_exc()
            return {"success": False, "message": f"Audio generation failed: {str(e)}"}
        
        # Ensure permanent audio directory exists
        permanent_audio_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/audio"))
        os.makedirs(permanent_audio_dir, exist_ok=True)
        
        filename = f"gen_song_{uuid.uuid4().hex[:8]}.wav"
        permanent_path = os.path.join(permanent_audio_dir, filename)
        download_path = os.path.join(UPLOAD_DIR, filename)
        
        # Handle file copying safely
        if os.path.exists(result.get('output_path', '')):
            shutil.copy2(result['output_path'], permanent_path)
            shutil.copy2(result['output_path'], download_path)
            print(f"DEBUG: File copied to {permanent_path} and {download_path}")
            
            # Insert generated song into DB for searching
            song_title = text[:25] + "..." if len(text) > 25 else text
            song_record = {
                "title": song_title,
                "audio_path": f"/audio/{filename}",
                "tags": [emotion, mode, singer, "generated"],
                "language": "English",
                "artist": f"AI Singer ({singer})",
                "emotion": emotion
            }
            try:
                insert_song(song_record)
                print("DEBUG: Generated song inserted into DB successfully.")
            except Exception as db_e:
                print(f"DEBUG: Error inserting song into DB: {db_e}")
        else:
            print("DEBUG: No output path in result")
            return {
                "success": False,
                "message": "Audio generation failed - no output file"
            }
        
        response = {
            "success": True,
            "audio_url": f"/download-audio/{filename}",
            "file_path": download_path,
            "message": "Audio generated successfully",
            "metadata": {
                "lyrics": result.get('lyrics', text),
                "phonemes": result.get('phonemes', []),
                "pitches": result.get('pitches', []),
                "durations": result.get('durations', []),
                "singer": result.get('singer', singer),
                "mode": result.get('mode', mode)
            }
        }
        print("DEBUG: Returning response:", response)
        return response
        
    except Exception as e:
        print("DEBUG: Exception occurred:", str(e))
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": f"Error generating audio: {str(e)}"
        }

@app.get("/download-audio/{filename}")
async def download_audio(filename: str):
    """Download generated audio file."""
    try:
        audio_path = os.path.join(UPLOAD_DIR, filename)
        
        if not os.path.exists(audio_path):
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        return FileResponse(
            audio_path, 
            media_type="audio/wav",
            filename=filename
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading audio: {str(e)}")

@app.post("/select-mood")
def select_mood(data: dict):
    """Handle mood selection and return appropriate songs"""
    print(f"DEBUG: Mood selection request: {data}")
    
    try:
        mood = data.get("mood", "")
        class_id = data.get("class_id", 0)
        
        if class_id != 0:
            return {"error": "Mood selection only available for class 0"}
        
        # Define mood to song mappings (same as detection)
        mood_songs = {
            "happy": {
                "primary": {
                    "_id": "mood_happy_1",
                    "title": "First-Last",
                    "artist": "TuneFlex Collection",
                    "album": "Class 0 Collection",
                    "duration": 240,
                    "audio_path": "/audio/0/First-Last.mp3",
                    "audio_url": f"https://variedly-unspirited-archie.ngrok-free.dev/audio/0/First-Last.mp3",
                    "emotion": "happy",
                    "tags": ["happy", "first_last"],
                    "language": "Tamil",
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z"
                }
            },
            "sad": {
                "primary": {
                    "_id": "mood_sad_1",
                    "title": "Unmaiorunaal-Vellum",
                    "artist": "TuneFlex Collection",
                    "album": "Class 0 Collection",
                    "duration": 195,
                    "audio_path": "/audio/0/Unmaiorunaal-Vellum.mp3",
                    "audio_url": f"https://variedly-unspirited-archie.ngrok-free.dev/audio/0/Unmaiorunaal-Vellum.mp3",
                    "emotion": "sad",
                    "tags": ["sad", "unmaiorunaal"],
                    "language": "Tamil",
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z"
                }
            },
            "positive_vibe": {
                "primary": {
                    "_id": "mood_positive_1",
                    "title": "Edhirthu-Nil",
                    "artist": "TuneFlex Collection",
                    "album": "Class 0 Collection",
                    "duration": 240,
                    "audio_path": "/audio/0/Edhirthu-Nil.mp3",
                    "audio_url": f"https://variedly-unspirited-archie.ngrok-free.dev/audio/0/Edhirthu-Nil.mp3",
                    "emotion": "positive_vibe",
                    "tags": ["positive_vibe", "edhirthu_nil"],
                    "language": "Tamil",
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z"
                }
            },
            "motivation": {
                "primary": {
                    "_id": "mood_motivation_1",
                    "title": "Jada-Jada-Jaada",
                    "artist": "TuneFlex Collection",
                    "album": "Class 0 Collection",
                    "duration": 210,
                    "audio_path": "/audio/0/Jada-Jada-Jaada.mp3",
                    "audio_url": f"https://variedly-unspirited-archie.ngrok-free.dev/audio/0/Jada-Jada-Jaada.mp3",
                    "emotion": "motivation",
                    "tags": ["motivation", "jada_jada"],
                    "language": "Tamil",
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z"
                }
            }
        }
        
        if mood not in mood_songs:
            return {"error": f"Invalid mood: {mood}"}
        
        selected_mood_songs = mood_songs[mood]
        
        # Build songs list based on mood
        if mood == "happy":
            # Happy gets both primary and secondary songs
            songs_list = [selected_mood_songs["primary"], selected_mood_songs["secondary"]]
            primary_song = selected_mood_songs["primary"]
        else:
            # Other moods get only primary song
            songs_list = [selected_mood_songs["primary"]]
            primary_song = selected_mood_songs["primary"]
        
        print(f"DEBUG: Selected mood: {mood}, returning {len(songs_list)} songs")
        
        return {
            "success": True,
            "mood": mood,
            "songs": songs_list,
            "primary_song": primary_song,
            "message": f"Playing {mood} songs"
        }
        
    except Exception as e:
        print(f"DEBUG: Mood selection error: {e}")
        return {"error": str(e)}

@app.get("/songs/playlist/{playlist_name}")
def get_playlist_songs(playlist_name: str, request: Request):
    """Get songs for a specific playlist"""
    print(f"DEBUG: Getting songs for playlist: {playlist_name}")
    try:
        all_songs = get_all_songs()
        print(f"DEBUG: Total songs in database: {len(all_songs)}")
        
        # Decode playlist name
        decoded_playlist = playlist_name.replace("%20", " ").strip().lower()
        print(f"DEBUG: Decoded playlist name: {decoded_playlist}")
        
        # Filter songs by actual playlist folder in audio path / URL
        playlist_songs = []
        for song in all_songs:
            song_playlist = song.get("playlist", "")
            audio_path = song.get("audio_path", "")
            audio_url = song.get("audio_url", "")
            
            normalized_audio_path = audio_path.lower() if isinstance(audio_path, str) else ""
            normalized_audio_url = audio_url.lower() if isinstance(audio_url, str) else ""
            
            folder_match = (
                f"/audio/playlist/{decoded_playlist}/" in normalized_audio_path or
                f"/audio/playlist/{decoded_playlist}/" in normalized_audio_url
            )
            playlist_aliases = {
                "red": {"nature mix"},
                "citizen": {"ocean waves"},
                "thuppaki": {"forest calm"},
                "visbarubam": {"sunset chill"}
            }
            alias_match = song_playlist.lower() in playlist_aliases.get(decoded_playlist, set())
            
            if folder_match or alias_match:
                # Ensure audio_url is set
                song_copy = song.copy()
                audio_path = song_copy.get("audio_path", "")
                audio_url = song_copy.get("audio_url", "")
                
                if not audio_url:
                    audio_url = build_audio_url(audio_path, request)
                
                song_copy["audio_url"] = audio_url
                
                # Ensure all required fields for Android SongResponse
                song_copy["_id"] = song_copy.get("_id", str(song_copy.get("title", "unknown")))
                song_copy["album"] = song_copy.get("album", f"{decoded_playlist} Collection")
                song_copy["duration"] = song_copy.get("duration", 200)
                song_copy["created_at"] = song_copy.get("created_at", "2024-01-01T00:00:00Z")
                song_copy["updated_at"] = song_copy.get("updated_at", "2024-01-01T00:00:00Z")
                
                playlist_songs.append(song_copy)
        
        # Limit to maximum 10 songs per playlist (like previous implementation)
        if len(playlist_songs) > 10:
            playlist_songs = playlist_songs[:10]
            print(f"DEBUG: Limited playlist to first 10 songs (was {len(playlist_songs)})")
        else:
            print(f"DEBUG: Playlist has {len(playlist_songs)} songs (no limit needed)")
        
        print(f"DEBUG: Found {len(playlist_songs)} songs for playlist {decoded_playlist}")
        return {"songs": playlist_songs}
        
    except Exception as e:
        print(f"DEBUG: Error getting playlist songs: {e}")
        return {"songs": []}

@app.get("/health")
def health():
    try:
        
        song_count = len(get_all_songs()) if songs_collection is not None else 0
        return {
            "status": "ok",
            "database": songs_collection is not None,
            "total_songs": song_count
        }
    except:
        return {
            "status": "ok",
            "database": False,
            "total_songs": 0
        }

@app.get("/")
def root():
    return {"message": "TuneFlex API running"}

@app.get("/audio-debug")
def audio_debug():
    """Debug audio files and create test file if needed"""
    audio_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/audio"))
    
    # List existing files
    files = []
    if os.path.exists(audio_dir):
        for root, dirs, filenames in os.walk(audio_dir):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                rel_path = os.path.relpath(file_path, audio_dir)
                files.append({
                    "filename": filename,
                    "relative_path": rel_path.replace("\\", "/"),  # Convert Windows path to web path
                    "size": os.path.getsize(file_path),
                    "url": f"/audio/{rel_path.replace('\\', '/')}"
                })
    
   
    test_file_path = os.path.join(audio_dir, "0", "First-Last.mp3")
    os.makedirs(os.path.dirname(test_file_path), exist_ok=True)
    
    if not os.path.exists(test_file_path):
      
        try:
            with open(test_file_path, 'wb') as f:
                
                f.write(b'RIFF\x24\x08\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x02\x00\x44\xAC\x00\x00\x10\xB1\x02\x00\x04\x00\x10\x00data\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
            files.append({
                "filename": "First-Last.mp3",
                "relative_path": "0/First-Last.mp3",
                "size": os.path.getsize(test_file_path),
                "url": "/audio/0/First-Last.mp3",
                "created": True
            })
        except Exception as e:
            return {"error": f"Failed to create test file: {e}"}
    
    return {
        "audio_directory": audio_dir,
        "files": files,
        "test_url": "http://localhost:8080/audio/0/First-Last.mp3"
    }

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    print("Shutting down TuneFlex API...")
    try:
        executor.shutdown(wait=False)
        print("Thread pool shutdown complete")
    except Exception as e:
        print(f"Error during shutdown: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
