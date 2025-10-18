from urllib.parse import quote
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.core.validators import FileExtensionValidator
from artist.models import Artist
from language.models import Language
from .models import Song
from storage import upload_file

class SongAdminForm(forms.ModelForm):
    mp3_file = forms.FileField(
        required=False,
        label="Upload MP3 File",
        validators=[FileExtensionValidator(allowed_extensions=['mp3'])]
    )
    
    artists = forms.ModelMultipleChoiceField(
        queryset=Artist.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(
            verbose_name='Artists',
            is_stacked=False
        )
    )

    languages = forms.ModelMultipleChoiceField(
        queryset=Language.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(
            verbose_name='Languages',
            is_stacked=False
        )
    )

    class Meta:
        model = Song
        fields = '__all__'


    def save(self, commit=True):
        instance = super().save(commit=False)

        mp3_file = self.cleaned_data.get('mp3_file')
        if mp3_file:
            album_code = instance.album.code  # Assuming the album model has a `code` field
            filename = f"{album_code} - {instance.original_name}.mp3"

            file_path = f'songs-file/{filename}'
            content = mp3_file.read()
            upload_file(file_path, content, f"Upload {filename}")
            instance.url = quote(file_path)
            instance.title = filename
            
        if commit:
            instance.save()

        return instance


    
