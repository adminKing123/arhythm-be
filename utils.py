from config import CONFIG

def get_download_url(file_path):
    return f'{CONFIG["MAIN_SRC_URL"]}{file_path}'

from actor.models import Actor
from album.models import Album
from artist.models import Artist
from language.models import Language
from song.models import Song


def get_database_as_dict():
    """
    Export database data to a Python dictionary.

    Preserves:
    - Primary keys
    - ForeignKey relationships
    - ManyToMany relationships
    - All fields currently required for database restoration

    Returns:
        dict: Complete database export.
    """

    data = {
        "actors": [],
        "artists": [],
        "languages": [],
        "albums": [],
        "songs": [],
    }

    
    for actor in Actor.objects.all():
        data["actors"].append({
            "id": actor.id,
            "name": actor.name,
            "thumbnail300x300": actor.thumbnail300x300,
            "thumbnail1200x1200": actor.thumbnail1200x1200,
        })

    
    for artist in Artist.objects.all():
        data["artists"].append({
            "id": artist.id,
            "name": artist.name,
            "thumbnail300x300": artist.thumbnail300x300,
            "thumbnail1200x1200": artist.thumbnail1200x1200,
        })

    
    for language in Language.objects.all():
        data["languages"].append({
            "id": language.id,
            "name": language.name,
        })

    
    for album in Album.objects.prefetch_related("actors"):
        data["albums"].append({
            "id": album.id,
            "code": album.code,
            "title": album.title,
            "year": album.year,
            "thumbnail300x300": album.thumbnail300x300,
            "thumbnail1200x1200": album.thumbnail1200x1200,

            # ManyToMany -> store Actor IDs
            "actors": list(
                album.actors.values_list("id", flat=True)
            ),
        })

    
    for song in Song.objects.prefetch_related(
        "artists",
        "languages",
    ):
        data["songs"].append({
            "id": song.id,
            "title": song.title,
            "url": song.url,
            "original_name": song.original_name,
            "lyrics": song.lyrics,
            "count": song.count,
            "liked_count": song.liked_count,
            "duration": song.duration,
            "short_video_url": song.short_video_url,

            # ForeignKey -> store ID
            "album_id": song.album_id,

            # ManyToMany -> store IDs
            "artists": list(
                song.artists.values_list("id", flat=True)
            ),

            "languages": list(
                song.languages.values_list("id", flat=True)
            ),
        })

    return data

