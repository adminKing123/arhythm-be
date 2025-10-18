from django.contrib import admin
from .models import Album
from .admin_forms import AlbumAdminForm
from utils import get_download_url
from django.utils.safestring import mark_safe
from urllib.parse import unquote
from storage import delete_file

# Register your models here.
@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    form = AlbumAdminForm

    list_display = ('title', 'year', 'code')
    search_fields = ('title', 'code', 'actors__name')

    def get_fields(self, request, obj=None):
        if obj:
            return ['code', 'title', 'year', 'thumbnail300x300', 'thumbnail1200x1200', 'actors', 'custom_thumbnailpreview']
        else:
            return ['code', 'title', 'year', 'image_file', 'actors']
        
    def get_readonly_fields(self, request, obj):
        if obj:
            return ['code', 'title', 'year', 'thumbnail300x300', 'thumbnail1200x1200', 'custom_thumbnailpreview']
        else:
            return ['thumbnail300x300', 'thumbnail1200x1200']
        
    def custom_thumbnailpreview(self, obj):
        link = f'{get_download_url(obj.thumbnail300x300)}'
        return mark_safe(f'<img src="{link}" alt="{obj.title}" width="300" height="300" style="border: 1px solid var(--border-color);border-radius:4px;" />')
    
    def delete_model(self, request, obj):
        delete_file_path_300 = unquote(obj.thumbnail300x300)
        delete_file(delete_file_path_300, f"Delete thumbnail300x300 for {obj.title}")
        delete_file_path_1200 = unquote(obj.thumbnail1200x1200)
        delete_file(delete_file_path_1200, f"Delete thumbnail1200x1200 for {obj.title}")
        return super().delete_model(request, obj)