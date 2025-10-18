from django.db import models

# Create your models here.
class Artist(models.Model):
    name = models.CharField(max_length=255, null=False, unique=True)
    thumbnail300x300 = models.CharField(max_length=10000, null=False)
    thumbnail1200x1200 = models.CharField(max_length=10000, null=False)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.name