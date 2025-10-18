from django.contrib import admin
from .models import Artist
from .admin_forms import ArtistAdminForm
from utils import get_download_url
from django.utils.safestring import mark_safe
from urllib.parse import unquote
from storage import delete_file

# Register your models here.
@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    form = ArtistAdminForm
    list_display = ('name',)
    search_fields = ('name',)

    def get_fields(self, request, obj=None):
        if obj:
            return ['name', 'thumbnail300x300', 'thumbnail1200x1200', 'custom_thumbnailpreview']
        else:
            return ['name', 'image_file']

        
    def get_readonly_fields(self, request, obj):
        if obj:
            return ['name', 'thumbnail300x300', 'thumbnail1200x1200', 'custom_thumbnailpreview']
        else:
            return ['thumbnail300x300', 'thumbnail1200x1200']
        
    def custom_thumbnailpreview(self, obj):
        link = f'{get_download_url(obj.thumbnail300x300)}'  # Generate the full URL
        return mark_safe(f'<img src="{link}" alt="{obj.name}" width="300" height="300" style="border: 1px solid var(--border-color);border-radius:4px;" />')
    

    def delete_model(self, request, obj):
        delete_file_path_300 = unquote(obj.thumbnail300x300)
        delete_file(delete_file_path_300, f"Delete thumbnail300x300 for {obj.name}")        
        delete_file_path_1200 = unquote(obj.thumbnail1200x1200)
        delete_file(delete_file_path_1200, f"Delete thumbnail1200x1200 for {obj.name}")
        return super().delete_model(request, obj)
    
