@app.post("/detect")
def detect_and_play(data: dict):
    """Handle class detection and play correct song using your CLASS_TO_EMOTION_MAP"""
    print(f"DEBUG: Detection request: {data}")
    
    try:
        class_id = data.get("class_id", 0)
        class_name = data.get("class_name", "")
        
        print(f"DEBUG: Best detection - class_id: {class_id}, class_name: {class_name}")
        
        # YOUR EXACT CLASS_TO_EMOTION_MAP
        CLASS_TO_EMOTION_MAP = {
            0  : "custom_0",
            1  : "apple",
            2  : "cucumber",
            3  : "ginger",
            4  : "grape",
            5  : "guava",
            6  : "lemon",
            7  : "mango",
            8  : "mulberry",
            9  : "nut",
            10 : "onion",
            11 : "orange",
            12 : "papaya",
            13 : "pepper",
            14 : "pineapple",
            15 : "potato",
            16 : "strawberry",
            17 : "Tomatoe",
            18 : "watermelon",
            19 : "angry",
            20 : "athikaalai",
            21 : "butterfly",
            22 : "candle",
            23 : "cat",
            24 : "chicken",
            25 : "classroom",
            26 : "cow",
            27 : "daytime",
            28 : "disgust",
            29 : "dog",
            30 : "ele",
            31 : "fear",
            32 : "flowers",
            33 : "gym",
            34 : "happy",
            35 : "har",
            36 : "neeum naanum",
            37 : "neutral",
            38 : "nighttime",
            39 : "oru sottu kadalum nee",
            40 : "",
            41 : "",
            42 : "rain",
            43 : "rural",
            44 : "sad",
            45 : "",
            46 : "sunrise",
            47 : "surprise",
            48 : "urban",
            49 : "neutral"  # Added for class 49
        }
        
        # Map class ID to emotion/class name
        detected_emotion = CLASS_TO_EMOTION_MAP.get(class_id, "neutral")
        print(f"DEBUG: Mapped to emotion/class: {detected_emotion}")
        
        # If empty emotion, use neutral
        if not detected_emotion:
            detected_emotion = "neutral"
            print(f"DEBUG: Empty emotion, using neutral")
        
        # Get all songs and find matching song
        all_songs = get_all_songs()
        
        # Search strategy: Exact match first, then keyword match
        found_song = None
        
        # Strategy 1: Look for exact song title match
        for song in all_songs:
            if song.get("priority", 0) == 1:  # User songs first
                title = song.get("title", "").lower()
                # Check if detected emotion matches song title
                if detected_emotion.lower() in title:
                    found_song = song
                    print(f"DEBUG: Found exact match: {song.get('title', 'Unknown')} for {detected_emotion}")
                    break
        
        # Strategy 2: Look for songs with matching keywords
        if not found_song:
            for song in all_songs:
                if song.get("priority", 0) == 1:  # User songs first
                    keywords = [tag.lower() for tag in song.get("tags", [])]
                    title = song.get("title", "").lower()
                    
                    # Check if detected emotion matches keywords or title
                    if detected_emotion.lower() in keywords or detected_emotion.lower() in title:
                        found_song = song
                        print(f"DEBUG: Found keyword match: {song.get('title', 'Unknown')} for {detected_emotion}")
                        break
        
        # Strategy 3: Look for AI songs if no user song found
        if not found_song:
            for song in all_songs:
                if song.get("priority", 0) != 1:  # AI songs
                    title = song.get("title", "").lower()
                    if detected_emotion.lower() in title:
                        found_song = song
                        print(f"DEBUG: Found AI song: {song.get('title', 'Unknown')} for {detected_emotion}")
                        break
        
        if found_song:
            audio_url = found_song.get("audio_url", "")
            if not audio_url:
                audio_path = found_song.get("audio_path", "")
                audio_url = f"https://variedly-unspirited-archie.ngrok-free.dev/audio/{audio_path}"
            
            print(f"DEBUG: Selected song: {found_song.get('title', 'Unknown')}")
            print(f"DEBUG: Audio URL: {audio_url}")
            
            return {
                "success": True,
                "song": {
                    "title": found_song.get("title", ""),
                    "artist": found_song.get("artist", ""),
                    "audio_url": audio_url,
                    "class_id": class_id,
                    "class_name": class_name,
                    "detected_emotion": detected_emotion
                }
            }
        else:
            print(f"DEBUG: No song found for class {class_id} ({detected_emotion})")
            
            # Fallback to First-Last if nothing found
            fallback_song = None
            for song in all_songs:
                if song.get("title", "").lower() == "first-last":
                    fallback_song = song
                    break
            
            if fallback_song:
                audio_url = fallback_song.get("audio_url", "")
                if not audio_url:
                    audio_path = fallback_song.get("audio_path", "")
                    audio_url = f"https://variedly-unspirited-archie.ngrok-free.dev/audio/{audio_path}"
                
                print(f"DEBUG: Using fallback song: {fallback_song.get('title', 'Unknown')}")
                
                return {
                    "success": True,
                    "song": {
                        "title": fallback_song.get("title", ""),
                        "artist": fallback_song.get("artist", ""),
                        "audio_url": audio_url,
                        "class_id": class_id,
                        "class_name": class_name,
                        "detected_emotion": detected_emotion,
                        "fallback": True
                    }
                }
            
            return {
                "success": False,
                "message": f"No song found for class {class_id} ({detected_emotion})",
                "class_id": class_id,
                "class_name": class_name,
                "detected_emotion": detected_emotion
            }
        
    except Exception as e:
        print(f"DEBUG: Detection error: {e}")
        return {"success": False, "message": str(e)}

@app.get("/test-mappings")
def test_class_mappings():
    """Test all class mappings to see what songs will be selected"""
    print("Testing Class Mappings")
    
    CLASS_TO_EMOTION_MAP = {
        0  : "custom_0",
        1  : "apple",
        2  : "cucumber",
        3  : "ginger",
        4  : "grape",
        5  : "guava",
        6  : "lemon",
        7  : "mango",
        8  : "mulberry",
        9  : "nut",
        10 : "onion",
        11 : "orange",
        12 : "papaya",
        13 : "pepper",
        14 : "pineapple",
        15 : "potato",
        16 : "strawberry",
        17 : "Tomatoe",
        18 : "watermelon",
        19 : "angry",
        20 : "athikaalai",
        21 : "butterfly",
        22 : "candle",
        23 : "cat",
        24 : "chicken",
        25 : "classroom",
        26 : "cow",
        27 : "daytime",
        28 : "disgust",
        29 : "dog",
        30 : "ele",
        31 : "fear",
        32 : "flowers",
        33 : "gym",
        34 : "happy",
        35 : "har",
        36 : "neeum naanum",
        37 : "neutral",
        38 : "nighttime",
        39 : "oru sottu kadalum nee",
        40 : "",
        41 : "",
        42 : "rain",
        43 : "rural",
        44 : "sad",
        45 : "",
        46 : "sunrise",
        47 : "surprise",
        48 : "urban",
        49 : "neutral"
    }
    
    try:
        all_songs = get_all_songs()
        results = []
        
        for class_id, emotion in CLASS_TO_EMOTION_MAP.items():
            if not emotion:  # Skip empty emotions
                results.append({
                    "class_id": class_id,
                    "emotion": emotion,
                    "song": "No emotion mapped"
                })
                continue
            
            # Find matching song
            found_song = None
            for song in all_songs:
                if song.get("priority", 0) == 1:  # User songs first
                    title = song.get("title", "").lower()
                    keywords = [tag.lower() for tag in song.get("tags", [])]
                    
                    if emotion.lower() in title or emotion.lower() in keywords:
                        found_song = song
                        break
            
            if found_song:
                results.append({
                    "class_id": class_id,
                    "emotion": emotion,
                    "song": found_song.get("title", "Unknown"),
                    "artist": found_song.get("artist", "Unknown")
                })
            else:
                results.append({
                    "class_id": class_id,
                    "emotion": emotion,
                    "song": "No song found"
                })
        
        return {"mappings": results}
        
    except Exception as e:
        return {"error": str(e)}
