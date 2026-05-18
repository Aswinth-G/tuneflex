

EMOTION_MAP = {





    # Positive
   # "happy": ["smile", "laugh", "fun", "joy", "party", "bright", "celebrate"],
   # "excited": ["cheer", "jump", "celebrate", "energy", "dance"],
   # "love": ["heart", "romantic", "kiss", "hug", "handshacke"],
   # "romantic": ["couple", "together", "love", "candlelight", "rose", "dinner"],

    # Calm / Focus
    #"calm": ["quiet", "peace", "relax", "soft", "nature"],
    #"focused": ["work", "study", "computer", "office", "book"],

    # Sad / Low
    #"sad": ["cry", "rain", "tears", "alone", "heartbreak", "silent"],
    #"lonely": ["alone", "empty", "silent"],
    #"anxious": ["nervous", "worried", "stress"],

    # High intensity
    #"angry": ["fight", "shout", "rage"],
    #"motivated": ["gym", "run", "strong", "power", "energy"],
    "custom_0": ["First-Last"]
}

CLASS_TO_EMOTION_MAP = {
    0  : "custom_0",
    1  : "apple",
    2  : "cucumber",
    3  : "ginger" ,
    4  : "grape",
    5  : "guava",
    6  : "lemon",
    7  : "mango",
    8  : "mulberry",
    9  : "nut",
    10 : "onion ",
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
    30 :"ele",
    31 : "fear",
    32 : "flowers",
    33 : "gym",
    34: "happy",
    35 : "har",
    36 : "neeum naanum",
    37 : "neutral",
    38 : "nighttime",
    39 : "oru sottu kadalum nee",
    40 : "",
    41 : "",
    42 :"rain",
    43 : "rural",
    44 :"sad",
    45 : "",
    46 : "sunrise",
    47 : "surprise",
    48 :"urban",
    }



    

"""Map detected keywords to emotions"""
def map_keywords_to_emotions(keywords):
    emotions = set()
    for word in keywords:
        for emotion, words in EMOTION_MAP.items():
            if word in words:
                emotions.add(emotion)
    return list(emotions)


"""Map YOLO class ID to emotion"""
def map_class_to_emotion(class_id):
    return CLASS_TO_EMOTION_MAP.get(class_id, "neutral")