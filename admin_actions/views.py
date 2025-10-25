from django.http import FileResponse, Http404, StreamingHttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
import sqlite3
import requests
from config import CONFIG

class DownloadDBView(APIView):
    def get(self, request, *args, **kwargs):
        # grab query param
        key = request.query_params.get("admin_actions_secret_key")
        as_filename = request.query_params.get("as_filename", "db.sqlite3")
        
        if key != CONFIG["ADMIN_ACTIONS_SECRET_KEY"]:
            return Response({"detail": "Unauthorized"}, status=403)

        file_path = "db.sqlite3"
        try:
            return FileResponse(open(file_path, "rb"), as_attachment=True, filename=as_filename)
        except FileNotFoundError:
            raise Http404("File not found")

# ---------- Fixed DotDict ---------- #
class DotDict(dict):
    """Dict that supports attribute access AND dynamic assignment."""
    def __init__(self, d=None):
        super().__init__()
        if d:
            for k, v in d.items():
                if isinstance(v, dict):
                    v = DotDict(v)
                self[k] = v

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(f"No attribute named '{name}'")

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        del self[name]

    def __getitem__(self, key):
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        if isinstance(value, dict) and not isinstance(value, DotDict):
            value = DotDict(value)
        super().__setitem__(key, value)

def dotdict_factory(cursor, row):
    return DotDict({col[0]: row[idx] for idx, col in enumerate(cursor.description)})

def dotdict_to_dict(obj):
    if isinstance(obj, DotDict):
        return {k: dotdict_to_dict(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [dotdict_to_dict(i) for i in obj]
    else:
        return obj

# ---------- SSE helper ---------- #
def sse(msg):
    return f"data: {msg}\n\n"

# ---------- Download file generator ---------- #
def download_file_with_log(url, save_as):
    yield sse(f"Starting download from {url}")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    total = 0
    with open(save_as, "wb") as f:
        for chunk in response.iter_content(chunk_size=1024*1024):
            if chunk:
                f.write(chunk)
                total += len(chunk)
                yield sse(f"Downloaded {total // 1024} KB")
    yield sse("Download complete!")

# ---------- Preprod DB to JSON generator ---------- #
def preprod_to_json_with_log(preprod_db_path):
    yield sse(f"Opening preprod DB: {preprod_db_path}")
    conn = sqlite3.connect(preprod_db_path)
    conn.row_factory = dotdict_factory
    cursor = conn.cursor()

    actors, albums, artists, languages, songs = DotDict(), DotDict(), DotDict(), DotDict(), DotDict()

    for row in cursor.execute("SELECT * FROM actor_actor"):
        actors[str(row.id)] = row
    yield sse(f"Loaded {len(actors)} actors")

    for row in cursor.execute("SELECT * FROM album_album"):
        albums[str(row.id)] = row
    yield sse(f"Loaded {len(albums)} albums")

    for row in cursor.execute("SELECT * FROM artist_artist"):
        artists[str(row.id)] = row
    yield sse(f"Loaded {len(artists)} artists")

    for row in cursor.execute("SELECT * FROM language_language"):
        languages[str(row.id)] = row
    yield sse(f"Loaded {len(languages)} languages")

    for row in cursor.execute("SELECT * FROM song_song"):
        songs[str(row.id)] = row
    yield sse(f"Loaded {len(songs)} songs")

    # Relations album -> actors
    for row in cursor.execute("SELECT * FROM album_album_actors"):
        album = albums[str(row.album_id)]
        if 'actors' in album:
            album['actors'].append(actors[str(row.actor_id)])
        else:
            album['actors'] = [actors[str(row.actor_id)]]
    yield sse("Linked actors to albums")

    # Add album to songs
    for song in songs.values():
        album = albums[str(song.album_id)]
        del song['album_id']
        song['album'] = album

    # Artists in songs
    for row in cursor.execute("SELECT * FROM song_song_artists"):
        song = songs[str(row.song_id)]
        artist = artists[str(row.artist_id)]
        if 'artists' in song:
            song['artists'].append(artist)
        else:
            song['artists'] = [artist]

    # Languages in songs
    for row in cursor.execute("SELECT * FROM song_song_languages"):
        song = songs[str(row.song_id)]
        lang = languages[str(row.language_id)]
        if 'languages' in song:
            song['languages'].append(lang)
        else:
            song['languages'] = [lang]

    conn.close()
    yield sse("Preprod DB converted to DotDict")
    yield DotDict({
        "songs": songs,
        "artists": artists,
        "languages": languages,
        "albums": albums,
        "actors": actors
    })

# ---------- Update DB generator ---------- #
def update_db_from_preprod_with_log(preprod_data, current_db_path):
    yield sse(f"Opening current DB: {current_db_path}")
    conn = sqlite3.connect(current_db_path)
    conn.row_factory = dotdict_factory
    cursor = conn.cursor()

    tables_to_clear = [
        "songs_tag",
        "songs_songtag",
        "songs_songartist",
        "songs_song",
        "songs_artist",
        "songs_album",
        "songrequest_songrequest"
    ]
    for t in tables_to_clear:
        cursor.execute(f"DELETE FROM {t}")
        yield sse(f"Cleared table {t}")

    # Albums
    for album in preprod_data.albums.values():
        cursor.execute("""
            INSERT INTO songs_album (id, code, title, year, thumbnail1200x1200, thumbnail300x300)
            VALUES (:id, :code, :title, :year, :thumbnail1200x1200, :thumbnail300x300)
        """, dotdict_to_dict(album))
    yield sse(f"Inserted {len(preprod_data.albums)} albums")

    # Languages
    for lang in preprod_data.languages.values():
        cursor.execute("INSERT INTO songs_tag (id, name) VALUES (:id, :name)", {"id": lang.id, "name": lang.name})
    yield sse(f"Inserted {len(preprod_data.languages)} languages")

    # Artists
    for artist in preprod_data.artists.values():
        cursor.execute("""
            INSERT INTO songs_artist (id, name, thumbnail1200x1200, thumbnail300x300)
            VALUES (:id, :name, :thumbnail1200x1200, :thumbnail300x300)
        """, dotdict_to_dict(artist))
    yield sse(f"Inserted {len(preprod_data.artists)} artists")

    # Songs + relations
    for idx, song in enumerate(preprod_data.songs.values(), start=1):
        for lang in song.languages:
            cursor.execute("INSERT INTO songs_songtag (song_id, tag_id) VALUES (:song_id, :tag_id)",
                           {"song_id": song.id, "tag_id": lang.id})
        for artist in song.artists:
            cursor.execute("INSERT INTO songs_songartist (song_id, artist_id) VALUES (:song_id, :artist_id)",
                           {"song_id": song.id, "artist_id": artist.id})
        cursor.execute("""
            INSERT INTO songs_song (id, title, url, original_name, album_id, duration, lyrics, count, liked_count)
            VALUES (:id, :title, :url, :original_name, :album_id, :duration, :lyrics, :count, :liked_count)
        """, {
            "id": song.id,
            "title": song.title,
            "url": song.url,
            "original_name": song.original_name,
            "album_id": song.album.id,
            "duration": song.duration,
            "lyrics": f"lrc/{song.id}.lrc",
            "count": 0,
            "liked_count": 0
        })
        if idx % 10 == 0:
            yield sse(f"Processed {idx}/{len(preprod_data.songs)} songs")

    conn.commit()
    cursor.execute("VACUUM;")
    conn.close()
    yield sse("DB update complete!")

# ---------- SSE API View ---------- #
class UpdateFromPreprodSSEView(APIView):
    PREPROD_URL = CONFIG["PREPROD_DB_URL"]
    CURRENT_DB_PATH = "db.sqlite3"
    PREPROD_DB_PATH = "preprod.sqlite3"

    def get(self, request, *args, **kwargs):
        key = request.query_params.get("admin_actions_secret_key")
        if key != CONFIG["ADMIN_ACTIONS_SECRET_KEY"]:
            return Response({"detail": "Unauthorized"}, status=403)

        def event_stream():
            try:
                yield from download_file_with_log(self.PREPROD_URL, self.PREPROD_DB_PATH)
                # preprod JSON
                preprod_gen = preprod_to_json_with_log(self.PREPROD_DB_PATH)
                preprod_data = None
                for item in preprod_gen:
                    if isinstance(item, DotDict):
                        preprod_data = item
                    else:
                        yield item
                yield from update_db_from_preprod_with_log(preprod_data, self.CURRENT_DB_PATH)
                yield sse("All done! ✅")
            except Exception as e:
                yield sse(f"Error: {str(e)}")

        return StreamingHttpResponse(event_stream(), content_type="text/event-stream")
