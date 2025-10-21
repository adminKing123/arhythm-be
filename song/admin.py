from urllib.parse import unquote
from django.utils.safestring import mark_safe
from django.contrib import admin
from .models import Song
from config import CONFIG
from .admin_forms import SongAdminForm
from utils import get_download_url
from storage import delete_file

@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    form = SongAdminForm

    list_display = ('original_name', 'album', 'count', 'liked_count', 'duration_formatted')
    search_fields = ('title', 'original_name', 'album__title', 'artists__name', 'album__actors__name', 'languages__name')
    autocomplete_fields = ['album']


    def get_fields(self, request, obj=None):
        if obj:
            return ['original_name', 'album', 'audio_preview', 'artists', 'languages', 'title', 'url', 'lyrics', 'duration', 'short_video_url', 'count', 'liked_count']
        return ['original_name', 'album', 'mp3_file', 'duration', 'short_video_url', 'artists', 'languages']

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['original_name', 'album', 'audio_preview', 'title', 'url', 'lyrics', 'duration', 'short_video_url', 'count', 'liked_count']
        return []
    
    def duration_formatted(self, obj):
        if obj.duration:
            minutes = int(obj.duration // 60)
            seconds = int(obj.duration % 60)
            return f"{minutes}:{seconds:02d}"
        return "-"    
    
    def audio_preview(self, obj):
        print(f'{CONFIG["MAIN_SRC_URL"]}{obj.url}')
        return mark_safe(f'<audio controls><source src="{get_download_url(obj.url)}" type="audio/mpeg"></audio>')

    duration_formatted.short_description = "Duration"

    def delete_model(self, request, obj):
        delete_file_path = unquote(obj.url)
        delete_file(delete_file_path, f"Delete {obj.title}")
        return super().delete_model(request, obj)

    class Media:
        js = ('js/mp3_duration.js', )
