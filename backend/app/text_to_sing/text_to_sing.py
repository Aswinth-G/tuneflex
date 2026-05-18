import os
import tempfile
import subprocess
import wave
import struct
import numpy as np
from typing import Optional, List, Tuple



class TextToSing:
    SUPPORTED_SINGERS = ("male", "female", "robot")
    SUPPORTED_MODES = ("pop", "hiphop", "calm", "melody")



    def __init__(self):
        self.sample_rate = 22050
        self.tts_engine = self._initialize_tts()
        print(f" TTS Engine: {type(self.tts_engine).__name__}")



    def _initialize_tts(self):
        """Initialize TTS engine with music support."""
        try:
            import pyttsx3
            print(" System TTS loaded - Ready for singing with music!")
            return SingingWithMusic()
        except ImportError:
            print(" System TTS not available")
            print(" Using musical tones fallback")
            return MusicalTonesFallback()



    def text_to_singing(self, text: str, emotion: str = "happy", singer: str = "female") -> str:
        """Convert text to singing with background music."""
        return self.tts_engine.text_to_singing(text, emotion, singer)



    def generate_song(self, lyrics: str, singer: Optional[str] = "female", mode: Optional[str] = "pop", output_path: Optional[str] = None) -> dict:
        """Generate singing with background music."""
        # Map mode to emotion for music generation
        emotion_map = {"pop": "happy", "hiphop": "angry", "calm": "sad", "melody": "neutral"}
        emotion = emotion_map.get(mode, "happy")
        
        output_path = self.text_to_singing(lyrics, emotion, singer)
        
        return {
            "lyrics": lyrics,
            "phonemes": [lyrics],
            "pitches": [440.0],
            "durations": [1.0],
            "singer": singer,
            "mode": mode,
            "output_path": output_path,
        }




class SingingWithMusic:
    """Singing with background music - all in one class!"""
    
    def __init__(self):
        self.sample_rate = 22050
        # Don't initialize engine here - create fresh engine for each request
        self.engine = None



    def _init_tts(self):
        """Initialize system TTS with timeout protection (Windows compatible)."""
        try:
            import pyttsx3
            # Use threading for timeout instead of signal (Windows compatible)
            import threading
            import queue
            
            result_queue = queue.Queue()
            error_queue = queue.Queue()
            
            def init_tts_thread():
                try:
                    engine = pyttsx3.init()
                    result_queue.put(engine)
                except Exception as e:
                    error_queue.put(e)
            
            # Start TTS initialization in a separate thread
            thread = threading.Thread(target=init_tts_thread, daemon=True)
            thread.start()
            thread.join(timeout=10)  # Increased to 10 seconds
            
            if thread.is_alive():
                print("TTS initialization timed out, using fallback")
                return None
            elif not error_queue.empty():
                error = error_queue.get()
                print(f"TTS initialization error: {error}")
                return None
            else:
                engine = result_queue.get()
                print("TTS initialized successfully")
                return engine
                
        except ImportError:
            print("pyttsx3 not available")
            return None
        except Exception as e:
            print(f"TTS initialization error: {e}")
            return None



    def text_to_singing(self, text: str, emotion: str, singer: str) -> str:
        """Generate singing with background music."""
        try:
            print(f"Starting text_to_singing for: '{text}'")
            
            # Generate voice
            voice_path = self._generate_voice(text, emotion, singer)
            print(f"Voice generated: {voice_path}")
            
            # Generate background music
            music_path = self._generate_background_music(emotion)
            print(f"Music generated: {music_path}")
            
            # Mix voice with music
            mixed_path = self._mix_audio_with_music(voice_path, music_path, emotion)
            print(f"Mixed audio: {mixed_path}")
            
            # Clean up
            try:
                os.remove(voice_path)
                os.remove(music_path)
                print("Temporary files cleaned up")
            except:
                pass
            
            return mixed_path
            
        except Exception as e:
            print(f"Singing with music error: {e}")
            import traceback
            traceback.print_exc()
            return self._fallback_voice(text, emotion, singer)



    def _generate_voice(self, text: str, emotion: str, singer: str) -> str:
        """Generate voice using system TTS - CREATE FRESH ENGINE EACH TIME."""
        print(f"Generating voice for: '{text}'")
        
        # Create fresh engine for each request to avoid timeout issues
        engine = self._init_tts()
        if not engine:
            print("Failed to initialize TTS engine, using fallback")
            return self._fallback_voice(text, emotion, singer)
        
        try:
            # Set voice properties
            voices = engine.getProperty('voices')
            if voices:
                voice_idx = 0 if singer == "female" else (1 if len(voices) > 1 else 0)
                engine.setProperty('voice', voices[voice_idx].id)
                print(f"Set voice to: {voices[voice_idx].name}")
            
            # Set rate based on emotion
            rates = {"happy": 150, "sad": 100, "angry": 180, "neutral": 120, "excited": 160}
            engine.setProperty('rate', rates.get(emotion, 120))
            print(f"Set rate to: {rates.get(emotion, 120)}")
            
            # Save to file
            fd, output_path = tempfile.mkstemp(suffix=".wav")
            os.close(fd)
            
            print(f"Saving TTS to: {output_path}")
            engine.save_to_file(text, output_path)
            
            # Use threading for timeout instead of signal (Windows compatible)
            import threading
            import queue
            
            result_queue = queue.Queue()
            error_queue = queue.Queue()
            
            def run_tts_thread():
                try:
                    engine.runAndWait()
                    result_queue.put(True)
                except Exception as e:
                    error_queue.put(e)
            
            # Start TTS processing in a separate thread
            thread = threading.Thread(target=run_tts_thread, daemon=True)
            thread.start()
            
            # DYNAMIC TIMEOUT: 30 seconds minimum + 1 second per character
            timeout_seconds = max(30, len(text) * 1)
            print(f"Using timeout: {timeout_seconds} seconds")
            thread.join(timeout=timeout_seconds)
            
            if thread.is_alive():
                print(f"TTS processing timed out after {timeout_seconds}s, using fallback")
                return self._fallback_voice(text, emotion, singer)
            elif not error_queue.empty():
                error = error_queue.get()
                print(f"TTS processing error: {error}")
                return self._fallback_voice(text, emotion, singer)
            
            # Check if file was created and has content
            if os.path.exists(output_path):
                size = os.path.getsize(output_path)
                print(f"TTS file size: {size} bytes")
                if size > 1000:  # Should be more than 1KB for actual speech
                    print("TTS file contains actual speech data")
                    return output_path
                else:
                    print("TTS file too small, using fallback")
                    return self._fallback_voice(text, emotion, singer)
            else:
                print("TTS file not created, using fallback")
                return self._fallback_voice(text, emotion, singer)
                
        except Exception as e:
            print(f"Voice generation error: {e}")
            import traceback
            traceback.print_exc()
            return self._fallback_voice(text, emotion, singer)



    def _generate_background_music(self, emotion: str) -> str:
        """Generate background music based on emotion."""
        fd, music_path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        
        # Music patterns for different emotions - ULTRA LOW DURATION for fast responses
        music_patterns = {
            "happy": {
                "tempo": 120,  # BPM
                "chords": ["C", "G", "Am", "F"],  
                "rhythm": "upbeat",
                "duration": 5.0   
            },
            "sad": {
                "tempo": 60,   # Slow tempo
                "chords": ["Am", "F", "C", "Gm"],  
                "rhythm": "slow",
                "duration": 5.0   
            },
            "angry": {
                "tempo": 140,  # Fast tempo
                "chords": ["Em", "G", "C", "Am"],  
                "rhythm": "intense",
                "duration": 5.0   
            },
            "neutral": {
                "tempo": 90,   # Medium tempo
                "chords": ["C", "G", "Am", "F"],  
                "rhythm": "steady",
                "duration": 5.0   
            },
            "excited": {
                "tempo": 130,  # Fast tempo
                "chords": ["C", "G", "Am", "F"],  
                "rhythm": "energetic",
                "duration": 5.0  
            }
        }
        
        pattern = music_patterns.get(emotion, music_patterns["happy"])
        self._create_simple_music(music_path, pattern)
        
        return music_path


    def _create_simple_music(self, output_path: str, pattern: dict):
        """Create simple background music."""
        try:
            tempo = pattern["tempo"]
            chords = pattern["chords"]
            duration = pattern["duration"]
            
            sample_rate = self.sample_rate
            total_samples = int(duration * sample_rate)
            t = np.linspace(0, duration, total_samples)
            
            # Create chord progression
            chord_duration = duration / len(chords)
            music = np.zeros(total_samples)
            
            for i, chord in enumerate(chords):
                start_sample = int(i * chord_duration * sample_rate)
                end_sample = int((i + 1) * chord_duration * sample_rate)
                
                # Generate chord frequencies
                chord_freqs = self._get_chord_frequencies(chord)
                
                for freq in chord_freqs:
                    chord_t = t[start_sample:end_sample] - (i * chord_duration)
                    chord_wave = 0.3 * np.sin(2 * np.pi * freq * chord_t)
                    music[start_sample:end_sample] += chord_wave
                
                # Add rhythm (drum beat)
                if i % 2 == 0:
                    beat_start = start_sample
                    beat_end = min(start_sample + int(0.1 * sample_rate), end_sample)
                    music[beat_start:beat_end] += 0.5 * np.sin(2 * np.pi * 100 * t[beat_start:beat_end])
            
            # Add envelope
            fade_samples = int(0.1 * sample_rate)
            music[:fade_samples] *= np.linspace(0, 1, fade_samples)
            music[-fade_samples:] *= np.linspace(1, 0, fade_samples)
            
            # Save as WAV
            with wave.open(output_path, "w") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                
                samples = (music * 32767).astype(np.int16)
                for sample in samples:
                    wf.writeframes(struct.pack('<h', int(sample)))
                    
        except Exception as e:
            print(f"Music generation error: {e}")



    def _get_chord_frequencies(self, chord: str) -> List[float]:
        """Get frequencies for a chord."""
        chord_freqs = {
            "C": [261.63, 329.63, 392.00],    # C major
            "G": [392.00, 493.88, 587.33],    # G major
            "Am": [220.00, 277.18, 329.63],   # A minor
            "F": [349.23, 440.00, 523.25],    # F major
            "Em": [329.63, 415.30, 493.88],   # E minor
            "Gm": [392.00, 493.88, 587.33],   # G minor
        }
        return chord_freqs.get(chord, chord_freqs["C"])



    def _mix_audio_with_music(self, voice_path: str, music_path: str, emotion: str) -> str:
        """Mix voice with background music."""
        try:
            # Read voice audio
            with wave.open(voice_path, "r") as wf:
                voice_frames = wf.readframes(-1)
                voice_data = np.frombuffer(voice_frames, dtype=np.int16)
                voice_float = voice_data.astype(np.float32) / 32768.0
                voice_length = len(voice_data)
            
            # Read music audio
            with wave.open(music_path, "r") as wf:
                music_frames = wf.readframes(-1)
                music_data = np.frombuffer(music_frames, dtype=np.int16)
                music_float = music_data.astype(np.float32) / 32768.0
                music_length = len(music_data)
            
            # Mix audio
            max_length = max(voice_length, music_length)
            
            # Pad shorter audio
            if len(voice_float) < max_length:
                voice_float = np.pad(voice_float, (0, max_length - len(voice_float)))
            if len(music_float) < max_length:
                music_float = np.pad(music_float, (0, max_length - len(music_float)))
            
            # Mix with emotion-based balance
            emotion_balance = {
                "happy": {"voice": 0.7, "music": 0.3},
                "sad": {"voice": 0.8, "music": 0.2},
                "angry": {"voice": 0.6, "music": 0.4},
                "neutral": {"voice": 0.7, "music": 0.3},
                "excited": {"voice": 0.6, "music": 0.4}
            }
            
            balance = emotion_balance.get(emotion, {"voice": 0.7, "music": 0.3})
            mixed_audio = balance["voice"] * voice_float + balance["music"] * music_float
            
            # Normalize
            max_val = np.max(np.abs(mixed_audio))
            if max_val > 0:
                mixed_audio = mixed_audio / max_val * 0.8
            
            # Save mixed audio
            fd, mixed_path = tempfile.mkstemp(suffix=".wav")
            os.close(fd)
            
            with wave.open(mixed_path, "w") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(self.sample_rate)
                
                samples = (mixed_audio * 32767).astype(np.int16)
                for sample in samples:
                    wf.writeframes(struct.pack('<h', int(sample)))
            
            return mixed_path
            
        except Exception as e:
            print(f"Audio mixing error: {e}")
            return voice_path



    def _fallback_voice(self, text: str, emotion: str, singer: str) -> str:
        """Fallback voice generation - creates simple tones, NOT speech."""
        print(f"WARNING: Using fallback voice for '{text}' - This creates musical tones, not speech!")
        fd, output_path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        
        # Generate simple tone as fallback
        emotion_freqs = {
            "happy": 523.25, "sad": 349.23, "angry": 440.00,
            "neutral": 392.00, "excited": 587.33
        }
        
        frequency = emotion_freqs.get(emotion, 440.0)
        duration = len(text) * 0.1
        
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        waveform = np.sin(2 * np.pi * frequency * t)
        
        envelope = np.exp(-t * 2)
        waveform = waveform * envelope
        
        with wave.open(output_path, "w") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            
            samples = (waveform * 32767).astype(np.int16)
            for sample in samples:
                wf.writeframes(struct.pack('<h', int(sample)))
        
        return output_path




class MusicalTonesFallback:
    def __init__(self):
        self.sample_rate = 22050



    def text_to_singing(self, text: str, emotion: str, singer: str) -> str:
        """Generate musical tones as fallback."""
        print(f"WARNING: MusicalTonesFallback for '{text}' - This creates musical tones, not speech!")
        fd, output_path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        
        emotion_freqs = {
            "happy": 523.25, "sad": 349.23, "angry": 440.00,
            "neutral": 392.00, "excited": 587.33
        }
        
        frequency = emotion_freqs.get(emotion, 440.0)
        duration = len(text) * 0.1
        
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        waveform = np.sin(2 * np.pi * frequency * t)
        
        envelope = np.exp(-t * 2)
        waveform = waveform * envelope
        
        with wave.open(output_path, "w") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            
            samples = (waveform * 32767).astype(np.int16)
            for sample in samples:
                wf.writeframes(struct.pack('<h', int(sample)))
        
        return output_path




if __name__ == "__main__":
    # Test singing with music
    tts = TextToSing()
    
    test_texts = [
        "hello world",
        "i love music",
        "beautiful day"
    ]
    
    for text in test_texts:
        print(f"\nGenerating singing for: '{text}'")
        result = tts.generate_song(text, singer="female", mode="pop")
        print(f"Generated: {result['output_path']}")
