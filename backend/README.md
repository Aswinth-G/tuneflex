# TuneFlex Backend

AI-powered music retrieval and generation backend service for the TuneFlex platform. Converts images and text into music through intelligent object detection, emotion mapping, and audio synthesis.

## Features

- **Image-to-Music**: Detect objects in images using YOLOv8 and retrieve relevant songs from the database
- **Search Engine**: Intelligent song matching based on keywords and emotions
- **Text-to-Singing**: Convert text input into singing audio with background music
- **Audio Management**: Stream local audio files with metadata management
- **User Authentication**: JWT-based user management with encrypted passwords
- **Database**: MongoDB integration for song metadata and user profiles
- **Emotion Mapping**: Map detected objects and keywords to music emotions
- **Cloudinary Integration**: Optional cloud storage for media files

## Project Structure

```
backend/
├── app/
│   ├── main.py                    # FastAPI application entry point
│   ├── audio_server.py            # Audio file serving configuration
│   ├── cloudinary_config.py       # Cloudinary setup
│   ├── db/
│   │   ├── mongodb.py             # MongoDB connection and initialization
│   │   └── song_repository.py     # Song database operations
│   ├── schemas/
│   │   └── songs.py               # Pydantic schemas for API validation
│   ├── yolo/
│   │   ├── detector.py            # YOLO image classification
│   │   └── best.pt                # YOLOv8 pre-trained model
│   └── text_to_sing/
│       ├── text_to_sing.py        # Text-to-singing engine
│       └── __pycache__/
├── search_engine/
│   ├── search.py                  # Main song search logic
│   ├── song_loader.py             # Load songs from database
│   ├── song_ranker.py             # Rank songs by relevance
│   ├── emotion_mapper.py           # Map keywords/classes to emotions
│   ├── similarity.py               # Similarity calculation
│   ├── text_utils.py              # Text processing utilities
│   └── db_operations.py           # Database query helpers
├── data/
│   ├── songs.json                 # Master song list
│   └── audio/                     # Audio files by category
├── requirements.txt               # Python dependencies
├── *.py                          # Data import scripts
└── temp_uploads/                 # Temporary file storage

```

## Installation

### Prerequisites

- Python 3.8+
- MongoDB running locally (default: `mongodb://localhost:27017`)
- Pip package manager

### Setup Steps

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment** (optional but recommended)
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # On Windows
   # or
   source venv/bin/activate      # On macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables** (if needed)
   - Create `.env` file in backend directory with MongoDB connection string
   - Or ensure MongoDB is running on default port `27017`

5. **Initialize sample data** (optional)
   - Sample songs are automatically initialized on first run

## Running the Server

### Development Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

- Server runs on `http://localhost:8080`
- API documentation available at `http://localhost:8080/docs`
- Alternative docs at `http://localhost:8080/redoc`

### Production Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080 --workers 4
```

## API Endpoints

### Authentication
- `POST /register` - Register new user
- `POST /login` - Login user and get JWT token

### Song Search
- `POST /search/query` - Search songs by text query
- `GET /songs` - Get all songs with pagination
- `POST /songs/emotion` - Find songs by emotion

### Image Processing
- `POST /detect/image` - Upload image for object detection
- `GET /classifications/{image_id}` - Get detection results

### Audio Synthesis
- `POST /text-to-sing` - Convert text to singing audio
- `GET /audio/{filename}` - Stream audio file

### Song Management
- `GET /songs/{id}` - Get song details
- `POST /songs` - Add new song to database
- `DELETE /songs/{id}` - Remove song from database

## Core Modules

### 1. Database (`app/db/`)

**mongodb.py** - MongoDB connection and collections:
- Initializes MongoDB client and database
- Manages songs and users collections
- Creates sample data on startup

**song_repository.py** - Repository pattern for database operations:
- `get_all_songs()` - Fetch all songs
- `find_songs_by_emotion(emotion)` - Filter by emotion
- `insert_song(song_data)` - Add new song

### 2. Image Detection (`app/yolo/`)

**detector.py** - YOLOv8 image classification:
- Loads pre-trained `best.pt` model
- Classifies objects in images
- Returns class names with confidence scores
- Used for image-to-music conversion

### 3. Search Engine (`search_engine/`)

**search.py** - Main search orchestrator:
- Coordinates search components
- Returns best matching song for query

**emotion_mapper.py** - Maps keywords to emotions:
- `map_keywords_to_emotions(keywords)` - Convert text to emotions
- `map_class_to_emotion(class_name)` - Convert object classes to emotions

**song_ranker.py** - Ranks songs by relevance:
- Scores songs based on keyword matches
- Filters by emotion
- Returns ranked results

**text_utils.py** - Text preprocessing:
- Tokenization
- Stopword removal
- Text normalization

**similarity.py** - Similarity calculations:
- Cosine similarity for text similarity
- Emotion matching scores

### 4. Text-to-Singing (`app/text_to_sing/`)

**text_to_sing.py** - Audio synthesis engine:
- Converts text to singing voice
- Supports multiple singers (male, female, robot)
- Supports multiple modes (pop, hiphop, calm, melody)
- Generates background music with singing
- Returns audio file path

### 5. Audio Serving (`app/audio_server.py`)

- Serves local audio files via static mounting
- Accessible at `/audio/` endpoint
- Supports various audio formats
- No external storage required

## Dependencies

Core dependencies in `requirements.txt`:
- **fastapi** - Web framework
- **uvicorn** - ASGI server
- **pymongo** - MongoDB driver
- **pydantic** - Data validation
- **ultralytics** - YOLOv8 model
- **numpy, scipy** - Numerical computing
- **opencv-python** - Image processing
- **cloudinary** - Cloud storage support
- **firebase-admin** - Firebase integration
- **bcrypt** - Password hashing
- **PyJWT** - JWT authentication
- **python-dotenv** - Environment variables

## Data Formats

### Song Document (MongoDB)

```json
{
  "_id": ObjectId,
  "title": "Song Title",
  "audio_path": "/audio/path/to/file.mp3",
  "tags": ["tag1", "tag2"],
  "language": "English",
  "artist": "Artist Name",
  "emotion": "happy",
  "created_at": "2024-01-01T12:00:00Z"
}
```

### Detection Response

```json
{
  "image_id": "uuid",
  "detections": [
    {
      "class_id": 1,
      "class_name": "dog",
      "confidence": 0.95
    }
  ],
  "mapped_emotion": "happy",
  "song_result": {
    "title": "Happy Song",
    "audio_path": "/audio/happy_song.mp3",
    "confidence": 0.87
  }
}
```

### Search Query

```json
{
  "query": "happy music for morning",
  "matched_song": {
    "title": "Morning Glory",
    "audio_path": "/audio/morning_glory.mp3",
    "emotion": "happy",
    "confidence": 0.92
  }
}
```

## Environment Variables

Optional `.env` file configuration:

```env
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=tuneflex
JWT_SECRET=your_secret_key
JWT_ALGORITHM=HS256
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

## File Upload

- **Max upload size**: Configure in FastAPI
- **Supported formats**: MP3, WAV, OGG, AAC
- **Upload location**: `temp_uploads/` or Cloudinary
- **Auto-cleanup**: Temporary files removed after processing

## Error Handling

The API includes comprehensive error handling:
- Validation errors (422)
- Not found errors (404)
- Authentication errors (401)
- Server errors (500)
- Optional service failures (graceful degradation)

Optional services (search, YOLO, emotion mapping) fail gracefully without crashing the server.

## Performance Considerations

- YOLO model (~100MB) loaded once on startup
- MongoDB connection pooled
- Async request handling
- Audio streaming for large files
- ThreadPoolExecutor for CPU-intensive tasks

## Development Scripts

- `add_class_songs.py` - Add songs with class labels
- `add_all_detection_songs.py` - Batch import detection songs
- `update_playlist_fields.py` - Update song metadata
- `update_movie_songs_db.py` - Import movie soundtrack data
- `final_fixed_detection.py` - Detection pipeline

## Troubleshooting

### MongoDB Connection Failed
- Ensure MongoDB is running: `mongod`
- Check connection string in code or `.env`

### YOLO Model Not Loading
- Verify `best.pt` exists in `app/yolo/`
- Check torch/ultralytics installation: `pip install -r requirements.txt`

### Audio Files Not Serving
- Ensure `data/audio/` directory exists
- Check file permissions
- Verify file paths in database

### Search Results Empty
- Check `songs.json` is properly loaded
- Verify emotion mapping configuration
- Check text preprocessing pipeline

## Contributing

When adding new features:
1. Update relevant modules in appropriate directories
2. Add/update MongoDB schemas if needed
3. Include error handling for optional services
4. Update API documentation in docstrings
5. Test with sample data

## Future Enhancements

- Real-time emotion detection from audio
- Playlist generation
- User preference learning
- Advanced similarity metrics
- Performance optimization
- Caching layer (Redis)
- API rate limiting

---

**Backend Service for TuneFlex** | AI-Powered Music Platform
