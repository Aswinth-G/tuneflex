#!/usr/bin/env python3
"""
Update playlist field for songs based on their folder structure.
This script assigns playlist names (red, citizen, thuppaki, visbarubam)
to songs based on their audio_path folder names.
"""

import os
import sys
sys.path.append(os.path.dirname(__file__))

from app.db.mongodb import songs_collection, users_collection
from app.db.song_repository import get_all_songs

def update_playlist_fields():
    """Update playlist field for all songs based on folder structure"""

    if songs_collection is None:
        print("ERROR: Database connection not available")
        return

    try:
        all_songs = get_all_songs()
        print(f"Found {len(all_songs)} songs in database")

        updated_count = 0

        display_name_map = {
            "nature mix": "red",
            "ocean waves": "citizen",
            "forest calm": "thuppaki",
            "sunset chill": "visbarubam"
        }
        actual_playlists = {"red", "citizen", "thuppaki", "visbarubam"}

        for song in songs_collection.find({}):
            audio_path = song.get("audio_path", "")
            audio_url = song.get("audio_url", "")
            title = song.get("title", "Unknown")
            current_playlist = song.get("playlist", "").lower()
            playlist_name = None

            normalized_audio_path = audio_path.lower() if isinstance(audio_path, str) else ""
            normalized_audio_url = audio_url.lower() if isinstance(audio_url, str) else ""

            if "/audio/playlist/red/" in normalized_audio_path or "/audio/playlist/red/" in normalized_audio_url:
                playlist_name = "red"
            elif "/audio/playlist/citizen/" in normalized_audio_path or "/audio/playlist/citizen/" in normalized_audio_url:
                playlist_name = "citizen"
            elif "/audio/playlist/thuppaki/" in normalized_audio_path or "/audio/playlist/thuppaki/" in normalized_audio_url:
                playlist_name = "thuppaki"
            elif "/audio/playlist/visbarubam/" in normalized_audio_path or "/audio/playlist/visbarubam/" in normalized_audio_url:
                playlist_name = "visbarubam"
            elif current_playlist in display_name_map:
                playlist_name = display_name_map[current_playlist]

            if playlist_name:
                if song.get("playlist", "") != playlist_name:
                    result = songs_collection.update_one(
                        {"_id": song["_id"]},
                        {"$set": {"playlist": playlist_name}}
                    )
                    if result.modified_count > 0:
                        updated_count += 1
                        print(f"✓ Updated '{title}' -> playlist: '{playlist_name}'")
                    else:
                        print(f"- No change needed for '{title}' (already '{playlist_name}')")
            elif current_playlist in actual_playlists:
                result = songs_collection.update_one(
                    {"_id": song["_id"]},
                    {"$unset": {"playlist": ""}}
                )
                if result.modified_count > 0:
                    updated_count += 1
                    print(f"✓ Cleared incorrect playlist for '{title}'")
                else:
                    print(f"- No playlist update needed for '{title}'")
            else:
                print(f"? No playlist folder detected for '{title}'")

        print(f"\n✅ Playlist update complete! Updated {updated_count} songs.")

        # Show playlist summary
        print("\n📊 Playlist Summary:")
        pipeline = [
            {"$match": {"playlist": {"$exists": True, "$ne": ""}}},
            {"$group": {"_id": "$playlist", "count": {"$sum": 1}}}
        ]

        results = list(songs_collection.aggregate(pipeline))
        for result in results:
            print(f"  {result['_id']}: {result['count']} songs")

    except Exception as e:
        print(f"ERROR: Failed to update playlists: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🎵 TuneFlex Playlist Field Updater")
    print("=" * 40)
    update_playlist_fields()