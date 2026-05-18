import os
import sys
from pymongo import MongoClient
from datetime import datetime

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "tuneflex"

CLASS_TO_SONG_MAPPINGS = {
    # Fruits
    "Apple": {
        "keywords": ["apple", "seppan", "fruit"],
        "song_title": "Apple Song",
        "artist": "AI Generated",
        "audio_path": "apple.mp3",
        "image": "apple"
    },
    "Cucumber 13": {
        "keywords": ["cucumber", "vellerikka", "vegetable"],
        "song_title": "Cucumber Song", 
        "artist": "AI Generated",
        "audio_path": "cucumber.mp3",
        "image": "cucumber"
    },
    "Ginger 2": {
        "keywords": ["ginger", "inji", "spice"],
        "song_title": "Ginger Song",
        "artist": "AI Generated", 
        "audio_path": "ginger.mp3",
        "image": "ginger"
    },
    "Grape Blue 1": {
        "keywords": ["grape", "drakshai", "fruit"],
        "song_title": "Grape Song",
        "artist": "AI Generated",
        "audio_path": "grape.mp3", 
        "image": "grape"
    },
    "Guava 1": {
        "keywords": ["guava", "koyya", "fruit"],
        "song_title": "Guava Song",
        "artist": "AI Generated",
        "audio_path": "guava.mp3",
        "image": "guava"
    },
    "Lemon 1": {
        "keywords": ["lemon", "elumichai", "citrus"],
        "song_title": "Lemon Song",
        "artist": "AI Generated",
        "audio_path": "lemon.mp3",
        "image": "lemon"
    },
    "Mango 1": {
        "keywords": ["mango", "maamaram", "fruit"],
        "song_title": "Mango Song",
        "artist": "AI Generated", 
        "audio_path": "mango.mp3",
        "image": "mango"
    },
    "Mulberry 1": {
        "keywords": ["mulberry", "maampazham", "fruit"],
        "song_title": "Mulberry Song",
        "artist": "AI Generated",
        "audio_path": "mulberry.mp3",
        "image": "mulberry"
    },
    "Nut 1": {
        "keywords": ["nut", "mottukottai", "dryfruit"],
        "song_title": "Nut Song",
        "artist": "AI Generated",
        "audio_path": "nut.mp3",
        "image": "nut"
    },
    "Onion 2": {
        "keywords": ["onion", "vengayam", "vegetable"],
        "song_title": "Onion Song",
        "artist": "AI Generated",
        "audio_path": "onion.mp3",
        "image": "onion"
    },
    "Orange 1": {
        "keywords": ["orange", "orange", "citrus"],
        "song_title": "Orange Song",
        "artist": "AI Generated",
        "audio_path": "orange.mp3",
        "image": "orange"
    },
    "Papaya 1": {
        "keywords": ["papaya", "pappali", "fruit"],
        "song_title": "Papaya Song",
        "artist": "AI Generated",
        "audio_path": "papaya.mp3",
        "image": "papaya"
    },
    "Pepper 1": {
        "keywords": ["pepper", "milagai", "vegetable"],
        "song_title": "Pepper Song",
        "artist": "AI Generated",
        "audio_path": "pepper.mp3",
        "image": "pepper"
    },
    "Pineapple 1": {
        "keywords": ["pineapple", "annasi", "fruit"],
        "song_title": "Pineapple Song",
        "artist": "AI Generated",
        "audio_path": "pineapple.mp3",
        "image": "pineapple"
    },
    "Potato Sweet 1": {
        "keywords": ["potato", "urulaikilangu", "vegetable"],
        "song_title": "Potato Song",
        "artist": "AI Generated",
        "audio_path": "potato.mp3",
        "image": "potato"
    },
    "Strawberry 1": {
        "keywords": ["strawberry", "strawberry", "fruit"],
        "song_title": "Strawberry Song",
        "artist": "AI Generated",
        "audio_path": "strawberry.mp3",
        "image": "strawberry"
    },
    "Tomatoe": {
        "keywords": ["tomato", "thakkali", "vegetable"],
        "song_title": "Tomato Song",
        "artist": "AI Generated",
        "audio_path": "tomato.mp3",
        "image": "tomato"
    },
    "Watermelon 1": {
        "keywords": ["watermelon", "tharpoosani", "fruit"],
        "song_title": "Watermelon Song",
        "artist": "AI Generated",
        "audio_path": "watermelon.mp3",
        "image": "watermelon"
    },
    
    # Animals
    "cat": {
        "keywords": ["cat", "poo", "meow", "cat meow"],
        "song_title": "Cat Meow",
        "artist": "AI Generated",
        "audio_path": "cat.mp3",
        "image": "cat"
    },
    "chicken": {
        "keywords": ["chicken", "koli", "bird"],
        "song_title": "Chicken Song", 
        "artist": "AI Generated",
        "audio_path": "chicken.mp3",
        "image": "chicken"
    },
    "cow": {
        "keywords": ["cow", "karavai", "maadu", "cattle"],
        "song_title": "Karavai Maadu",
        "artist": "AI Generated",
        "audio_path": "cow.mp3",
        "image": "cow"
    },
    "dog": {
        "keywords": ["dog", "naai", "doggy", "barking"],
        "song_title": "Doggy Song",
        "artist": "AI Generated",
        "audio_path": "dog.mp3",
        "image": "dog"
    },
    "ele": {
        "keywords": ["ele", "yennai", "elephant", "trunk"],
        "song_title": "Elephant Song",
        "artist": "AI Generated",
        "audio_path": "ele.mp3",
        "image": "ele"
    },
    
    # Emotions & Concepts
    "angry": {
        "keywords": ["angry", "kovam", "anger", "rage"],
        "song_title": "Angry Song",
        "artist": "AI Generated",
        "audio_path": "angry.mp3",
        "image": "angry"
    },
    "athikaalai": {
        "keywords": ["athikaalai", "disgust", "disguise"],
        "song_title": "Disguise Song",
        "artist": "AI Generated",
        "audio_path": "disguise.mp3",
        "image": "disguise"
    },
    "butterfly": {
        "keywords": ["butterfly", "oh", "butterfly"],
        "song_title": "Oh Butterfly",
        "artist": "AI Generated",
        "audio_path": "butterfly.mp3",
        "image": "butterfly"
    },
    "candle": {
        "keywords": ["candle", "ullukulla", "light", "flame"],
        "song_title": "Candle Song",
        "artist": "AI Generated",
        "audio_path": "candle.mp3",
        "image": "candle"
    },
    "classroom": {
        "keywords": ["classroom", "school", "education"],
        "song_title": "Classroom Smiles",
        "artist": "AI Generated",
        "audio_path": "classroom.mp3",
        "image": "classroom"
    },
    "daytime": {
        "keywords": ["daytime", "day", "sunlight"],
        "song_title": "Daytime Song",
        "artist": "AI Generated",
        "audio_path": "daytime.mp3",
        "image": "daytime"
    },
    "disgust": {
        "keywords": ["disgust", "disguise", "hide"],
        "song_title": "Disguise Song",
        "artist": "AI Generated",
        "audio_path": "disguise.mp3",
        "image": "disguise"
    },
    "fear": {
        "keywords": ["fear", "bayam", "scared", "afraid"],
        "song_title": "Fear Song",
        "artist": "AI Generated",
        "audio_path": "fear.mp3",
        "image": "fear"
    },
    "flowers": {
        "keywords": ["flowers", "poo", "blossom", "garden"],
        "song_title": "Pookum Flowers",
        "artist": "AI Generated",
        "audio_path": "flowers.mp3",
        "image": "flowers"
    },
    "gym": {
        "keywords": ["gym", "workout", "exercise", "fitness"],
        "song_title": "Gym Power",
        "artist": "AI Generated",
        "audio_path": "gym.mp3",
        "image": "gym"
    },
    "happy": {
        "keywords": ["happy", "santhosham", "joy", "smile"],
        "song_title": "Happy Song",
        "artist": "AI Generated",
        "audio_path": "happy.mp3",
        "image": "happy"
    },
    "har": {
        "keywords": ["har", "scoiattolo", "plow", "farm"],
        "song_title": "Scoiattolo Song",
        "artist": "AI Generated",
        "audio_path": "har.mp3",
        "image": "har"
    },
    "neeum naanum": {
        "keywords": ["neeum", "naanum", "we", "together"],
        "song_title": "Neeum Naanum Song",
        "artist": "AI Generated",
        "audio_path": "neeum.mp3",
        "image": "neeum"
    },
    "neutral": {
        "keywords": ["neutral", "normal", "calm"],
        "song_title": "Neutral Song",
        "artist": "AI Generated",
        "audio_path": "neutral.mp3",
        "image": "neutral"
    },
    "nighttime": {
        "keywords": ["nighttime", "night", "dark", "sleep"],
        "song_title": "Nighttime Song",
        "artist": "AI Generated",
        "audio_path": "nighttime.mp3",
        "image": "nighttime"
    },
    "oru sottu kadalum nee": {
        "keywords": ["oru", "sottu", "kadalum", "nee", "love"],
        "song_title": "Oru Sottu Song",
        "artist": "AI Generated",
        "audio_path": "oru_sottu.mp3",
        "image": "love"
    },
    "pecora": {
        "keywords": ["pecora", "raging", "angry"],
        "song_title": "Raging Song",
        "artist": "AI Generated",
        "audio_path": "raging.mp3",
        "image": "raging"
    },
    "ragno": {
        "keywords": ["ragno", "anger", "rage"],
        "song_title": "Ragno Song",
        "artist": "AI Generated",
        "audio_path": "ragno.mp3",
        "image": "angry"
    },
    "rain": {
        "keywords": ["rain", "thuli", "water", "weather"],
        "song_title": "Rain Song",
        "artist": "AI Generated",
        "audio_path": "rain.mp3",
        "image": "rain"
    },
    "rural": {
        "keywords": ["rural", "country", "village"],
        "song_title": "Rural Song",
        "artist": "AI Generated",
        "audio_path": "rural.mp3",
        "image": "rural"
    },
    "sad": {
        "keywords": ["sad", "kashtam", "cry", "sorrow"],
        "song_title": "Sad Song",
        "artist": "AI Generated",
        "audio_path": "sad.mp3",
        "image": "sad"
    },
    "scoiattolo": {
        "keywords": ["scoiattolo", "vellerikka", "cucumber"],
        "song_title": "Cucumber Song",
        "artist": "AI Generated",
        "audio_path": "scoiattolo.mp3",
        "image": "cucumber"
    },
    "sunrise": {
        "keywords": ["sunrise", "morning", "dawn"],
        "song_title": "Sunrise Song",
        "artist": "AI Generated",
        "audio_path": "sunrise.mp3",
        "image": "sunrise"
    },
    "surprise": {
        "keywords": ["surprise", "unexpected", "shock"],
        "song_title": "Surprise Song",
        "artist": "AI Generated",
        "audio_path": "surprise.mp3",
        "image": "surprise"
    },
    "urban": {
        "keywords": ["urban", "city", "town"],
        "song_title": "Urban Song",
        "artist": "AI Generated",
        "audio_path": "urban.mp3",
        "image": "urban"
    },
    "vellerikka": {
        "keywords": ["vellerikka", "cucumber", "vegetable"],
        "song_title": "Cucumber Song",
        "artist": "AI Generated",
        "audio_path": "vellerikka.mp3",
        "image": "cucumber"
    },
    "yaanai": {
        "keywords": ["yaanai", "elephant", "animal"],
        "song_title": "Elephant Song",
        "artist": "AI Generated",
        "audio_path": "elephant.mp3",
        "image": "elephant"
    }
}

def add_class_songs():
    """Add class-based songs to database"""
    try:
        # Connect to MongoDB
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        songs_collection = db.songs
        
        added_count = 0
        updated_count = 0
        
        for class_name, song_data in CLASS_TO_SONG_MAPPINGS.items():
            # Check if song already exists
            existing_song = songs_collection.find_one({"title": song_data["song_title"]})
            
            if existing_song:
                print(f"Song '{song_data['song_title']}' already exists. Updating...")
                
                # Update existing song
                update_data = {
                    "$set": {
                        "keywords": song_data["keywords"],
                        "audio_url": f"https://variedly-unspirited-archie.ngrok-free.dev/audio/{song_data['audio_path']}",
                        "updated_at": datetime.now().isoformat()
                    }
                }
                
                result = songs_collection.update_one(
                    {"title": song_data["song_title"]},
                    update_data
                )
                
                if result.modified_count:
                    updated_count += 1
                    print(f"Updated '{song_data['song_title']}' with new keywords and audio URL")
                else:
                    print(f"Failed to update '{song_data['song_title']}'")
                    
            else:
                # Add new song
                new_song = {
                    "_id": f"class_{class_name.lower().replace(' ', '_')}",
                    "title": song_data["song_title"],
                    "artist": song_data["artist"],
                    "album": "AI Generated Songs",
                    "duration": 180,
                    "emotion": "neutral",
                    "keywords": song_data["keywords"],
                    "language": "English",
                    "audio_path": song_data["audio_path"],
                    "audio_url": f"https://variedly-unspirited-archie.ngrok-free.dev/audio/{song_data['audio_path']}",
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
                
                result = songs_collection.insert_one(new_song)
                if result.inserted_id:
                    added_count += 1
                    print(f"Added '{song_data['song_title']}' to database")
                else:
                    print(f"Failed to add '{song_data['song_title']}'")
        
        print(f"\nSummary:")
        print(f"   Added: {added_count} new songs")
        print(f"   Updated: {updated_count} existing songs")
        print(f"   Total processed: {len(CLASS_TO_SONG_MAPPINGS)} songs")
        
        # Show some examples
        print(f"\nClass to Song Examples:")
        examples = ["cat", "dog", "apple", "angry", "flowers", "rain"]
        for example in examples:
            if example in CLASS_TO_SONG_MAPPINGS:
                mapping = CLASS_TO_SONG_MAPPINGS[example]
                print(f"  {example} -> {mapping['song_title']} (keywords: {mapping['keywords']})")
        
        client.close()
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("Adding Class-Based Songs to TuneFlex Database")
    print("=" * 60)
    
    print("Class Mappings:")
    print("- When AI detects 'cat' -> plays 'Cat Meow'")
    print("- When AI detects 'dog' -> plays 'Doggy Song'")
    print("- When AI detects 'apple' -> plays 'Apple Song'")
    print("- When AI detects 'angry' -> plays 'Angry Song'")
    print("- And 40+ more mappings!")
    
    print(f"\nProcessing {len(CLASS_TO_SONG_MAPPINGS)} class mappings...")
    add_class_songs()
