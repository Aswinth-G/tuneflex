import sys
sys.path.append('.')
from app.db.mongodb import songs_collection

playlists = ['red', 'citizen', 'thuppaki', 'visbarubam']
for playlist in playlists:
    count = len(list(songs_collection.find({'playlist': playlist})))
    print(f'{playlist.upper()}: {count} songs')