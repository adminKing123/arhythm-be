from django.db import models
from album.models import Album
from artist.models import Artist
from language.models import Language

# Create your models here.
class Song(models.Model):
    title = models.CharField(max_length=255, unique=True, null=False)
    url = models.CharField(max_length=10000, null=False)
    original_name = models.CharField(max_length=255, null=False)
    lyrics = models.CharField(max_length=10000, null=False)
    count = models.PositiveBigIntegerField(default=0)
    liked_count = models.PositiveBigIntegerField(default=0)
    duration = models.FloatField(default=0, null=True, blank=True)
    short_video_url = models.CharField(max_length=500, null=True, blank=True)

    # Relationships
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='songs')
    artists = models.ManyToManyField(Artist, related_name='songs')
    languages = models.ManyToManyField(Language, related_name='songs')

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.original_name