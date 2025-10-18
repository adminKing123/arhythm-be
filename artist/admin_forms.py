from PIL import Image
from django import forms
from django.core.validators import FileExtensionValidator
from io import BytesIO
from artist.models import Artist
from storage import upload_file
from urllib.parse import quote

class ArtistAdminForm(forms.ModelForm):
    image_file = forms.FileField(
        required=False,
        label="Upload Image File (1:1 aspect ratio)",
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )

    class Meta:
        model = Artist  # Replace 'Artist' with the actual model you're using
        fields = '__all__'

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Handle the image file upload
        image_file = self.cleaned_data.get('image_file')
        if image_file:
            # Open the image
            img = Image.open(image_file)

            # Ensure the image has a 1:1 aspect ratio
            width, height = img.size
            if width != height:
                raise ValueError("The uploaded image must have a 1:1 aspect ratio.")

            # Resizing logic
            target_sizes = [(300, 300), (1200, 1200)]
            buffers = {}

            for size in target_sizes:
                resized_img = img.copy()

                # Resize image to the exact dimensions
                resized_img = resized_img.resize(size, Image.Resampling.LANCZOS)
                
                # Save resized image to buffer
                buffer = BytesIO()
                resized_img.save(buffer, format='PNG')
                buffer.seek(0)  # Reset buffer position
                buffers[size] = buffer

            # Upload to GitHub
            filename = f'{instance.name}.png'

            for size, buffer in buffers.items():
                file_path = f'artist-images/{size[0]}x{size[1]}/{filename}'
                buffer.seek(0)  # Ensure buffer is at the start for reading
                content = buffer.read()

                try:
                    upload_file(
                        file_path,
                        content,
                        f"Upload {filename} at size {size[0]}x{size[1]}"
                    )
                    instance.__setattr__(f'thumbnail{size[0]}x{size[1]}', quote(file_path))
                    print(f"Successfully uploaded {file_path} to GitHub.")
                except Exception as e:
                    print(f"Failed to upload {file_path} to GitHub: {e}")

        # Save the instance
        if commit:
            instance.save()
        return instance