from PIL import Image
from django import forms
from django.core.validators import FileExtensionValidator
from io import BytesIO
from album.models import Album
from storage import upload_file
from urllib.parse import quote

class AlbumAdminForm(forms.ModelForm):
    image_file = forms.FileField(
        required=False,
        label="Upload Image File (1:1 aspect ratio)",
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )

    class Meta:
        model = Album  
        fields = '__all__'

    def save(self, commit=True):
        instance = super().save(commit=False)
        image_file = self.cleaned_data.get('image_file')
        if image_file:
            
            img = Image.open(image_file)
   
            width, height = img.size
            if width != height:
                raise ValueError("The uploaded image must have a 1:1 aspect ratio.")
            
            target_sizes = [(300, 300), (1200, 1200)]
            buffers = {}

            for size in target_sizes:
                resized_img = img.copy()

                
                resized_img = resized_img.resize(size, Image.Resampling.LANCZOS)
                
                
                buffer = BytesIO()
                resized_img.save(buffer, format='PNG')
                buffer.seek(0)  
                buffers[size] = buffer

            filename = f'{instance.code} - {instance.title} ({instance.year}).png'
            for size, buffer in buffers.items():
                file_path = f'album-images/{size[0]}x{size[1]}/{filename}'
                buffer.seek(0)  
                content = buffer.read()
                upload_file(
                    file_path,
                    content,
                    f"Upload {filename} at size {size[0]}x{size[1]}"
                )
                instance.__setattr__(f'thumbnail{size[0]}x{size[1]}', quote(file_path))

        
        if commit:
            instance.save()
        return instance
